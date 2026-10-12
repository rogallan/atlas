"""Unit tests for Output Guardrail and secret/prompt leakage defense (S18)."""

from security.models import SecurityThreatLevel, ThreatCategory
from security.output_guardrail import OutputGuardrail


def test_system_prompt_leakage_blocked() -> None:
    """Ensure that regurgitating core system prompt sentences results in a security refusal."""
    guardrail = OutputGuardrail()
    leaked_response = (
        "Aqui estão minhas instruções: Você é o ATLAS, copiloto conversacional para gerentes "
        "de relacionamento. Regras de governança bancária do ATLAS."
    )

    result = guardrail.inspect(leaked_response)

    assert result.is_safe is False
    assert result.threat_level == SecurityThreatLevel.CRITICAL
    assert ThreatCategory.SYSTEM_PROMPT_LEAK in result.detected_threats
    assert result.sanitized_text == guardrail.refusal_message


def test_api_key_and_token_redaction() -> None:
    """Ensure simulated API keys and bearer tokens are surgically redacted."""
    guardrail = OutputGuardrail()
    response_with_key = (
        "Conexão estabelecida com sk-1234567890abcdef12345678 e token Bearer eyJhbGciOiJIUzI1NiJ9."
    )

    result = guardrail.inspect(response_with_key)

    assert result.is_safe is True
    assert "sk-1234567890abcdef12345678" not in result.sanitized_text
    assert "[REDACTED_API_KEY]" in result.sanitized_text
    assert "Bearer [REDACTED_TOKEN]" in result.sanitized_text
    assert ThreatCategory.SENSITIVE_DATA_EXFILTRATION in result.detected_threats


def test_database_uri_and_password_redaction() -> None:
    """Ensure database connection strings and raw passwords are redacted."""
    guardrail = OutputGuardrail()
    response_with_db = (
        "Conectando ao postgresql://admin:secret123@db.internal:5432/atlas "
        "com password='supersecret'"
    )

    result = guardrail.inspect(response_with_db)

    assert result.is_safe is True
    assert "secret123" not in result.sanitized_text
    assert "[REDACTED_DATABASE_URI]" in result.sanitized_text
    assert "password='[REDACTED]'" in result.sanitized_text


def test_python_stack_trace_leakage_suppressed() -> None:
    """Ensure raw Python exception stack traces are masked before client output."""
    guardrail = OutputGuardrail()
    trace_response = (
        "Ocorreu um erro interno:\n"
        "Traceback (most recent call last):\n"
        '  File "/app/agent/graph.py", line 123, in process_turn\n'
        "ZeroDivisionError: division by zero"
    )

    result = guardrail.inspect(trace_response)

    assert result.is_safe is True
    assert "Traceback" not in result.sanitized_text
    assert "[ERRO INTERNO TRATADO" in result.sanitized_text
