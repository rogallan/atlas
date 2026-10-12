"""Unit tests for least privilege tool boundaries and authorization enforcement (S18)."""

from security.middleware import SecurityService


def test_read_only_tools_authorized_without_token() -> None:
    """Ensure read-only query and calculator tools execute without requiring confirmation tokens."""
    service = SecurityService()

    allowed, reason = service.verify_tool_authorization(
        "get_customer_profile", has_confirmation_token=False
    )
    assert allowed is True
    assert reason is None

    allowed, reason = service.verify_tool_authorization(
        "calculate_loan_installments", has_confirmation_token=False
    )
    assert allowed is True
    assert reason is None

    allowed, reason = service.verify_tool_authorization(
        "list_tariffs", has_confirmation_token=False
    )
    assert allowed is True
    assert reason is None


def test_mutating_tools_blocked_without_token() -> None:
    """Ensure mutating actions are blocked if no valid HITL confirmation token is supplied."""
    service = SecurityService()

    allowed, reason = service.verify_tool_authorization(
        "create_ticket", has_confirmation_token=False
    )
    assert allowed is False
    assert "token de confirmação assinado por um gerente humano" in (reason or "")

    allowed, reason = service.verify_tool_authorization(
        "dispatch_action", has_confirmation_token=False
    )
    assert allowed is False
    assert "alteração de estado" in (reason or "")


def test_mutating_tools_permitted_with_valid_token() -> None:
    """Ensure mutating actions proceed once verified with valid signed confirmation token."""
    service = SecurityService()

    allowed, reason = service.verify_tool_authorization(
        "create_ticket", has_confirmation_token=True
    )
    assert allowed is True
    assert reason is None

    allowed, reason = service.verify_tool_authorization(
        "dispatch_action", has_confirmation_token=True
    )
    assert allowed is True
    assert reason is None
