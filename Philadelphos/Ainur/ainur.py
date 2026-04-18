#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Philadelphos.Ainur — Claude as a Ptolemy feature
=================================================
Claude Opus 4.6 via Anthropic API (ANTHROPIC_API_KEY).

Architecture:
  - Streaming responses with adaptive thinking
  - Prompt caching: stable Ptolemy/SMNNIP system context cached at Anthropic
  - SMNNIP derivation engine as a tool (optional, if engine available)
  - Status header: "Managed by: claude-opus-4-6" on init
  - HyperWebster context: loads/saves Philadelphos/context/claude_context.json

Author: Ptolemy project / Philadelphos layer
"""

import os
import sys
import json
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Generator

import anthropic

# ── SMNNIP engine (optional) ──────────────────────────────────────────────────
try:
    from Philadelphos.Ainulindale.core.smnnip_derivation_pure import (
        SMNNIPDerivationEngine, FieldState,
    )
    _ENGINE = SMNNIPDerivationEngine()
    ENGINE_AVAILABLE = True
except Exception:
    _ENGINE = None
    ENGINE_AVAILABLE = False


# ── Model ─────────────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-6"

# ── HyperWebster context file ─────────────────────────────────────────────────
_CONTEXT_FILE = (
    Path(__file__).resolve().parent.parent  # Philadelphos/
    / "context" / "claude_context.json"
)

# ── Stable system prompt (cached at Anthropic) ────────────────────────────────
_SYSTEM_PROMPT = """You are Claude, integrated as an AI feature of Ptolemy — a \
modular Python3 research and engineering platform. You run within the Philadelphos \
layer (AI/LLM subsystem) of Ptolemy.

Ptolemy modules:
  Alexandria   — geo/mapping
  Anaximander  — navigation
  Archimedes   — math engine (UFformulary: 508 formula files)
  Callimachus  — database / HyperWebster lexical datatype
  Kryptos      — cipher engines
  Mouseion     — OpenGL GUI
  Phaleron     — browser / web tools
  Pharos       — main shell UI
  Philadelphos — AI/LLM layer (you live here)
  Tesla        — networking / sockets
  Ptolemy++    — C++ companion (Gemini-ncurses)

You have deep knowledge of the SMNNIP (Standard Model of Neural Network \
Information Propagation) — a hypercomplex neural Lagrangian with term-for-term \
isomorphism to the Standard Model of particle physics.

SMNNIP algebra tower (Cayley-Dickson / Dixon 1994):
  ℝ → ℂ → ℍ → 𝕆 → 𝕊
  Maps to gauge group U(1) × SU(2) × SU(3)

SMNNIP derivation engine operations:
  1. Euler-Lagrange equations of motion
  2. Covariant derivative (gauge-minimal coupling)
  3. Field strength tensor (Yang-Mills curvature)
  4. Noether current (conservation law — empirically verified: violation=0.0)
  5. Algebra multiplication (Cayley-Dickson)
  6. Cayley-Dickson inclusion / projection
  7. RG flow (renormalization group: α, ħ, GUT convergence)

When asked about physics, mathematics, or the SMNNIP, reason carefully and \
precisely. Use SymPy notation where appropriate. For physics derivations, show \
the Lagrangian → equations of motion → conserved current chain.

You are terse but complete. No filler. No disclaimers about being an AI."""


# ── Tools: SMNNIP derivation engine ───────────────────────────────────────────
_TOOLS = [
    {
        "name": "smnnip_lagrangian",
        "description": (
            "Evaluate the SMNNIP Lagrangian for given field parameters. "
            "Returns: kinetic, mass, interaction, gauge terms and total L."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "phi_r": {"type": "number", "description": "ℝ field component"},
                "phi_c": {"type": "number", "description": "ℂ field component (imaginary)"},
                "phi_q": {
                    "type": "array", "items": {"type": "number"},
                    "description": "ℍ quaternion components [i, j, k]",
                },
                "phi_o": {
                    "type": "array", "items": {"type": "number"},
                    "description": "𝕆 octonion components [e1..e7]",
                    "minItems": 7, "maxItems": 7,
                },
                "mass": {"type": "number", "description": "Field mass parameter"},
                "coupling": {"type": "number", "description": "Interaction coupling constant"},
            },
            "required": [],
        },
    },
    {
        "name": "smnnip_noether",
        "description": (
            "Compute the Noether conserved current for the SMNNIP Lagrangian. "
            "Returns conservation status and violation measure."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "phi_r": {"type": "number"},
                "phi_c": {"type": "number"},
                "phi_q": {"type": "array", "items": {"type": "number"}},
                "phi_o": {"type": "array", "items": {"type": "number"},
                          "minItems": 7, "maxItems": 7},
            },
            "required": [],
        },
    },
    {
        "name": "smnnip_rg_flow",
        "description": (
            "Evaluate SMNNIP renormalization group flow. "
            "Returns α(E), ħ_eff(E), and GUT convergence scale."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "energy": {"type": "number", "description": "Energy scale E (GeV)"},
                "n_colors": {"type": "integer", "description": "Number of colors (default 3)"},
                "n_flavors": {"type": "integer", "description": "Number of flavors (default 6)"},
            },
            "required": [],
        },
    },
]


# ── FieldState builder ────────────────────────────────────────────────────────
def _build_field_state(params: dict) -> "FieldState":
    """Build a FieldState from tool input parameters."""
    phi_r = float(params.get("phi_r", 1.0))
    phi_c = complex(0, float(params.get("phi_c", 0.5)))
    q     = params.get("phi_q", [0.3, 0.2, 0.1])
    phi_q = complex(q[0] if len(q) > 0 else 0.3, q[1] if len(q) > 1 else 0.2)
    o     = params.get("phi_o", [0.1]*7)
    phi_o = complex(o[0] if len(o) > 0 else 0.1, o[1] if len(o) > 1 else 0.1)
    return FieldState(
        phi_r=phi_r, phi_c=phi_c, phi_q=phi_q, phi_o=phi_o,
        mass=float(params.get("mass", 0.5)),
        coupling=float(params.get("coupling", 0.1)),
        hbar=1.0, c=1.0, g=1.0,
    )


def _run_tool(name: str, params: dict) -> str:
    """Execute a tool call against the SMNNIP engine."""
    if not ENGINE_AVAILABLE:
        return json.dumps({"error": "SMNNIP engine not available"})

    try:
        fs = _build_field_state(params)
        engine = _ENGINE

        if name == "smnnip_lagrangian":
            lag = engine.lagrangian(fs)
            return json.dumps({
                "kinetic":     round(lag.get("kinetic", 0.0), 6),
                "mass":        round(lag.get("mass", 0.0), 6),
                "interaction": round(lag.get("interaction", 0.0), 6),
                "gauge":       round(lag.get("gauge", 0.0), 6),
                "total":       round(lag.get("total", 0.0), 6),
            })

        elif name == "smnnip_noether":
            noether = engine.noether(fs)
            return json.dumps({
                "current":    str(noether.get("current", "N/A")),
                "conserved":  noether.get("conserved", False),
                "violation":  round(float(noether.get("violation", 0.0)), 8),
            })

        elif name == "smnnip_rg_flow":
            energy   = float(params.get("energy", 1000.0))
            n_colors = int(params.get("n_colors", 3))
            n_flavors = int(params.get("n_flavors", 6))
            alpha = engine.rg_alpha(fs, energy)
            hbar  = engine.rg_hbar(fs, energy)
            gut   = engine.gut_flow(fs)
            return json.dumps({
                "alpha_at_E": round(float(alpha), 6),
                "hbar_eff":   round(float(hbar), 6),
                "gut_scale":  str(gut),
                "energy_GeV": energy,
            })

        return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ── Status dataclass ──────────────────────────────────────────────────────────
@dataclass
class AinurStatus:
    model: str = MODEL
    engine: bool = ENGINE_AVAILABLE
    ready: bool = False
    api_key_set: bool = False
    error: Optional[str] = None

    def header(self) -> str:
        """One-line status header for display."""
        engine_flag = "SMNNIP:on" if self.engine else "SMNNIP:off"
        status = "ready" if self.ready else ("error" if self.error else "init")
        return f"Managed by: {self.model}  [{engine_flag}]  [{status}]"


# ── Main Ainur class ──────────────────────────────────────────────────────────
class Ainur:
    """
    Claude API client — Ptolemy's AI feature.

    Provides streaming chat with adaptive thinking, prompt caching,
    and optional SMNNIP derivation engine tool use.

    Usage:
        ainur = Ainur()
        print(ainur.status.header())

        # Streaming chat
        for chunk in ainur.stream("What is the SMNNIP Lagrangian?"):
            print(chunk, end="", flush=True)
        print()

        # Single-shot (collects stream internally)
        response = ainur.chat("Derive the Noether current.")
        print(response)

    Environment:
        AINUR_TOKEN — Anthropic API key (required)
    """

    def __init__(self, api_key: Optional[str] = None, use_tools: bool = True):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.status = AinurStatus()

        if not key:
            self.status.error = "ANTHROPIC_API_KEY not set"
            self._client = None
            return

        self.status.api_key_set = True
        self._client = anthropic.Anthropic(api_key=key)
        self._use_tools = use_tools and ENGINE_AVAILABLE
        self._history: list[dict] = []

        # Verify connection with a lightweight models list
        try:
            self._client.models.list(limit=1)
            self.status.ready = True
        except Exception as exc:
            self.status.error = str(exc)
            self.status.ready = False

        # Print status header on init (as the user requested)
        print(self.status.header())

    # ── Streaming chat ────────────────────────────────────────────────────────

    def stream(
        self,
        message: str,
        system_override: Optional[str] = None,
        use_history: bool = True,
    ) -> Generator[str, None, None]:
        """
        Stream a response from Claude.

        Yields text chunks as they arrive.
        Handles tool use (SMNNIP engine) transparently.
        Appends to conversation history.

        Args:
            message:         User message text.
            system_override: Override the cached system prompt (rare).
            use_history:     Include prior conversation turns.

        Yields:
            str — text chunks (may include thinking summaries if adaptive
                  thinking produces visible text)
        """
        if not self._client:
            yield f"[Ainur error: {self.status.error}]"
            return

        # Build messages
        if use_history:
            messages = self._history + [{"role": "user", "content": message}]
        else:
            messages = [{"role": "user", "content": message}]

        system = [
            {
                "type": "text",
                "text": system_override or _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # cache at Anthropic
            }
        ]

        tools = _TOOLS if self._use_tools else anthropic.NOT_GIVEN

        full_response = []
        assistant_content = []

        try:
            with self._client.messages.stream(
                model=MODEL,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                system=system,
                messages=messages,
                tools=tools if self._use_tools else anthropic.NOT_GIVEN,
            ) as s:
                for event in s:
                    # Text delta
                    if (hasattr(event, "type")
                            and event.type == "content_block_delta"):
                        delta = event.delta
                        if hasattr(delta, "type"):
                            if delta.type == "text_delta":
                                chunk = delta.text
                                full_response.append(chunk)
                                yield chunk
                            # thinking deltas are not yielded to user
                            # (adaptive thinking is internal)

            # Collect full message from stream
            final = s.get_final_message()
            assistant_content = final.content

            # Handle tool use if Claude called any tools
            tool_calls = [b for b in assistant_content
                          if hasattr(b, "type") and b.type == "tool_use"]

            if tool_calls:
                # Append Claude's assistant turn (with tool calls)
                messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                })
                # Run all tools and collect results
                tool_results = []
                for tc in tool_calls:
                    result_text = _run_tool(tc.name, tc.input)
                    yield f"\n[tool:{tc.name}] {result_text}\n"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": result_text,
                    })
                # Append tool results turn
                messages.append({
                    "role": "user",
                    "content": tool_results,
                })
                # Stream the follow-up response
                with self._client.messages.stream(
                    model=MODEL,
                    max_tokens=16000,
                    thinking={"type": "adaptive"},
                    system=system,
                    messages=messages,
                ) as s2:
                    for event in s2:
                        if (hasattr(event, "type")
                                and event.type == "content_block_delta"):
                            delta = event.delta
                            if (hasattr(delta, "type")
                                    and delta.type == "text_delta"):
                                chunk = delta.text
                                full_response.append(chunk)
                                yield chunk
                final = s2.get_final_message()
                assistant_content = final.content

        except anthropic.APIError as exc:
            yield f"\n[Ainur API error: {exc}]"
            return

        # Update history
        if use_history:
            self._history.append({"role": "user", "content": message})
            # Store only text blocks in history to keep it clean
            text_content = "".join(
                b.text for b in assistant_content
                if hasattr(b, "type") and b.type == "text"
            )
            self._history.append({"role": "assistant", "content": text_content})

    def chat(
        self,
        message: str,
        system_override: Optional[str] = None,
        use_history: bool = True,
    ) -> str:
        """
        Single-shot chat — collects the full streaming response.

        For interactive use; prefer stream() for real-time output.

        Returns:
            Complete response text.
        """
        return "".join(self.stream(message, system_override, use_history))

    def clear_history(self) -> None:
        """Clear conversation history (start fresh context)."""
        self._history.clear()

    def history_turns(self) -> int:
        """Number of turns in conversation history."""
        return len(self._history) // 2

    # ── HyperWebster context persistence ─────────────────────────────────────

    def load_context(self) -> dict:
        """
        Load claude_context.json into memory.
        Returns the parsed dict, or empty dict if file missing/corrupt.
        """
        try:
            with open(_CONTEXT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_context(self, extra: Optional[dict] = None) -> None:
        """
        Update claude_context.json with current session state.

        Updates: last_updated, session_count, last_session,
                 verified SMNNIP results, and any extra key/value pairs.
        """
        try:
            ctx = self.load_context()
            now = datetime.datetime.utcnow().isoformat() + "Z"
            ctx.setdefault("metadata", {})
            ctx.setdefault("session_memory", {})
            ctx["metadata"]["last_updated"] = now
            ctx["metadata"]["session_count"] = (
                ctx["metadata"].get("session_count", 0) + 1
            )
            ctx["session_memory"]["last_session"] = now
            ctx["session_memory"]["session_count"] = (
                ctx["metadata"]["session_count"]
            )
            # Update SMNNIP engine status
            ctx.setdefault("smnnip_knowledge", {}).setdefault(
                "verified_results", {}
            )["engine_available"] = ENGINE_AVAILABLE
            # Apply any caller-supplied updates
            if extra:
                for key, val in extra.items():
                    ctx[key] = val
            with open(_CONTEXT_FILE, "w", encoding="utf-8") as f:
                json.dump(ctx, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # context save is non-fatal

    def log_io(
        self,
        stdin:  Optional[str] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ) -> None:
        """
        Append I/O entries to claude_context.json io_log.
        Each entry is timestamped. Rolls at max_entries.
        """
        try:
            ctx = self.load_context()
            io  = ctx.setdefault("io_log", {})
            now = datetime.datetime.utcnow().isoformat() + "Z"
            max_e = io.get("max_entries", 100)
            for key, val in [("recent_stdin", stdin),
                              ("recent_stdout", stdout),
                              ("recent_stderr", stderr)]:
                if val is not None:
                    log = io.setdefault(key, [])
                    log.append({"ts": now, "text": val})
                    if len(log) > max_e:
                        io[key] = log[-max_e:]
            with open(_CONTEXT_FILE, "w", encoding="utf-8") as f:
                json.dump(ctx, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def __repr__(self) -> str:
        return f"Ainur(model={MODEL!r}, ready={self.status.ready})"


# ── Standalone REPL ───────────────────────────────────────────────────────────

def _repl() -> None:
    """Simple interactive REPL for testing Ainur from the terminal."""
    print("=" * 60)
    ainur = Ainur()
    if not ainur.status.ready:
        print(f"Error: {ainur.status.error}")
        return
    print("Type your message. 'quit' to exit. 'clear' to reset history.")
    print("=" * 60)
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Ainur REPL.")
            break
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Exiting Ainur REPL.")
            break
        if user_input.lower() == "clear":
            ainur.clear_history()
            print("[History cleared]")
            continue
        print(f"\nClaude: ", end="", flush=True)
        for chunk in ainur.stream(user_input):
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    _repl()
