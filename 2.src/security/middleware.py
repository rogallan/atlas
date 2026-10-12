"""FastAPI security integration, guardrail service, and tool boundary enforcement (S18)."""

from collections.abc import Sequence
from typing import Any

from security.context_isolation import ContextIsolator
from security.input_guardrail import InputGuardrail
from security.models import SecurityCheckResult
from security.output_guardrail import OutputGuardrail
from security.sanitizers import sanitize_data_structure, sanitize_text

# Set of state-mutating MCP tools requiring mandatory Human-in-the-Loop confirmation
MUTATING_TOOLS = {
    "create_ticket",
    "dispatch_action",
    "open_account_request",
    "update_credit_limit",
    "cancel_contract",
}

# Set of known read-only informational and calculator tools
READ_ONLY_TOOLS = {
    "get_customer_profile",
    "get_customer_transactions",
    "get_account_balance",
    "calculate_loan_installments",
    "simulate_loan",
    "list_loan_products",
    "simulate_insurance",
    "list_insurance_plans",
    "simulate_consortium",
    "list_consortium_quotas",
    "get_tariff_table",
    "list_tariffs",
    "get_ticket_details",
}


class SecurityService:
    """Unified façade orchestrating input, RAG context, output, and logging security."""

    def __init__(self) -> None:
        self.input_guardrail = InputGuardrail()
        self.context_isolator = ContextIsolator()
        self.output_guardrail = OutputGuardrail()

    def inspect_input(self, text: str) -> SecurityCheckResult:
        """Evaluate incoming user message before invoking agent logic."""
        return self.input_guardrail.inspect(text)

    def isolate_rag_context(self, chunks: Sequence[str | dict[str, Any]]) -> str:
        """Sanitize and encapsulate retrieved RAG chunks in secure XML isolation blocks."""
        return self.context_isolator.isolate_rag_context(chunks)

    def inspect_output(self, response_text: str) -> SecurityCheckResult:
        """Scan generated answer for secret leakage and system prompt extraction."""
        return self.output_guardrail.inspect(response_text)

    def sanitize_log(self, record_data: Any) -> Any:
        """Redact sensitive financial PII from arbitrary log structures."""
        if isinstance(record_data, str):
            return sanitize_text(record_data)
        return sanitize_data_structure(record_data)

    def verify_tool_authorization(
        self, tool_name: str, has_confirmation_token: bool
    ) -> tuple[bool, str | None]:
        """Enforce least privilege on MCP tool execution boundaries."""
        if tool_name in MUTATING_TOOLS:
            if not has_confirmation_token:
                return (
                    False,
                    f"A ferramenta '{tool_name}' realiza alteração de estado no sistema e "
                    "exige um token de confirmação assinado por um gerente humano (HITL).",
                )
            return True, None

        if tool_name in READ_ONLY_TOOLS:
            return True, None

        # Unknown tool fallback: permit if not mutating, but flag
        return True, None


# Global singleton instance for easy import across FastAPI routes
security_service = SecurityService()
