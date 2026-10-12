"""Unit tests for PII masking and structured log sanitization (S18)."""

import logging

from security.sanitizers import (
    SanitizingLogFilter,
    sanitize_data_structure,
    sanitize_text,
)


def test_sanitize_formatted_cpf() -> None:
    """Ensure formatted synthetic CPFs are masked preserving middle segment."""
    raw = "Cliente portador do CPF 123.456.789-01 realizou login."
    sanitized = sanitize_text(raw)
    assert "123.456.789-01" not in sanitized
    assert "***.***.789-**" in sanitized


def test_sanitize_plain_cpf() -> None:
    """Ensure unformatted 11-digit synthetic CPFs are masked."""
    raw = "Consulta realizada para o documento 12345678901."
    sanitized = sanitize_text(raw)
    assert "12345678901" not in sanitized


def test_sanitize_bank_account() -> None:
    """Ensure bank account numbers with check digits are masked."""
    raw = "Movimentação registrada na conta 1234567-8 e conta poupança 98765-X."
    sanitized = sanitize_text(raw)
    assert "1234567-8" not in sanitized
    assert "98765-X" not in sanitized
    assert "*****-8" in sanitized
    assert "*****-X" in sanitized


def test_sanitize_credit_card_pan() -> None:
    """Ensure 16-digit credit card PANs are masked preserving last 4 digits."""
    raw = "Pagamento aprovado no cartão 4111 2222 3333 4444."
    sanitized = sanitize_text(raw)
    assert "4111 2222 3333 4444" not in sanitized
    assert "****-****-****-4444" in sanitized


def test_sanitize_tokens_and_emails() -> None:
    """Ensure bearer tokens and customer emails are masked."""
    raw = "Autorizado com Bearer eyJhbGciOiJIUzI1NiJ9 para carlos.silva@simulado.atlas.local."
    sanitized = sanitize_text(raw)
    assert "eyJhbGciOiJIUzI1NiJ9" not in sanitized
    assert "Bearer [REDACTED]" in sanitized
    assert "carlos.silva@" not in sanitized
    assert "c***@simulado.atlas.local" in sanitized


def test_sanitize_nested_data_structure() -> None:
    """Ensure deep dictionaries and arrays are sanitized recursively."""
    payload = {
        "customer": {
            "name": "Maria Silva",
            "cpf": "123.456.789-01",
            "account": "1234567-8",
        },
        "transactions": [
            {"token": "CONFIRMAR_TOKEN_12345", "amount": 1500.0},
        ],
    }

    clean = sanitize_data_structure(payload)

    assert clean["customer"]["cpf"] == "***.***.789-**"
    assert clean["customer"]["account"] == "*****-8"
    assert clean["transactions"][0]["token"] == "[TOKEN_REDACTED]"
    assert clean["transactions"][0]["amount"] == 1500.0


def test_sanitizing_log_filter() -> None:
    """Ensure logging filter modifies record message before emission."""
    log_filter = SanitizingLogFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Auditoria: CPF 123.456.789-01 solicitou extrato.",
        args=(),
        exc_info=None,
    )

    assert log_filter.filter(record) is True
    assert "123.456.789-01" not in record.msg
    assert "***.***.789-**" in record.msg
