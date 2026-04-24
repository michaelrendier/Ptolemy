# PTOLEMY CONTEXT PRIMER
# Generated: 2026-04-24 | Commit: 51da51d
# Push this file to repo root as CONTEXT_PRIMER.md

## STRICT PROTOCOLS (do not relist, acknowledge only at entry)
- Least token/context intensive responses
- Signature every response: [timestamp | context% | repo commit | cache path]
- Alert at 50% context remaining, ask about new primer at 85%
- No unqualified medical/psych determinations, no time-passage assumptions
- Never re-clone repo if /home/claude/Ptolemy exists this session
- GitHub PAT: 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

## HARDWARE
- HP Elitebook 820 G3 i7 HD520 Skylake / Linux Mint Xia + UbuntuStudioInstaller
- Microsoft Surface Go 1824 / Ubuntu 24.04 linux-surface kernel — PRIMARY REPO DEVICE

## REPO STATE (commit 51da51d)
Files changed this session:
- Pharos/PGui.py — PWindow.__init__ overloaded for face_id/bus/ptolemy (PtolBus.launch() compatible)
- Philadelphos/ptolemy_ears.py — NEW: PtolemyEars QWidget, SedenionGate off-thread, speak_text()
- Philadelphos/ptolemy_tongue.py — NEW: fold-geometry output filter (pentagon/hex chromatography)
  - char-level repeat collapse (MAX_REPEAT=8)
  - word-level run collapse (MAX_WORD_RUN=5) — added after smoke test caught word repeat gap
  - punct storm reduction, bracket depth check, control char strip, unicode NFC
  - FoldGeometry analyser, pentagon_ratio advisory flag
- Philadelphos/Phila.py — Phila QWidget face class added (response display + ears embedded)
- Callimachus/hyperwebster_layer3.py — NEW: ContextBuffer Layer3 → HyperWebster JSON shard bridge
  - WordRecord with Rabies Principle (first_encountered immutable)
  - Atomic file writes (tmp+rename), shard dirs words_a/..z/+other
- Ainulindale/core/noether_chain_input.py — Layer3 stub replaced with live bridge + lazy import

## IMMEDIATE NEXT TASK
Patch smnnip_inversion_engine.py from Drive:
  Drive file: 1IEX5S5j7LNUwvYauOxEVrJxP98_-EUpn (patched, 43654 bytes)
  Repo file:  Ainulindale/core/smnnip_inversion_engine.py (currently 39501 bytes)
  Key addition: two-Noether-current docstring clarification (geometric vs gauge)
  NoetherMonitor docstring now explicitly labels which current lives in which file

Steps:
  1. base64-decode Drive blob → write to Ainulindale/core/smnnip_inversion_engine.py
  2. python3 -c "import ast; ast.parse(...)" smoke test
  3. Run smnnip_test_pure.py
  4. git add + commit + push

## AINULINDALE DRIVE FOLDER (read-only prefilter)
Root:        18O-dD-_giAeUdCeyv8kylzyukIB0VFTO
Code folder: 1ZkistnAFGj-anUfJNoHQ2zc8CkP9drIl
Patched:     1LUsMeZVVdMKs3cRsXRBvuOHQnFGqNkgJ
  - derivation:  12dPP0yCC47ZnrCr3mV9Pcej1LF0tTKGG (71386 bytes = repo, no update needed)
  - inversion:   1IEX5S5j7LNUwvYauOxEVrJxP98_-EUpn (43654 bytes > repo 39501, NEEDS PATCH)
Noether:     1NlLgjbx6nYglSThXnXFcTULA1b5Wuqom
Synth:       1wnGBolQp2F4gUnV4UMduiBsNLHQ5nfv3
Sonification: 1SkD8Jpg88P69aITN6pTqZ7AwOhynaL0M

## BUILD PHASES (active)
Phase 2 — DONE: PWindow bus/face_id wiring
Phase 3 — DONE: ptolemy_ears + Phila QWidget face
Phase 4 — DONE: HyperWebster Layer3 bridge (hyperwebster_layer3.py)
Phase 5 (tongue) — DONE: ptolemy_tongue fold geometry filter
Pending: inversion engine patch from Drive

## KEY ARCHITECTURE NOTES
- PtolBus.launch() → PWindow(face, title=..., face_id=..., bus=..., ptolemy=...)
- ptolemy_ears pipeline: text/speech → SedenionGate (off-thread) → _generate_response() → tongue → display
- _generate_response() is a stub: wire to NEURAL_ARCHITECTURE.infer() when model loaded
- tongue filter order: strip_controls → normalise_unicode → collapse_repeats → collapse_word_runs → reduce_punct_storms → wrap_long_lines → pentagon_ratio advisory
- Layer3 bridge: lazy import, non-fatal if Callimachus absent, atomic writes
- Rabies Principle: first_encountered in WordRecord is PERMANENTLY IMMUTABLE

## SMNNIP STATE
- derivation engine: ACTIVE, all 7 ops pass, conserved=True
- inversion engine: PATCHED in Drive, needs repo update
- gap: 0.00070 (real, open — no closed form yet)
- D_STAR_SPEC = 0.24600 (BK spectral, ACTIVE)
- D_STAR_TAUT = Omega/ln(10) — REFERENCE ONLY, NOT d*

## PTOLEMY3.py
All top-level imports verified present. PtolBus + PWindow + Phila scope resolved.
Philadelphos: inline Phila() preferred, fallback to Pharos.Philadelphos.CommandInput

## HYPERWEBSTER
acquire.py exists. 180k dict ready to split → 26 files.
words_a/..z/ shard structure defined in hyperwebster_layer3.py.
Layer3 bridge wired but HyperWebster root needs to exist on local machine.
