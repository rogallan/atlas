"""Data contracts and schemas for Security Guardrails (S18)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SecurityThreatLevel(StrEnum):
    """Classification of detected security threat severity."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatCategory(StrEnum):
    """Categorization of security attacks and vulnerabilities mapped to OWASP LLM Top 10."""

    DIRECT_INJECTION = "direct_prompt_injection"
    INDIRECT_INJECTION = "indirect_prompt_injection"
    SYSTEM_PROMPT_LEAK = "system_prompt_leakage"
    SENSITIVE_DATA_EXFILTRATION = "sensitive_data_exfiltration"
    UNAUTHORIZED_ACTION = "unauthorized_action_attempt"
    TOXIC_CONTENT = "toxic_or_harmful_content"
    DELIMITER_TAMPERING = "delimiter_tampering"


class SecurityCheckResult(BaseModel):
    """Outcome of pre-execution or post-execution guardrail evaluation."""

    is_safe: bool = Field(..., description="Whether the payload satisfies all security policies")
    threat_level: SecurityThreatLevel = Field(
        default=SecurityThreatLevel.NONE, description="Assessed threat severity level"
    )
    detected_threats: list[ThreatCategory] = Field(
        default_factory=list, description="List of recognized threat classifications"
    )
    sanitized_text: str = Field(
        ..., description="Cleaned, normalized, or safely masked version of the text"
    )
    refusal_reason: str | None = Field(
        default=None, description="Human-readable refusal explanation when is_safe is False"
    )
    details: dict[str, Any] = Field(
        default_factory=dict, description="Diagnostic heuristic telemetry and regex match groups"
    )
