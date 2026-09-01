# Spec — S04 · Ollama Provider

> **Domain:** LLM · **Quarter:** Q1 · **Depends on:** S01 (Python Toolchain)

## 1. Goal

Provide a decoupled LLM provider that talks to Ollama, so the Agent Orchestrator (S05, S14) can
call a stable interface without depending on Ollama specifics — enabling model swaps and reliable
failure handling.

## 2. Context

Per `architecture.md`, the Agent boundary uses Ollama as its local LLM. To keep that boundary
testable and swappable, the LLM call must sit behind an adapter/interface rather than being called
directly from agent code.

## 3. In scope

- A provider interface (abstract) plus a concrete Ollama implementation.
- Model selection via configuration (not hardcoded).
- Timeout, retry, and fallback behavior.
- Structured output support (the provider can request/validate JSON-shaped responses).

## 4. Out of scope

- The Intent Router and agent logic that will consume this provider (covered in S05, S14).
- Any non-Ollama provider implementation (kept possible via the interface, not built now).

## 5. Requirements

- **R1.** A `LLMProvider` interface defines at least `generate()` and `generate_structured()`
  methods, independent of Ollama's specific API.
- **R2.** The Ollama implementation is selected and configured (model name, host, etc.) via
  environment/config, not hardcoded.
- **R3.** Calls to Ollama have a configurable timeout.
- **R4.** Failed calls are retried with backoff, up to a configurable limit, before falling back to
  a defined failure behavior (e.g., raising a typed error the caller can handle).
- **R5.** `generate_structured()` validates the model's output against a given schema and surfaces
  a clear error when validation fails (no silent corruption of malformed output).

## 6. Acceptance criteria

- Swapping the configured model name changes behavior without any code change.
- A simulated Ollama timeout/failure in tests triggers the configured retry/fallback behavior.
- Structured output is validated against a schema in a contract test.
