#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PtolBus.py — Ptolemy Message Bus
==================================
Pharos Layer

Real implementation replacing PtolBusStub.

Architecture:
    - Channel-based pub/sub (string channel names)
    - T0/T1 priority queue (rotary semaphore — traffic circle, not binary gate)
    - Thread-safe: QMutex-guarded queue, QThread dispatcher
    - Faces subscribe by channel; bus delivers in priority order
    - LuthSpell wires into PROMPT / INFERENCE_COORDS / LUTHSPELL channels
    - All channel names are module-level constants — swappable via Settings

Rotary Semaphore:
    T0 = system / halting priority  (always goes first)
    T1 = normal face traffic
    Arbitration: drain all T0 before any T1 — no starvation because
    T0 messages are short-lived control signals, not data streams.

Settings (module hooks → Settings tab):
    PTOL_BUS_SETTINGS keys map 1:1 to PtolBusSettings tab fields.
"""

import time
import queue
import threading
from enum import IntEnum
from typing import Callable, Dict, List, Optional

from PyQt5.QtCore import QObject, QThread, QMutex, QMutexLocker, pyqtSignal


# ── Channel names ─────────────────────────────────────────────────────────────
CH_PROMPT         = "PROMPT"
CH_INFERENCE      = "INFERENCE_COORDS"
CH_LUTHSPELL      = "LUTHSPELL"
CH_FACE_EVENT     = "FACE_EVENT"
CH_SENSOR         = "SENSOR"
CH_LOG            = "LOG"
CH_BLOCKCHAIN     = "BLOCKCHAIN"
CH_SETTINGS       = "SETTINGS"

# ── Settings block (→ PtolBusSettings tab) ────────────────────────────────────
PTOL_BUS_SETTINGS = {
    "priority_scheme":   "rotary",      # rotary | fifo
    "queue_maxsize":     1024,
    "dispatch_interval_ms": 10,         # dispatcher poll interval
    "log_channel":       CH_LOG,
}


class Priority(IntEnum):
    T0 = 0   # system / halting
    T1 = 1   # normal


class BusMessage:
    """Atomic unit on the bus."""
    __slots__ = ('channel', 'payload', 'priority', 'timestamp', 'sender')

    def __init__(self, channel: str, payload, priority: Priority = Priority.T1,
                 sender: str = None):
        self.channel   = channel
        self.payload   = payload
        self.priority  = priority
        self.timestamp = time.time()
        self.sender    = sender

    def __lt__(self, other):
        # For priority queue: lower priority value = higher urgency
        return self.priority < other.priority

    def __repr__(self):
        return (f"BusMessage(ch={self.channel!r}, pri={self.priority.name}, "
                f"sender={self.sender!r})")


class _DispatchThread(QThread):
    """
    Background thread: drains priority queue, delivers to subscribers.
    Runs inside PtolBus lifetime.
    """
    def __init__(self, bus: 'PtolBus'):
        super().__init__(bus)
        self._bus    = bus
        self._active = True

    def stop(self):
        self._active = False

    def run(self):
        interval = PTOL_BUS_SETTINGS["dispatch_interval_ms"] / 1000.0
        while self._active:
            self._bus._drain()
            time.sleep(interval)


class PtolBus(QObject):
    """
    Ptolemy Message Bus — channel pub/sub with rotary priority arbitration.

    Usage:
        bus = PtolBus(ptolemy)
        bus.start()

        bus.subscribe(CH_PROMPT, my_handler)          # register
        bus.publish(BusMessage(CH_PROMPT, "hello"))   # send
        bus.stop()                                    # shutdown

    Convenience:
        bus.emit(channel, payload, priority=Priority.T1, sender=None)
    """

    # Qt signals for process graph / face monitor
    message_dispatched = pyqtSignal(str, str)   # channel, sender

    def __init__(self, ptolemy=None, parent=None):
        super().__init__(parent or ptolemy)
        self.Ptolemy     = ptolemy
        self._queue      = queue.PriorityQueue(
            maxsize=PTOL_BUS_SETTINGS["queue_maxsize"])
        self._subscribers: Dict[str, List[Callable]] = {}
        self._mutex      = QMutex()
        self._thread     = _DispatchThread(self)
        self._seq        = 0   # tie-break for equal-priority messages

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        """Start the dispatch thread."""
        self._thread.start()

    def stop(self):
        """Graceful shutdown — drain remaining messages, stop thread."""
        self._thread.stop()
        self._thread.quit()
        self._thread.wait(2000)

    # ── Pub/Sub ───────────────────────────────────────────────────────────────

    def subscribe(self, channel: str, handler: Callable):
        """Register handler for channel. Thread-safe."""
        with QMutexLocker(self._mutex):
            self._subscribers.setdefault(channel, [])
            if handler not in self._subscribers[channel]:
                self._subscribers[channel].append(handler)

    def unsubscribe(self, channel: str, handler: Callable):
        with QMutexLocker(self._mutex):
            subs = self._subscribers.get(channel, [])
            if handler in subs:
                subs.remove(handler)

    def publish(self, message: BusMessage):
        """
        Enqueue message. Non-blocking — drops silently if queue full
        (T1 traffic) or logs to CH_LOG (T0 traffic).
        """
        self._seq += 1
        try:
            # PriorityQueue item: (priority_value, seq, message)
            # seq is tie-breaker to preserve insertion order within same priority
            self._queue.put_nowait((message.priority, self._seq, message))
        except queue.Full:
            if message.priority == Priority.T0:
                # T0 is critical — force in by displacing oldest T1
                self._evict_t1_and_insert(message)

    def emit(self, channel: str, payload,
             priority: Priority = Priority.T1, sender: str = None):
        """Convenience: build and publish a BusMessage."""
        self.publish(BusMessage(channel, payload, priority, sender))

    # ── Internal ──────────────────────────────────────────────────────────────

    def _evict_t1_and_insert(self, message: BusMessage):
        """Emergency: remove one T1 item to make room for T0."""
        items = []
        evicted = False
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if not evicted and item[0] == Priority.T1:
                    evicted = True   # drop this one
                else:
                    items.append(item)
            except queue.Empty:
                break
        for item in items:
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                break
        self._seq += 1
        try:
            self._queue.put_nowait((message.priority, self._seq, message))
        except queue.Full:
            pass

    def _drain(self):
        """Called by dispatch thread. Deliver all queued messages."""
        # Rotary scheme: drain ALL T0 first, then one batch of T1
        t0_batch = []
        t1_batch = []
        while not self._queue.empty():
            try:
                pri, seq, msg = self._queue.get_nowait()
                if pri == Priority.T0:
                    t0_batch.append(msg)
                else:
                    t1_batch.append(msg)
            except queue.Empty:
                break

        for msg in t0_batch:
            self._deliver(msg)
        for msg in t1_batch:
            self._deliver(msg)

    def _deliver(self, message: BusMessage):
        """Deliver one message to all subscribers. Catches handler exceptions."""
        with QMutexLocker(self._mutex):
            handlers = list(self._subscribers.get(message.channel, []))
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                # Emit to log channel (won't recurse — CH_LOG handlers are safe)
                if message.channel != CH_LOG:
                    self.emit(CH_LOG,
                              {"error": str(e), "channel": message.channel},
                              Priority.T0, sender="PtolBus")
        self.message_dispatched.emit(message.channel, message.sender or "")

    # ── Status ────────────────────────────────────────────────────────────────

    def queue_depth(self) -> int:
        return self._queue.qsize()

    def subscriber_count(self, channel: str) -> int:
        return len(self._subscribers.get(channel, []))

    def channels(self) -> List[str]:
        return list(self._subscribers.keys())

    def __repr__(self):
        return (f"PtolBus(channels={len(self._subscribers)}, "
                f"queue={self.queue_depth()})")


# ══════════════════════════════════════════════════════════════════════════════
#  ARCHITECTURE FLAGS & TODOS
#  These define what the Bus becomes — not what it handles for others
# ══════════════════════════════════════════════════════════════════════════════

# FLAG: BUS_IS_THREADS
# The Bus owns and IS the thread pool. Fully isolated from Ptolemy kernel.
# Ptolemy hands Bus a resource budget at start. Bus manages allocation internally.
# TODO: Extract Bus into fully isolated module with zero Ptolemy imports.
# TODO: Bus registers itself to Ptolemy via single handshake, then operates autonomously.

# FLAG: FACE_POST_BOOT
# No Face exists to the system until Face.POST() completes.
# POST registers: face_id, channel subscriptions, thread requirements, stdio triple.
# Faces are NPCs — they respond, they do not initiate.
# TODO: Implement Face.POST() handshake in PtolFace mixin.
# TODO: Bus rejects any message to/from a Face that has not completed POST.

# FLAG: PER_FACE_STDIO
# Each Face gets its own stdin/stdout/stderr channels and threads.
# CH_FACE_IN, CH_FACE_OUT, CH_FACE_ERR — named by face_id.
# TODO: Allocate stdio channel triple on Face.POST().
# TODO: Per-Face thread allocation: stdin(A), stdout(B), stderr(C), work(D).

# FLAG: THREAD_POOL_DYNAMIC
# Ptolemy reserves Threads 0-4 (permanent, never parked by Bus).
# Per-Face minimum: 4 threads (stdio triple + work).
# Pool beyond that: dynamically sized by Aule based on available resources.
# Faces may request additional threads — Aule approves/denies via dmesg.
# TODO: Implement thread request/grant protocol via CH_LOG -> dmesg -> Aule.
# TODO: Aule writes pool size decisions back to dmesg; Bus reads and resizes.

# FLAG: ALL_BUS_EVENTS_TO_DMESG
# Every Bus event (launch, suspend, resume, terminate, error) writes to dmesg.
# Aule watches dmesg only. Bus never calls Aule directly.
# TODO: Replace all print() in Bus with dmesg writes via Aule channel.

# FLAG: EARLY_SYMPTOM_DETECTION
# Monitor recursion depth, memory growth rate, queue backpressure,
# thread starvation, SIGXCPU/SIGXFSZ approach — warn before losing control.
# Symptoms as color gradient on Heartbeat/TuningDisplay — not binary.
# TODO: Per-thread resource monitor with configurable thresholds.
# TODO: Queue depth growth rate (delta) as backpressure metric.
# TODO: Thread wait-time monitor — flag starvation before deadlock.

# FLAG: CYCLIC_CONTEXT_BUFFER_SHARED
# CyclicContextBuffer owned by Ptolemy kernel, not Philadelphos.
# All Faces read from it. Ptolemy routes SMNNIP data to per-Face instances.
# Surface behavior monolithic. Face separation explicit/requested only.
# TODO: Move CyclicContextBuffer ownership to Ptolemy3 kernel init.
# TODO: Bus delivers context updates to all subscribed Faces via CH_CONTEXT.

# FLAG: EMERGENCY_LK
# Little Kernel — AppArmor-level containment. Owned by Ptolemy kernel.
# Not managed by Bus — Bus is what LK manages during emergency.
# LK.engage(): graceful Face quit -> stop SMNNIP -> flush caches ->
#              force-terminate stragglers -> Desktop stays up ->
#              Bus restarts clean -> Aule gets full authority.
# Desktop cannot be a Face. Desktop is the floor Bus runs on.
# TODO: Implement LithKernel class at Ptolemy root (not Pharos, not a Face).
# TODO: LK owns Qt event loop reference directly — cannot be revoked by Bus.
# TODO: LK restart path: known good state, fast resume. Same as PC firmware.

# FLAG: FACE_NAME_DEMETRIUS
# Demetrius of Phaleron proposed the Library, designed the Mouseion model.
# Web/university Face = Demetrius. Mouseion is the place, not the Face.
# TODO: Rename Mouseion Face references to Demetrius where appropriate.

# FLAG: IMPORT_PTOLEMY_FINAL
# Ptolemy3.py is the last file with that name.
# Final state: `import Ptolemy` only. All structure in __init__.py chains.
# TODO: Each Face directory gets __init__.py exporting its canonical class.
# TODO: Ptolemy root __init__.py is the single public surface.
