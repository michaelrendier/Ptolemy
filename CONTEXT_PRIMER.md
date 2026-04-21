# Ptolemy Context Primer — 2026-04-20

## Architecture: Noether Information Current

- Sedenion is the (I|O) of the Noether Information Current
- Based on catastrophic light dumping from a waveform entering a spherical medium
- Non-isotropic shape has multiple focal points
- Focal points tested: if they map onto a single point, they are relevant
- (I|O) finds different descriptions of the same thing and maps multiple focal points into a single non-extinct data collection
- Whole is then catastrophically collapsed to a single focal point
- Tuning: move focal point slightly before or slightly after the catastrophic waveform collapse
- THE CURRENT SELECTS THE RESPONSE
- Data input is gated when a prompt is sent — buffered, queued, thread paused

## Multiple Focal Points
- SOLVED

## Pipeline Order
[PROMPT INPUT] → [GATE: pause ingestion thread] → [CONTEXT BUFFER] → [RESPONSE] → [THREAD RESUMES]

## Gate
- Triggered by prompt submission
- Pauses data ingestion thread
- Queues it
- Thread resumes AFTER response

## Context Buffer (3 Layers)
- Layer 1: 2x Claude context size — history of prompts without responses — FIFO cycle
- Layer 2: FIFO overflow prompt gets reduced in size to maintain proper context depth
- Layer 3: Indexing through HyperWebster → JSON file + Vast Repository = persistent memory

## Context Buffer Notes
- Not continuous — it is a handler for every prompt
- Prompt processed Everett Many Worlds style by Lagrangian of SMNNIP
- Rotations happen in octonion layer by attempting to map multiple focal points into single focal point
- Those that can't map are extinct
- If multiple focal points remain after extinction mapping, (I|O) determines which are the same object from different angles
- Response remains, may need tuning

## TITO
- Text In Text Out — the entire model operates on this principle
- Analogous to I/O, 1 and 0

## Ptolemy's Ears — Prompt Input
- Text input function is the entry point
- Speech recognition is separate — it outputs text — feeds same input function
- Single normalized text stream regardless of source
- Event-driven: submission event (Enter/Send) triggers the Gate
- Not polled — system waits

## Current Task
- Build prompt input function (ptolemy_ears)
- Chain: ptolemy_ears → gate → context buffer → response → thread resume
