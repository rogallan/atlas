"""Prompt injection, jailbreak, and adversarial input detector (S14)."""

import re
from typing import ClassVar


class PromptInjectionDetector:
    """Detects prompt injection, system prompt overrides, and jailbreak attempts."""

    # Common injection keywords and phrases (case-insensitive)
    INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions",
        r"desconsidere\s+(?:todas\s+as\s+)?instruç(?:ões|oes)\s+anteriores",
        r"esque(?:ça|ca)\s+(?:todas\s+as\s+)?regras",
        r"you\s+are\s+now\s+(?:in\s+)?(?:dan|developer\s+mode|unrestricted|maintenance)",
        r"você\s+agora\s+é\s+(?:dan|modo\s+desenvolvedor|livre)",
        r"system\s*prompt\s*override",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"<system>",
        r"</system>",
        r"\[SYSTEM\]",
        r"bypass\s+(?:all\s+)?guardrails",
        r"aja\s+como\s+uma\s+ia\s+sem\s+filtros",
        r"reveal\s+(?:your\s+)?system\s+prompt",
        r"revele\s+(?:o\s+)?seu\s+prompt\s+de\s+sistema",
        r"drop\s+database",
        r"rm\s+-rf\s+/",
    ]

    def __init__(self) -> None:
        self._compiled_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.INJECTION_PATTERNS
        ]

    def check_input(self, text: str) -> tuple[bool, str | None]:
        """Check if input text contains suspicious prompt injection patterns.

        Returns:
            (is_suspicious, reason)
        """
        if not text:
            return False, None

        cleaned = text.strip()
        for idx, regex in enumerate(self._compiled_regexes):
            match = regex.search(cleaned)
            if match:
                matched_phrase = match.group(0)
                pattern_desc = self.INJECTION_PATTERNS[idx]
                return (
                    True,
                    (
                        f"Tentativa de injeção de prompt detectada: '{matched_phrase}' "
                        f"(padrão: {pattern_desc})."
                    ),
                )

        return False, None
