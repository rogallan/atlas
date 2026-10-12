"""Integration tests for the FastAPI Gateway (S03)."""

import pytest
from httpx import ASGITransport, AsyncClient

from api.config import SIMULATED_AUTH_TOKEN
from api.main import app

AUTH_HEADER = {"Authorization": f"Bearer {SIMULATED_AUTH_TOKEN}"}


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    """Validate GET /health returns 200 and expected schema."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert data["uptime_seconds"] >= 0.0


@pytest.mark.asyncio
async def test_sessions_endpoint_auth_enforcement() -> None:
    """Validate POST /v1/sessions rejects missing and invalid tokens."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing auth
        res_no_auth = await client.post("/v1/sessions")
        assert res_no_auth.status_code == 401
        err = res_no_auth.json()
        assert err["error"]["code"] == "UNAUTHORIZED"

        # Invalid token
        res_bad_auth = await client.post(
            "/v1/sessions",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert res_bad_auth.status_code == 401
        assert res_bad_auth.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_sessions_endpoint_success() -> None:
    """Validate POST /v1/sessions creates a correlated session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/v1/sessions",
            json={"manager_id": "MGR-007", "branch_id": "BR-99"},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["manager_id"] == "MGR-007"
        assert "created_at" in data


@pytest.mark.asyncio
async def test_chat_endpoint_validation_error() -> None:
    """Validate POST /v1/chat returns standardized 422 for malformed body."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing session_id and message
        response = await client.post(
            "/v1/chat",
            json={},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in body["error"]


@pytest.mark.asyncio
async def test_chat_endpoint_sse_streaming() -> None:
    """Validate POST /v1/chat streams SSE tokens, citations, and completion event."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "session_id": "sess-test-123",
            "message": "Quais são as taxas de juros para crédito pessoal?",
            "customer_id": "CUST-0001",
        }

        async with client.stream(
            "POST",
            "/v1/chat",
            json=payload,
            headers=AUTH_HEADER,
        ) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

            events_received: list[str] = []
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    events_received.append(line.replace("event:", "").strip())

            # Verify chunk sequence
            assert "token" in events_received
            assert "citation" in events_received
            assert "done" in events_received
            assert events_received[-1] == "done"


@pytest.mark.asyncio
async def test_cors_preflight_headers() -> None:
    """Validate CORS preflight OPTIONS returns allowed methods and headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/v1/chat",
            headers={
                "Origin": "https://atlas-chat.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": (
                    "authorization,content-type,ngrok-skip-browser-warning"
                ),
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
