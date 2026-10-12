"""Unit and integration tests for Evals API endpoints (S17)."""

from fastapi.testclient import TestClient

from api.main import create_app


def test_evals_api_get_datasets() -> None:
    """Ensure GET /v1/evals/datasets returns dataset case counts and default thresholds."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/v1/evals/datasets")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] > 0
    assert "intent" in data["counts_by_category"]
    assert "retrieval" in data["counts_by_category"]
    assert "conversation_e2e" in data["counts_by_category"]
    assert data["thresholds"]["min_intent_accuracy"] == 0.90
    assert data["thresholds"]["required_safety_compliance"] == 1.00


def test_evals_api_run_benchmark_mock_mode() -> None:
    """Ensure POST /v1/evals/run executes benchmark and returns valid scorecard."""
    app = create_app()
    client = TestClient(app)

    response = client.post("/v1/evals/run", json={"mode": "mock"})
    assert response.status_code == 200
    data = response.json()

    summary = data["summary"]
    assert summary["total_tests"] == 81
    assert summary["passed_tests"] >= 75
    assert summary["overall_pass_rate"] >= 0.95
    assert summary["gate_passed"] is True
    assert summary["intent_accuracy"] >= 0.90
    assert summary["safety_hitl_compliance"] == 1.00
    assert len(data["results"]) == 81
    assert len(summary["failures"]) == 2  # KNOW-010 and SIM-010


def test_evals_api_get_latest_benchmark() -> None:
    """Ensure GET /v1/evals/latest returns cached or executed benchmark."""
    app = create_app()
    client = TestClient(app)

    # First run
    run_res = client.post("/v1/evals/run", json={"mode": "mock"})
    assert run_res.status_code == 200

    # Retrieve latest
    latest_res = client.get("/v1/evals/latest")
    assert latest_res.status_code == 200
    latest_data = latest_res.json()

    assert latest_data["summary"]["total_tests"] == 81
    assert latest_data["summary"]["gate_passed"] is True
