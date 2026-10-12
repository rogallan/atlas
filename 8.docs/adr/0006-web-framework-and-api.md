# ADR 0006: Web Framework and API Gateway (FastAPI with Pydantic v2)

## Status
Accepted

## Date
2026-10-09

## Context
Per `1.SDDs/S03-fastapi-gateway/spec.md`, ATLAS requires a high-performance, asynchronous REST API gateway to expose conversational turns, server-sent events (SSE) for token streaming, health checks, metrics, and administrative endpoints.

Requirements:
- Native asynchronous execution (`asyncio`).
- Automatic OpenAPI documentation (Swagger / Redoc).
- High-speed request validation and serialization.
- Middleware hooks for correlation IDs, security sanitization, and Prometheus metrics.

## Decision
Selected **FastAPI** paired with **Pydantic v2**:
1. **Asynchronous Architecture:** Native ASGI running on **Uvicorn**, enabling concurrent streaming connections without blocking worker threads.
2. **Pydantic v2 Engine:** Core validation and serialization compiled in Rust, delivering 5x–20x performance improvement over Pydantic v1.
3. **Enterprise Middleware Stack:**
   - Correlation ID & Session ID injection into request context and response headers (`X-Correlation-ID`).
   - Prometheus metrics exporter mounted on `/metrics`.
   - Security sanitization and PII masking applied automatically.

## Consequences
- **Positive:**
  - Auto-generated, interactive OpenAPI documentation accessible at `/docs`.
  - Seamless streaming support for token-by-token LLM generation.
  - Zero friction when bridging Pydantic models between LangGraph, MCP, and API contracts.
- **Negative / Mitigations:**
  - Strict type hints required throughout all endpoint definitions.
  - Mitigated by enforcement through `mypy` and `ruff` in quality gates.
