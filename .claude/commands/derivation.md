---
description: Launch the SMNNIP derivation engine console (curses GUI with SymPy)
allowed-tools: Bash(python3 -m Philadelphos.Ainulindale.console.smnnip_proof_engine_console:*)
---

Launch the SMNNIP Proof Engine — curses console GUI wired to the live derivation engine with SymPy mathematical notation.

Run from the Ptolemy root:

```
cd /home/rendier/Ptolemy && python3 -m Philadelphos.Ainulindale.console.smnnip_proof_engine_console
```

The console provides:
- Full algebra tower: ℝ → ℂ → ℍ → 𝕆 → 𝕊 (Langlands Master Key)
- Live derivation engine: Lagrangian, Yang-Mills, RedBlue Hamiltonian, Noether conservation
- SymPy rendering: press `s` to toggle symbolic math output
- MATH / TOPIC sort modes: press `m` to toggle
- Researcher options: `Tab` to cycle, `←→` to change values
- Parameter input: type `param=value` pairs in the input bar, `Enter` to apply
- Navigation: `↑↓` or `j/k`, `PgUp/PgDn` to scroll display
- Run engine: press `r` to evaluate current entry against live derivation engine
- Help: press `?` or `h`
- Quit: press `q`
