"""Deterministic financial mathematics engine for loan amortization and CET (S09)."""

from decimal import ROUND_HALF_UP, Decimal

from mcp.loan.models import AmortizationScheduleItem


def round_currency(val: Decimal) -> Decimal:
    """Round monetary values to two decimal places using standard banking rules."""
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_iof(principal: Decimal, term_months: int) -> Decimal:
    """Calculate estimated federal IOF tax for personal/commercial credit operations.

    Formula based on Brazilian regulations (Decreto nº 6.306/2007):
        - Fixed rate: 0.38% (alíquota básica adicional)
        - Daily rate: 0.0082% per day, capped at 365 days (~2.993%)
    """
    days = min(term_months * 30, 365)
    daily_rate = Decimal("0.000082") * Decimal(days)
    fixed_rate = Decimal("0.0038")
    total_rate = fixed_rate + daily_rate
    return round_currency(principal * total_rate)


def calculate_pmt(pv: Decimal, monthly_rate: Decimal, n: int) -> Decimal:
    """Calculate monthly installment using the French Amortization (Tabela Price) formula.

    Formula:
        PMT = PV * (i * (1 + i)^n) / ((1 + i)^n - 1)
    """
    if monthly_rate <= Decimal("0"):
        return round_currency(pv / Decimal(n))

    one_plus_i = Decimal("1") + monthly_rate
    factor = one_plus_i ** n
    numerator = pv * monthly_rate * factor
    denominator = factor - Decimal("1")
    pmt = numerator / denominator
    return round_currency(pmt)


def calculate_effective_rate_monthly(
    net_principal: Decimal,
    pmt: Decimal,
    n: int,
    initial_guess: Decimal,
) -> Decimal:
    """Compute the monthly internal rate of return (IRR) via Newton-Raphson approximation.

    Solves for r such that:
        net_principal = sum_{t=1}^n [ pmt / (1 + r)^t ]
    """
    rate = initial_guess
    for _ in range(50):
        # f(r) = sum(pmt / (1+r)^t) - net_principal
        # f'(r) = - sum(t * pmt / (1+r)^(t+1))
        f_val = Decimal("0")
        f_prime = Decimal("0")
        for t in range(1, n + 1):
            disc = (Decimal("1") + rate) ** t
            f_val += pmt / disc
            f_prime -= Decimal(t) * pmt / ((Decimal("1") + rate) ** (t + 1))

        f_val -= net_principal

        if abs(f_val) < Decimal("0.0001"):
            break

        if f_prime == Decimal("0"):
            break

        rate = rate - (f_val / f_prime)

    return max(Decimal("0.0001"), rate)


def calculate_annual_cet(
    net_principal: Decimal,
    pmt: Decimal,
    n: int,
    monthly_nominal_rate: Decimal,
) -> Decimal:
    """Calculate the annualized Total Effective Cost (CET - Resolução CMN 4.881).

    Formula:
        CET_anual = (1 + r_efetivo_mensal)^12 - 1
    """
    r_monthly_eff = calculate_effective_rate_monthly(
        net_principal=net_principal,
        pmt=pmt,
        n=n,
        initial_guess=monthly_nominal_rate,
    )
    cet_annual = ((Decimal("1") + r_monthly_eff) ** 12) - Decimal("1")
    return cet_annual.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def generate_amortization_schedule(
    financed_amount: Decimal,
    monthly_rate: Decimal,
    pmt: Decimal,
    n: int,
) -> list[AmortizationScheduleItem]:
    """Generate the chronological month-by-month Tabela Price amortization schedule."""
    schedule: list[AmortizationScheduleItem] = []
    balance = financed_amount

    for m in range(1, n + 1):
        interest = round_currency(balance * monthly_rate)
        amortization = pmt - interest

        # Last month adjustment to guarantee zero residual balance
        if m == n or amortization > balance:
            amortization = balance
            pmt_actual = round_currency(amortization + interest)
            balance = Decimal("0")
        else:
            balance = round_currency(balance - amortization)
            pmt_actual = pmt

        schedule.append(
            AmortizationScheduleItem(
                month=m,
                installment=float(pmt_actual),
                interest=float(interest),
                amortization=float(amortization),
                remaining_balance=float(balance),
            )
        )

    return schedule
