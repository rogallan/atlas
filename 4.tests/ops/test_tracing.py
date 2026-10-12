"""Unit tests validating OpenTelemetry tracing and span attributes (S19)."""

import pytest
from opentelemetry.trace import StatusCode

from ops.context import correlation_context
from ops.tracing import (
    clear_in_memory_spans,
    configure_tracing,
    get_in_memory_spans,
    trace_span,
    trace_span_async,
    traced,
)


@pytest.fixture(autouse=True)
def setup_tracing() -> None:
    """Ensure in-memory tracing is active for tests and cleared between runs."""
    configure_tracing(service_name="atlas-test", in_memory=True)
    clear_in_memory_spans()


def test_sync_trace_span_attributes() -> None:
    """Verify synchronous span creation with attributes and correlation context."""
    with (
        correlation_context(correlation_id="trace-cid-1", session_id="trace-sid-1"),
        trace_span("agent.router", attributes={"confidence": 0.95, "model": "local"}),
    ):
        pass

    spans = get_in_memory_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "agent.router"
    assert span.attributes is not None
    assert span.attributes["correlation_id"] == "trace-cid-1"
    assert span.attributes["session_id"] == "trace-sid-1"
    assert span.attributes["confidence"] == 0.95
    assert span.attributes["model"] == "local"
    assert span.status.status_code == StatusCode.OK


@pytest.mark.asyncio
async def test_async_trace_span_attributes() -> None:
    """Verify asynchronous span creation."""
    with correlation_context(correlation_id="async-cid", session_id="async-sid"):
        async with trace_span_async("agent.mcp_tool", attributes={"tool": "calculate_loan"}):
            pass

    spans = get_in_memory_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "agent.mcp_tool"
    assert span.attributes is not None
    assert span.attributes["correlation_id"] == "async-cid"
    assert span.attributes["tool"] == "calculate_loan"
    assert span.status.status_code == StatusCode.OK


def test_trace_span_exception_recording() -> None:
    """Verify that exceptions inside a span are recorded with ERROR status."""
    with (
        correlation_context(correlation_id="err-cid", session_id="err-sid"),
        pytest.raises(ValueError, match="Synthetic failure"),
        trace_span("agent.failing_stage"),
    ):
        raise ValueError("Synthetic failure")

    spans = get_in_memory_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "agent.failing_stage"
    assert span.status.status_code == StatusCode.ERROR
    assert "Synthetic failure" in str(span.status.description)
    assert len(span.events) > 0  # Exception event recorded


@pytest.mark.asyncio
async def test_traced_decorator() -> None:
    """Verify @traced decorator for both sync and async functions."""

    @traced("service.sync_operation")
    def sync_op(x: int) -> int:
        return x * 2

    @traced("service.async_operation")
    async def async_op(x: int) -> int:
        return x + 10

    with correlation_context(correlation_id="dec-cid", session_id="dec-sid"):
        res1 = sync_op(5)
        res2 = await async_op(5)

    assert res1 == 10
    assert res2 == 15

    spans = get_in_memory_spans()
    span_names = [s.name for s in spans]
    assert "service.sync_operation" in span_names
    assert "service.async_operation" in span_names
