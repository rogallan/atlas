"""Deterministic accounting calculator for Brazilian consortium installments and bids (S11)."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from mcp.consortium.models import ConsortiumInstallmentBreakdown, GroupRulesInfo


def _round_currency(value: Decimal) -> Decimal:
    """Round a Decimal value to 2 decimal places using standard ROUND_HALF_UP."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_consortium_quota(
    credit_amount: float,
    term_months: int,
    rules: GroupRulesInfo,
    embedded_bid_pct: float = 0.0,
) -> dict[str, Any]:
    """Calculate common fund, admin fee, reserve fund, and bid impact.

    Args:
        credit_amount: Total nominal letter of credit in BRL.
        term_months: Duration in months.
        rules: Group parameters (admin fee pct, reserve fund pct).
        embedded_bid_pct: Ratio of letter of credit used as bid.

    Returns:
        Dictionary with installments breakdown, totals, and bid metrics.
    """
    dec_credit = Decimal(str(credit_amount))
    dec_n = Decimal(str(term_months))
    dec_admin_pct = Decimal(str(rules.total_admin_fee_pct))
    dec_reserve_pct = Decimal(str(rules.reserve_fund_pct))

    # 1. Base monthly shares
    dec_common_fund = dec_credit / dec_n
    dec_admin_fee = (dec_credit * dec_admin_pct) / dec_n
    dec_reserve_fund = (dec_credit * dec_reserve_pct) / dec_n

    dec_monthly_total = dec_common_fund + dec_admin_fee + dec_reserve_fund

    # 2. Accumulated totals over the term
    dec_total_payable = dec_monthly_total * dec_n
    dec_total_fees = (dec_admin_fee + dec_reserve_fund) * dec_n
    dec_total_cost_pct = ((dec_total_payable / dec_credit) - Decimal("1")) * Decimal("100")

    # 3. Bid projections
    simulated_bid_amount: float | None = None
    net_credit: float | None = None
    post_bid_installment: float | None = None

    if embedded_bid_pct > 0.0:
        dec_bid_pct = Decimal(str(embedded_bid_pct))
        dec_bid_val = dec_credit * dec_bid_pct
        dec_net_credit = dec_credit - dec_bid_val

        # Amortization of common fund balance: new FC = (Credit - Bid) / n
        dec_new_common_fund = dec_net_credit / dec_n
        dec_post_bid_total = dec_new_common_fund + dec_admin_fee + dec_reserve_fund

        simulated_bid_amount = float(_round_currency(dec_bid_val))
        net_credit = float(_round_currency(dec_net_credit))
        post_bid_installment = float(_round_currency(dec_post_bid_total))

    rounded_fc = _round_currency(dec_common_fund)
    rounded_ta = _round_currency(dec_admin_fee)
    rounded_fr = _round_currency(dec_reserve_fund)
    rounded_monthly = _round_currency(dec_monthly_total)
    rounded_total_payable = _round_currency(dec_total_payable)
    rounded_total_fees = _round_currency(dec_total_fees)
    rounded_cost_pct = dec_total_cost_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    installments = ConsortiumInstallmentBreakdown(
        common_fund_amount=float(rounded_fc),
        admin_fee_amount=float(rounded_ta),
        reserve_fund_amount=float(rounded_fr),
        monthly_total=float(rounded_monthly),
    )

    return {
        "installments": installments,
        "total_payable_amount": float(rounded_total_payable),
        "total_fees_amount": float(rounded_total_fees),
        "total_cost_percentage": float(rounded_cost_pct),
        "simulated_bid_amount": simulated_bid_amount,
        "net_credit_with_embedded_bid": net_credit,
        "post_bid_installment_estimate": post_bid_installment,
    }
