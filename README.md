# Ptolemy

**A self-contained, self-managing learning kernel.**  
author: michaelrendier | status: active development — private pre-release

---

## AI In Your Hands. No Cloud. No Permission.

Current AI runs on someone else's hardware, trained on someone else's data, under
someone else's terms. Every query leaves your device. Every answer is someone else's
decision about what you're allowed to know.

Ptolemy is the other thing.

A Ptolemy kernel ships **fully trained, fully operational, on the device.** Watch,
phone, server — same kernel, different resource envelope. It boots. It knows what it
knows. It learns from your use. It manages itself. No cloud required. No subscription.
No terms of service between you and your own intelligence layer.

The reason this is possible is the memory architecture.

---

## The Feature: Infinite Knowledge, Zero Storage Medium

Every string ever written has always had a number.  
Every number maps to a deterministic coordinate in eight-dimensional space.  
The device holds a key and an entry point. That's it.

**The NVRAM block contains:** one address, one data length, one timestamp — the entry
point to the next layer of addressing. Not content. Not a database. A bookmark into
an address space that is infinite by mathematics, not by hardware.

Reconstruction doesn't retrieve. It **navigates.** The knowledge isn't stored on the
device. It exists in the mathematics of the address space, which was always there.
A watch and a datacenter have access to the same infinite address space. The difference
is navigation speed, not knowledge ceiling.

This is the HyperWebster. It is not a dictionary. It is an addressing system for
all information — words, sensor streams, images, conversations, mathematical objects —
unified by Horner's bijection into octonion space.

There is no separate search engine. No separate database. No separate inference layer.
**Input is an address. Search is proximity. Reconstruction is resolution. Learning is
geometry update.** One operation handles all of it.

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

## Architecture: Eleven Trusted Advisors

Ptolemy is organized into **Faces** — eleven sovereign capability domains, each named
after a historical figure of the Library of Alexandria. Each Face runs its own
**SMNNIP Instance Engine** — a local conservation verifier trained on that domain's
signal. When Faces consult each other, the engine signs the output. Conserved = trusted.

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

Ptolemy is not software that runs on a processor. Ptolemy *is* the processor model.

One addressing operation handles input, search, storage, retrieval, reconstruction,
and output. The Cayley-Dickson tower is the compute substrate. The NVRAM block is
measured in kilobytes. The knowledge ceiling is infinite.

**[PROCESSOR_VISION.md](PROCESSOR_VISION.md)** — full architectural spec for IC
engineers: NVRAM allocation, Cayley-Dickson compute layers, focal-point interferometer
display, sensory stream integration via Tesla.

---

## Documentation

> ⚠️ **Wiki TODO — Step 1:** The Ptolemy GitHub Wiki must be enabled and initialized
> with at least one page via the GitHub UI before Wiki links above will resolve.
> All eleven Face Wiki pages are stubbed and pending.

| | |
|---|---|
| [Wiki](../../wiki) | Full technical reference — all Faces, all subsystems |
| [docs/INDEX.md](docs/INDEX.md) | Face documentation index |
| [INSTALL.md](INSTALL.md) | Dependencies, build, venv |
| [SERVER_SPEC.md](SERVER_SPEC.md) | Server architecture |
| [Ainulindalë](https://github.com/michaelrendier/Ainulindale) | SMNNIP conjecture, Noether engine |

---

## Hardware

Built and running on:

| | |
|---|---|
| **Machine** | HP EliteBook 820 G3 |
| **OS** | Linux Mint 22.1 Xia — kernel 6.8.0-110-lowlatency |
| **CPU** | Intel Core i7-6600U — Skylake, 4 threads @ 3.4GHz |
| **RAM** | 8 GiB |
| **GPU** | Intel HD Graphics 520 — OpenGL 4.6 |
| **Storage** | 953 GiB NVMe + 111 GiB Samsung 840 EVO |

Full spec: [docs/Hardware/](docs/Hardware/)

---

*Ex Fidelitas, Et Integritas, Nobilitas.*
