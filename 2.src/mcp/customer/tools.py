"""Typed MCP tool handlers for synthetic customer queries (S08)."""

import logging
from datetime import UTC, datetime

from mcp.customer.auth import AuthContext, SecurityManager
from mcp.customer.models import (
    AccountSummary,
    CustomerNotFoundError,
    CustomerProfileResponse,
    CustomerSegment,
    CustomerSummaryResponse,
    FinancialEventItem,
)
from mcp.customer.repository import CustomerRepository

logger = logging.getLogger(__name__)


def _compute_score_range(score: int) -> str:
    """Format credit score into standardized range bracket."""
    if score < 500:
        return "0-499 (Baixo)"
    if score < 700:
        return "500-699 (Médio)"
    if score < 850:
        return "700-849 (Bom)"
    return "850-1000 (Excelente)"


class CustomerTools:
    """Business tool operations querying synthetic customer database with authorization."""

    def __init__(
        self,
        repository: CustomerRepository | None = None,
        security_manager: SecurityManager | None = None,
    ) -> None:
        """Initialize CustomerTools.

        Args:
            repository: Customer data repository adapter.
            security_manager: Simulated authorization & audit manager.
        """
        self.repository = repository or CustomerRepository()
        self.security = security_manager or SecurityManager()

    def get_customer_profile(
        self,
        customer_id: str,
        auth_context: AuthContext | None = None,
    ) -> CustomerProfileResponse:
        """Retrieve synthetic customer profile, segment, and credit indicators.

        Args:
            customer_id: Synthetic customer ID (e.g. CUST-0001).
            auth_context: Operator authorization context.

        Returns:
            CustomerProfileResponse with personal, segment, and score data.

        Raises:
            CustomerNotFoundError: If customer does not exist.
            UnauthorizedError: If operator is unauthorized.
        """
        ctx = self.security.verify_authorization(auth_context, "get_customer_profile", customer_id)

        customer = self.repository.get_customer(customer_id)
        if not customer:
            self.security.record_audit(
                operator_id=ctx.operator_id,
                role=ctx.role,
                customer_id=customer_id,
                tool="get_customer_profile",
                status="not_found",
            )
            raise CustomerNotFoundError(customer_id)

        history = self.repository.get_history(customer_id)
        current_year = datetime.now(UTC).year
        relationship_years = max(1, current_year - customer.created_at.year)

        risk_tier = (
            history.credit_risk_tier
            if history
            else (
                "HIGH"
                if customer.credit_score < 400
                else "MEDIUM"
                if customer.credit_score < 700
                else "LOW"
            )
        )

        response = CustomerProfileResponse(
            customer_id=customer.id,
            full_name=customer.name,
            email=customer.email,
            document_hash=customer.document_hash,
            segment=CustomerSegment(customer.segment.value),
            monthly_income=float(customer.income_monthly),
            relationship_years=relationship_years,
            credit_score=customer.credit_score,
            credit_score_range=_compute_score_range(customer.credit_score),
            risk_rating=risk_tier,
        )

        self.security.record_audit(
            operator_id=ctx.operator_id,
            role=ctx.role,
            customer_id=customer_id,
            tool="get_customer_profile",
            status="success",
        )
        return response

    def get_customer_accounts(
        self,
        customer_id: str,
        auth_context: AuthContext | None = None,
    ) -> list[AccountSummary]:
        """Retrieve all synthetic bank accounts for a customer.

        Args:
            customer_id: Synthetic customer ID.
            auth_context: Operator authorization context.

        Returns:
            List of AccountSummary models.
        """
        ctx = self.security.verify_authorization(auth_context, "get_customer_accounts", customer_id)

        customer = self.repository.get_customer(customer_id)
        if not customer:
            self.security.record_audit(
                operator_id=ctx.operator_id,
                role=ctx.role,
                customer_id=customer_id,
                tool="get_customer_accounts",
                status="not_found",
            )
            raise CustomerNotFoundError(customer_id)

        accounts = self.repository.get_accounts(customer_id)
        results = [
            AccountSummary(
                account_id=acc.id,
                account_number=f"{acc.id.replace('ACC-', '')}-1",
                branch="0001",
                account_type=acc.type.value,
                balance=float(acc.balance),
                currency=acc.currency,
                status=acc.status.value,
            )
            for acc in accounts
        ]

        self.security.record_audit(
            operator_id=ctx.operator_id,
            role=ctx.role,
            customer_id=customer_id,
            tool="get_customer_accounts",
            status="success",
            details={"accounts_count": len(results)},
        )
        return results

    def get_financial_history(
        self,
        customer_id: str,
        limit: int = 10,
        auth_context: AuthContext | None = None,
    ) -> list[FinancialEventItem]:
        """Retrieve recent chronological transactions and financial ledger events.

        Args:
            customer_id: Synthetic customer ID.
            limit: Maximum events to return (1-50).
            auth_context: Operator authorization context.

        Returns:
            List of FinancialEventItem objects.
        """
        if limit < 1 or limit > 50:
            raise ValueError(f"Parâmetro 'limit' deve estar entre 1 e 50. Recebido: {limit}")

        ctx = self.security.verify_authorization(auth_context, "get_financial_history", customer_id)

        customer = self.repository.get_customer(customer_id)
        if not customer:
            self.security.record_audit(
                operator_id=ctx.operator_id,
                role=ctx.role,
                customer_id=customer_id,
                tool="get_financial_history",
                status="not_found",
            )
            raise CustomerNotFoundError(customer_id)

        events = self.repository.get_events(customer_id, limit=limit)
        results = [
            FinancialEventItem(
                event_id=evt.id,
                account_id=evt.account_id,
                event_date=evt.timestamp.isoformat(),
                description=evt.description,
                amount=float(evt.amount),
                category=evt.type.value,
            )
            for evt in events
        ]

        self.security.record_audit(
            operator_id=ctx.operator_id,
            role=ctx.role,
            customer_id=customer_id,
            tool="get_financial_history",
            status="success",
            details={"events_count": len(results)},
        )
        return results

    def get_customer_summary(
        self,
        customer_id: str,
        auth_context: AuthContext | None = None,
    ) -> CustomerSummaryResponse:
        """Generate an aggregated briefing summary for the relationship manager.

        Args:
            customer_id: Synthetic customer ID.
            auth_context: Operator authorization context.

        Returns:
            CustomerSummaryResponse combining profile, accounts, active contracts, and events.
        """
        ctx = self.security.verify_authorization(auth_context, "get_customer_summary", customer_id)

        # 1. Profile
        profile = self.get_customer_profile(customer_id, auth_context=ctx)

        # 2. Accounts
        accounts = self.get_customer_accounts(customer_id, auth_context=ctx)
        total_balance = sum(a.balance for a in accounts)

        # 3. Active contracts
        contracts = self.repository.get_contracts(customer_id)
        active_contracts = [c for c in contracts if c.status.value == "active"]

        # 4. Recent events
        recent_events = self.get_financial_history(customer_id, limit=5, auth_context=ctx)

        # 5. Briefing note
        notes = (
            f"Cliente {profile.full_name} ({profile.segment.value.upper()}) com saldo total de "
            f"R$ {total_balance:,.2f} e {len(active_contracts)} contrato(s) ativo(s). "
            f"Classificação de risco: {profile.risk_rating}."
        )

        response = CustomerSummaryResponse(
            profile=profile,
            accounts=accounts,
            total_balance=round(total_balance, 2),
            active_contracts_count=len(active_contracts),
            recent_events=recent_events,
            relationship_notes=notes,
        )

        self.security.record_audit(
            operator_id=ctx.operator_id,
            role=ctx.role,
            customer_id=customer_id,
            tool="get_customer_summary",
            status="success",
        )
        return response
