#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ptolemy Project — Root Layer
LuthSpell: Error Handler + Garbage Collector + Error Catalog
Belongs to: LuthSpell (which belongs to Ptolemy)
"""

from __future__ import annotations
import time, traceback
from enum import IntEnum
from typing import Callable, Optional, Any


ERROR_HANDLER_SETTINGS = {
    "gc_on_fatal":   True,
    "gc_on_error":   False,
    "log_backend":   "stdout",
    "report_to_ptolemy_severity": "ERROR",
}


class Severity(IntEnum):
    INFO=0; WARN=1; ERROR=2; FATAL=3


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR CATALOG — all Ptolemy errors typed here
# ═══════════════════════════════════════════════════════════════════════════════

class PtolemyError(Exception):
    code="PTL_000"; severity=Severity.ERROR; gc_trigger=False
    def __init__(self, detail="", context=None):
        self.detail=detail; self.context=context; self.timestamp=time.time()
        super().__init__(f"[{self.code}] {detail}")
    def to_dict(self):
        return {"code":self.code,"severity":self.severity.name,
                "detail":self.detail,"context":str(self.context),"timestamp":self.timestamp}

# BUS (PTL_1xx)
class BusChannelNotFound(PtolemyError):     code="PTL_101"; severity=Severity.WARN
class BusMessageMalformed(PtolemyError):    code="PTL_102"; severity=Severity.ERROR
class BusOverflow(PtolemyError):            code="PTL_103"; severity=Severity.FATAL; gc_trigger=True
class BusPriorityViolation(PtolemyError):   code="PTL_104"; severity=Severity.ERROR
class BusDeadlock(PtolemyError):            code="PTL_105"; severity=Severity.FATAL; gc_trigger=True

# LuthSpell / Halting (PTL_2xx)
class BoundaryNotSet(PtolemyError):         code="PTL_201"; severity=Severity.WARN
class HaltPassFailed(PtolemyError):         code="PTL_202"; severity=Severity.FATAL; gc_trigger=True
class BoundaryCorrupted(PtolemyError):      code="PTL_203"; severity=Severity.FATAL; gc_trigger=True
class InfiniteHaltLoop(PtolemyError):       code="PTL_204"; severity=Severity.FATAL; gc_trigger=True
class RedirectFailed(PtolemyError):         code="PTL_205"; severity=Severity.FATAL; gc_trigger=True

# Cyclic Context Buffer (PTL_3xx)
class BufferEvictionFailed(PtolemyError):   code="PTL_301"; severity=Severity.ERROR
class BufferIntegrityViolation(PtolemyError):code="PTL_302";severity=Severity.FATAL; gc_trigger=True
class BufferOverCapacity(PtolemyError):     code="PTL_303"; severity=Severity.ERROR
class CompressionFailed(PtolemyError):      code="PTL_304"; severity=Severity.ERROR
class HyperindexFailed(PtolemyError):       code="PTL_305"; severity=Severity.ERROR

# Blockchain (PTL_4xx)
class BlockchainCommitFailed(PtolemyError): code="PTL_401"; severity=Severity.FATAL; gc_trigger=True
class ChainIntegrityViolation(PtolemyError):code="PTL_402"; severity=Severity.FATAL; gc_trigger=True
class GenesisBlockMissing(PtolemyError):    code="PTL_403"; severity=Severity.FATAL; gc_trigger=True
class BranchOrphan(PtolemyError):           code="PTL_404"; severity=Severity.ERROR

# Acquisition / HyperWebster (PTL_5xx)
class WordAcquisitionFailed(PtolemyError):  code="PTL_501"; severity=Severity.WARN
class AcquisitionAPITimeout(PtolemyError):  code="PTL_502"; severity=Severity.WARN
class WordRecordCorrupted(PtolemyError):    code="PTL_503"; severity=Severity.ERROR
class RabiesViolation(PtolemyError):
    """first_encountered is IMMUTABLE. No GC — violation is logical, not memory."""
    code="PTL_504"; severity=Severity.FATAL; gc_trigger=False
class SemanticWordBridgeFailed(PtolemyError):code="PTL_505";severity=Severity.ERROR

# LSH Model (PTL_6xx)
class MonadIsolationViolation(PtolemyError):code="PTL_601"; severity=Severity.FATAL; gc_trigger=True
class InferenceCoordInvalid(PtolemyError):  code="PTL_602"; severity=Severity.ERROR
class LSHModelNotInitialized(PtolemyError): code="PTL_603"; severity=Severity.FATAL; gc_trigger=False
class GrammarNeuronFailed(PtolemyError):    code="PTL_604"; severity=Severity.WARN
class SelfAdjointViolation(PtolemyError):   code="PTL_605"; severity=Severity.ERROR

# Module / Settings (PTL_7xx)
class ModuleNotWired(PtolemyError):         code="PTL_701"; severity=Severity.ERROR
class SettingsKeyMissing(PtolemyError):     code="PTL_702"; severity=Severity.ERROR
class ModuleSwapFailed(PtolemyError):       code="PTL_703"; severity=Severity.FATAL; gc_trigger=True
class SettingsIntegrityViolation(PtolemyError):code="PTL_704";severity=Severity.FATAL;gc_trigger=False

# System / Root (PTL_9xx)
class PtolemyNotInitialized(PtolemyError):  code="PTL_901"; severity=Severity.FATAL; gc_trigger=False
class FaceNotFound(PtolemyError):           code="PTL_902"; severity=Severity.ERROR
class LuthSpellNotWired(PtolemyError):      code="PTL_903"; severity=Severity.FATAL; gc_trigger=False
class UnknownError(PtolemyError):           code="PTL_999"; severity=Severity.FATAL; gc_trigger=True


# ═══════════════════════════════════════════════════════════════════════════════
# GARBAGE COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class GarbageCollector:
    """
    Tracks object lifecycle. Triggered by ErrorHandler.
    C++ mirror: RAII destructor chain in Ptolemy++ (deferred).
    Module hook: swap backend via Settings.
    """
    def __init__(self):
        self._registry: dict[int,Any] = {}
        self._gc_log: list[dict] = []

    def register(self, obj: Any):
        self._registry[id(obj)] = obj

    def release(self, obj: Any):
        self._registry.pop(id(obj), None)

    def collect(self, reason: str = "triggered") -> int:
        count = len(self._registry)
        self._gc_log.append({"reason":reason,"count":count,"timestamp":time.time()})
        self._registry.clear()
        return count

    @property
    def gc_log(self): return list(self._gc_log)
    def __len__(self): return len(self._registry)


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class ErrorHandler:
    """
    LuthSpell's Error Handler.
    Catches → classifies → routes → triggers GC if needed → reports to Ptolemy.
    """
    def __init__(self, gc: Optional[GarbageCollector]=None, on_error: Optional[Callable]=None):
        self._gc = gc or GarbageCollector()
        self._on_error = on_error
        self._log: list[dict] = []

    def handle(self, error: Exception, context: Any=None) -> Severity:
        if not isinstance(error, PtolemyError):
            error = UnknownError(detail=str(error), context=traceback.format_exc())

        record = error.to_dict()
        if context: record["handler_context"] = str(context)
        self._log.append(record)
        self._emit(error)

        if error.gc_trigger:
            record["gc_collected"] = self._gc.collect(reason=error.code)

        min_sev = Severity[ERROR_HANDLER_SETTINGS["report_to_ptolemy_severity"]]
        if error.severity >= min_sev and self._on_error:
            self._on_error(error)

        return error.severity

    def _emit(self, error: PtolemyError):
        backend = ERROR_HANDLER_SETTINGS["log_backend"]
        if backend == "stdout":
            print(f"[{error.severity.name}] {error.code}: {error.detail}")

    @property
    def log(self): return list(self._log)
    @property
    def gc(self): return self._gc
