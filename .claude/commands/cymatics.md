# /cymatics — Ainulindale Sonification Engine

Launches the Ainulindale sonification pipeline.

## Usage
```
/cymatics [movement] [--output path] [--demo]
```

## Arguments
- `movement` : mv1 (intro), mars, electron_orbitals, beginning_of_light (default: mv1)
- `--output` : WAV output path (default: ./output.wav)
- `--demo`   : run with synthetic demo data

## Invokes
- `Ainulindale/sonification/ainulindale_sonification_mv1.py`   — Movement I: Introduction
- `Ainulindale/sonification/ainulindale_mars.py`               — Mars sonification
- `Ainulindale/sonification/ainulindale_electron_orbitals.py`  — Electron orbitals
- `Ainulindale/sonification/ainulindale_beginning_of_light.py` — Beginning of light

## SMNNIP integration
The sonification engine maps the Cayley-Dickson algebra tower to instrument families:
  ℝ → Higgs (cello), ℂ → Photon (flute), ℍ → W/Z bosons (brass), 𝕆 → Gluons (percussion)

Noether current violations → amplitude anomalies in the output waveform.
