"""
Pharos/ptol_face_wiring.py
--------------------------
Standard wiring factory for all Ptolemy Faces.

Usage in every Face module:

    from Pharos.ptol_face_wiring import wire_face, face_handler

    wire_face(FACE_NAME, get_state_fn=lambda: {"key": "value"})

    # Then in any try/except:
    try:
        ...
    except Exception as e:
        face_handler(FACE_NAME).handle(e)

Mandos checkpoint-before-GC is automatic via ErrorHandler._mandos_intercept().
Aule heartbeat beat() is called from within handle() for all Faces.
"""

from __future__ import annotations
from typing import Callable

from Pharos.luthspell_error_handler import ErrorHandler, GarbageCollector
from Pharos.PtolDmesg import dmesg

_registry: dict[str, dict] = {}


def wire_face(
    face_name:    str,
    get_state_fn: Callable | None = None,
) -> ErrorHandler:
    """
    Wire ErrorHandler + GC for a Face. Idempotent -- safe to call on restart.
    Returns the ErrorHandler for this Face.
    """
    gc      = GarbageCollector()
    handler = ErrorHandler(
        gc=gc,
        face_name=face_name,
        on_error=lambda e: dmesg.error(face_name, str(e)),
        get_state_fn=get_state_fn,
    )
    _registry[face_name] = {"handler": handler, "gc": gc}
    dmesg.info(face_name, f"{face_name} wired.")
    return handler


def face_handler(face_name: str) -> ErrorHandler:
    """Return the wired ErrorHandler for face_name. Raises ModuleNotWired if absent."""
    from Pharos.luthspell_error_handler import ModuleNotWired
    entry = _registry.get(face_name)
    if entry is None:
        raise ModuleNotWired(f"{face_name} has no wired ErrorHandler. Call wire_face() first.")
    return entry["handler"]


def face_gc(face_name: str) -> GarbageCollector:
    """Return the GarbageCollector for face_name."""
    from Pharos.luthspell_error_handler import ModuleNotWired
    entry = _registry.get(face_name)
    if entry is None:
        raise ModuleNotWired(f"{face_name} has no wired GC. Call wire_face() first.")
    return entry["gc"]


def all_wired() -> list[str]:
    """Return list of all wired Face names."""
    return list(_registry.keys())
