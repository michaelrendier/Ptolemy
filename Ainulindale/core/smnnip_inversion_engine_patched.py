#!/usr/bin/env python3
"""
==============================================================================
SMNNIP INSIDE-OUT INVERSION ENGINE
==============================================================================
Standard Model of Neural Network Information Propagation
Ainulindale Conjecture — Equation Engine Core

Purpose:
    Compute the gradient flow of the Inside-Out Inversion map J_N:
        (r, theta) -> (1/r, theta + pi/2)

    Determine numerically whether the traversal from the inversion
    boundary (r=1, governed by pi) to the recursion attractor (phi,
    the golden ratio) passes through hbar_NN or hbar (= h / 2*pi).

    If convergence = phi to within the known 0.00070 correction gap,
    the open derivation in section 7 of the Ainulindale Conjecture closes.

PATCH NOTES (April 2026):
    D_STAR was previously defined as OMEGA / ln(10) — a tautology that
    displayed gap = 0.00000. This was a display bug, not a simulation error.
    Fixed: D_STAR_SPEC = 0.24600 (Berry-Keating spectral literature value,
    independent of SMNNIP). D_STAR_TAUT retained as reference only.
    True gap = 0.00070. Open derivation stands.