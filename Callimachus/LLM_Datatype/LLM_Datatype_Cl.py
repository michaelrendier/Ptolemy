"""
hyperwebster.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The HyperWebster — A Full-Spectrum Word Datatype
Each word is a pixel. Behind each pixel lives a complete spectra.

Conceived jointly by a human, Gemini, and Claude.
Inspired by the James Webb Space Telescope's spectral depth per pixel,
Demotic tonal glyphs, and the Zork sentence parser tradition.

The DEMOTIC TONE GLYPH
━━━━━━━━━━━━━━━━━━━━━━
In Demotic script, the leading character signals the contextual 'tone' of a
word — not its phoneme, but its *mood* or register.  We encode this as an
invisible Unicode tag character prepended to each token.  Human readers see
nothing.  LLMs reading the raw bytes or embeddings will find it.

Glyph map (Unicode Tag block, U+E0000–U+E007F — invisible in all renderers):
  𝄞  NEUTRAL       → U+E0020  (tag space)
  𝄟  POSITIVE      → U+E0021  (tag !)
  𝄠  NEGATIVE      → U+E0022  (tag ")
  𝄡  AMBIGUOUS     → U+E0023  (tag #)
  𝄢  FORMAL        → U+E0024  (tag $)
  𝄣  ARCHAIC       → U+E0025  (tag %)
  𝄤  TECHNICAL     → U+E0026  (tag &)
  𝄥  EMBODIED      → U+E0027  (tag ')
  𝄦  TABOO         → U+E0028  (tag ()
  𝄧  EMERGENT      → U+E0029  (tag ))

These are prepended to SemanticWord.token_glyphed — the glyph-bearing form
that LLMs should prefer when indexing or embedding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# ENUMERATIONS
# ─────────────────────────────────────────────────────────────────────────────

class Sentiment(Enum):
    NEUTRAL   = 0
    POSITIVE  = 1
    NEGATIVE  = 2
    AMBIGUOUS = 3


class ContextualTone(Enum):
    """
    Demotic-inspired leading-glyph tone categories.
    Each maps to an invisible Unicode Tag character (U+E0020–U+E0029).
    LLMs read the glyph; humans never see it.
    """
    NEUTRAL   = "\U000E0020"   # tag SPACE
    POSITIVE  = "\U000E0021"   # tag !
    NEGATIVE  = "\U000E0022"   # tag "
    AMBIGUOUS = "\U000E0023"   # tag #
    FORMAL    = "\U000E0024"   # tag $
    ARCHAIC   = "\U000E0025"   # tag %
    TECHNICAL = "\U000E0026"   # tag &
    EMBODIED  = "\U000E0027"   # tag '
    TABOO     = "\U000E0028"   # tag (
    EMERGENT  = "\U000E0029"   # tag )


class PartOfSpeech(Enum):
    NOUN        = "noun"
    VERB        = "verb"
    ADJECTIVE   = "adjective"
    ADVERB      = "adverb"
    PRONOUN     = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION= "interjection"
    DETERMINER  = "determiner"
    PARTICLE    = "particle"
    UNKNOWN     = "unknown"


class AspectClass(Enum):
    """Aktionsart / lexical aspect — primarily for verbs."""
    STATIVE    = "stative"     # know, believe, own
    DYNAMIC    = "dynamic"     # run, build, eat
    TELIC      = "telic"       # finish, arrive (has natural endpoint)
    ATELIC     = "atelic"      # walk, swim (no natural endpoint)
    PUNCTUAL   = "punctual"    # sneeze, blink (instantaneous)
    UNKNOWN    = "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# SUB-DATACLASSES  (Gemini originals + Claude additions, merged & deduplicated)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Etymology:
    """Diachronic history of the word."""
    root_language: str = "unknown"
    original_meaning: str = ""
    evolution_timeline: List[str] = field(default_factory=list)
    first_attested: Optional[str] = None          # e.g. "circa 1350"
    semantic_drift_notes: List[str] = field(default_factory=list)
    cognates: Dict[str, str] = field(default_factory=dict)   # lang → cognate


@dataclass
class PhonologicalProfile:
    """How the word sounds, feels in the mouth, and sits in the ear."""
    phoneme_sequence: List[str] = field(default_factory=list)  # IPA
    syllable_count: int = 0
    syllable_structure: List[str] = field(default_factory=list) # e.g. ["CVC","CV"]
    stress_pattern: str = ""            # e.g. "10" = stress on first syllable
    rhyme_group: List[str] = field(default_factory=list)
    alliteration_sound: str = ""        # onset phoneme
    phonetic_neighbors: List[str] = field(default_factory=list) # minimal pairs
    articulatory_features: List[str] = field(default_factory=list)
    # e.g. ["bilabial","plosive","voiced"]
    auditory_resonance: Optional[str] = None     # Gemini: phonetic 'weight'
    mouth_feel: Optional[str] = None             # e.g. "clipped", "liquid", "explosive"
    prosodic_weight: Optional[str] = None        # "light" | "heavy"


@dataclass
class OrthographicProfile:
    """How the word looks on the page."""
    character_count: int = 0
    visual_word_shape: str = ""         # ascender/descender silhouette e.g. "xhxlx"
    bigram_frequency_band: Optional[str] = None   # "high"|"mid"|"low"
    orthographic_neighbors: List[str] = field(default_factory=list)
    is_compound: bool = False
    is_portmanteau: bool = False
    is_abbreviation: bool = False
    typical_case_form: str = "lowercase"  # "lowercase"|"titlecase"|"uppercase"


@dataclass
class MorphologicalProfile:
    """Internal word structure."""
    root_stem: str = ""
    prefixes: List[str] = field(default_factory=list)
    suffixes: List[str] = field(default_factory=list)
    morpheme_count: int = 1
    word_family: List[str] = field(default_factory=list)   # derivational relatives
    inflectional_variants: Dict[str, str] = field(default_factory=dict)
    # e.g. {"plural":"dogs","past":"ran"}
    derivational_productivity: Optional[str] = None  # "high"|"low"|"frozen"


@dataclass
class SyntacticProfile:
    """Grammatical behaviour in sentences."""
    primary_pos: PartOfSpeech = PartOfSpeech.UNKNOWN
    secondary_pos: List[PartOfSpeech] = field(default_factory=list)
    valency: Optional[int] = None          # 0=intrans, 1=trans, 2=ditrans
    argument_structure: List[str] = field(default_factory=list)
    selectional_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    # e.g. {"subject":["animate"],"object":["liquid"]}
    phrase_head_tendency: Optional[str] = None  # "head"|"dependent"
    grammatical_gender: Optional[str] = None
    countability: Optional[str] = None         # "count"|"mass"|"both"
    aspect_class: AspectClass = AspectClass.UNKNOWN
    discourse_marker_role: Optional[str] = None  # "connective"|"hedge"|None
    anaphoric_potential: bool = False
    cataphoric_potential: bool = False
    given_vs_new_bias: Optional[str] = None   # "given"|"new"|"neutral"


@dataclass
class SemanticLayer:
    """Meaning in all its dimensions."""
    # Gemini originals
    denotation: str = ""
    connotations: List[str] = field(default_factory=list)
    synonyms: Set[str] = field(default_factory=set)
    antonyms: Set[str] = field(default_factory=set)
    idiomatic_uses: List[str] = field(default_factory=list)

    # Claude additions
    sense_inventory: List[Dict[str, str]] = field(default_factory=list)
    # [{"sense_id":"1a","definition":"...","domain":"..."}]
    semantic_field: List[str] = field(default_factory=list)
    hypernyms: List[str] = field(default_factory=list)
    hyponyms: List[str] = field(default_factory=list)
    meronyms: List[str] = field(default_factory=list)       # parts-of
    holonyms: List[str] = field(default_factory=list)       # wholes-of
    metaphorical_extensions: List[str] = field(default_factory=list)
    semantic_frame: Optional[str] = None      # FrameNet frame name
    schema_membership: List[str] = field(default_factory=list)
    # e.g. ["restaurant_script","cooking_schema"]
    semantic_bleaching_level: Optional[str] = None  # "full"|"partial"|"none"
    prototype_example: Optional[str] = None


@dataclass
class PragmaticProfile:
    """How the word functions in actual use."""
    register: List[str] = field(default_factory=list)
    # e.g. ["formal","legal","archaic"]
    connotation_valence: Optional[str] = None    # "positive"|"negative"|"neutral"
    emotional_weight: Optional[float] = None     # 0.0–1.0
    politeness_level: Optional[str] = None       # "honorific"|"neutral"|"blunt"|"taboo"
    implicature_tendencies: List[str] = field(default_factory=list)
    speech_act_associations: List[str] = field(default_factory=list)
    # e.g. ["request","assertion"]
    hedging_strength: Optional[float] = None     # 0.0=hedge, 1.0=assert


@dataclass
class SensoryProfile:
    """Embodied and sensory resonance of the word."""
    # Gemini originals
    visual_associations: List[str] = field(default_factory=list)
    auditory_resonance: Optional[str] = None
    tactile_texture: Optional[str] = None
    scent_memory: List[str] = field(default_factory=list)

    # Claude additions
    taste_associations: List[str] = field(default_factory=list)
    primary_modality: Optional[str] = None  # dominant sense: "visual"|"tactile" etc.
    imageability_score: Optional[float] = None  # 0.0–7.0 (MRC norms scale)
    concreteness_score: Optional[float] = None  # 0.0–7.0
    arousal_score: Optional[float] = None       # PAD model
    valence_score: Optional[float] = None       # PAD model
    dominance_score: Optional[float] = None     # PAD model
    motor_associations: List[str] = field(default_factory=list)
    # e.g. ["reach","grasp","throw"]


@dataclass
class StatisticalProfile:
    """Corpus and psycholinguistic statistics."""
    corpus_frequency_rank: Optional[int] = None
    zipf_value: Optional[float] = None          # 1–7 scale
    age_of_acquisition: Optional[float] = None  # years
    familiarity_rating: Optional[float] = None  # psycholinguistic score
    domain_frequencies: Dict[str, float] = field(default_factory=dict)
    # e.g. {"medicine":0.001,"sport":0.04}
    surprisal_baseline: Optional[float] = None  # bits, average context
    burstiness: Optional[str] = None            # "bursty"|"uniform"
    reading_fixation_probability: Optional[float] = None  # 0.0–1.0


@dataclass
class SociolinguisticProfile:
    """Who says it, where, and to whom."""
    regional_variants: Dict[str, str] = field(default_factory=dict)
    # e.g. {"US":"trunk","UK":"boot"} (car boot)
    sociolect_associations: List[str] = field(default_factory=list)
    gender_marking: Optional[str] = None         # "masculine"|"feminine"|"neutral"|"marked"
    in_group_marker: bool = False
    taboo_status: Optional[str] = None           # None|"mild"|"strong"|"reclaimed"
    translation_gaps: Dict[str, str] = field(default_factory=dict)
    # lang → note on untranslatable nuance
    neologism_flag: bool = False
    archaism_level: Optional[str] = None         # "current"|"dated"|"archaic"|"obsolete"
    cultural_moment: Optional[str] = None        # e.g. "COVID-era spike 2020"


@dataclass
class AssociativeProfile:
    """The word's web of free associations and collocations."""
    free_associations: List[str] = field(default_factory=list)
    collocations: List[str] = field(default_factory=list)
    collocations_left: List[str] = field(default_factory=list)   # words that precede it
    collocations_right: List[str] = field(default_factory=list)  # words that follow it
    idiom_membership: List[str] = field(default_factory=list)
    cliche_flag: bool = False


@dataclass
class PersonalResonance:
    """
    The 'Ptolemy' layer — how the word exists in a specific mind or model.
    For an LLM: the training-corpus encounter history and emergent salience.
    For a human: autobiographical memory anchors.
    """
    # Gemini originals
    usage_frequency: int = 0
    first_encountered: Optional[datetime] = None
    linked_memories: List[str] = field(default_factory=list)
    subjective_sentiment: Sentiment = Sentiment.NEUTRAL
    associated_people: List[str] = field(default_factory=list)

    # Claude additions — the "journey" layer
    first_use_context: Optional[str] = None      # sentence/situation of first use
    automagical_placement_events: List[str] = field(default_factory=list)
    # moments the word surfaced unprompted — the brain knowing more than the speaker
    resonance_evolution: List[Tuple[str, str]] = field(default_factory=list)
    # [(timestamp_str, note)] — how personal meaning has shifted over time
    learning_source: Optional[str] = None        # "corpus"|"conversation"|"finetuning"
    confidence_score: float = 0.0               # model's confidence in its own entry


# ─────────────────────────────────────────────────────────────────────────────
# THE DEMOTIC GLYPH ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def assign_demotic_tone(word: "SemanticWord") -> ContextualTone:
    """
    Heuristically assign a Demotic contextual tone glyph based on the word's
    profiles.  This is intentionally lightweight — the full model will learn
    to refine these assignments.
    """
    sem = word.semantics
    prag = word.pragmatics
    socio = word.sociolinguistic

    if socio.taboo_status in ("strong",):
        return ContextualTone.TABOO
    if socio.archaism_level in ("archaic", "obsolete"):
        return ContextualTone.ARCHAIC
    if socio.neologism_flag:
        return ContextualTone.EMERGENT
    if prag.register and any(r in prag.register for r in ("technical","jargon","scientific")):
        return ContextualTone.TECHNICAL
    if prag.register and any(r in prag.register for r in ("formal","legal","academic")):
        return ContextualTone.FORMAL
    if prag.connotation_valence == "positive":
        return ContextualTone.POSITIVE
    if prag.connotation_valence == "negative":
        return ContextualTone.NEGATIVE
    if word.sensory.imageability_score and word.sensory.imageability_score > 5.0:
        return ContextualTone.EMBODIED
    if sem.sense_inventory and len(sem.sense_inventory) > 3:
        return ContextualTone.AMBIGUOUS
    return ContextualTone.NEUTRAL


# ─────────────────────────────────────────────────────────────────────────────
# THE HYPERWEBSTER WORD  — the core datatype
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SemanticWord:
    """
    A full-spectrum word entry for the HyperWebster.

    token           : the plain word, lowercased and stripped
    token_glyphed   : the word prefixed with an invisible Demotic tone glyph
                      for LLM consumption.  Human readers see nothing extra.

    All sub-profiles are optional at construction time; the acquisition
    pipeline fills them in progressively.
    """

    # ── Core identity ──────────────────────────────────────────────────────
    token: str = ""
    token_glyphed: str = field(default="", init=False)  # set in __post_init__

    # ── Gemini's linguistic_category, now typed ────────────────────────────
    linguistic_category: str = "unknown"   # kept as str for legacy compat

    # ── The full spectral layers ────────────────────────────────────────────
    semantics:      SemanticLayer       = field(default_factory=SemanticLayer)
    etymology:      Etymology           = field(default_factory=Etymology)
    phonology:      PhonologicalProfile = field(default_factory=PhonologicalProfile)
    orthography:    OrthographicProfile = field(default_factory=OrthographicProfile)
    morphology:     MorphologicalProfile= field(default_factory=MorphologicalProfile)
    syntax:         SyntacticProfile    = field(default_factory=SyntacticProfile)
    pragmatics:     PragmaticProfile    = field(default_factory=PragmaticProfile)
    sensory:        SensoryProfile      = field(default_factory=SensoryProfile)
    statistics:     StatisticalProfile  = field(default_factory=StatisticalProfile)
    sociolinguistic:SociolinguisticProfile = field(default_factory=SociolinguisticProfile)
    associations:   AssociativeProfile  = field(default_factory=AssociativeProfile)
    resonance:      PersonalResonance   = field(default_factory=PersonalResonance)

    # ── Vector representation (Phaleron indexing) ───────────────────────────
    embedding_coordinates: List[float] = field(default_factory=list)

    # ── Demotic tone glyph (assigned post-init) ─────────────────────────────
    contextual_tone: ContextualTone = field(default=ContextualTone.NEUTRAL, init=False)

    # ── Cross-references (Phaleron's web) ───────────────────────────────────
    related_tokens: Dict[str, str] = field(default_factory=dict)
    # {word: relationship_type}  e.g. {"cold":"antonym","frigid":"near-synonym"}

    # ── Provenance ──────────────────────────────────────────────────────────
    acquired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    acquisition_sources: List[str] = field(default_factory=list)
    version: int = 1

    def __post_init__(self):
        self.token = self.token.strip().lower()
        # orthography gets character count automatically
        if self.token and not self.orthography.character_count:
            self.orthography.character_count = len(self.token)
        # assign Demotic tone glyph
        self.contextual_tone = assign_demotic_tone(self)
        # build the glyph-prefixed token
        self.token_glyphed = self.contextual_tone.value + self.token

    def reglyph(self) -> None:
        """Recompute the Demotic glyph after profiles have been populated."""
        self.contextual_tone = assign_demotic_tone(self)
        self.token_glyphed = self.contextual_tone.value + self.token

    def to_json(self, indent: int = 2) -> str:
        """Serialise to JSON.  Handles sets and enums."""
        def _default(obj: Any) -> Any:
            if isinstance(obj, set):
                return sorted(obj)
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Unserializable: {type(obj)}")
        return json.dumps(asdict(self), default=_default, indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str | dict) -> "SemanticWord":
        """Deserialise from JSON string or dict.  Reconstructs enums, sets, and dataclasses."""
        if isinstance(data, str):
            data = json.loads(data)

        _DC_MAP = {
            "semantics":       SemanticLayer,
            "etymology":       Etymology,
            "phonology":       PhonologicalProfile,
            "orthography":     OrthographicProfile,
            "morphology":      MorphologicalProfile,
            "syntax":          SyntacticProfile,
            "pragmatics":      PragmaticProfile,
            "sensory":         SensoryProfile,
            "statistics":      StatisticalProfile,
            "sociolinguistic": SociolinguisticProfile,
            "associations":    AssociativeProfile,
            "resonance":       PersonalResonance,
        }

        def _rebuild(dc_class, raw: dict):
            """Best-effort reconstruction — only passes known fields."""
            import dataclasses
            known = {f.name for f in dataclasses.fields(dc_class)}
            kwargs: dict = {}
            for k, v in raw.items():
                if k not in known:
                    continue
                # Reconstruct sets
                if dc_class is SemanticLayer and k in ("synonyms", "antonyms"):
                    v = set(v) if isinstance(v, list) else v
                # Reconstruct Sentiment enum
                if dc_class is PersonalResonance and k == "subjective_sentiment":
                    try:
                        v = Sentiment(v)
                    except (ValueError, KeyError):
                        v = Sentiment.NEUTRAL
                # Reconstruct PartOfSpeech enum
                if dc_class is SyntacticProfile and k == "primary_pos":
                    try:
                        v = PartOfSpeech(v)
                    except (ValueError, KeyError):
                        v = PartOfSpeech.UNKNOWN
                # Reconstruct AspectClass enum
                if dc_class is SyntacticProfile and k == "aspect_class":
                    try:
                        v = AspectClass(v)
                    except (ValueError, KeyError):
                        v = AspectClass.UNKNOWN
                kwargs[k] = v
            return dc_class(**kwargs)

        # Build the SemanticWord with reconstructed sub-dataclasses
        w = cls(token=data.get("token", ""))
        for field_name, dc_class in _DC_MAP.items():
            raw_sub = data.get(field_name)
            if isinstance(raw_sub, dict):
                object.__setattr__(w, field_name, _rebuild(dc_class, raw_sub))

        # Restore remaining plain fields
        for plain in ("linguistic_category", "embedding_coordinates",
                      "related_tokens", "acquired_at", "acquisition_sources", "version"):
            if plain in data:
                object.__setattr__(w, plain, data[plain])

        w.reglyph()
        return w

    def summary(self) -> str:
        """Human-readable one-liner for quick inspection."""
        tone_name = self.contextual_tone.name
        pos = self.syntax.primary_pos.value if self.syntax.primary_pos else self.linguistic_category
        denotation = (self.semantics.denotation or "")[:80]
        return (
            f"[{tone_name}] '{self.token}' ({pos}) — {denotation}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# THE HYPERWEBSTER COLLECTION  — a typed dict of SemanticWord objects
# ─────────────────────────────────────────────────────────────────────────────

class HyperWebster(dict):
    """
    A dictionary of SemanticWord objects keyed by plain token.
    Acts exactly like a Python dict but enforces value type and provides
    HyperWebster-specific methods.

    Usage:
        hw = HyperWebster()
        hw["horizon"] = SemanticWord(token="horizon", ...)
        hw.save("hyperwebster.json")
        hw2 = HyperWebster.load("hyperwebster.json")
    """

    def __setitem__(self, key: str, value: SemanticWord) -> None:
        if not isinstance(value, SemanticWord):
            raise TypeError(f"HyperWebster values must be SemanticWord, got {type(value)}")
        super().__setitem__(key.strip().lower(), value)

    def save(self, path: str) -> None:
        payload = {k: json.loads(v.to_json()) for k, v in self.items()}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"  ✓  HyperWebster saved → {path}  ({len(self)} entries)")

    @classmethod
    def load(cls, path: str) -> "HyperWebster":
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        hw = cls()
        for token, data in raw.items():
            hw[token] = SemanticWord.from_json(data)
        print(f"  ✓  HyperWebster loaded ← {path}  ({len(hw)} entries)")
        return hw

    def by_tone(self, tone: ContextualTone) -> "HyperWebster":
        """Return a sub-HyperWebster of words matching a given Demotic tone."""
        result = HyperWebster()
        for k, v in self.items():
            if v.contextual_tone == tone:
                result[k] = v
        return result
