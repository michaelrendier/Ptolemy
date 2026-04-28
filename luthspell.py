#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ptolemy Project — Root Layer
LuthSpell: BUS Controller + Halting Monitor
Belongs to: Ptolemy (overseer), not a Face

Architecture:
  Ptolemy
  └── LuthSpell
      ├── T0/T1 priority arbitration (traffic circle, not binary gate)
      ├── set_boundary()     — marks inference boundary on T1
      ├── check()            — called each inference step
      ├── halt_pass()        — YOU SHALL NOT PASS (boundary marker, not kill)
      ├── Halting Monitor    — internal sensing organ
      └── reports to Ptolemy → Ptolemy issues redirect

Design:
  - LuthSpell has NO state beyond what the blockchain holds
  - Blockchain = source of truth for boundary and halt records
  - Modular: channel names, priority scheme, blockchain backend all swappable
"""

import hashlib
import time
from enum import IntEnum
from typing import Callable, Optional


# ─── Settings (module hooks → Settings tab) ───────────────────────────────────

CHANNEL_PROMPT         = "PROMPT"
CHANNEL_INFERENCE      = "INFERENCE_COORDS"
CHANNEL_LUTHSPELL      = "LUTHSPELL"
BLOCKCHAIN_BACKEND     = "branch"       # module hook
PRIORITY_SCHEME        = "rotary"       # module hook: rotary semaphore T0/T1


LUTHSPELL_SETTINGS = {
    "channel_prompt":     CHANNEL_PROMPT,
    "channel_inference":  CHANNEL_INFERENCE,
    "channel_luthspell":  CHANNEL_LUTHSPELL,
    "blockchain_backend": BLOCKCHAIN_BACKEND,
    "priority_scheme":    PRIORITY_SCHEME,
}


# ─── Priority ─────────────────────────────────────────────────────────────────

class Priority(IntEnum):
    T0 = 0   # system / Ptolemy-level
    T1 = 1   # inference / Face-level


# ─── Halt Record (what gets committed to blockchain) ─────────────────────────

class HaltRecord:
    def __init__(self, reason: str, coords, boundary_hash: str, timestamp: float = None):
        self.reason         = reason
        self.coords         = coords
        self.boundary_hash  = boundary_hash
        self.timestamp      = timestamp or time.time()

    def to_dict(self) -> dict:
        return {
            "reason":        self.reason,
            "coords":        str(self.coords),
            "boundary_hash": self.boundary_hash,
            "timestamp":     self.timestamp,
        }


# ─── Halting Monitor (internal to LuthSpell) ─────────────────────────────────

class HaltingMonitor:
    """
    Sensing organ of LuthSpell.
    Watches inference coordinates for halt conditions.
    Reports to LuthSpell — does not act independently.
    """

    def __init__(self):
        self._boundary      = None
        self._boundary_hash = None
        self._halt_records: list[HaltRecord] = []

    def set_boundary(self, coords) -> str:
        """Mark inference boundary. Returns boundary hash."""
        seed = f"{str(coords)}|{time.time()}"
        self._boundary      = coords
        self._boundary_hash = hashlib.sha256(seed.encode()).hexdigest()
        return self._boundary_hash

    def check(self, coords) -> tuple[bool, Optional[str]]:
        """
        Check current inference coords against boundary.
        Returns (halt: bool, reason: str | None).
        """
        if self._boundary is None:
            return False, None

        halt, reason = self._evaluate(coords)
        if halt:
            record = HaltRecord(reason, coords, self._boundary_hash)
            self._halt_records.append(record)
            return True, reason

        return False, None

    def _evaluate(self, coords) -> tuple[bool, Optional[str]]:
        """
        Module hook — swap evaluation logic via Settings.
        Stub: halt if coords == boundary (crossed marker).
        """
        if coords == self._boundary:
            return True, "boundary_crossed"
        return False, None

    @property
    def boundary_hash(self) -> Optional[str]:
        return self._boundary_hash

    @property
    def halt_records(self) -> list[HaltRecord]:
        return list(self._halt_records)


# ─── PtolBus stub (module hook — real bus wired externally) ──────────────────

class BusMessage:
    def __init__(self, channel: str, payload, priority: Priority = Priority.T1):
        self.channel   = channel
        self.payload   = payload
        self.priority  = priority
        self.timestamp = time.time()


class PtolBusStub:
    """
    Stub bus. Real PtolBus wired in externally via Settings/module swap.
    Provides subscribe/publish interface only.
    """
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, channel: str, handler: Callable):
        self._subscribers.setdefault(channel, []).append(handler)

    def publish(self, message: BusMessage):
        for handler in self._subscribers.get(message.channel, []):
            handler(message)


# ─── LuthSpell ────────────────────────────────────────────────────────────────

class LuthSpell:
    """
    Ptolemy's BUS controller.
    Owns T0/T1 arbitration, boundary marking, halt detection.
    Halting Monitor is internal — LuthSpell reports up to Ptolemy.
    LuthSpell has no persistent state — blockchain is source of truth.

    Ptolemy provides the redirect callback on instantiation.
    """

    def __init__(self,
                 bus=None,
                 chain=None,
                 on_halt: Optional[Callable] = None):
        """
        on_halt: Ptolemy's redirect callback — called with HaltRecord on halt pass.
        """
        self._bus        = bus or PtolBusStub()
        self._chain      = chain
        self._on_halt    = on_halt
        self._monitor    = HaltingMonitor()
        self._wired      = False

    def wire(self):
        """Subscribe to BUS channels. Call once from Ptolemy init."""
        self._bus.subscribe(CHANNEL_PROMPT,    self._on_prompt)
        self._bus.subscribe(CHANNEL_INFERENCE, self._on_inference_coord)
        self._wired = True

    # ── BUS handlers ─────────────────────────────────────────────────────────

    def _on_prompt(self, message: BusMessage):
        """PROMPT channel → set boundary on T1."""
        if message.priority <= Priority.T1:
            boundary_hash = self._monitor.set_boundary(message.payload)
            self._publish(f"boundary_set:{boundary_hash}", Priority.T0)

    def _on_inference_coord(self, message: BusMessage):
        """INFERENCE_COORDS channel → check each step."""
        halt, reason = self._monitor.check(message.payload)
        if halt:
            self._halt_pass(reason, message.payload)

    # ── Halt pass ─────────────────────────────────────────────────────────────

    def _halt_pass(self, reason: str, coords):
        """
        YOU SHALL NOT PASS — boundary marker, not kill signal.
        Commits halt record to blockchain, publishes LUTHSPELL, calls Ptolemy.
        """
        record = HaltRecord(reason, coords, self._monitor.boundary_hash)

        if self._chain:
            self._chain.add_block(record.to_dict())

        self._publish(f"halt:{reason}", Priority.T0)

        if self._on_halt:
            self._on_halt(record)

    # ── Priority arbitration (traffic circle) ─────────────────────────────────

    def arbitrate(self, messages: list[BusMessage]) -> list[BusMessage]:
        """
        Rotary semaphore: T0 always before T1, FIFO within same priority.
        Module hook — swap scheme via Settings.
        """
        if PRIORITY_SCHEME == "rotary":
            return sorted(messages, key=lambda m: m.priority)
        raise NotImplementedError(f"Priority scheme '{PRIORITY_SCHEME}' not wired")

    # ── Publish ───────────────────────────────────────────────────────────────

    def _publish(self, payload, priority: Priority = Priority.T0):
        msg = BusMessage(CHANNEL_LUTHSPELL, payload, priority)
        self._bus.publish(msg)

    # ── Passthrough for Ptolemy ───────────────────────────────────────────────

    def set_boundary(self, coords) -> str:
        """Direct call from Ptolemy to set boundary manually."""
        return self._monitor.set_boundary(coords)

    def check(self, coords) -> tuple[bool, Optional[str]]:
        """Direct call from Ptolemy to check coords manually."""
        return self._monitor.check(coords)

    @property
    def halt_records(self) -> list[HaltRecord]:
        return self._monitor.halt_records

    def __repr__(self):
        return f"LuthSpell(wired={self._wired}, halts={len(self.halt_records)})"
