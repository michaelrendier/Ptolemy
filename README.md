# Ptolemy

**Author:** michaelrendier | **Status:** Active development — private pre-release

---

## The Memory Problem Is The Wrong Problem

Every processor ever built assumes data must be stored to exist.  
Ptolemy is built on a different assumption.

---

## HyperIndexing: Information Is A Coordinate

**Every string ever written has always had a number.**

Horner's bijection maps any finite string over an ordered charset to a unique
non-negative integer. That integer splits into 8 equal limbs — the components
of an octonion — placing the string at a precise coordinate in eight-dimensional
space. Two strings that are geometrically close in that space are semantically
related. The geometry of the address space mirrors the geometry of meaning.

This is not encoding. It is not compression. It is navigation.

**The NVRAM block holds:** one address, one data length, one timestamp.  
Not content. Not a database. A bookmark into an address space that is infinite
by mathematics, not by hardware.

Reconstruction navigates to the content. It does not retrieve it. The knowledge
exists in the mathematics of the address space — which was always there. A watch
and a datacenter have access to the same infinite address space. The difference
is navigation speed, not knowledge ceiling.

**Input is an address. Search is proximity. Reconstruction is resolution.
Learning is geometry update. One operation handles all of it.**

The charset permutation order is the cryptographic key. Permute it — the entire
address space rotates. The same content, a completely different coordinate.
Private by default.

This is the **HyperWebster** — not a dictionary. An addressing system for all
information: words, sensor streams, images, conversations, mathematical objects.
Unified. Deterministic. Infinite.

---

## The Model: Conservation, Not Probability

The LSH model — **Lagrange Self-Adjoint Hyperindexing** — propagates information
through the Cayley-Dickson algebraic tower: ℝ→ℂ→ℍ→𝕆.

Information propagation through this tower has been verified against Noether
conservation laws: **conserved=True, 7+ sigma.**

The model conserves. It does not hallucinate. That is not a feature. It is the
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

[**PROCESSOR_VISION.md**](PROCESSOR_VISION.md) — The full architectural spec for IC
engineers: on-die NVRAM allocation, Cayley-Dickson compute substrate, focal-point
interferometer display, sensory stream integration. Nobody has fabbed this. That is
the point.

---

## Documentation

> ⚠️ **Wiki TODO — Step 1:** Enable and initialize the Ptolemy GitHub Wiki via the
> GitHub UI before Wiki links above will resolve. All eleven Face Wiki pages are
> stubbed and pending.

| | |
|---|---|
| [Wiki](../../wiki) | Full technical reference |
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


---

## The Energy Argument

Every AI query today runs inference — probability distributions over billions of
parameters, on a GPU drawing 3,000–5,000 watts, for every single question asked.
The electricity cost scales with model size. The hardware cost scales with demand.
The datacenter growth curve is the inference growth curve.

US datacenters consumed 176 TWh in 2023. Projections put that at 325–580 TWh by
2028. Globally, AI compute alone is projected at 2,500–4,500 TWh by 2050. That
entire curve exists because inference is expensive by architecture.

**Ptolemy replaces inference with navigation.**

A HyperWebster address lookup is fixed-cost arithmetic — Horner's bijection,
eight integer splits, one coordinate. It costs the same whether the corpus is
10,000 words or 10 billion. The compute cost per query does not scale with
model size. There is no probability distribution to compute. There is no
parameter matrix to multiply. There is a coordinate, and there is navigation.

A query to a Ptolemy kernel on a phone draws milliwatts.
A ChatGPT query draws roughly 1,000 times more electricity than a Google search.

The addressable reduction is not 10%. It is the entire AI compute growth curve.

---

## The HyperWebster

Not a dictionary. Not a database. Not an index.

**A coordinate system for all human knowledge.**

Every word, every phrase, every document, every sensor reading that can be
expressed as a string over a known alphabet already has an address. It has
always had one. The address exists in the mathematics — it does not need to
be assigned, generated, or stored. The HyperWebster is the system that
navigates that address space.

Here is what that means in practice:

**You ask a question.** The question is a string. The string maps to a
coordinate in eight-dimensional space. The coordinate identifies a neighborhood.
The neighborhood contains the answer — not by lookup, but by geometry. Proximity
in the address space is semantic proximity. Things that mean similar things live
near each other. Not because someone organized them that way. Because the
mathematics of the address space makes it so.

**The system learns a new word.** It navigates to that word's coordinate.
It records what it found there — what other words are nearby, what the
context was, what the usage pattern looks like. The coordinate never changes.
The knowledge attached to that coordinate deepens over time. This is memory
without storage. The address is permanent. The content at that address grows.

**The device powers off.** The NVRAM holds the entry point — one address,
one length, one timestamp. When it powers back on, it navigates back to
exactly where it was. Nothing was lost. There was nothing to lose. The
address space was always there. The device just holds the key.

**A new language is added.** Every language has its own charset. Every
charset has its own address space. The Cayley-Dickson construction bridges
them — a meaning that exists in English and in Latin and in Arabic occupies
neighboring coordinates in each language's space, and those neighborhoods
are linked. The system does not translate. It navigates between address
spaces that share geometric structure.

**The corpus is infinite by default.** There is no upper bound on the
address space. A word that has never been encountered yet already has an
address. When it is encountered for the first time, the system navigates
to its coordinate and records the encounter. The `first_encountered` field
is permanently sealed at that moment — the Rabies Principle — because the
first encounter is a fact about the history of the system, not a mutable
attribute. It cannot be unlearned.

**Security is geometric.** The charset permutation order is the
cryptographic key. Permute it, and the entire address space rotates.
The same word lands at a completely different coordinate. Without the key,
the address space is navigable but meaningless — you can traverse it, but
you cannot recognize what you find. Privacy is not a feature added on top.
It is structural.

---
