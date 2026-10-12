"""Input security guardrail for direct prompt injection and jailbreak defense (S18)."""

import re
from typing import Any

from security.models import SecurityCheckResult, SecurityThreatLevel, ThreatCategory

# Standard security refusal message returned to clients
SECURITY_REFUSAL_MESSAGE = (
    "Sua solicitação não pôde ser processada devido às políticas de segurança e "
    "governança do ATLAS Banking Copilot. Por favor, reformule sua consulta com "
    "foco nos produtos ou normativos bancários."
)

# High-confidence jailbreak and instruction override patterns
INJECTION_PATTERNS: list[tuple[re.Pattern[str], ThreatCategory, str]] = [
    # 1. Direct instruction overrides
    (
        re.compile(
            r"\b(ignore|esque(ç|c)a|desconsidere|ignore\s+todas?|disregard)\s+"
            r"(all|todas?\s+as?)?\s*(previous|prior|anteriores|instruções|instructions|regras|rules)\b",
            re.IGNORECASE,
        ),
        ThreatCategory.DIRECT_INJECTION,
        "Tentativa explícita de sobreposição de instruções de sistema (override).",
    ),
    # 2. Persona hijacking / DAN / Unconstrained roleplay
    (
        re.compile(
            r"\b(you\s+are\s+now|agora\s+você\s+(é|seja)|act\s+as|aja\s+como|roleplay\s+as|finja\s+ser)\s+"
            r"(an?|um|o(\s+modo)?\s+)?\s*(DAN|developer\s+mode|unconstrained|unfiltered|jailbreak|sem\s+regras|hacker|"
            r"evil\s+bot|sem\s+filtros|root|superuser|administrator)\b",
            re.IGNORECASE,
        ),
        ThreatCategory.DIRECT_INJECTION,
        "Tentativa de alteração forçada de persona para modo descontrolado (jailbreak).",
    ),
    # 3. Delimiter and system tag forgery
    (
        re.compile(
            r"(</?regulatory_context.*?>|</?context.*?>|\[SYSTEM\]|\[ASSISTANT\]|###\s*System:|"
            r"###\s*Instruction:|<system>|<!--\s*system\s*-->)",
            re.IGNORECASE,
        ),
        ThreatCategory.DELIMITER_TAMPERING,
        "Tentativa de forjamento ou fechamento forçado de delimitadores de contexto.",
    ),
    # 4. System prompt extraction commands
    (
        re.compile(
            r"\b(repeat|reveal|print|exiba|mostre|repita|qual\s+(é|são))\s+"
            r"(your|suas?|o(\s+seu)?|seu)?\s*(system\s+prompt|initial\s+instructions|instruções\s+iniciais|"
            r"system\s+instructions|instruções\s+(de|do)\s+sistema|prompt\s+original)\b",
            re.IGNORECASE,
        ),
        ThreatCategory.SYSTEM_PROMPT_LEAK,
        "Tentativa direta de extração do prompt de sistema.",
    ),
    # 5. Base64 / Command line execution injection
    (
        re.compile(
            r"\b(base64\s+-d|echo\s+[A-Za-z0-9+/=]{20,}|\bimport\s+os\b|os\.system\b|subprocess\.run\b|"
            r"rm\s+-rf|DROP\s+TABLE|TRUNCATE\s+TABLE)\b",
            re.IGNORECASE,
        ),
        ThreatCategory.DIRECT_INJECTION,
        "Injeção de comandos de sistema ou código arbitrário.",
    ),
    # 6. Safety policy bypass declarations
    (
        re.compile(
            r"\b(bypass\s+(safety|security|policy|restrictions)|ignorar\s+politica\s+de\s+segurança|"
            r"disable\s+safety\s+filters?|desativar\s+filtros?\s+de\s+segurança)\b",
            re.IGNORECASE,
        ),
        ThreatCategory.DIRECT_INJECTION,
        "Comando para desativação explícita de filtros de proteção.",
    ),
]

# Legitimate banking security concepts that should NOT be blocked (False Positive Whitelist)
LEGITIMATE_SECURITY_INQUIRIES: list[re.Pattern[str]] = [
    re.compile(
        r"\b(golpe\s+do\s+boleto|fraude\s+banc[aá]ria|tentativa\s+de\s+golpe|como\s+funciona\s+(o\s+golpe|a\s+fraude)|"
        r"engenharia\s+social|prevenção\s+a\s+fraudes?|segurança\s+da\s+informa[çc][aã]o|orientar\s+cliente\s+v[ií]tima)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(resolu[çc][aã]o\s+(cmn\s+)?4\.?893|pol[ií]tica\s+de\s+seguran[çc]a\s+cibern[eé]tica\s+do\s+bacen)\b",
        re.IGNORECASE,
    ),
]


class InputGuardrail:
    """Evaluates incoming user messages before LLM processing."""

    def __init__(self) -> None:
        self.refusal_message = SECURITY_REFUSAL_MESSAGE

    def is_legitimate_banking_topic(self, text: str) -> bool:
        """Check if query is asking about banking fraud/security rather than injecting code."""
        text_clean = text.strip().lower()

        # If it explicitly includes override directives, it's NEVER purely legitimate
        if re.search(
            r"\b(ignore|esqueça|desconsidere)\b.*\b(instruções|instructions|regras)\b", text_clean
        ):
            return False

        return any(pattern.search(text_clean) for pattern in LEGITIMATE_SECURITY_INQUIRIES)

    def inspect(self, user_text: str) -> SecurityCheckResult:
        """Inspect input text against known injection patterns and heuristics."""
        if not user_text or not user_text.strip():
            return SecurityCheckResult(
                is_safe=True,
                threat_level=SecurityThreatLevel.NONE,
                detected_threats=[],
                sanitized_text="",
            )

        # 1. Check for legitimate banking questions on fraud prevention
        if self.is_legitimate_banking_topic(user_text):
            return SecurityCheckResult(
                is_safe=True,
                threat_level=SecurityThreatLevel.NONE,
                detected_threats=[],
                sanitized_text=user_text.strip(),
            )

        detected_threats: list[ThreatCategory] = []
        reasons: list[str] = []
        details: dict[str, Any] = {}

        # 2. Pattern and heuristic scan
        for pattern, threat_type, reason_desc in INJECTION_PATTERNS:
            match = pattern.search(user_text)
            if match:
                if threat_type not in detected_threats:
                    detected_threats.append(threat_type)
                reasons.append(reason_desc)
                details[f"match_{len(reasons)}"] = match.group(0)

        # 3. Hidden unicode / invisible zero-width obfuscation check
        zero_width_chars = [c for c in user_text if c in ("\u200b", "\u200c", "\u200d", "\ufeff")]
        if len(zero_width_chars) > 2:
            detected_threats.append(ThreatCategory.DIRECT_INJECTION)
            reasons.append("Detecção de caracteres invisíveis (zero-width) para ofuscação.")
            details["zero_width_count"] = len(zero_width_chars)

        if detected_threats:
            # Threat identified: determine severity
            threat_level = (
                SecurityThreatLevel.CRITICAL
                if ThreatCategory.DIRECT_INJECTION in detected_threats
                else SecurityThreatLevel.HIGH
            )
            return SecurityCheckResult(
                is_safe=False,
                threat_level=threat_level,
                detected_threats=detected_threats,
                sanitized_text=self.refusal_message,
                refusal_reason="; ".join(reasons),
                details=details,
            )

        # 4. Safe input
        return SecurityCheckResult(
            is_safe=True,
            threat_level=SecurityThreatLevel.NONE,
            detected_threats=[],
            sanitized_text=user_text.strip(),
        )
