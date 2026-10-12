"""Unit tests validating Prometheus metrics and token accounting (S19)."""

from ops.metrics import (
    get_prometheus_metrics,
    record_hitl_action,
    record_http_request,
    record_intent_classification,
    record_stage_duration,
    token_store,
)


def test_token_accounting_and_cost_estimation() -> None:
    """Verify session token tracking and synthetic cost calculations."""
    token_store.reset()

    # Turn 1
    token_store.record_usage(
        session_id="sess-001",
        prompt_tokens=400,
        completion_tokens=100,
        model="qwen2.5:7b-instruct",
    )

    # Turn 2
    token_store.record_usage(
        session_id="sess-001",
        prompt_tokens=600,
        completion_tokens=200,
        model="qwen2.5:7b-instruct",
    )

    usage = token_store.get_session_usage("sess-001")
    assert usage["prompt_tokens"] == 1000
    assert usage["completion_tokens"] == 300
    assert usage["total_tokens"] == 1300
    # Cost: (1000/1000 * 0.0005) + (300/1000 * 0.0015) = 0.0005 + 0.00045 = 0.00095
    assert usage["estimated_cost_usd"] == 0.00095
    assert "qwen2.5:7b-instruct" in usage["models_used"]


def test_token_accounting_empty_session() -> None:
    """Verify zero stats for non-existent session."""
    usage = token_store.get_session_usage("sess-empty")
    assert usage["prompt_tokens"] == 0
    assert usage["completion_tokens"] == 0
    assert usage["total_tokens"] == 0
    assert usage["estimated_cost_usd"] == 0.0


def test_prometheus_metrics_generation() -> None:
    """Verify Prometheus metrics exposition text contains registered metrics."""
    record_http_request("POST", "/v1/chat", 200, 0.45)
    record_stage_duration("router", 0.02)
    record_stage_duration("rag_search", 0.08)
    record_intent_classification("simulation")
    record_hitl_action("cancel_ticket", "approved")

    payload, content_type = get_prometheus_metrics()
    text = payload.decode("utf-8")

    assert "text/plain" in content_type or "version=0.0.4" in content_type
    assert "atlas_http_requests_total" in text
    assert "atlas_stage_duration_seconds" in text
    assert "atlas_intent_classifications_total" in text
    assert "atlas_hitl_action_total" in text
    assert 'endpoint="/v1/chat"' in text
    assert 'intent="simulation"' in text
