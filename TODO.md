# Ptolemy — TODO

Tracked development intentions, hardware notes, and deferred work.
Items move to commits when implemented. GitHub handles version history.

---

## Incoming Hardware

### Dell XPS 13 9345 — Snapdragon X Elite
**Status:** Purchasing in ~days

| Component | Spec |
|---|---|
| CPU | Snapdragon X Elite X1E-80-100 — 12 cores / 3.4 GHz (4.0 GHz boost) |
| NPU | Qualcomm Hexagon — 45 TOPS |
| GPU | Qualcomm Adreno — 3.8 TFLOPS |
| RAM | 32 GB LPDDR5X (minimum — get this config) |
| Storage | 1 TB NVMe PCIe 4.0 |
| OS | Ubuntu 24.04 LTS (official Dell support confirmed) |
| Wi-Fi | Qualcomm FastConnect 7800 — Wi-Fi 7 / BT 5.4 |

**On arrival:**
- [ ] Run `inxi -Fxz` and update `docs/Hardware/` with XPS hardware report
- [ ] Update README.md hardware table
- [ ] Verify Ubuntu 24.04 lowlatency kernel availability for JACK/PipeWire audio
- [ ] Confirm HYPER_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY env vars transferred
- [ ] Test Aulë monitor live stream against acquire.py on new hardware
- [ ] Benchmark HWAS Horner vs SHA-256 on ARM (AVX2 gone — NEON instead)

---

## Qualcomm Integration Primer

**Status:** Deferred — implement after XPS 13 9345 arrives

The Qualcomm AI Hub developer access (API keys in hand) enables a distinct
inference pathway for SMNNIP that bypasses the CPU-only constraint.

### The Three-Layer Stack

```
PyTorch (training, local CPU)
    ↓  torch.jit.trace()
qai_hub.submit_compile_job()   ←  target: "Snapdragon X Elite CRD"
    ↓  compile to ONNX / QNN
Hexagon NPU (45 TOPS on-device inference)
```

### Key Facts
- `qai_hub_models` requires **x64 Python** on ARM Windows (not ARM64 Python)
- On Ubuntu ARM: native Python works, no emulation needed
- AI Hub Workbench hosts real Snapdragon X Elite devices in the cloud for
  profiling before you have the hardware
- PyTorch 2.7+ has ARM-native Windows builds; Hexagon NPU support is
  not yet in upstream PyTorch (routes through ONNX Runtime / DirectML)
- Target device string: `hub.Device("Snapdragon X Elite CRD")`
- Runtimes available: `onnx`, `onnx_runtime`, `qnn` (Qualcomm Neural Network)

### Tasks
- [ ] `pip install qai_hub qai_hub_models` on XPS after arrival
- [ ] `qai-hub configure --api_token <QUALCOMM_AI_HUB_TOKEN>`
- [ ] Trace a SMNNIP layer with `torch.jit.trace()` as proof of concept
- [ ] Submit compile job targeting Snapdragon X Elite CRD
- [ ] Profile on cloud-hosted device via AI Hub Workbench
- [ ] Compare Hexagon NPU inference latency vs CPU baseline
- [ ] Document results in `docs/Philadelphos/` as Qualcomm integration report
- [ ] Add `QUALCOMM_AI_HUB_TOKEN` to `.env.example`
- [ ] Integrate compile/profile workflow into Aulë Forge as a named script

### Reference
- AI Hub Workbench docs: https://workbench.aihub.qualcomm.com/docs/
- AI Hub Models (GitHub): https://github.com/qualcomm/ai-hub-models
- Snapdragon X Elite device string: `"Snapdragon X Elite CRD"`
- PyTorch ARM Windows: https://pytorch.org/get-started/locally/

---

## Processor Architecture Research

**Status:** Concept — separate project, not Ptolemy

Methodology derived from SMNNIP / HyperWebster addressing applied to
processor architecture design. Own repo when ready. Not tracked here.

---

## Ptolemy Faces — Pending Work

### Callimachus / HyperWebster
- [ ] Split 180,000-word dictionary into 26 alphabetical files
- [ ] Run `acquire.py` full pass — return with results + 23 sample JSON files
- [ ] Review incomplete flag firing on `hiraeth` and other edge cases
- [ ] Begin Callimachus SQL deprecation — replace row IDs with HyperWebster addresses

### Philadelphos / Julius Caesar Face
- [ ] Define Julius Caesar face configuration (corpus: Caesar, Cicero, Cato)
- [ ] First LLM model experiment — architecture decision pending
- [ ] Connect Julius Caesar face to Aulë stream monitoring

### Kryptos
- [ ] Implement KCF-1 equation in Python (`kryptos/kcf.py`)
- [ ] Build Kryptos Encrypted Secrets Store (KES) — AES-256 + HyperWebster addressing
- [ ] Add `kcf_profiles/` registry of per-Face KCF configurations

### Aulë
- [ ] Wire `stream_event()` shim into `acquire.py`
- [ ] Wire shim into `Philadelphos/Ainur/ainur.py` (API call monitoring)
- [ ] Test full monitor → forge → replay cycle on live acquisition run

### Ptolemy++
- [ ] Port HWAS Horner computation to C++ with GMP
- [ ] Benchmark C++/GMP vs Python bignum (projected 50–100× speedup)
- [ ] Expose via Python bindings (pybind11)

### Repository
- [ ] Scrub git history with `git filter-repo` before going public
- [ ] Verify no secrets remain: `grep -r "TOKEN\|API_KEY" .git/`
- [ ] Confirm `.env` in `.gitignore`, `.env.example` committed
- [ ] Set repository visibility to public (post-SMNNIP publication)

---

## .gitignore Layer Architecture

Ptolemy uses layered `.gitignore` files — one at root, one per Face where
needed. This allows directory structure to be cloned without data contents.

**Root `.gitignore`** — global rules (secrets, cache, ML binaries, media)
**`Aule/.gitignore`** — excludes `streams/`, `replays/`, `probe_history/`, `aule.log`

**Principle:** anyone cloning the repo gets the code and directory scaffolding.
Captured stream data, acquisition output, model state, and secrets stay local.
Pull requests cannot include gitignored files — contributors cannot accidentally
submit private data.

To add a new Face-level ignore layer:
```bash
echo "data/" >> NewFace/.gitignore
echo "*.json" >> NewFace/.gitignore
git add NewFace/.gitignore
```

---

*Last updated: April 2026*
