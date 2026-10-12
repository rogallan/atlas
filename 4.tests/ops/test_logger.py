import json

import pytest

from ops.context import correlation_context
from ops.logger import StructuredLogRecord, configure_logging, get_logger


def test_structured_json_log_schema(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that emitted log lines conform strictly to StructuredLogRecord schema."""
    configure_logging(log_level="DEBUG", json_format=True)
    logger = get_logger("test_service")

    with correlation_context(correlation_id="test-cid-101", session_id="test-sid-202"):
        logger.info("Test execution event", action="login", attempt=1)

    captured = capsys.readouterr().out.strip()
    assert captured, "Log stream should not be empty"

    lines = [line for line in captured.split("\n") if line.strip()]
    last_line = lines[-1]
    data = json.loads(last_line)

    # Validate against Pydantic schema
    record = StructuredLogRecord.model_validate(data)
    assert record.level == "INFO"
    assert record.correlation_id == "test-cid-101"
    assert record.session_id == "test-sid-202"
    assert record.component == "test_service"
    assert record.message == "Test execution event"
    assert record.metadata.get("action") == "login"
    assert record.metadata.get("attempt") == 1


def test_structured_log_pii_sanitization(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify that Brazilian synthetic CPFs, account numbers, and tokens are redacted from logs."""
    configure_logging(log_level="INFO", json_format=True)
    logger = get_logger("banking_audit")

    with correlation_context(correlation_id="cid-sec", session_id="sid-sec"):
        logger.info(
            "Processando cliente com CPF 123.456.789-00 e conta 12345-6 "
            "com token Bearer secret_123",
            raw_cpf="12345678900",
            email="cliente@banco.com.br",
        )

    captured = capsys.readouterr().out.strip()
    lines = [line for line in captured.split("\n") if line.strip()]
    data = json.loads(lines[-1])

    message = data.get("message", "")
    # Formatted CPF masked
    assert "123.456.789-00" not in message
    assert "***.***.789-**" in message

    # Account number masked
    assert "12345-6" not in message
    assert "*****-6" in message

    # Bearer token masked
    assert "secret_123" not in message
    assert "Bearer [REDACTED]" in message

    # Metadata fields masked
    metadata = data.get("metadata", {})
    assert "12345678900" not in str(metadata)
    assert metadata.get("email") == "c***@banco.com.br"
