"""Concrete Ollama provider implementation with retry and structured output (S04)."""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from providers.base import (
    LLMProvider,
    LLMProviderError,
    LLMTimeoutError,
    StructuredOutputError,
)
from providers.config import OllamaSettings

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    """Concrete adapter for local Ollama instances."""

    def __init__(
        self,
        settings: OllamaSettings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or OllamaSettings()
        self._client = client

    def _resolve_url(self, endpoint: str) -> str:
        """Resolve full URL combining configured host with endpoint."""
        return f"{self.settings.host.rstrip('/')}/{endpoint.lstrip('/')}"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(
            base_url=self.settings.host,
            timeout=httpx.Timeout(self.settings.timeout_seconds),
        )

    async def _post_with_retry(self, endpoint: str, payload: dict[str, Any]) -> httpx.Response:
        """Execute HTTP POST with exponential backoff on transient network/timeout errors."""
        client = await self._get_client()
        should_close = self._client is None
        url = endpoint if str(client.base_url) else self._resolve_url(endpoint)

        retries = self.settings.max_retries
        last_error: Exception | None = None

        try:
            for attempt in range(retries + 1):
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    return response
                except httpx.TimeoutException as exc:
                    last_error = exc
                    if attempt == retries:
                        raise LLMTimeoutError(
                            f"Ollama request timed out after {self.settings.timeout_seconds}s "
                            f"(attempt {attempt + 1}/{retries + 1})",
                            details={"endpoint": endpoint, "model": self.settings.model},
                        ) from exc
                except (httpx.NetworkError, httpx.HTTPStatusError) as exc:
                    last_error = exc
                    if attempt == retries:
                        raise LLMProviderError(
                            f"Ollama communication failed: {exc}",
                            details={"endpoint": endpoint, "model": self.settings.model},
                        ) from exc

                await asyncio.sleep(0.05 * (2**attempt))

            raise LLMProviderError("Exhausted retries without response", details=str(last_error))
        finally:
            if should_close:
                await client.aclose()

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate a complete text response via Ollama's /api/generate endpoint."""
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        if kwargs:
            payload["options"] = kwargs

        response = await self._post_with_retry("/api/generate", payload)
        data = response.json()
        return str(data.get("response", ""))

    async def stream_generate(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens as NDJSON lines from Ollama."""
        client = await self._get_client()
        should_close = self._client is None
        url = "/api/generate" if str(client.base_url) else self._resolve_url("/api/generate")

        payload: dict[str, Any] = {
            "model": self.settings.model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system
        if kwargs:
            payload["options"] = kwargs

        try:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            yield str(chunk.get("response", ""))
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("Streaming request to Ollama timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Streaming error from Ollama: {exc}") from exc
        finally:
            if should_close:
                await client.aclose()

    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Generate a structured response adhering strictly to a Pydantic schema.

        Includes a corrective retry attempt if the model outputs malformed JSON.
        """
        json_schema = schema.model_json_schema()
        schema_instruction = (
            f"\nYou must respond ONLY with a valid JSON object matching this schema:\n"
            f"{json.dumps(json_schema, indent=2)}\nDo not include commentary or markdown fences."
        )

        full_prompt = f"{prompt}\n{schema_instruction}"
        full_system = f"{system or ''}\nOutput strictly valid JSON."

        # Attempt 1: Standard generation with format=json
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "prompt": full_prompt,
            "system": full_system,
            "format": "json",
            "stream": False,
        }
        if kwargs:
            payload["options"] = kwargs

        response = await self._post_with_retry("/api/generate", payload)
        raw_text = response.json().get("response", "")

        try:
            return schema.model_validate_json(raw_text)
        except (ValidationError, ValueError) as err:
            # Attempt 2: Corrective prompt
            corrective_prompt = (
                f"Your previous output failed schema validation.\n"
                f"Previous output:\n{raw_text}\n\n"
                f"Validation error:\n{err}\n\n"
                f"Please fix the JSON and return only valid JSON matching:\n"
                f"{json.dumps(json_schema, indent=2)}"
            )
            retry_payload = {
                "model": self.settings.model,
                "prompt": corrective_prompt,
                "system": full_system,
                "format": "json",
                "stream": False,
            }
            retry_response = await self._post_with_retry("/api/generate", retry_payload)
            retry_text = retry_response.json().get("response", "")

            try:
                return schema.model_validate_json(retry_text)
            except (ValidationError, ValueError) as second_err:
                raise StructuredOutputError(
                    f"Model failed to generate structured output for {schema.__name__}: "
                    f"{second_err}",
                    details={"raw_text": retry_text, "schema": json_schema},
                ) from second_err
