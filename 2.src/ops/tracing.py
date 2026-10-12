"""OpenTelemetry distributed tracing configuration and span decorators (S19)."""

import contextlib
import functools
import inspect
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, TypeVar

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode

from ops.context import get_correlation_id, get_session_id

_in_memory_exporter: InMemorySpanExporter | None = None
_tracer_provider: TracerProvider | None = None
F = TypeVar("F", bound=Callable[..., Any])


def configure_tracing(
    service_name: str = "atlas-copilot",
    in_memory: bool = False,
) -> TracerProvider:
    """Initialize OpenTelemetry tracer provider with local or in-memory exporters."""
    global _tracer_provider, _in_memory_exporter

    if _tracer_provider is None:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        if in_memory:
            _in_memory_exporter = InMemorySpanExporter()
            processor = SimpleSpanProcessor(_in_memory_exporter)
            provider.add_span_processor(processor)

        with contextlib.suppress(Exception):
            trace.set_tracer_provider(provider)
        _tracer_provider = provider
    else:
        if in_memory and _in_memory_exporter is None:
            _in_memory_exporter = InMemorySpanExporter()
            processor = SimpleSpanProcessor(_in_memory_exporter)
            _tracer_provider.add_span_processor(processor)

    return _tracer_provider


def get_in_memory_spans() -> list[ReadableSpan]:
    """Retrieve exported in-memory spans for unit testing and trace verification."""
    if _in_memory_exporter is not None:
        return list(_in_memory_exporter.get_finished_spans())
    return []


def clear_in_memory_spans() -> None:
    """Clear previously captured in-memory spans."""
    if _in_memory_exporter is not None:
        _in_memory_exporter.clear()


def get_tracer(name: str = "atlas-copilot") -> trace.Tracer:
    """Obtain OpenTelemetry tracer instance."""
    if _tracer_provider is not None:
        return _tracer_provider.get_tracer(name)
    return trace.get_tracer(name)


@contextmanager
def trace_span(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> Generator[trace.Span, None, None]:
    """Synchronous context manager creating a distributed trace span."""
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        cid = get_correlation_id()
        sid = get_session_id()
        span.set_attribute("correlation_id", cid)
        span.set_attribute("session_id", sid)
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    span.set_attribute(k, str(v) if not isinstance(v, (int, float, bool)) else v)
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, description=str(exc)))
            raise


@asynccontextmanager
async def trace_span_async(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> AsyncGenerator[trace.Span, None]:
    """Asynchronous context manager creating a distributed trace span."""
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        cid = get_correlation_id()
        sid = get_session_id()
        span.set_attribute("correlation_id", cid)
        span.set_attribute("session_id", sid)
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    span.set_attribute(k, str(v) if not isinstance(v, (int, float, bool)) else v)
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, description=str(exc)))
            raise


def traced(
    span_name: str | None = None, attributes: dict[str, Any] | None = None
) -> Callable[[F], F]:
    """Decorator to instrument sync or async functions with an OpenTelemetry trace span."""

    def decorator(func: F) -> F:
        name = span_name or func.__qualname__

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                async with trace_span_async(name, attributes):
                    return await func(*args, **kwargs)

            return async_wrapper  # type: ignore[return-value]
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                with trace_span(name, attributes):
                    return func(*args, **kwargs)

            return sync_wrapper  # type: ignore[return-value]

    return decorator
