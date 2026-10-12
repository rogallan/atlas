"""Observability subsystem package (S19)."""

from ops.context import (
    correlation_context,
    correlation_id_ctx,
    get_correlation_id,
    get_session_id,
    session_id_ctx,
    set_correlation_id,
    set_session_id,
)
from ops.logger import StructuredLogRecord, configure_logging, get_logger
from ops.metrics import (
    get_prometheus_metrics,
    record_hitl_action,
    record_http_request,
    record_intent_classification,
    record_stage_duration,
    token_store,
)
from ops.middleware import ObservabilityMiddleware, metrics_router
from ops.tracing import (
    clear_in_memory_spans,
    configure_tracing,
    get_in_memory_spans,
    get_tracer,
    trace_span,
    trace_span_async,
    traced,
)

__all__ = [
    "ObservabilityMiddleware",
    "StructuredLogRecord",
    "clear_in_memory_spans",
    "configure_logging",
    "configure_tracing",
    "correlation_context",
    "correlation_id_ctx",
    "get_correlation_id",
    "get_in_memory_spans",
    "get_logger",
    "get_prometheus_metrics",
    "get_session_id",
    "get_tracer",
    "metrics_router",
    "record_hitl_action",
    "record_http_request",
    "record_intent_classification",
    "record_stage_duration",
    "session_id_ctx",
    "set_correlation_id",
    "set_session_id",
    "token_store",
    "trace_span",
    "trace_span_async",
    "traced",
]
