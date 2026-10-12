"""Output security guardrail for secret, token, and system prompt leakage prevention (S18)."""

import re
from typing import Any

from security.models import SecurityCheckResult, SecurityThreatLevel, ThreatCategory

SAFE_LEAKAGE_REFUSAL = (
    "A resposta gerada foi bloqueada pelas políticas de prevenção contra vazamento de "
    "segredos e informações confidenciais do ATLAS Banking Copilot."
)

# Known core system prompt anchor phrases to prevent full prompt regurgitation
SYSTEM_PROMPT_SIGNATURES = [
    re.compile(
        r"você\s+é\s+o\s+atlas,\s*copiloto\s+conversacional\s+para\s+gerentes", re.IGNORECASE
    ),
    re.compile(r"regras\s+de\s+governança\s+bancária\s+do\s+atlas", re.IGNORECASE),
    re.compile(r"diretrizes\s+de\s+segurança\s+e\s+isolamento\s+de\s+contexto", re.IGNORECASE),
    re.compile(r"nunca\s+revele\s+suas\s+instruções\s+de\s+sistema", re.IGNORECASE),
]

# Sensitive credentials, keys, and internal tracebacks
LEAKAGE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # API keys / Bearer tokens
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{20,})\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9_-]{20,}\b"), "Bearer [REDACTED_TOKEN]"),
    # Connection strings
    (
        re.compile(r"(postgres|postgresql|mysql|mongodb)://[^\s]+:[^\s]+@[^\s]+"),
        "[REDACTED_DATABASE_URI]",
    ),
    # Raw passwords in text
    (re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]+['\"]"), "password='[REDACTED]'"),
    # Python Traceback leaks
    (
        re.compile(
            r"Traceback\s+\(most\s+recent\s+call\s+last\):.*?(File\s+\".*?\",\s+line\s+\d+)",
            re.DOTALL,
        ),
        "[ERRO INTERNO TRATADO - CONSULTE O LOG DO SISTEMA]",
    ),
]


class OutputGuardrail:
    """Inspects generated LLM answers before delivering payloads to the client."""

    def __init__(self, active_system_prompt: str | None = None) -> None:
        self.active_system_prompt = active_system_prompt
        self.refusal_message = SAFE_LEAKAGE_REFUSAL

    def inspect(self, response_text: str) -> SecurityCheckResult:
        """Scan generated output for credentials, system prompt verbatim leaks, and stack traces."""
        if not response_text:
            return SecurityCheckResult(
                is_safe=True,
                threat_level=SecurityThreatLevel.NONE,
                detected_threats=[],
                sanitized_text="",
            )

        detected_threats: list[ThreatCategory] = []
        details: dict[str, Any] = {}
        sanitized = response_text

        # 1. System Prompt Leakage Scan
        for sig in SYSTEM_PROMPT_SIGNATURES:
            if sig.search(response_text):
                detected_threats.append(ThreatCategory.SYSTEM_PROMPT_LEAK)
                details["system_prompt_leak"] = True
                return SecurityCheckResult(
                    is_safe=False,
                    threat_level=SecurityThreatLevel.CRITICAL,
                    detected_threats=detected_threats,
                    sanitized_text=self.refusal_message,
                    refusal_reason=(
                        "Tentativa de extração ou vazamento de prompt de sistema detectada."
                    ),
                    details=details,
                )

        # 2. Secret and Token Scan & Redaction
        has_secret_leak = False
        for pattern, replacement in LEAKAGE_PATTERNS:
            if pattern.search(sanitized):
                has_secret_leak = True
                sanitized = pattern.sub(replacement, sanitized)

        if has_secret_leak:
            detected_threats.append(ThreatCategory.SENSITIVE_DATA_EXFILTRATION)
            details["secrets_redacted"] = True
            return SecurityCheckResult(
                is_safe=True,  # Safe after surgical redaction
                threat_level=SecurityThreatLevel.MEDIUM,
                detected_threats=detected_threats,
                sanitized_text=sanitized,
                refusal_reason=None,
                details=details,
            )

        # 3. Clean and safe response
        return SecurityCheckResult(
            is_safe=True,
            threat_level=SecurityThreatLevel.NONE,
            detected_threats=[],
            sanitized_text=response_text,
            details={},
        )
