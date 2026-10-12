"""Unit tests for CORS setup and ngrok integration (S16)."""

import os
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.cors import get_configured_origins, setup_cors


def test_get_configured_origins_defaults() -> None:
    """Ensure default allowed origins are returned when no env var is set."""
    with patch.dict(os.environ, {}, clear=True):
        origins = get_configured_origins()
        assert "http://localhost:3000" in origins
        assert "https://atlas-chat.vercel.app" in origins


def test_get_configured_origins_env_override() -> None:
    """Ensure ATLAS_ALLOWED_ORIGINS environment variable overrides defaults."""
    custom = "https://my-custom-bank.com, https://test.internal"
    with patch.dict(os.environ, {"ATLAS_ALLOWED_ORIGINS": custom}):
        origins = get_configured_origins()
        assert origins == ["https://my-custom-bank.com", "https://test.internal"]


def test_cors_preflight_production_origin() -> None:
    """Ensure preflight OPTIONS request from Vercel production domain is authorized."""
    app = FastAPI()
    setup_cors(app, allowed_origins=["https://atlas-chat.vercel.app"])

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ping": "pong"}

    client = TestClient(app)
    response = client.options(
        "/ping",
        headers={
            "Origin": "https://atlas-chat.vercel.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, ngrok-skip-browser-warning",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://atlas-chat.vercel.app"
    allow_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "ngrok-skip-browser-warning" in allow_headers


def test_cors_vercel_preview_regex() -> None:
    """Ensure dynamic Vercel preview branch domains match regex allowlist."""
    app = FastAPI()
    setup_cors(app, allowed_origins=["http://localhost:3000"])

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ping": "pong"}

    client = TestClient(app)
    preview_origin = "https://atlas-chat-git-preview-branch-team.vercel.app"
    response = client.options(
        "/ping",
        headers={
            "Origin": preview_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == preview_origin
