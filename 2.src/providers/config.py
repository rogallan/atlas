"""Configuration settings for LLM providers (S04)."""

import os
import urllib.parse

from pydantic import BaseModel, Field, field_validator


def _normalize_ollama_host(raw_host: str) -> str:
    host = raw_host.strip()
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    parsed = urllib.parse.urlparse(host)
    hostname = parsed.hostname or "127.0.0.1"
    if hostname == "0.0.0.0":
        hostname = "127.0.0.1"
    port = (
        f":{parsed.port}"
        if parsed.port
        else (":11434" if parsed.port is None and not (parsed.scheme == "http" and ":80" in raw_host or parsed.scheme == "https" and ":443" in raw_host) else "")
    )
    return f"{parsed.scheme}://{hostname}{port}"


class OllamaSettings(BaseModel):
    """Ollama local provider settings."""

    host: str = Field(
        default_factory=lambda: _normalize_ollama_host(
            os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ),
        validate_default=True,
        description="Base URL for the local Ollama instance",
    )
    model: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2:latest"),
        description="Default model name to run",
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30.0")),
        ge=1.0,
        description="Per-request HTTP timeout in seconds",
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("OLLAMA_MAX_RETRIES", "3")),
        ge=0,
        description="Maximum retry attempts on network or timeout failure",
    )

    @field_validator("host", mode="before")
    @classmethod
    def validate_host(cls, v: str) -> str:
        return _normalize_ollama_host(v)
