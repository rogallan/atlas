"""Unit tests validating ContextVar-based Correlation ID and Session ID propagation (S19)."""

import asyncio

import pytest

from ops.context import (
    correlation_context,
    get_correlation_id,
    get_session_id,
    set_correlation_id,
    set_session_id,
)


@pytest.mark.asyncio
async def test_correlation_id_defaults_and_explicit_setting() -> None:
    """Verify default correlation ID handling and explicit overrides."""
    with correlation_context(correlation_id="explicit-cid-123", session_id="sess-456"):
        assert get_correlation_id() == "explicit-cid-123"
        assert get_session_id() == "sess-456"

        # Dynamically overwrite
        set_correlation_id("new-cid-999")
        assert get_correlation_id() == "new-cid-999"


@pytest.mark.asyncio
async def test_correlation_context_isolation_across_async_tasks() -> None:
    """Verify that concurrent asyncio tasks maintain independent correlation contexts."""

    async def worker(task_id: str) -> tuple[str, str]:
        with correlation_context(correlation_id=f"cid-{task_id}", session_id=f"sess-{task_id}"):
            await asyncio.sleep(0.01)
            return get_correlation_id(), get_session_id()

    results = await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
    )

    assert results[0] == ("cid-A", "sess-A")
    assert results[1] == ("cid-B", "sess-B")
    assert results[2] == ("cid-C", "sess-C")


@pytest.mark.asyncio
async def test_context_manager_cleanup() -> None:
    """Verify that correlation context resets to previous state after exiting context manager."""
    set_correlation_id("outer-cid")
    set_session_id("outer-sess")

    with correlation_context(correlation_id="inner-cid", session_id="inner-sess"):
        assert get_correlation_id() == "inner-cid"
        assert get_session_id() == "inner-sess"

    assert get_correlation_id() == "outer-cid"
    assert get_session_id() == "outer-sess"


def test_auto_uuid_generation_when_blank() -> None:
    """Verify automatic UUID generation when empty or whitespace correlation ID is supplied."""
    with correlation_context(correlation_id="  ", session_id=""):
        cid = get_correlation_id()
        sid = get_session_id()

        assert len(cid) == 36  # Standard UUID format
        assert "-" in cid
        assert sid == "anonymous"
