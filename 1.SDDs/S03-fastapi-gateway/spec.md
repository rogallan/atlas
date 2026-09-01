# Spec — S03 · FastAPI Gateway

> **Domain:** API · **Quarter:** Q1 · **Depends on:** S01 (Python Toolchain)

## 1. Goal

Stand up the FastAPI Gateway that will front every other ATLAS component (Agent, RAG, MCP) and be
the only entry point the React Chat frontend talks to, including through the ngrok tunnel.

## 2. Context

Per `architecture.md`, the API boundary owns contracts, streaming, simulated authentication, and
standardized error handling. This phase builds that boundary before any agent logic exists behind
it, so later phases (S05, S14) can be developed against a stable contract.

## 3. In scope

- `/health` and `/v1/sessions` endpoints.
- `/v1/chat` endpoint with streaming support.
- OpenAPI contract definition and payload validation.
- Standardized error handling.
- Simulated authentication (no real identity provider — per Constitution scope).

## 4. Out of scope

- Actual agent/RAG/MCP logic behind the endpoints (covered by S05–S14; this phase can return
  stubbed responses).
- Real authentication/identity provider integration.

## 5. Requirements

- **R1.** `GET /health` returns a liveness/readiness signal.
- **R2.** `POST /v1/sessions` creates a session (used to correlate a conversation).
- **R3.** `POST /v1/chat` accepts a chat message and streams the response (SSE).
- **R4.** All request/response schemas are defined and published via OpenAPI.
- **R5.** Invalid payloads return a standardized error format (consistent status codes and error
  body shape).
- **R6.** A simulated authentication mechanism (e.g., a static token/header check) gates access to
  `/v1/chat` and `/v1/sessions`.

## 6. Acceptance criteria

- OpenAPI docs are generated and browsable (e.g., `/docs`).
- Integration tests cover happy path and invalid-payload cases for each endpoint.
- Streaming responses are verified end-to-end in a test (chunked output received incrementally).
