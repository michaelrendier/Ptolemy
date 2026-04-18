#!/usr/bin/env python3
"""
acquire.py
══════════════════════════════════════════════════════════════════════════════
HyperWebster Acquisition Pipeline
Ptolemy Project — Pharos/Philadelphos

Reads a dictionary file (one word per line), queries public APIs and
Wikipedia for linguistic data, and writes one SemanticWord JSON file per
word into a sharded directory structure:

    output_dir/
        words_a/abandon.json
        words_a/aberrant.json
        ...
        words_z/zenith.json
        words_other/   ← non-alpha first char (numerics, punctuation, etc.)

Data sources (in order per word):
    1. Free Dictionary API  — definitions, phonetics, POS, etymology
    2. Datamuse API         — synonyms, antonyms, related words, collocations
    3. Wikipedia (lxml)     — etymology, semantic context, usage notes

Rate limiting and bot-avoidance:
    - Realistic randomised delays between requests
    - Firefox user-agent (required by Wikipedia)
    - Per-domain request throttling
    - Automatic resume: already-written word files are skipped

Usage:
    python3 acquire.py words.txt --output ./lexicon
    python3 acquire.py words_a.txt --output ./lexicon --delay-min 1.2 --delay-max 3.5
    python3 acquire.py words.txt --output ./lexicon --dry-run --limit 5

Arguments:
    dictionary      Path to word list file (one word per line)
    --output        Output directory (default: ./lexicon)
    --delay-min     Minimum seconds between requests (default: 1.0)
    --delay-max     Maximum seconds between requests (default: 2.5)
    --limit         Only process first N words (for testing)
    --dry-run       Parse and validate words, don't hit any APIs
    --resume        Skip words whose output files already exist (default: True)
    --no-resume     Force re-acquisition even if file exists
    --log           Log file path (default: acquire.log)
    --wikipedia     Enable Wikipedia scraping (default: True)
    --no-wikipedia  Skip Wikipedia (faster, fewer requests)

Author: Ptolemy project
Compatible: Python 3.10+
Dependencies: see requirements_acquire.txt
"""

import argparse
import json
import logging
import os
import random
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import quote as urlquote

import requests
from lxml import html as lxmlhtml
from lxml import etree

# ── Import the SemanticWord datatype ─────────────────────────────────────────
# acquire.py is expected to live alongside LLM_Datatype_Cl.py in Pharos/Philadelphos.
# If it's run from a different directory, set PYTHONPATH accordingly.
try:
    from LLM_Datatype_Cl import (
        SemanticWord, HyperWebster, ContextualTone,
        PartOfSpeech, AspectClass, Sentiment,
        SemanticLayer, Etymology, PhonologicalProfile,
        OrthographicProfile, MorphologicalProfile,
        SyntacticProfile, PragmaticProfile, SensoryProfile,
        StatisticalProfile, SociolinguisticProfile,
        AssociativeProfile, PersonalResonance,
    )
    DATATYPE_AVAILABLE = True
except ImportError:
    print("ERROR: LLM_Datatype_Cl.py not found in Python path.")
    print("Run from the same directory as LLM_Datatype_Cl.py, or:")
    print("  export PYTHONPATH=/path/to/Pharos/Philadelphos:$PYTHONPATH")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"

# User-agent that Wikipedia accepts without flagging
FIREFOX_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) "
    "Gecko/20100101 Firefox/124.0"
)

# API endpoints
FREE_DICT_API   = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
DATAMUSE_API    = "https://api.datamuse.com/words"
WIKIPEDIA_API   = "https://en.wikipedia.org/w/api.php"
WIKTIONARY_API  = "https://en.wiktionary.org/w/api.php"

# Datamuse relation codes
# ml=means like, rel_syn=synonyms, rel_ant=antonyms,
# rel_trg=triggers, lc=left context, rc=right context
DATAMUSE_SYNONYMS    = "rel_syn"
DATAMUSE_ANTONYMS    = "rel_ant"
DATAMUSE_SIMILAR     = "ml"
DATAMUSE_TRIGGERS    = "rel_trg"
DATAMUSE_COLLOCATES_L = "lc"
DATAMUSE_COLLOCATES_R = "rc"

# Per-domain minimum gap in seconds between requests
DOMAIN_GAPS = {
    "api.dictionaryapi.dev": 0.5,
    "api.datamuse.com":      0.3,
    "en.wikipedia.org":      1.5,
    "en.wiktionary.org":     1.5,
}

INCOMPLETE_FLAG = "__incomplete__"


# ══════════════════════════════════════════════════════════════════════════════
# Rate limiter — per-domain throttle
# ══════════════════════════════════════════════════════════════════════════════

class DomainThrottle:
    """
    Tracks the last request time per domain and enforces a minimum gap.
    Thread-safety not required — this is a single-threaded sequential script.
    """
    def __init__(self):
        self._last: Dict[str, float] = {}

    def wait(self, domain: str, extra_jitter: float = 0.0) -> None:
        min_gap = DOMAIN_GAPS.get(domain, 0.5)
        elapsed = time.time() - self._last.get(domain, 0.0)
        gap = min_gap + extra_jitter
        if elapsed < gap:
            time.sleep(gap - elapsed)
        self._last[domain] = time.time()


throttle = DomainThrottle()


# ══════════════════════════════════════════════════════════════════════════════
# HTTP session — shared across all requests
# ══════════════════════════════════════════════════════════════════════════════

def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": FIREFOX_UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/html, */*;q=0.8",
    })
    return session


SESSION = build_session()


def get_json(url: str, params: dict = None, domain: str = None,
             jitter: float = 0.0, timeout: int = 10) -> Optional[Any]:
    """GET request returning parsed JSON, or None on any failure."""
    d = domain or _domain(url)
    throttle.wait(d, jitter)
    try:
        r = SESSION.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None   # word not found — normal
        logging.warning(f"HTTP {r.status_code} for {url}")
        return None
    except requests.RequestException as e:
        logging.warning(f"Request failed {url}: {e}")
        return None


def get_html(url: str, params: dict = None, domain: str = None,
             jitter: float = 0.0, timeout: int = 12) -> Optional[lxmlhtml.HtmlElement]:
    """GET request returning parsed lxml HTML tree, or None on failure."""
    d = domain or _domain(url)
    throttle.wait(d, jitter)
    try:
        r = SESSION.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return lxmlhtml.fromstring(r.content)
        logging.warning(f"HTTP {r.status_code} for {url}")
        return None
    except requests.RequestException as e:
        logging.warning(f"Request failed {url}: {e}")
        return None


def _domain(url: str) -> str:
    """Extract bare domain from a URL string."""
    return url.split("/")[2] if "/" in url else url


# ══════════════════════════════════════════════════════════════════════════════
# Source 1 — Free Dictionary API
# ══════════════════════════════════════════════════════════════════════════════

def fetch_free_dict(word: str) -> Optional[dict]:
    """
    Returns the first entry dict from Free Dictionary API, or None.

    Response structure (simplified):
      [{
        "word": ...,
        "phonetic": ...,
        "phonetics": [{"text": ..., "audio": ...}],
        "meanings": [{
            "partOfSpeech": ...,
            "definitions": [{"definition":..., "example":..., "synonyms":[], "antonyms":[]}],
            "synonyms": [],
            "antonyms": []
        }],
        "etymology": ...    ← not always present at top level
      }]
    """
    url = FREE_DICT_API.format(word=urlquote(word))
    data = get_json(url, domain="api.dictionaryapi.dev", jitter=random.uniform(0, 0.3))
    if not data or not isinstance(data, list):
        return None
    return data[0]


def parse_free_dict(entry: dict, sw: SemanticWord) -> SemanticWord:
    """Populate SemanticWord fields from a Free Dictionary API entry."""
    if not entry:
        return sw

    # ── Phonology ────────────────────────────────────────────────────────────
    phonetic_text = entry.get("phonetic", "")
    phonetics = entry.get("phonetics", [])
    if not phonetic_text and phonetics:
        phonetic_text = next(
            (p.get("text", "") for p in phonetics if p.get("text")), "")

    if phonetic_text:
        # IPA stored as a list of individual phoneme symbols
        sw.phonology.phoneme_sequence = list(phonetic_text.strip("/[]"))
        sw.phonology.syllable_count = phonetic_text.count("ˈ") + phonetic_text.count("ˌ") + 1

    # ── Meanings → SemanticLayer + SyntacticProfile ──────────────────────────
    meanings = entry.get("meanings", [])
    if not meanings:
        return sw

    all_definitions = []
    all_synonyms    = set()
    all_antonyms    = set()
    pos_list        = []

    for meaning in meanings:
        pos_str = meaning.get("partOfSpeech", "").lower()
        pos_enum = _str_to_pos(pos_str)
        pos_list.append(pos_enum)

        # Collect synonyms/antonyms at meaning level
        all_synonyms.update(meaning.get("synonyms", []))
        all_antonyms.update(meaning.get("antonyms", []))

        for defn in meaning.get("definitions", []):
            definition_text = defn.get("definition", "")
            example_text    = defn.get("example", "")

            if definition_text:
                sense = {
                    "sense_id":  f"{pos_str}_{len(all_definitions)+1}",
                    "definition": definition_text,
                    "domain":    "",
                    "example":   example_text,
                    "pos":       pos_str,
                }
                all_definitions.append(sense)

            # Collect synonyms/antonyms at definition level too
            all_synonyms.update(defn.get("synonyms", []))
            all_antonyms.update(defn.get("antonyms", []))

    # Primary definition = first one
    if all_definitions:
        sw.semantics.denotation = all_definitions[0]["definition"]
        sw.semantics.sense_inventory = all_definitions
        # Idiomatic uses: pick examples as a lightweight stand-in
        sw.semantics.idiomatic_uses = [
            s["example"] for s in all_definitions if s.get("example")]

    sw.semantics.synonyms = all_synonyms
    sw.semantics.antonyms = all_antonyms

    if pos_list:
        sw.syntax.primary_pos = pos_list[0]
        sw.syntax.secondary_pos = pos_list[1:]

    # ── Etymology (top-level field, present on some entries) ─────────────────
    etym = entry.get("etymology", "")
    if etym:
        sw.etymology.semantic_drift_notes = [etym]

    sw.acquisition_sources.append("free_dictionary_api")
    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Source 2 — Datamuse API
# ══════════════════════════════════════════════════════════════════════════════

def _datamuse_query(rel_code: str = None, word: str = "",
                    ml: str = None, limit: int = 20) -> List[str]:
    """Return list of word strings from a Datamuse query."""
    params: dict = {"max": limit}
    if rel_code:
        params[rel_code] = word
    if ml:
        params["ml"] = ml
    data = get_json(DATAMUSE_API, params=params,
                    domain="api.datamuse.com", jitter=random.uniform(0, 0.2))
    if not data:
        return []
    return [item["word"] for item in data if "word" in item]


def fetch_datamuse(word: str, sw: SemanticWord) -> SemanticWord:
    """Query Datamuse for synonyms, antonyms, collocates, triggers."""

    synonyms  = _datamuse_query(rel_code=DATAMUSE_SYNONYMS, word=word)
    antonyms  = _datamuse_query(rel_code=DATAMUSE_ANTONYMS, word=word)
    triggers  = _datamuse_query(rel_code=DATAMUSE_TRIGGERS, word=word, limit=15)
    collocL   = _datamuse_query(rel_code=DATAMUSE_COLLOCATES_L, word=word, limit=10)
    collocR   = _datamuse_query(rel_code=DATAMUSE_COLLOCATES_R, word=word, limit=10)

    # Merge into existing sets (Free Dict may have already seeded these)
    sw.semantics.synonyms.update(synonyms)
    sw.semantics.antonyms.update(antonyms)

    # Free associations = triggers
    sw.associations.free_associations = triggers

    # Collocations
    sw.associations.collocations_left  = collocL
    sw.associations.collocations_right = collocR

    if synonyms or antonyms or triggers:
        sw.acquisition_sources.append("datamuse_api")

    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Source 3 — Wiktionary (lxml scrape)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_wiktionary(word: str, sw: SemanticWord) -> SemanticWord:
    """
    Scrape Wiktionary for etymology and IPA pronunciation.
    Uses the Wiktionary action=parse API to get rendered HTML,
    then lxml to pull specific sections.
    """
    params = {
        "action":   "parse",
        "page":     word,
        "prop":     "text",
        "section":  "0",      # lead section — often has etymology + pronunciation
        "format":   "json",
        "disabletoc": "1",
    }
    data = get_json(WIKTIONARY_API, params=params,
                    domain="en.wiktionary.org", jitter=random.uniform(0.2, 0.6))

    if not data:
        return sw

    try:
        html_text = data["parse"]["text"]["*"]
    except (KeyError, TypeError):
        return sw

    tree = lxmlhtml.fromstring(html_text)

    # ── Etymology ─────────────────────────────────────────────────────────────
    etym_paras = tree.xpath(
        '//h3[.//span[@id="Etymology"] or .//span[contains(@id,"Etymology")]]'
        '/following-sibling::p[1]'
    )
    if not etym_paras:
        # Try h4 variant
        etym_paras = tree.xpath(
            '//h4[.//span[contains(@id,"Etymology")]]'
            '/following-sibling::p[1]'
        )

    if etym_paras:
        etym_text = etym_paras[0].text_content().strip()
        if etym_text and etym_text not in sw.etymology.semantic_drift_notes:
            sw.etymology.semantic_drift_notes.append(etym_text)
            # Attempt crude root language extraction
            # "From Old French ...", "From Latin ...", "From Proto-Germanic ..."
            lang_match = re.search(
                r'[Ff]rom\s+(Old\s+\w+|Middle\s+\w+|Proto-\w+|Ancient\s+\w+|\w+)',
                etym_text)
            if lang_match and not sw.etymology.root_language:
                sw.etymology.root_language = lang_match.group(1)

    # ── IPA / Pronunciation ───────────────────────────────────────────────────
    ipa_spans = tree.xpath('//span[@class="IPA"]')
    if ipa_spans and not sw.phonology.phoneme_sequence:
        raw_ipa = ipa_spans[0].text_content().strip().strip("/[]")
        sw.phonology.phoneme_sequence = list(raw_ipa)

    sw.acquisition_sources.append("wiktionary")
    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Source 4 — Wikipedia summary (optional, flag-controlled)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_wikipedia_summary(word: str, sw: SemanticWord) -> SemanticWord:
    """
    Pull the first paragraph of a Wikipedia article for the word.
    Used to supplement SemanticLayer.denotation for proper nouns
    and Class 4 compound terms. Skipped for pure function words.

    Wikipedia is picky about user-agent. The session already sends
    Firefox UA, which is accepted.
    """
    params = {
        "action":     "query",
        "titles":     word,
        "prop":       "extracts",
        "exintro":    True,
        "exsentences": 3,       # first 3 sentences only
        "explaintext": True,
        "format":     "json",
    }
    data = get_json(WIKIPEDIA_API, params=params,
                    domain="en.wikipedia.org", jitter=random.uniform(0.3, 0.9))
    if not data:
        return sw

    try:
        pages = data["query"]["pages"]
        page  = next(iter(pages.values()))
        if "missing" in page:
            return sw
        extract = page.get("extract", "").strip()
    except (KeyError, StopIteration):
        return sw

    if extract:
        # If denotation is empty, use the Wikipedia extract
        if not sw.semantics.denotation:
            sw.semantics.denotation = extract[:500]
        # Store full extract as a connotation/contextual note
        sw.semantics.connotations.append(f"[Wikipedia] {extract[:300]}")
        sw.acquisition_sources.append("wikipedia")

    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Orthographic + morphological auto-population (no network required)
# ══════════════════════════════════════════════════════════════════════════════

def populate_orthography(word: str, sw: SemanticWord) -> SemanticWord:
    """Derive orthographic profile from the word string alone."""
    sw.orthography.character_count = len(word)

    # Visual word shape: x=lowercase, X=uppercase, h=tall (b,d,f,h,k,l,t),
    # p=descender (g,j,p,q,y)
    shape = []
    for ch in word:
        if ch.isupper():
            shape.append("X")
        elif ch in "bdfhklt":
            shape.append("h")
        elif ch in "gjpqy":
            shape.append("p")
        else:
            shape.append("x")
    sw.orthography.visual_word_shape = "".join(shape)

    # Compound flag — naive heuristic: contains hyphen or known compound markers
    sw.orthography.is_compound = ("-" in word)

    # Abbreviation flag — all caps and length ≤ 5
    sw.orthography.is_abbreviation = (word.isupper() and len(word) <= 5)

    # Typical case form
    if word[0].isupper() and not word.isupper():
        sw.orthography.typical_case_form = "titlecase"
    elif word.isupper():
        sw.orthography.typical_case_form = "uppercase"
    else:
        sw.orthography.typical_case_form = "lowercase"

    return sw


def populate_morphology_basic(word: str, sw: SemanticWord) -> SemanticWord:
    """
    Populate morphology fields with what we can derive heuristically.
    A proper morphological analyser (spaCy, NLTK) can enrich this later.
    """
    common_prefixes = [
        "un", "re", "in", "im", "ir", "il", "dis", "mis", "non", "pre",
        "pro", "anti", "auto", "bi", "co", "de", "ex", "hyper", "inter",
        "micro", "mid", "multi", "over", "post", "semi", "sub", "super",
        "trans", "under",
    ]
    common_suffixes = [
        "tion", "sion", "ness", "ment", "ity", "ism", "ist", "ous", "ful",
        "less", "able", "ible", "al", "ial", "ic", "ical", "ive", "ative",
        "ize", "ise", "ify", "ly", "er", "or", "age", "ance", "ence",
        "ship", "hood", "ward", "wise",
    ]
    w = word.lower()
    found_prefixes = [p for p in common_prefixes if w.startswith(p) and len(w) > len(p)+2]
    found_suffixes = [s for s in common_suffixes if w.endswith(s) and len(w) > len(s)+2]

    sw.morphology.prefixes = found_prefixes[:2]   # take at most 2
    sw.morphology.suffixes  = found_suffixes[:2]
    sw.morphology.morpheme_count = 1 + len(found_prefixes) + len(found_suffixes)

    # Root stem: crude — strip longest matching suffix
    stem = w
    for sfx in sorted(found_suffixes, key=len, reverse=True):
        if stem.endswith(sfx):
            stem = stem[:-len(sfx)]
            break
    sw.morphology.root_stem = stem

    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Statistical profile — basic corpus stats (no network)
# ══════════════════════════════════════════════════════════════════════════════

def populate_statistics_basic(word: str, sw: SemanticWord) -> SemanticWord:
    """
    Assign a rough Zipf-like estimate based on word length and character
    frequency. This is a placeholder — a proper corpus frequency table
    (e.g. from SUBTLEX or BNC) can replace this later.

    Zipf scale: 1=rare, 7=extremely common ("the").
    """
    # Very rough heuristic — short common words score high
    length = len(word)
    if length <= 3:
        zipf = 6.0
    elif length <= 5:
        zipf = 5.0
    elif length <= 8:
        zipf = 4.0
    elif length <= 12:
        zipf = 3.0
    else:
        zipf = 2.0

    sw.statistics.zipf_value = zipf
    return sw


# ══════════════════════════════════════════════════════════════════════════════
# POS string → PartOfSpeech enum
# ══════════════════════════════════════════════════════════════════════════════

def _str_to_pos(pos_str: str) -> PartOfSpeech:
    mapping = {
        "noun":         PartOfSpeech.NOUN,
        "verb":         PartOfSpeech.VERB,
        "adjective":    PartOfSpeech.ADJECTIVE,
        "adverb":       PartOfSpeech.ADVERB,
        "pronoun":      PartOfSpeech.PRONOUN,
        "preposition":  PartOfSpeech.PREPOSITION,
        "conjunction":  PartOfSpeech.CONJUNCTION,
        "interjection": PartOfSpeech.INTERJECTION,
        "determiner":   PartOfSpeech.DETERMINER,
        "particle":     PartOfSpeech.PARTICLE,
    }
    return mapping.get(pos_str.lower(), PartOfSpeech.UNKNOWN)


# ══════════════════════════════════════════════════════════════════════════════
# Incomplete flag
# ══════════════════════════════════════════════════════════════════════════════

def mark_completeness(sw: SemanticWord) -> SemanticWord:
    """
    Set a flag in the PersonalResonance.learning_source field if key
    fields are empty, so a future enrichment pass can target these files.
    Uses a sentinel string that a filter script can grep for.

    Fields considered 'key' for skeleton completeness:
      - semantics.denotation
      - syntax.primary_pos (not UNKNOWN)
      - phonology.phoneme_sequence (not empty)
      - etymology.root_language (not 'unknown')
    """
    incomplete_fields = []
    if not sw.semantics.denotation:
        incomplete_fields.append("denotation")
    if sw.syntax.primary_pos == PartOfSpeech.UNKNOWN:
        incomplete_fields.append("pos")
    if not sw.phonology.phoneme_sequence:
        incomplete_fields.append("phonemes")
    if sw.etymology.root_language in ("unknown", ""):
        incomplete_fields.append("etymology")

    if incomplete_fields:
        sw.resonance.learning_source = f"{INCOMPLETE_FLAG}:{','.join(incomplete_fields)}"
    else:
        sw.resonance.learning_source = "acquired"

    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Output path resolution
# ══════════════════════════════════════════════════════════════════════════════

def output_path(word: str, output_dir: Path) -> Path:
    """
    Return the full path for a word's JSON file.
    words_a/abandon.json, words_other/42nd.json, etc.
    """
    first = word[0].lower() if word else "_"
    if first.isalpha():
        subdir = output_dir / f"words_{first}"
    else:
        subdir = output_dir / "words_other"
    subdir.mkdir(parents=True, exist_ok=True)
    # Sanitize word for use as filename (handles edge cases like slashes)
    safe = re.sub(r'[^\w\-.]', '_', word)
    return subdir / f"{safe}.json"


# ══════════════════════════════════════════════════════════════════════════════
# Core acquisition function — one word
# ══════════════════════════════════════════════════════════════════════════════

def acquire_word(word: str, use_wikipedia: bool = True,
                 delay_min: float = 1.0, delay_max: float = 2.5) -> SemanticWord:
    """
    Full acquisition pipeline for a single word.
    Returns a populated SemanticWord (may be partial — check completeness flag).
    """
    word = word.strip()
    sw = SemanticWord(token=word)
    sw.acquisition_sources = []

    # ── 1. Free Dictionary API ────────────────────────────────────────────────
    fd_entry = fetch_free_dict(word)
    if fd_entry:
        sw = parse_free_dict(fd_entry, sw)

    # ── 2. Datamuse ───────────────────────────────────────────────────────────
    sw = fetch_datamuse(word, sw)

    # ── 3. Wiktionary ─────────────────────────────────────────────────────────
    sw = fetch_wiktionary(word, sw)

    # ── 4. Wikipedia (optional) ───────────────────────────────────────────────
    if use_wikipedia:
        sw = fetch_wikipedia_summary(word, sw)

    # ── 5. Local derivations (no network) ────────────────────────────────────
    sw = populate_orthography(word, sw)
    sw = populate_morphology_basic(word, sw)
    sw = populate_statistics_basic(word, sw)

    # ── 6. Reglyph (Demotic tone) after all data is in ────────────────────────
    sw.reglyph()

    # ── 7. Completeness flag ──────────────────────────────────────────────────
    sw = mark_completeness(sw)

    # ── 8. Human-facing random delay (bot avoidance) ─────────────────────────
    time.sleep(random.uniform(delay_min, delay_max))

    return sw


# ══════════════════════════════════════════════════════════════════════════════
# Progress tracking
# ══════════════════════════════════════════════════════════════════════════════

class Progress:
    """Simple terminal progress display."""
    def __init__(self, total: int):
        self.total   = total
        self.done    = 0
        self.skipped = 0
        self.failed  = 0
        self.start   = time.time()

    def update(self, word: str, status: str) -> None:
        self.done += 1
        elapsed = time.time() - self.start
        rate = self.done / elapsed if elapsed > 0 else 0
        eta  = (self.total - self.done) / rate if rate > 0 else 0
        pct  = 100 * self.done / self.total
        bar_len = 30
        filled  = int(bar_len * self.done / self.total)
        bar     = "█" * filled + "░" * (bar_len - filled)
        print(
            f"\r[{bar}] {pct:5.1f}% | "
            f"{self.done}/{self.total} | "
            f"{rate:.1f} w/s | "
            f"ETA {eta/60:.0f}m | "
            f"{status:12s} {word[:20]:<20}",
            end="", flush=True
        )

    def final(self) -> None:
        elapsed = time.time() - self.start
        print(f"\n\nDone. {self.done} words in {elapsed/60:.1f} min.")
        print(f"  Skipped (already existed): {self.skipped}")
        print(f"  Failed/empty:              {self.failed}")
        print(f"  Acquired:                  {self.done - self.skipped - self.failed}")


# ══════════════════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════════════════

def load_word_list(path: Path, limit: Optional[int]) -> List[str]:
    """Read word list, strip blanks and comments, apply limit."""
    words = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            w = line.strip()
            if w and not w.startswith("#"):
                words.append(w)
    if limit:
        words = words[:limit]
    return words


def run_acquisition(
    dictionary_path: Path,
    output_dir:      Path,
    delay_min:       float = 1.0,
    delay_max:       float = 2.5,
    resume:          bool  = True,
    use_wikipedia:   bool  = True,
    dry_run:         bool  = False,
    limit:           Optional[int] = None,
    log_path:        str   = "acquire.log",
) -> None:

    # ── Logging setup ─────────────────────────────────────────────────────────
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info(f"acquire.py v{VERSION} started")
    logging.info(f"Dictionary: {dictionary_path}")
    logging.info(f"Output:     {output_dir}")
    logging.info(f"Wikipedia:  {use_wikipedia}")

    # ── Load word list ─────────────────────────────────────────────────────────
    words = load_word_list(dictionary_path, limit)
    total = len(words)
    print(f"acquire.py v{VERSION}")
    print(f"Dictionary: {dictionary_path}  ({total} words)")
    print(f"Output:     {output_dir}")
    print(f"Wikipedia:  {'yes' if use_wikipedia else 'no'}")
    print(f"Resume:     {'yes' if resume else 'no'}")
    if dry_run:
        print(f"DRY RUN — no network requests will be made.\n")

    output_dir.mkdir(parents=True, exist_ok=True)
    progress = Progress(total)

    for word in words:
        out = output_path(word, output_dir)

        # ── Resume logic ──────────────────────────────────────────────────────
        if resume and out.exists():
            progress.skipped += 1
            progress.update(word, "SKIP")
            logging.debug(f"SKIP {word}")
            continue

        if dry_run:
            progress.update(word, "DRY-RUN")
            continue

        # ── Acquire ───────────────────────────────────────────────────────────
        try:
            sw = acquire_word(
                word,
                use_wikipedia=use_wikipedia,
                delay_min=delay_min,
                delay_max=delay_max,
            )
            # Write JSON
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(sw.to_json(indent=2))
            status = "INCOMPLETE" if INCOMPLETE_FLAG in (sw.resonance.learning_source or "") else "OK"
            progress.update(word, status)
            logging.info(f"{status} {word} → {out.name} sources={sw.acquisition_sources}")

        except Exception as e:
            progress.failed += 1
            progress.update(word, "FAIL")
            logging.error(f"FAIL {word}: {e}", exc_info=True)

    progress.final()
    logging.info("acquire.py finished")


# ══════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="HyperWebster Acquisition Pipeline — acquire.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Acquire full dictionary into ./lexicon
  python3 acquire.py english_a.txt --output ./lexicon

  # Test with 10 words, no Wikipedia
  python3 acquire.py english_a.txt --output ./lexicon --limit 10 --no-wikipedia

  # Resume an interrupted run
  python3 acquire.py english_a.txt --output ./lexicon

  # Force re-acquire even if files exist
  python3 acquire.py english_a.txt --output ./lexicon --no-resume
        """
    )
    parser.add_argument(
        "dictionary",
        type=Path,
        help="Path to word list file (one word per line)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("./lexicon"),
        help="Output directory (default: ./lexicon)"
    )
    parser.add_argument(
        "--delay-min",
        type=float,
        default=1.0,
        help="Minimum seconds between words (default: 1.0)"
    )
    parser.add_argument(
        "--delay-max",
        type=float,
        default=2.5,
        help="Maximum seconds between words (default: 2.5)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only first N words"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse word list only, no network requests"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Skip words whose output files already exist (default)"
    )
    parser.add_argument(
        "--no-resume",
        action="store_false",
        dest="resume",
        help="Re-acquire even if file already exists"
    )
    parser.add_argument(
        "--wikipedia",
        action="store_true",
        default=True,
        help="Enable Wikipedia scraping (default)"
    )
    parser.add_argument(
        "--no-wikipedia",
        action="store_false",
        dest="wikipedia",
        help="Skip Wikipedia (faster)"
    )
    parser.add_argument(
        "--log",
        default="acquire.log",
        help="Log file path (default: acquire.log)"
    )

    args = parser.parse_args()

    if not args.dictionary.exists():
        print(f"ERROR: Dictionary file not found: {args.dictionary}")
        sys.exit(1)

    run_acquisition(
        dictionary_path = args.dictionary,
        output_dir      = args.output,
        delay_min       = args.delay_min,
        delay_max       = args.delay_max,
        resume          = args.resume,
        use_wikipedia   = args.wikipedia,
        dry_run         = args.dry_run,
        limit           = args.limit,
        log_path        = args.log,
    )


if __name__ == "__main__":
    main()
