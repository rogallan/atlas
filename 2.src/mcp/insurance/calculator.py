"""Deterministic actuarial calculation engine for synthetic insurance quotes (S10)."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from mcp.insurance.models import CoverageItem, InsuranceProductInfo

ANNUAL_DISCOUNT_FACTOR = Decimal("0.95")  # 5% discount for annual upfront payment


def _round_currency(value: Decimal) -> Decimal:
    """Round a Decimal value to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_customer_risk_factor(
    age: int | None = None,
    segment: str | None = None,
) -> tuple[Decimal, dict[str, Any]]:
    """Determine actuarial risk multiplier and rationale based on synthetic profile.

    Args:
        age: Customer age in years.
        segment: Customer commercial segment (ex: 'PRIVATE', 'PRIME', 'VAREJO').

    Returns:
        Tuple of (risk_multiplier, premises_dict).
    """
    premises: dict[str, Any] = {}

    # 1. Age multiplier
    if age is None:
        age_multiplier = Decimal("1.00")
        premises["age_factor"] = "Padrao (idade nao informada: 1.00x)"
    elif age < 35:
        age_multiplier = Decimal("1.00")
        premises["age_factor"] = f"Faixa Jovem ({age} anos: 1.00x)"
    elif age < 50:
        age_multiplier = Decimal("1.25")
        premises["age_factor"] = f"Faixa Adulta ({age} anos: 1.25x)"
    else:
        age_multiplier = Decimal("1.60")
        premises["age_factor"] = f"Faixa Senior ({age} anos: 1.60x)"

    # 2. Segment multiplier
    norm_segment = (segment or "").upper()
    if "PRIVATE" in norm_segment:
        segment_multiplier = Decimal("0.90")
        premises["segment_factor"] = "Private Banking (-10% desconto de relacionamento)"
    elif "PRIME" in norm_segment:
        segment_multiplier = Decimal("0.95")
        premises["segment_factor"] = "Segmento Prime (-5% desconto de relacionamento)"
    else:
        segment_multiplier = Decimal("1.00")
        premises["segment_factor"] = "Segmento Geral/Varejo (1.00x)"

    combined_factor = age_multiplier * segment_multiplier
    premises["combined_risk_multiplier"] = float(combined_factor)

    return combined_factor, premises


def calculate_insurance_premium(
    insured_capital: float,
    selected_coverages: list[CoverageItem],
    product_info: InsuranceProductInfo,
    customer_age: int | None = None,
    customer_segment: str | None = None,
) -> dict[str, Any]:
    """Compute monthly and annual premiums, IOF taxes, and underwriting premises.

    Args:
        insured_capital: Financed or protected capital in BRL.
        selected_coverages: List of included coverage items.
        product_info: Product catalog information with IOF rate.
        customer_age: Customer age for risk evaluation.
        customer_segment: Customer banking tier.

    Returns:
        Dictionary with monthly_premium, annual_premium, net_monthly_premium,
        estimated_iof, iof_rate, and underwriting_premises.
    """
    dec_capital = Decimal(str(insured_capital))
    dec_iof_rate = Decimal(str(product_info.iof_rate))

    # 1. Base monthly premium from individual coverage rate factors
    total_rate_factor = sum(Decimal(str(cov.rate_factor)) for cov in selected_coverages)
    base_monthly_net = dec_capital * total_rate_factor

    # 2. Risk adjustment
    risk_factor, premises = calculate_customer_risk_factor(
        age=customer_age, segment=customer_segment
    )
    adjusted_monthly_net = base_monthly_net * risk_factor

    # 3. Monthly IOF and gross premium
    monthly_iof = adjusted_monthly_net * dec_iof_rate
    monthly_gross = adjusted_monthly_net + monthly_iof

    # 4. Annual payment with upfront discount
    annual_net = adjusted_monthly_net * Decimal("12") * ANNUAL_DISCOUNT_FACTOR
    annual_iof = annual_net * dec_iof_rate
    annual_gross = annual_net + annual_iof

    rounded_monthly_gross = _round_currency(monthly_gross)
    rounded_annual_gross = _round_currency(annual_gross)
    rounded_monthly_net = _round_currency(adjusted_monthly_net)
    rounded_monthly_iof = _round_currency(monthly_iof)

    premises["base_monthly_rate_total"] = float(total_rate_factor)
    premises["annual_discount_applied"] = "5% de desconto para pagamento a vista anual"

    return {
        "monthly_premium": float(rounded_monthly_gross),
        "annual_premium": float(rounded_annual_gross),
        "net_monthly_premium": float(rounded_monthly_net),
        "estimated_iof": float(rounded_monthly_iof),
        "iof_rate": float(dec_iof_rate),
        "underwriting_premises": premises,
    }
