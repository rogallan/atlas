"""Structured JSON logging with correlation propagation and PII sanitization (S19)."""

import logging
import sys
from datetime import UTC, datetime
from typing import Any, cast

import structlog
from pydantic import BaseModel, Field
from structlog.types import EventDict, WrappedLogger

from ops.context import get_correlation_id, get_session_id
from security.sanitizers import sanitize_data_structure, sanitize_text


class StructuredLogRecord(BaseModel):
    """Schema specification for machine-parsable JSON application logs."""

    timestamp: str
    level: str
    correlation_id: str
    session_id: str
    component: str = "atlas-core"
    message: str
    duration_ms: float | None = None
    token_usage: dict[str, int] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def _add_context_vars(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Inject active correlation_id and session_id into every log record."""
    event_dict.setdefault("correlation_id", get_correlation_id())
    event_dict.setdefault("session_id", get_session_id())
    return event_dict


def _add_iso_timestamp(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO-8601 UTC timestamp to log record."""
    event_dict.setdefault("timestamp", datetime.now(UTC).isoformat())
    return event_dict


def _sanitize_pii_processor(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Mask synthetic Brazilian PII, CPFs, account numbers, and tokens in log event."""
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = sanitize_text(event_dict["event"])

    if "message" in event_dict and isinstance(event_dict["message"], str):
        event_dict["message"] = sanitize_text(event_dict["message"])

    # Sanitize metadata fields
    for key, val in list(event_dict.items()):
        if key not in ("timestamp", "level", "correlation_id", "session_id", "component"):
            event_dict[key] = sanitize_data_structure(val)

    return event_dict


def _format_for_schema(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Ensure output event conforms to StructuredLogRecord standard field names."""
    if "event" in event_dict and "message" not in event_dict:
        event_dict["message"] = event_dict.pop("event")
    event_dict["level"] = str(event_dict.get("level", method_name)).upper()

    standard_keys = {
        "timestamp",
        "level",
        "correlation_id",
        "session_id",
        "component",
        "message",
        "duration_ms",
        "token_usage",
        "metadata",
        "logger",
    }
    meta = dict(event_dict.get("metadata", {}))
    extra_keys = [k for k in event_dict if k not in standard_keys]
    for k in extra_keys:
        meta[k] = event_dict.pop(k)
    event_dict["metadata"] = meta
    return event_dict


def configure_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """Configure structlog and standard logging pipeline."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        _add_context_vars,
        _add_iso_timestamp,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _sanitize_pii_processor,
        _format_for_schema,
    ]

    if json_format:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: str = "atlas") -> structlog.stdlib.BoundLogger:
    """Obtain a structured logger instance bound to a specific component."""
    logger = structlog.get_logger(name)
    return cast(structlog.stdlib.BoundLogger, logger.bind(component=name))
