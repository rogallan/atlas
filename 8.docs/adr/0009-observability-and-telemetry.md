# ADR 0009: Observability, Metrics, and Distributed Tracing Architecture

## Status
Accepted

## Date
2026-10-11

## Context
Per `1.SDDs/S19-observability/spec.md`, operating an enterprise GenAI copilot requires high-fidelity visibility into:
1. Operational HTTP traffic (throughput, status codes, latency percentiles p50/p95/p99).
2. Agent stage breakdown (router, RAG search, MCP tool invocation, validation, synthesis).
3. Token consumption and synthetic inference cost modeling.
4. End-to-end distributed trace propagation across the frontend, gateway, and backend services.

## Decision
Implemented a unified observability stack:
1. **Prometheus Metrics Exporter:**
   - Native endpoint at `/metrics`.
   - Core metrics: `atlas_http_requests_total`, `atlas_request_duration_seconds`, `atlas_stage_duration_seconds`, `atlas_tokens_consumed_total`, `atlas_hitl_action_total`.
2. **Token Accounting & Cost Store (`TokenAccountingStore`):**
   - In-memory thread-safe store tracking prompt and completion tokens per session, computing real-time estimated USD cost.
3. **Structured JSON Logging (`structlog`):**
   - Standard machine-parsable schema with ISO-8601 UTC timestamps, `correlation_id`, `session_id`, execution duration, and automatic PII sanitization.
4. **OpenTelemetry / AWS X-Ray Tracing (`tracing.py`):**
   - Context propagation via W3C Trace Context headers and AWS X-Ray compliant segment generation.

## Consequences
- **Positive:**
  - Real-time performance auditing and granular bottleneck identification.
  - Transparent token and cost accounting displayed directly on the management dashboard.
  - Full compatibility with Grafana, Prometheus scrapers, and CloudWatch Container Insights.
- **Negative / Mitigations:**
  - Minor memory overhead for session token metrics.
  - Addressed via periodic TTL cleanup and thread-safe data structures.
