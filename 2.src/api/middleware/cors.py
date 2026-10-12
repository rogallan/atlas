"""Cross-Origin Resource Sharing (CORS) setup for Vercel, ngrok, and local clients (S16)."""

import os
from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import ALLOWED_ORIGINS

DEFAULT_VERCEL_PREVIEW_REGEX = r"https:\/\/.*\.vercel\.app"


def get_configured_origins() -> list[str]:
    """Resolve CORS origins merging defaults with optional environment overrides."""
    env_origins = os.getenv("ATLAS_ALLOWED_ORIGINS")
    if env_origins:
        parsed = [o.strip() for o in env_origins.split(",") if o.strip()]
        if parsed:
            return parsed
    return list(ALLOWED_ORIGINS)


def setup_cors(
    app: FastAPI,
    allowed_origins: Sequence[str] | None = None,
    allow_origin_regex: str | None = None,
) -> None:
    """Attach configured CORSMiddleware with Vercel and ngrok compatibility.

    Args:
        app: Target FastAPI instance.
        allowed_origins: Optional explicit list of origins. If None, uses defaults.
        allow_origin_regex: Optional regex pattern for preview subdomains (e.g. Vercel previews).
    """
    origins = list(allowed_origins) if allowed_origins is not None else get_configured_origins()
    origin_regex = allow_origin_regex or os.getenv(
        "ATLAS_ALLOWED_ORIGIN_REGEX", DEFAULT_VERCEL_PREVIEW_REGEX
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=origin_regex,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Session-ID",
            "ngrok-skip-browser-warning",
            "Accept",
        ],
        expose_headers=["Content-Type", "X-Session-ID"],
    )
