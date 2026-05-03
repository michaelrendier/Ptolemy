# Ptolemy

**Author:** michaelrendier | **Status:** Active development — private pre-release

---

## The Memory Problem Is The Wrong Problem

Every processor ever built assumes data must be stored to exist.

Ptolemy is built on a different assumption: **every string ever written has always had a
number.** Every number maps to a deterministic coordinate in eight-dimensional space.
Given the coordinate and the key, the content is reconstructed — not retrieved. The
system navigates to information. It does not fetch it.

This is not compression. Shannon entropy is a property of stored artifacts. A coordinate
has no entropy in that sense. The address space is infinite, pre-existing, and requires
no maintenance. A dedicated NVRAM block holds addresses only — at 512 bits per octonion
coordinate, a 16MB block covers the full 180,000-word English lexicon plus operational
context, across power cycles, without a database.

Nobody has fabbed the processor this implies. That is the point of this project.

---

## The Model That Runs On It

The LSH model — **Lagrange Self-Adjoint Hyperindexing** — is grounded in Standard Model
conservation laws. Information propagation through the Cayley-Dickson tower (ℝ→ℂ→ℍ→𝕆)
has been verified against Noether conservation: **conserved=True, 7+ sigma.**

The model conserves. It does not hallucinate. That is not a feature. It is the
architecture.

The mathematical foundations are in the
[Ainulindalë repository](https://github.com/michaelrendier/Ainulindale) — withheld
pending publication.

---

## What Ptolemy Is

A modular Python research and engineering platform — eleven **Faces**, each named after
a historical figure of the Library of Alexandria, each a distinct capability domain.

| Face | Figure | Domain |
|---|---|---|
| [Alexandria](Alexandria/) | Library of Alexandria | OpenGL visualization, fractal renderer |
| [Anaximander](Anaximander/) | Anaximander of Miletus | Navigation, GPS, location services |
| [Archimedes](Archimedes/) | Archimedes of Syracuse | Mathematics, science, signal processing |
| [Aulë](Aule/) | Aulë the Smith | Diagnostic forge, stream monitor, audit trail |
| [Callimachus](Callimachus/) | Callimachus of Cyrene | HyperWebster acquisition and addressing |
| [Kryptos](Kryptos/) | *Kryptos* (hidden) | KCF-1 encryption, charset key derivation |
| [Mouseion](Mouseion/) | The Mouseion | Flask web interface — thewanderinggod.tech |
| [Phaleron](Phaleron/) | Port of Phaleron | Internal search, OCR, API inspection |
| [Pharos](Pharos/) | Pharos Lighthouse | Core, PtolBus, LuthSpell, desktop, settings |
| [Philadelphos](Philadelphos/) | Ptolemy II Philadelphos | LSH inference, language models, context buffer |
| [Tesla](Tesla/) | Nikola Tesla | Device interfacing, sensors, Android bridge |

The system is unified by the addressing layer. Every Face is a consumer or producer of
octonion addresses. The blockchain (Callimachus) uses HyperWebster addresses as hash
seeds — semantic corruption is detectable at the hash level.

---

## The Processor Vision

[**PROCESSOR_VISION.md**](PROCESSOR_VISION.md) — The full architectural spec:
on-die NVRAM allocation, Cayley-Dickson compute substrate, focal-point interferometer
display, sensory stream integration. Written for IC engineers.

---

## Documentation

Full technical reference in the [Wiki](../../wiki) and [docs/](docs/).

| | |
|---|---|
| [docs/INDEX.md](docs/INDEX.md) | All face documentation |
| [INSTALL.md](INSTALL.md) | Dependencies, QTermWidget build, venv |
| [SERVER_SPEC.md](SERVER_SPEC.md) | Server architecture |
| [Ainulindalë](https://github.com/michaelrendier/Ainulindale) | SMNNIP conjecture and Noether engine |

---

## Hardware

Designed and developed on:

| | |
|---|---|
| **Machine** | HP EliteBook 820 G3 |
| **OS** | Linux Mint 22.1 Xia — kernel 6.8.0-110-lowlatency |
| **CPU** | Intel Core i7-6600U — Skylake, 4 threads @ 3.4GHz |
| **RAM** | 8 GiB |
| **GPU** | Intel HD Graphics 520 — OpenGL 4.6 |
| **Storage** | 953 GiB NVMe + 111 GiB Samsung 840 EVO |

Full spec: [docs/Hardware/](docs/Hardware/)

