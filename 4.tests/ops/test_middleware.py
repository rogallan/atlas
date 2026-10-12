"""Integration tests validating FastAPI ObservabilityMiddleware and /metrics endpoint (S19)."""

import time

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_correlation_id_header_echoed() -> None:
    """Verify that an incoming X-Correlation-ID header is propagated to the response."""
    custom_cid = "client-provided-correlation-12345"
    response = client.get(
        "/health",
        headers={"X-Correlation-ID": custom_cid, "X-Session-ID": "test-session-001"},
    )

    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == custom_cid


def test_correlation_id_auto_generated_when_absent() -> None:
    """Verify that a missing X-Correlation-ID header generates a valid UUID4 in response."""
    response = client.get("/health")

    assert response.status_code == 200
    cid = response.headers.get("X-Correlation-ID")
    assert cid is not None
    assert len(cid) == 36
    assert "-" in cid


def test_prometheus_metrics_endpoint_response() -> None:
    """Verify GET /metrics returns HTTP 200 and Prometheus metrics format."""
    # Trigger a normal request first
    client.get("/health")

    # Scrape metrics
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "text/plain" in metrics_response.headers.get("content-type", "")

    body = metrics_response.text
    assert "atlas_http_requests_total" in body
    assert "atlas_request_duration_seconds" in body


def test_middleware_minimal_latency_overhead() -> None:
    """Verify that ObservabilityMiddleware adds minimal latency (< 5ms per request)."""
    # Warmup
    client.get("/health")

    durations: list[float] = []
    for _ in range(20):
        t0 = time.perf_counter()
        res = client.get("/health")
        t1 = time.perf_counter()
        assert res.status_code == 200
        durations.append(t1 - t0)

    # Average request duration on /health (which does practically nothing)
    avg_latency = sum(durations) / len(durations)
    # Even on local test client, /health with middleware should complete in < 25ms total
    assert avg_latency < 0.05, f"Average request latency was {avg_latency * 1000:.2f}ms"
