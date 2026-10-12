"""Log sanitizer and PII masking engine for Brazilian banking entities (S18)."""

import logging
import re
from typing import Any

# Formatted CPF: 123.456.789-01 -> ***.***.789-**
REGEX_CPF_FORMATTED = re.compile(r"\b(\d{3})\.(\d{3})\.(\d{3})-(\d{2})\b")

# Plain 11-digit CPF: 12345678901 -> *******8901
REGEX_CPF_PLAIN = re.compile(r"\b(\d{7})(\d{4})\b")

# Bank account number with check digit: 123456-7 or 12345-X -> ****5-7
REGEX_ACCOUNT = re.compile(r"\b\d{4,8}-([0-9Xx])\b")

# PAN / Credit Card number (16 digits with or without spaces/dashes)
REGEX_CARD_PAN = re.compile(r"\b(?:\d{4}[ -]?){3}(\d{4})\b")

# Bearer Token: Bearer <token> -> Bearer [REDACTED]
REGEX_BEARER_TOKEN = re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{8,}\b", re.IGNORECASE)

# Confirmation tokens: CONFIRMAR_TOKEN_<id> or UUID tokens
REGEX_CONFIRMATION_TOKEN = re.compile(
    r"\b(CONFIRMAR_TOKEN_[A-Za-z0-9_-]+|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b",
    re.IGNORECASE,
)

# Email address masking: name@domain -> n***@domain
REGEX_EMAIL = re.compile(r"\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")


def mask_formatted_cpf(match: re.Match[str]) -> str:
    """Mask CPF keeping only middle branch for trace identification: ***.***.789-**."""
    return f"***.***.{match.group(3)}-**"


def mask_card_pan(match: re.Match[str]) -> str:
    """Mask credit card keeping last 4 digits: ****-****-****-1234."""
    return f"****-****-****-{match.group(1)}"


def mask_account(match: re.Match[str]) -> str:
    """Mask account keeping check digit: *****-X."""
    return f"*****-{match.group(1)}"


def mask_plain_cpf(match: re.Match[str]) -> str:
    """Mask 11-digit unformatted CPF keeping only last 4 digits: *******8901."""
    return f"*******{match.group(2)}"


def mask_email(match: re.Match[str]) -> str:
    """Partially mask email address: j***@domain.com."""
    return f"{match.group(1)}***@{match.group(2)}"


def sanitize_text(text: str) -> str:
    """Sanitize Brazilian PII, account numbers, and credentials within a string."""
    if not text:
        return text

    # 1. Bearer and confirmation tokens
    text = REGEX_BEARER_TOKEN.sub("Bearer [REDACTED]", text)
    text = REGEX_CONFIRMATION_TOKEN.sub("[TOKEN_REDACTED]", text)

    # 2. Credit Cards / PAN
    text = REGEX_CARD_PAN.sub(mask_card_pan, text)

    # 3. Formatted and unformatted Brazilian CPFs
    text = REGEX_CPF_FORMATTED.sub(mask_formatted_cpf, text)
    text = REGEX_CPF_PLAIN.sub(mask_plain_cpf, text)

    # 4. Bank account numbers
    text = REGEX_ACCOUNT.sub(mask_account, text)

    # 5. Customer emails
    text = REGEX_EMAIL.sub(mask_email, text)

    return text


def sanitize_data_structure(data: Any) -> Any:
    """Recursively sanitize dictionary or list structures."""
    if isinstance(data, str):
        return sanitize_text(data)
    elif isinstance(data, dict):
        return {k: sanitize_data_structure(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data_structure(item) for item in data]
    return data


class SanitizingLogFilter(logging.Filter):
    """Logging filter that automatically redacts sensitive financial PII from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = sanitize_data_structure(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_text(arg) if isinstance(arg, str) else arg for arg in record.args
                )
        return True
