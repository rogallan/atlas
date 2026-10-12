"""Integration tests validating /v1/ops endpoints for frontend dashboard consumption (S19)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_get_ops_summary_endpoint() -> None:
    """Verify GET /v1/ops/summary returns populated operational metrics."""
    # Generate at least one request
    client.get("/health")

    response = client.get("/v1/ops/summary")
    assert response.status_code == 200
    data = response.json()

    assert "timestamp" in data
    assert "total_http_requests" in data
    assert "stage_latencies" in data
    assert "tokens" in data
    assert "intent_distribution" in data
    assert "hitl_actions" in data
    assert isinstance(data["stage_latencies"], list)
    assert len(data["stage_latencies"]) > 0


def test_get_recent_traces_endpoint() -> None:
    """Verify GET /v1/ops/traces returns list of recent OpenTelemetry spans."""
    response = client.get("/v1/ops/traces?limit=10")
    assert response.status_code == 200
    traces = response.json()
    assert isinstance(traces, list)


def test_simulate_traffic_endpoint() -> None:
    """Verify POST /v1/ops/simulate-traffic generates sample traffic successfully."""
    response = client.post("/v1/ops/simulate-traffic?count=3")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["simulated_interactions"] == 3

    # Check that summary reflects the traffic
    summary_res = client.get("/v1/ops/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["tokens"]["total_tokens"] > 0
