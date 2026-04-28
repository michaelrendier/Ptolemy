# Ptolemy

**Modular Python3 research and engineering platform.**  
Author: michaelrendier | Branch: `main` | Status: Active development — private pre-release

---

## Overview

Ptolemy is a personal software system built around the Library of Alexandria as an organizational metaphor. Each major capability is called a **Face**, named after a historical figure associated with the Library. The system has been in active development since 2010.

Current focus areas:
- **HyperWebster** — a 180,000-word lexical acquisition and addressing pipeline (Callimachus)
- **LLM model experimentation** — Julius Caesar, Cicero, Cato corpus (Philadelphos / SMNNIP)
- **Kryptos addressing** — Horner bijection + octonion addresses via Cayley-Dickson construction
- **Aulë** — diagnostic forge / sandbox face for live stream monitoring and experimental code

The neural architecture (SMNNIP — Standard Model of Neural Network Information Propagation) is referenced here by name and links to the [Ainulindalë Conjecture](https://github.com/michaelrendier/Ainulindale) repository for structural/mathematical history. The model itself is withheld pending publication and peer review.

---

## Faces

| Face | Historical Figure | Responsibility |
|---|---|---|
| [Alexandria](Alexandria/) | Library of Alexandria | OpenGL visualization experiments |
| [Anaximander](Anaximander/) | Anaximander of Miletus | Navigation and travel |
| [Archimedes](Archimedes/) | Archimedes of Syracuse | Mathematics, science, signal processing |
| [Aulë](Aule/) | Aulë the Smith *(Ainulindalë)* | Sandbox diagnostic forge — stream monitoring, experimental runner, REPL |
| [Callimachus](Callimachus/) | Callimachus of Cyrene | Archival, database, HyperWebster acquisition |
| [Kryptos](Kryptos/) | *Kryptos* (hidden) | Encryption, HyperWebster addressing, Kryptos Complexity Factor |
| [Mouseion](Mouseion/) | The Mouseion | Flask website — thewanderinggod.tech |
| [Phaleron](Phaleron/) | Port of Phaleron | Internal search |
| [Pharos](Pharos/) | Pharos Lighthouse | Core functions, main shell UI |
| [Philadelphos](Philadelphos/) | Ptolemy II Philadelphos | AI / LLM layer — Claude (Ainur), Gemini, Agora dual-chat |
| [Tesla](Tesla/) | Nikola Tesla | Device interfacing |
| [Ptolemy++](Ptolemy++/) | — | C++ port for performance-critical components |

---

## Hardware

Ptolemy is designed to run on the following system. See [docs/Hardware/](docs/Hardware/) for the full specification report.

| | |
|---|---|
| **Machine** | HP EliteBook 820 G3 |
| **OS** | Linux Mint 22.1 Xia — kernel 6.8.0-110-lowlatency |
| **CPU** | Intel Core i7-6600U — Skylake, 2 cores / 4 threads @ 400MHz–3.4GHz |
| **RAM** | 8 GiB (7.64 GiB available) |
| **GPU** | Intel HD Graphics 520 (Skylake GT2) — Mesa 25.2.8, OpenGL 4.6 |
| **Storage** | 953 GiB NVMe SSD (Timetec MS10) + 111 GiB Samsung 840 EVO |
| **Audio** | Intel Sunrise Point-LP HD Audio — ALSA / PipeWire / JACK |
| **Display** | 1366×768 @ 60Hz, 12.5" |

---

## Documentation

All face documentation lives in [docs/](docs/). GitHub handles version control — documents reflect the state of the code at time of commit.

### Kryptos
| Document | Description |
|---|---|
| [KCF-1 — Kryptos Complexity Factor](docs/Kryptos/KCF-1_Kryptos_Complexity_Factor.docx) | Formal specification of the KCF encryption strength metric — analogous to NIST FIPS / RFC publications |
| [KCF-1-BM — Benchmark Report](docs/Kryptos/KCF-1-BM_Benchmark_Report.docx) | Live benchmarks vs MD5, SHA-256, SHA-512, SHA3-256, AES-128/256, ChaCha20, RSA-2048/4096, PBKDF2 |
| [Repository Preparation & Secret Management](docs/Kryptos/Kryptos_Repository_Preparation.docx) | git history scrub procedure, .env pattern, pre-release checklist |

### Aulë
| Document | Description |
|---|---|
| [Aulë Face Documentation](docs/Aule/Aule_Face_Documentation.docx) | StreamMonitor, Forge, ReplayEngine, Probe — architecture and usage |

### Hardware
| Document | Description |
|---|---|
| [System Hardware Report](docs/Hardware/Ptolemy_Hardware_Report.docx) | Full hardware specification — HP EliteBook 820 G3, inxi output, capability analysis |

---

## Environment Variables

See [.env.example](.env.example) for the full list. Critical variables:

| Variable | Purpose |
|---|---|
| `PTOL_TOKEN` | GitHub PAT — Ptolemy repo management |
| `AINUR_TOKEN` | GitHub PAT — Ainulindalë repo access |
| `ANTHROPIC_API_KEY` | Claude API — Philadelphos/Ainur |
| `GEMINI_API_KEY` | Google Gemini API — Philadelphos/Gemini |
| `HYPER_KEY` | HyperWebster charset permutation — Kryptos addressing key |

**Tokens ≠ API keys.** Never cross-use them. See [Kryptos Repository Preparation](docs/Kryptos/Kryptos_Repository_Preparation.docx) for secret management.

---

## Session Context

Claude Code sessions: read [CONTEXT.md](CONTEXT.md) at session start to restore full context.

---

## LSH Model — Lagrange Self-Adjoint Hyperindexing

The neural model powering Philadelphos is designated **LSH** — Lagrange Self-Adjoint Hyperindexing Model.

| Component | Description |
|---|---|
| **Lagrangian** | Variational path optimization through semantic space — inference finds its own optimal path |
| **Self-Adjoint** | Model is its own measurement. No external validator — output is self-consistent under adjoint check. Maps to blockchain-as-truth-source principle |
| **Hyperindexing** | The emergent layer. Not engineered — recognized during structure constant experimentation. 8-component octonion addresses derived from Cayley-Dickson construction |

Hyperindexing is the feature, not a component. The self-adjoint property ties directly to the octonion algebra used in hyperindex addresses.

---

## LuthSpell — BUS Controller

`luthspell.py` lives at the root layer above all Faces. It is not a Face.

| Component | Role |
|---|---|
| **LuthSpell** | Ptolemy's BUS controller — T0/T1 priority arbitration, rotary semaphore (traffic circle, not binary gate) |
| **HaltingMonitor** | Internal sensing organ of LuthSpell — watches inference coordinates for halt conditions |
| **ErrorHandler** | Catches, classifies, routes all Ptolemy errors — 27 typed errors across 8 subsystems |
| **GarbageCollector** | Triggered by ErrorHandler on gc_trigger errors — C++ RAII mirror deferred to Ptolemy++ |

Bus math: `Priority` is `IntEnum` — ordering is lexicographic `(priority, timestamp)`. T0 always before T1, FIFO within tier.

### Error Catalog

| Range | Subsystem |
|---|---|
| PTL_1xx | BUS |
| PTL_2xx | LuthSpell / Halting |
| PTL_3xx | Cyclic Context Buffer |
| PTL_4xx | Blockchain |
| PTL_5xx | Acquisition / HyperWebster |
| PTL_6xx | LSH Model |
| PTL_7xx | Module / Settings |
| PTL_9xx | System / Root |

`RabiesViolation` (PTL_504): FATAL, **no GC** — `first_encountered` is permanently immutable. Violation is logical, not memory-based. Audit, do not clean up.

---

## Cyclic Context Buffer

`Philadelphos/cyclic_context_buffer.py` — FIFO sliding window context management.

- Unit: **lines** (one `EntryObject` = one `PromptObject` + one `ResponseObject`)
- **Confirmed eviction**: Entry stays in buffer until compress → octonion hyperindex → blockchain commit all succeed. No index manipulation during iteration.
- Evicted entries compressed to L2, hyperindexed (8-component octonion address), committed to branch blockchain
- All backends modular — swappable via Settings tab

---

## Modular Architecture Principle

**Modular EVERYTHING.** Every component is a swappable module. Every hole left by modularity gets a Settings page/tab under a Modules parent category. This is a load-bearing design principle, not a preference.

Current Settings hooks (all stub → real implementation pending):
`buffer_size_lines` · `compression_model` · `hyperindex_method` · `blockchain_backend` · `priority_scheme` · `gc_on_fatal` · `gc_on_error` · `log_backend` · `report_to_ptolemy_severity` · `halt_evaluation_logic`

---

## Related Repositories

| Repo | Description |
|---|---|
| [Ainulindalë](https://github.com/michaelrendier/Ainulindale) | Structural and mathematical history of the SMNNIP development. The naming system (Valar, Ainulindalë) originates here. |

---

## License

Private pre-release. Open source publication planned following SMNNIP peer review.  
Neural architecture (SMNNIP) excluded from open-source release pending publication.
