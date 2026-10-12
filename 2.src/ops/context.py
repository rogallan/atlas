"""Asynchronous context management for Correlation ID and Session ID (S19)."""

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

# Global context variables for distributed tracing across async calls
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="undefined")
session_id_ctx: ContextVar[str] = ContextVar("session_id", default="undefined")


def get_correlation_id() -> str:
    """Retrieve the current correlation ID, or 'undefined' if not set."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set the correlation ID in the current async context, generating one if absent."""
    cid = correlation_id.strip() if correlation_id and correlation_id.strip() else str(uuid.uuid4())
    correlation_id_ctx.set(cid)
    return cid


def get_session_id() -> str:
    """Retrieve the current session ID, or 'undefined' if not set."""
    return session_id_ctx.get()


def set_session_id(session_id: str | None = None) -> str:
    """Set the session ID in the current async context, defaulting if absent."""
    sid = session_id.strip() if session_id and session_id.strip() else "anonymous"
    session_id_ctx.set(sid)
    return sid


@contextmanager
def correlation_context(
    correlation_id: str | None = None,
    session_id: str | None = None,
) -> Generator[tuple[str, str], None, None]:
    """Context manager setting correlation and session IDs with automated reset."""
    cid = correlation_id.strip() if correlation_id and correlation_id.strip() else str(uuid.uuid4())
    sid = session_id.strip() if session_id and session_id.strip() else "anonymous"

    token_cid = correlation_id_ctx.set(cid)
    token_sid = session_id_ctx.set(sid)
    try:
        yield cid, sid
    finally:
        correlation_id_ctx.reset(token_cid)
        session_id_ctx.reset(token_sid)
