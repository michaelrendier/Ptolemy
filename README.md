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
