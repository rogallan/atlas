"""Typed MCP tool handlers for loan simulation and eligibility estimation (S09)."""

import logging
from decimal import Decimal

from mcp.customer.models import CustomerNotFoundError
from mcp.customer.repository import CustomerRepository
from mcp.loan.calculator import (
    calculate_annual_cet,
    calculate_iof,
    calculate_pmt,
    generate_amortization_schedule,
)
from mcp.loan.catalog import get_all_modalities, get_modality_info, validate_loan_request
from mcp.loan.models import (
    DEFAULT_LOAN_DISCLAIMER,
    LoanModality,
    LoanSimulationResult,
    ModalityInfo,
    PreConditionsCheckResult,
)

logger = logging.getLogger(__name__)


class LoanTools:
    """Core financial logic providing loan simulation and eligibility tools."""

    def __init__(self, customer_repository: CustomerRepository | None = None) -> None:
        """Initialize LoanTools.

        Args:
            customer_repository: Optional CustomerRepository to verify customer income.
        """
        self.customer_repo = customer_repository or CustomerRepository()

    def get_loan_modalities(self) -> list[ModalityInfo]:
        """Return all registered credit modalities with current interest rates and limits."""
        return get_all_modalities()

    def simulate_loan(
        self,
        customer_id: str | None = None,
        amount: float = 10000.0,
        term_months: int = 24,
        modality: LoanModality = LoanModality.PERSONAL_CREDIT,
    ) -> LoanSimulationResult:
        """Simulate a loan scenario with exact Price table amortization, IOF, and CET.

        Args:
            customer_id: Optional synthetic customer ID to evaluate debt-to-income margin.
            amount: Requested principal amount in BRL.
            term_months: Financing duration in months.
            modality: Selected credit modality.

        Returns:
            LoanSimulationResult with complete breakdown and disclaimer.
        """
        # 1. Validate parameters against modality constraints
        modality_info = validate_loan_request(modality, amount, term_months)

        # 2. Financial calculation in high precision Decimal
        dec_principal = Decimal(str(amount))
        dec_rate = Decimal(str(modality_info.monthly_interest_rate))

        # IOF tax is financed on top of principal in Brazilian personal credit
        dec_iof = calculate_iof(dec_principal, term_months)
        dec_financed = dec_principal + dec_iof

        # Monthly installment (Price formula)
        dec_pmt = calculate_pmt(dec_financed, dec_rate, term_months)

        # Total payable and total interest
        dec_total_payable = dec_pmt * Decimal(term_months)
        dec_total_interest = dec_total_payable - dec_financed

        # CET annualized (IRR over net principal received)
        dec_cet = calculate_annual_cet(dec_principal, dec_pmt, term_months, dec_rate)

        # 3. Full amortization schedule & compact summary
        full_schedule = generate_amortization_schedule(
            financed_amount=dec_financed,
            monthly_rate=dec_rate,
            pmt=dec_pmt,
            n=term_months,
        )
        # Summary: first 3 installments + last installment if n > 3
        summary_schedule = full_schedule[:3] + (
            [full_schedule[-1]] if len(full_schedule) > 3 else []
        )

        # 4. Check synthetic customer income if customer_id provided
        customer_income: float | None = None
        debt_income_ratio: float | None = None
        is_within_margin = True

        if customer_id:
            customer = self.customer_repo.get_customer(customer_id)
            if customer:
                customer_income = float(customer.income_monthly)
                if customer_income > 0:
                    debt_income_ratio = round(float(dec_pmt) / customer_income, 4)
                    is_within_margin = debt_income_ratio <= modality_info.max_debt_income_ratio
            else:
                logger.warning(
                    "Customer ID %s provided for loan simulation not found.", customer_id
                )

        return LoanSimulationResult(
            customer_id=customer_id,
            modality=modality,
            modality_display_name=modality_info.display_name,
            requested_amount=float(dec_principal),
            term_months=term_months,
            monthly_installment=float(dec_pmt),
            total_interest=float(dec_total_interest),
            total_amount_payable=float(dec_total_payable),
            monthly_interest_rate=modality_info.monthly_interest_rate,
            annual_interest_rate=modality_info.annual_interest_rate,
            annual_cet=float(dec_cet),
            estimated_iof=float(dec_iof),
            customer_monthly_income=customer_income,
            debt_to_income_ratio=debt_income_ratio,
            is_within_margin=is_within_margin,
            margin_limit_ratio=modality_info.max_debt_income_ratio,
            disclaimer=DEFAULT_LOAN_DISCLAIMER,
            schedule_summary=summary_schedule,
        )

    def check_loan_pre_conditions(
        self,
        customer_id: str,
        monthly_installment: float,
        modality: LoanModality = LoanModality.PERSONAL_CREDIT,
    ) -> PreConditionsCheckResult:
        """Evaluate synthetic debt-to-income margin eligibility for a proposed installment.

        Args:
            customer_id: Synthetic customer ID.
            monthly_installment: Proposed monthly payment in BRL.
            modality: Target credit modality.

        Returns:
            PreConditionsCheckResult with diagnostic assessment.

        Raises:
            CustomerNotFoundError: If customer does not exist in synthetic database.
        """
        customer = self.customer_repo.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        modality_info = get_modality_info(modality)
        income = float(customer.income_monthly)

        ratio = 1.0 if income <= 0 else round(monthly_installment / income, 4)

        is_eligible = ratio <= modality_info.max_debt_income_ratio
        ratio_pct = ratio * 100
        limit_pct = modality_info.max_debt_income_ratio * 100

        if is_eligible:
            msg = (
                f"Parcela de R$ {monthly_installment:,.2f} compromete {ratio_pct:.1f}% "
                f"da renda mensal (R$ {income:,.2f}), dentro do limite regulatório "
                f"de {limit_pct:.0f}% para {modality_info.display_name}."
            )
        else:
            msg = (
                f"Parcela de R$ {monthly_installment:,.2f} compromete {ratio_pct:.1f}% "
                f"da renda mensal (R$ {income:,.2f}), excedendo o limite máximo "
                f"de {limit_pct:.0f}% para {modality_info.display_name}."
            )

        return PreConditionsCheckResult(
            customer_id=customer_id,
            modality=modality,
            customer_monthly_income=income,
            monthly_installment=monthly_installment,
            debt_to_income_ratio=ratio,
            margin_limit_ratio=modality_info.max_debt_income_ratio,
            is_eligible=is_eligible,
            message=msg,
        )
