# ADR 0003: Local-First Open LLM Runtime (Ollama with Qwen 2.5 7B Instruct)

## Status
Accepted

## Date
2026-10-07

## Context
Per `constitution.md` (Principle 1: Local-First) and `1.SDDs/S04-ollama-provider/spec.md`, ATLAS requires an open-weights, high-performance LLM runtime capable of local execution without sending sensitive financial queries or banking interactions to third-party commercial APIs.

Evaluation criteria:
1. Native Portuguese language fluency and compliance with Brazilian financial and regulatory nuances.
2. Structured output capabilities (JSON Mode / function calling) for routing and synthesis.
3. Reasonable hardware footprint (runs smoothly on consumer GPUs / Apple Silicon / modern x86 workstations).
4. Local daemon with standard REST API and streaming support.

## Decision
1. **LLM Runtime Daemon:** Selected **Ollama** as the local model runtime engine.
   - Standard HTTP API on `localhost:11434`, robust lifecycle management, zero cloud latency.
2. **Primary Foundation Model:** Selected **`qwen2.5:7b-instruct`**.
   - State-of-the-art benchmark results for 7B parameter models in multilingual reasoning, structured JSON generation, and adherence to system instructions.
3. **Resilience & Fallback Architecture:**
   - Implemented an asynchronous client (`OllamaClient`) with exponential backoff retry, health check validation, and mock fallback mode for continuous integration (CI) test isolation.

## Consequences
- **Positive:**
  - 100% data privacy: Customer financial profiles and regulatory queries never leave the developer machine.
  - Zero recurring API billing during development, testing, and evaluation harness runs.
  - High determinism with configurable temperature (0.0 for routing/validation).
- **Negative / Mitigations:**
  - Requires local machine to run Ollama daemon with ~5GB VRAM.
  - Mitigated by providing deterministic Mock providers for CI pipelines and test execution without GPU requirements.
