# Verify — S19 · Observability

## Evidence checklist

- [ ] Trace correlation test output proving `correlation_id` continuity from FastAPI Gateway through Router, MCP tools, and Validator down to log lines.
- [ ] Structured log sample inspection confirming valid JSON schema, formatted timestamps, correlation IDs, and zero unmasked synthetic PII.
- [ ] Distributed trace visual export (OTel span list or Jaeger screenshot) showing granular sub-spans for all agent execution stages with accurate duration measurements.
- [ ] Token accounting verification output confirming recorded prompt and completion tokens per chat turn and session totals.
- [ ] Prometheus metrics scrape test showing valid Prometheus text output from `GET /metrics` with populated counters and histograms.
- [ ] Benchmarking test report confirming that observability middleware adds < 5ms of latency overhead per request.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — OpenTelemetry instrumentation, metric names, and log schema match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
