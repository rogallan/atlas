"""Loan modalities catalog and business parameter constraints (S09)."""

from mcp.loan.models import InvalidLoanParameterError, LoanModality, ModalityInfo

MODALITIES_CATALOG: dict[LoanModality, ModalityInfo] = {
    LoanModality.PERSONAL_CREDIT: ModalityInfo(
        modality=LoanModality.PERSONAL_CREDIT,
        display_name="Crédito Pessoal (CDC)",
        min_amount=500.0,
        max_amount=50000.0,
        min_term_months=6,
        max_term_months=48,
        monthly_interest_rate=0.0219,
        annual_interest_rate=0.2970,
        max_debt_income_ratio=0.30,
        description="Crédito pessoal direto ao consumidor com parcelas fixas pré-fixadas.",
    ),
    LoanModality.PAYROLL_LOAN: ModalityInfo(
        modality=LoanModality.PAYROLL_LOAN,
        display_name="Empréstimo Consignado",
        min_amount=1000.0,
        max_amount=120000.0,
        min_term_months=12,
        max_term_months=84,
        monthly_interest_rate=0.0145,
        annual_interest_rate=0.1887,
        max_debt_income_ratio=0.35,
        description=(
            "Crédito com desconto automático em folha de pagamento e margem legal de até 35%."
        ),
    ),
    LoanModality.WORKING_CAPITAL: ModalityInfo(
        modality=LoanModality.WORKING_CAPITAL,
        display_name="Capital de Giro PJ",
        min_amount=5000.0,
        max_amount=250000.0,
        min_term_months=12,
        max_term_months=60,
        monthly_interest_rate=0.0185,
        annual_interest_rate=0.2460,
        max_debt_income_ratio=0.40,
        description=(
            "Financiamento para reforço de caixa e capital de giro de pessoas jurídicas e MEI."
        ),
    ),
}


def get_all_modalities() -> list[ModalityInfo]:
    """Return list of all registered credit modalities."""
    return list(MODALITIES_CATALOG.values())


def get_modality_info(modality: LoanModality) -> ModalityInfo:
    """Retrieve configuration info for a specific loan modality."""
    if modality not in MODALITIES_CATALOG:
        raise InvalidLoanParameterError(f"Modalidade desconhecida: '{modality}'")
    return MODALITIES_CATALOG[modality]


def validate_loan_request(
    modality: LoanModality,
    amount: float,
    term_months: int,
) -> ModalityInfo:
    """Validate requested amount and term against modality boundaries.

    Raises:
        InvalidLoanParameterError: If amount or term violate modality constraints.
    """
    info = get_modality_info(modality)

    if amount < info.min_amount:
        raise InvalidLoanParameterError(
            f"Valor R$ {amount:,.2f} abaixo do mínimo permitido para {info.display_name} "
            f"(Mínimo: R$ {info.min_amount:,.2f})."
        )
    if amount > info.max_amount:
        raise InvalidLoanParameterError(
            f"Valor R$ {amount:,.2f} acima do teto máximo permitido para {info.display_name} "
            f"(Máximo: R$ {info.max_amount:,.2f})."
        )

    if term_months < info.min_term_months:
        raise InvalidLoanParameterError(
            f"Prazo de {term_months} meses abaixo do mínimo permitido para {info.display_name} "
            f"(Mínimo: {info.min_term_months} meses)."
        )
    if term_months > info.max_term_months:
        raise InvalidLoanParameterError(
            f"Prazo de {term_months} meses acima do teto permitido para {info.display_name} "
            f"(Máximo: {info.max_term_months} meses)."
        )

    return info
