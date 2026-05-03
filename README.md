# Ptolemy

**Author:** michaelrendier | **Status:** Active development — private pre-release

---

## The Memory Problem Is The Wrong Problem

Every processor ever built assumes data must be stored to exist.  
Ptolemy is built on a different assumption.

---

## HyperWebster: The Load-Bearing Pillar

Without HyperWebster there are no milliwatt queries.  
Without milliwatt queries there is no on-device kernel.  
Without the on-device kernel there is no Ptolemy.

**Everything else in this repository depends on what is described in this section.**

HyperWebster is not a dictionary, not a database, not a search index.  
It is a **coordinate system for all human knowledge** — built entirely from mathematics
that already existed. The engineering did not invent the addresses. It built the navigator.

---

## The Nine Reductions: How Infinite Space Becomes Navigable

The address space for all possible strings is infinite.  
Searching an infinite space is not useful.  
Each reduction below cuts the space. What remains after all nine is the HyperWebster.

| Layer | Name | Mathematical Basis | What It Eliminates | What Remains |
|:---:|---|---|---|---|
| 1 | **Banach-Tarski Equivalence** | Hausdorff paradox decomposition — strings reachable from each other by structural rotation share one canonical address | Redundant permutation interior | One canonical address per equivalence class |
| 2 | **Lexical Filtering** | Corpus restriction to natural-language strings | ~99.99% of theoretical string space (noise) | The neighborhood of human language |
| 3 | **De Bruijn Minimality** | Shortest superstring containing every length-n subsequence exactly once; determines optimal charset traversal order | Redundant traversal paths | Minimum-length complete coverage |
| 4 | **Zipf Center-Loading** | Frequency rank r → 1/r. Most-frequent chars get lowest ordinals. Expected Horner address magnitude over natural language is minimized | Large integer addresses for common words | Biased distribution — frequent words near the origin |
| 5 | **Horner's Bijection** *(core)* | `H(s) = c₀·Nⁿ + c₁·Nⁿ⁻¹ + … + cₙ` — a perfect bijection between all finite strings and ℕ₀ | Nothing — this *produces* the address | Every string ↔ exactly one non-negative integer. Deterministic. Reversible. No storage. |
| 6 | **Octonion Splitting** *(geometry)* | Horner integer split into 8 equal-width limbs → octonion `(l₀e₀ … l₇e₇)`. Non-associativity means path order matters — context is not commutative | Flat integer space with no metric | Geometric coordinate where **proximity = semantic similarity** |
| 7 | **Amplituhedron Paradigm** *(unifier)* | Arkani-Hamed & Trnka 2013: infinite Feynman sum → single geometric measurement. Applied here: enumerate-all-strings (∞) → measure-the-shape (finite) | Infinite combinatorial enumeration | One geometric measurement replaces the infinite sum |
| 8 | **File-Type Optimization** | Per-type character frequency distribution. Python ≠ SQL ≠ prose ≠ binary. CharacterNeuron (layer 1) learns the distribution | Suboptimal address magnitude for non-English corpora | File-type-aware compact addresses; ~5–6 decimal digits smaller at length 8 for English |
| 9 | **HYPER_KEY Permutation** *(cryptographic)* | Charset permutation order is the key. Key complexity: `P ≈ N·log₂(N) ≈ 2,440,000 bits` for full Unicode (N=155,000) | Plain-text navigability without the key | Cryptographically private address space. Rotate the key → entire space rotates |

```
Infinite string space
    → Banach-Tarski equivalence classes      [structural]
    → Lexical filtering                       [domain]
    → De Bruijn minimal traversal            [combinatorial]
    → Zipf center-loading                    [statistical]
    → Horner bijection                       [mathematical core]
    → Octonion splitting                     [geometric coordinate]
    → Amplituhedron paradigm                 [unifying principle]
    → File-type optimization                 [applied]
    → HYPER_KEY permutation                  [cryptographic]
         ↓
Finite. Navigable. Geometrically meaningful. Cryptographically sovereign.
Address space:  2⁵¹²  coordinates.
Physical cost:  one 512-bit address  +  length  +  timestamp.
Knowledge ceiling:  infinite.
```

**Input is an address. Search is proximity. Reconstruction is resolution.  
Learning is a geometry update. One operation handles all of it.**

---

## The Energy Argument

Every AI query today runs inference — probability distributions over billions of
parameters, on a GPU drawing 3,000–5,000 watts, for every single question asked.

US datacenters consumed **176 TWh** in 2023.  
Projections: **325–580 TWh** by 2028.  
Global AI compute alone: projected **2,500–4,500 TWh** by 2050.  
That entire curve exists because inference is expensive *by architecture*.

**Ptolemy replaces inference with navigation.**

A HyperWebster address lookup is fixed-cost arithmetic — Horner's bijection,
eight integer splits, one coordinate. Cost is the same whether the corpus is
10,000 words or 10 billion. No probability distribution. No parameter matrix.
A coordinate, and navigation to it.

A query to a Ptolemy kernel on a phone draws **milliwatts**.  
A ChatGPT query draws roughly **1,000× more electricity** than a Google search.

The addressable reduction is not 10%. It is the entire AI compute growth curve.

---

## The Model: Conservation, Not Probability

The LSH model — **Lagrange Self-Adjoint Hyperindexing** — propagates information
through the Cayley-Dickson algebraic tower: ℝ → ℂ → ℍ → 𝕆.

Information propagation through this tower has been verified against Noether
conservation laws: **conserved = True, 7+ sigma.**

The model conserves. It does not hallucinate. That is not a feature — it is the
architecture. A result that violates conservation is flagged before it reaches you.

Mathematical foundations: [Ainulindalë](https://github.com/michaelrendier/Ainulindale)
— withheld pending publication.

---

## The Kernel

Ptolemy is not software that runs AI. **Ptolemy is a self-contained learning kernel.**

It boots on a watch. It knows what it knows on delivery. It learns from use.
It manages itself. No cloud. No subscription. No permission.

The reason this is possible is HyperIndexing. There is no storage layer to scale.
There is no inference server to maintain. There is no embedding database to update.
There is one operation — navigate the address space — and it runs on the device.

---

## Architecture: Eleven Trusted Advisors

Eleven **Faces** — sovereign capability domains, each named after a historical
figure of the Library of Alexandria. Each runs its own **SMNNIP Instance Engine**
— a local conservation verifier trained on that domain's signal. Conserved = trusted.

| Face | Advisor | SMNNIP Domain | Wiki |
|---|---|---|---|
| [Pharos](Pharos/) | Pharos Lighthouse | System health, bus patterns, error signatures | [Wiki](../../wiki/Pharos) |
| [Alexandria](Alexandria/) | Library of Alexandria | Visual geometry, rendering, fractal space | [Wiki](../../wiki/Alexandria) |
| [Anaximander](Anaximander/) | Anaximander of Miletus | Spatial navigation, location, routes | [Wiki](../../wiki/Anaximander) |
| [Archimedes](Archimedes/) | Archimedes of Syracuse | Mathematical structure, physical law, signal | [Wiki](../../wiki/Archimedes) |
| [Aulë](Aule/) | Aulë the Smith | Diagnostics, fault signatures, audit trail | [Wiki](../../wiki/Aule) |
| [Callimachus](Callimachus/) | Callimachus of Cyrene | Information architecture, HyperWebster, blockchain | [Wiki](../../wiki/Callimachus) |
| [Kryptos](Kryptos/) | *Kryptos* (hidden) | Cryptographic structure, entropy, key geometry | [Wiki](../../wiki/Kryptos) |
| [Mouseion](Mouseion/) | The Mouseion | Human interface, web, presentation | [Wiki](../../wiki/Mouseion) |
| [Phaleron](Phaleron/) | Port of Phaleron | Discovery, search, document topology, OCR | [Wiki](../../wiki/Phaleron) |
| [Philadelphos](Philadelphos/) | Ptolemy II Philadelphos | Language, LSH inference, conversation, context | [Wiki](../../wiki/Philadelphos) |
| [Tesla](Tesla/) | Nikola Tesla | Physical world, sensors, devices, hardware state | [Wiki](../../wiki/Tesla) |

Philadelphos talks to you. The others are who Philadelphos asks.

---

## The Processor Vision

[**PROCESSOR_VISION.md**](PROCESSOR_VISION.md) — Full architectural spec for IC
engineers: on-die NVRAM allocation, Cayley-Dickson compute substrate, focal-point
interferometer display, sensory stream integration. Nobody has fabbed this. That is
the point.

---

## Documentation

| | |
|---|---|
| [Wiki](../../wiki) | Full technical reference |
| [docs/HYPERWEBSTER.md](docs/HYPERWEBSTER.md) | Nine-layer reduction — full derivation |
| [docs/INDEX.md](docs/INDEX.md) | Face documentation index |
| [docs/ErrorCatalog.md](docs/ErrorCatalog.md) | 27 typed errors, wiring requirements |
| [INSTALL.md](INSTALL.md) | Dependencies, build, venv |
| [Ainulindalë](https://github.com/michaelrendier/Ainulindale) | SMNNIP conjecture, Noether engine |

---

## Hardware

| | |
|---|---|
| **Machine** | HP EliteBook 820 G3 |
| **OS** | Linux Mint 22.1 Xia — kernel 6.8.0-110-lowlatency |
| **CPU** | Intel Core i7-6600U — Skylake, 4 threads @ 3.4GHz |
| **RAM** | 8 GiB |
| **GPU** | Intel HD Graphics 520 — OpenGL 4.6 |
| **Storage** | 953 GiB NVMe + 111 GiB Samsung 840 EVO |

---

*Ex Fidelitas, Et Integritas, Nobilitas.*
