# Tasks — S19 · Observability

- [ ] Implement asynchronous context management for `correlation_id` and `session_id` using `ContextVar` in `src/ops/context.py`.
- [ ] Configure structured JSON logging with `structlog` and integrate PII sanitization in `src/ops/logger.py`.
- [ ] Configure OpenTelemetry tracer provider, span decorators, and context injection in `src/ops/tracing.py`.
- [ ] Define Prometheus metrics (latency histograms, token counters, stage durations) in `src/ops/metrics.py`.
- [ ] Implement FastAPI middleware extracting/injecting `X-Correlation-ID` and exposing `GET /metrics` in `src/ops/middleware.py`.
- [ ] Instrument Agent Graph nodes (Router, RAG, MCP, Validator) with dedicated tracing spans and duration timers.
- [ ] Instrument Ollama provider adapter to capture token usage (`prompt_eval_count`, `eval_count`).
- [ ] Create Grafana dashboard definition in `ops/dashboards/atlas_overview.json`.
- [ ] Build unit and integration test suite in `tests/ops/` validating correlation propagation, log formatting, and metric endpoints.

## Definition of Done

- All tasks above are complete and merged.
- 100% of logs, traces, and metrics are bound to the active `correlation_id`.
- End-to-end trace view clearly visualizes all stages of the agent pipeline with accurate latency breakdown.
- Prometheus `/metrics` endpoint exports request rates, stage latencies, and token counters.
- Zero unhandled logging exceptions and zero unmasked sensitive PII in log records.
- Integration tests pass in CI.
