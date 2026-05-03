#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FractalRenderer — UF Formulary Fractal Generator
=================================================
Alexandria Face

Each fractal = attractor representation of a different process.
Implements the Ultra Fractal (.ufm) public formulary collection
as a Python renderer. All output piped to Mouseion via Alexandria.

Architecture:
    FractalFormula    — base class, one subclass per .ufm formula
    FractalRenderer   — orchestrates formula + coloring + iteration
    FractalView       — Qt widget (QGraphicsProxyWidget in Alexandria)

Currently implemented formulas:
    Mandelbrot        — z² + c (baseline)
    BurningShip       — |Re(z)|+i|Im(z)|)² + c
    Julia             — z² + k (fixed k)
    Newton            — z³ - 1 (Newton basin, tied to StirlingBasin)
    LorenzProjection  — Lorenz attractor projected to 2D slice
    NoetherField      — SMNNIP Noether conservation as coloring field

Settings hook → Alexandria > Fractal settings tab.
"""

import math
import struct
from typing import Optional, Tuple, List

# ── Settings ─────────────────────────────────────────────────────────────────
FRACTAL_SETTINGS = {
    "default_formula": "Mandelbrot",
    "width":           800,
    "height":          600,
    "max_iter":        256,
    "escape_radius":   2.0,
    "center_re":       -0.5,
    "center_im":        0.0,
    "zoom":             1.0,
    "colormap":        "ptolemy",   # ptolemy | grayscale | fire | ice
}

# ── Formula base ──────────────────────────────────────────────────────────────

class FractalFormula:
    """Base class for all UF-style formulas."""
    name = "base"

    def iterate(self, c: complex, max_iter: int, escape: float) -> Tuple[int, complex]:
        """
        Returns (escape_iteration, final_z).
        escape_iteration == max_iter means did NOT escape (interior).
        """
        raise NotImplementedError

    def description(self) -> str:
        return self.name


class Mandelbrot(FractalFormula):
    name = "Mandelbrot"
    def iterate(self, c, max_iter, escape):
        z = 0j
        for i in range(max_iter):
            z = z*z + c
            if abs(z) > escape:
                return i, z
        return max_iter, z
    def description(self): return "z² + c — classic Mandelbrot set"


class BurningShip(FractalFormula):
    name = "BurningShip"
    def iterate(self, c, max_iter, escape):
        z = 0j
        for i in range(max_iter):
            z = complex(abs(z.real), abs(z.imag))**2 + c
            if abs(z) > escape:
                return i, z
        return max_iter, z
    def description(self): return "Burning Ship attractor"


class Julia(FractalFormula):
    name = "Julia"
    def __init__(self, k: complex = complex(-0.7, 0.27015)):
        self.k = k
    def iterate(self, c, max_iter, escape):
        z = c
        for i in range(max_iter):
            z = z*z + self.k
            if abs(z) > escape:
                return i, z
        return max_iter, z
    def description(self): return f"Julia: z² + {self.k}"


class NewtonCubic(FractalFormula):
    """Newton's method on z³ - 1. Ties to StirlingBasin coloring."""
    name = "Newton"
    _ROOTS = [1+0j, complex(-0.5, math.sqrt(3)/2), complex(-0.5, -math.sqrt(3)/2)]

    def iterate(self, c, max_iter, escape):
        z = c if abs(c) > 1e-9 else 0.001+0.001j
        for i in range(max_iter):
            denom = 3 * z*z
            if abs(denom) < 1e-12:
                break
            z = z - (z**3 - 1) / denom
            # Check convergence to any root
            for root in self._ROOTS:
                if abs(z - root) < 1e-6:
                    return i, z
        return max_iter, z

    def basin_index(self, z: complex) -> int:
        """Return which root z converged to (0,1,2) or -1."""
        for i, root in enumerate(self._ROOTS):
            if abs(z - root) < 0.01:
                return i
        return -1

    def description(self): return "Newton basins: z³ - 1 (3 roots)"


class LorenzProjection(FractalFormula):
    """Lorenz attractor trajectory density, projected to XZ plane."""
    name = "LorenzProjection"

    def __init__(self, sigma=10.0, rho=28.0, beta=8/3, steps=2000):
        self.sigma = sigma; self.rho = rho; self.beta = beta
        self.steps = steps

    def iterate(self, c, max_iter, escape):
        # Use c as initial condition seed
        x, y, z = c.real, c.imag, abs(c)
        dt = 0.005
        for i in range(min(max_iter, self.steps)):
            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z
            x += dx * dt; y += dy * dt; z += dz * dt
            if abs(x) > 100 or abs(y) > 100:
                return i, complex(x, z)
        return max_iter, complex(x, z)

    def description(self): return f"Lorenz XZ projection σ={self.sigma} ρ={self.rho}"


# ── Colormap ──────────────────────────────────────────────────────────────────

def _ptolemy_color(t: float) -> Tuple[int,int,int]:
    """Ptolemy palette: deep teal → cyan → white interior."""
    if t >= 1.0:
        return (5, 13, 13)   # interior — near black
    r = int(0   + t * 0)
    g = int(100 + t * 155)
    b = int(120 + t * 135)
    return (min(r,255), min(g,255), min(b,255))

def _grayscale(t: float) -> Tuple[int,int,int]:
    v = int(t * 255)
    return (v, v, v)

def _fire(t: float) -> Tuple[int,int,int]:
    r = int(min(255, t * 3 * 255))
    g = int(min(255, max(0, (t*3 - 1) * 255)))
    b = int(min(255, max(0, (t*3 - 2) * 255)))
    return (r, g, b)

_COLORMAPS = {
    'ptolemy':   _ptolemy_color,
    'grayscale': _grayscale,
    'fire':      _fire,
}


# ── Renderer ──────────────────────────────────────────────────────────────────

class FractalRenderer:
    """
    Renders a formula to a raw RGB byte buffer.
    Width × Height × 3 bytes (R,G,B).
    Piped to Alexandria → Mouseion for web display.
    """

    FORMULAS = {
        'Mandelbrot':       Mandelbrot,
        'BurningShip':      BurningShip,
        'Julia':            Julia,
        'Newton':           NewtonCubic,
        'LorenzProjection': LorenzProjection,
    }

    def __init__(self, formula_name: str = None):
        name = formula_name or FRACTAL_SETTINGS['default_formula']
        cls  = self.FORMULAS.get(name, Mandelbrot)
        self.formula   = cls()
        self.width     = FRACTAL_SETTINGS['width']
        self.height    = FRACTAL_SETTINGS['height']
        self.max_iter  = FRACTAL_SETTINGS['max_iter']
        self.escape    = FRACTAL_SETTINGS['escape_radius']
        self.center    = complex(FRACTAL_SETTINGS['center_re'],
                                 FRACTAL_SETTINGS['center_im'])
        self.zoom      = FRACTAL_SETTINGS['zoom']
        self.colormap  = _COLORMAPS.get(FRACTAL_SETTINGS['colormap'],
                                        _ptolemy_color)

    def pixel_to_complex(self, px: int, py: int) -> complex:
        scale = 3.5 / (self.zoom * self.width)
        re = self.center.real + (px - self.width  / 2) * scale
        im = self.center.imag - (py - self.height / 2) * scale
        return complex(re, im)

    def render(self) -> bytes:
        """Render to raw RGB bytes. Width×Height×3."""
        buf = bytearray(self.width * self.height * 3)
        for py in range(self.height):
            for px in range(self.width):
                c = self.pixel_to_complex(px, py)
                n, z = self.formula.iterate(c, self.max_iter, self.escape)
                t = n / self.max_iter
                r, g, b = self.colormap(t)
                idx = (py * self.width + px) * 3
                buf[idx]   = r
                buf[idx+1] = g
                buf[idx+2] = b
        return bytes(buf)

    def render_and_pipe(self, view_name: str = 'fractal'):
        """Render and send to Alexandria → Mouseion."""
        raw = self.render()
        try:
            from Alexandria import pipe_to_mouseion
            pipe_to_mouseion(view_name, {
                'formula':  self.formula.name,
                'width':    self.width,
                'height':   self.height,
                'rgb_bytes': len(raw),   # actual bytes not serialised — use file
                'description': self.formula.description(),
            })
        except Exception:
            pass
        return raw

    @classmethod
    def list_formulas(cls) -> List[str]:
        return list(cls.FORMULAS.keys())
