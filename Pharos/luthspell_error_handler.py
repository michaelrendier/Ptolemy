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


class PtolemyError(Exception):
    code="PTL_000"; severity=Severity.ERROR; gc_trigger=False
    def __init__(self, detail="", context=None):
        self.detail=detail; self.context=context; self.timestamp=time.time()
        super().__init__(f"[{self.code}] {detail}")
    def to_dict(self):
        return {"code":self.code,"severity":self.severity.name,
                "detail":self.detail,"context":str(self.context),"timestamp":self.timestamp}

class BusChannelNotFound(PtolemyError):
    """Published message targets a channel with no subscribers."""     code="PTL_101"; severity=Severity.WARN
class BusMessageMalformed(PtolemyError):
    """BusMessage missing required fields or has invalid payload type."""    code="PTL_102"; severity=Severity.ERROR
class BusOverflow(PtolemyError):
    """Priority queue full and T1 eviction failed. GC triggered."""            code="PTL_103"; severity=Severity.FATAL; gc_trigger=True
class BusPriorityViolation(PtolemyError):
    """Message priority value outside T0/T1 range."""   code="PTL_104"; severity=Severity.ERROR
class BusDeadlock(PtolemyError):
    """Dispatch thread detected circular wait condition. GC triggered."""             code="PTL_105"; severity=Severity.FATAL; gc_trigger=True
class BoundaryNotSet(PtolemyError):
    """LuthSpell.check() called before set_boundary() on this inference."""         code="PTL_201"; severity=Severity.WARN
class HaltPassFailed(PtolemyError):
    """halt_pass() could not write HaltRecord to blockchain. FATAL."""         code="PTL_202"; severity=Severity.FATAL; gc_trigger=True
class BoundaryCorrupted(PtolemyError):
    """Boundary hash mismatch — record tampered or bit-flipped. FATAL."""      code="PTL_203"; severity=Severity.FATAL; gc_trigger=True
class InfiniteHaltLoop(PtolemyError):
    """halt_pass() triggered from within a halt handler. FATAL."""       code="PTL_204"; severity=Severity.FATAL; gc_trigger=True
class RedirectFailed(PtolemyError):
    """Ptolemy could not redirect inference after halt. FATAL."""         code="PTL_205"; severity=Severity.FATAL; gc_trigger=True
class BufferEvictionFailed(PtolemyError):
    """CyclicContextBuffer eviction policy could not free a slot."""   code="PTL_301"; severity=Severity.ERROR
class BufferIntegrityViolation(PtolemyError):
    """Buffer checksum mismatch — context window corrupted. FATAL."""code="PTL_302";severity=Severity.FATAL; gc_trigger=True
class BufferOverCapacity(PtolemyError):
    """Buffer write exceeds max capacity and eviction is disabled."""     code="PTL_303"; severity=Severity.ERROR
class CompressionFailed(PtolemyError):
    """HyperWebster payload compression/encoding step failed."""      code="PTL_304"; severity=Severity.ERROR
class HyperindexFailed(PtolemyError):
    """Horner bijection could not index string — charset mismatch."""        code="PTL_305"; severity=Severity.ERROR
class BlockchainCommitFailed(PtolemyError):
    """PtolChain block write failed — disk, lock, or integrity error. FATAL.""" code="PTL_401"; severity=Severity.FATAL; gc_trigger=True
class ChainIntegrityViolation(PtolemyError):
    """Block hash chain broken — tampering or corruption detected. FATAL."""code="PTL_402"; severity=Severity.FATAL; gc_trigger=True
class GenesisBlockMissing(PtolemyError):
    """Chain opened but genesis block absent — uninitialized or deleted. FATAL."""    code="PTL_403"; severity=Severity.FATAL; gc_trigger=True
class BranchOrphan(PtolemyError):
    """Branch block references unknown parent hash."""           code="PTL_404"; severity=Severity.ERROR
class WordAcquisitionFailed(PtolemyError):
    """acquire() returned empty result for all sources."""  code="PTL_501"; severity=Severity.WARN
class AcquisitionAPITimeout(PtolemyError):
    """FreeDictionary/Datamuse/Wiktionary request timed out."""  code="PTL_502"; severity=Severity.WARN
class WordRecordCorrupted(PtolemyError):
    """JSON shard on disk failed validation — field missing or wrong type."""    code="PTL_503"; severity=Severity.ERROR
class RabiesViolation(PtolemyError):
    """first_encountered IMMUTABLE. No GC — logical violation, not memory."""
    code="PTL_504"; severity=Severity.FATAL; gc_trigger=False
class SemanticWordBridgeFailed(PtolemyError):
    """Cross-language bridge could not resolve meaning vector."""code="PTL_505";severity=Severity.ERROR
class MonadIsolationViolation(PtolemyError):
    """WordMonad state was written from outside its owning layer. FATAL."""code="PTL_601"; severity=Severity.FATAL; gc_trigger=True
class InferenceCoordInvalid(PtolemyError):
    """Octonion coordinate outside valid address space bounds."""  code="PTL_602"; severity=Severity.ERROR
class LSHModelNotInitialized(PtolemyError):
    """LSH inference called before model weights loaded. FATAL, no GC.""" code="PTL_603"; severity=Severity.FATAL; gc_trigger=False
class GrammarNeuronFailed(PtolemyError):
    """GrammarNeuron could not parse sentence structure for this language."""    code="PTL_604"; severity=Severity.WARN
class SelfAdjointViolation(PtolemyError):
    """Operator failed self-adjoint check — Hermitian property violated."""   code="PTL_605"; severity=Severity.ERROR
class ModuleNotWired(PtolemyError):
    """Face module called before PtolBus.subscribe() completed wiring."""         code="PTL_701"; severity=Severity.ERROR
class SettingsKeyMissing(PtolemyError):
    """Required key absent from settings.json — module cannot start."""     code="PTL_702"; severity=Severity.ERROR
class ModuleSwapFailed(PtolemyError):
    """Hot-swap of module failed — old module unloaded, new failed to wire. FATAL."""       code="PTL_703"; severity=Severity.FATAL; gc_trigger=True
class SettingsIntegrityViolation(PtolemyError):
    """settings.json checksum mismatch — file tampered after load. FATAL, no GC."""code="PTL_704";severity=Severity.FATAL;gc_trigger=False
class PtolemyNotInitialized(PtolemyError):
    """Face or subsystem called before Ptolemy root initialised. FATAL, no GC."""  code="PTL_901"; severity=Severity.FATAL; gc_trigger=False
class FaceNotFound(PtolemyError):
    """PtolBus.import_face() could not locate named Face module."""            code="PTL_902"; severity=Severity.ERROR
class LuthSpellNotWired(PtolemyError):
    """System operation called before LuthSpell.wire() completed. FATAL, no GC."""      code="PTL_903"; severity=Severity.FATAL; gc_trigger=False
class UnknownError(PtolemyError):
    """Unclassified exception — wraps any non-PtolemyError. GC triggered."""            code="PTL_999"; severity=Severity.FATAL; gc_trigger=True


class GarbageCollector:
    """
    Ptolemy GC — object registry with triggered collection.

    All objects that need cleanup on fatal errors register here.
    ErrorHandler calls collect() when error.gc_trigger is True.
    Aule is the sole caller of collect() outside ErrorHandler.

    Note: PTL_504 RabiesViolation is FATAL but gc_trigger=False —
    a Rabies violation is a logical error, not a memory leak.
    """
    def __init__(self):
        self._registry: dict[int,Any] = {}
        self._gc_log: list[dict] = []
    def register(self, obj): self._registry[id(obj)] = obj
    def release(self, obj): self._registry.pop(id(obj), None)
    def collect(self, reason="triggered"):
        count = len(self._registry)
        self._gc_log.append({"reason":reason,"count":count,"timestamp":time.time()})
        self._registry.clear(); return count
    @property
    def gc_log(self): return list(self._gc_log)
    def __len__(self): return len(self._registry)


class ErrorHandler:
    def __init__(self, gc=None, on_error=None):
        self._gc = gc or GarbageCollector()
        self._on_error = on_error; self._log = []
    def handle(self, error, context=None):
        if not isinstance(error, PtolemyError):
            error = UnknownError(detail=str(error), context=traceback.format_exc())
        record = error.to_dict()
        if context: record["handler_context"] = str(context)
        self._log.append(record)
        self._emit(error)
        if error.gc_trigger:
            record["gc_collected"] = self._gc.collect(reason=error.code)
        min_sev = Severity[ERROR_HANDLER_SETTINGS["report_to_ptolemy_severity"]]
        if error.severity >= min_sev and self._on_error: self._on_error(error)
        return error.severity
    def _emit(self, error):
        if ERROR_HANDLER_SETTINGS["log_backend"] == "stdout":
            print(f"[{error.severity.name}] {error.code}: {error.detail}")
    @property
    def log(self): return list(self._log)
    @property
    def gc(self): return self._gc