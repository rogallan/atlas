"""In-memory synthetic catalog of consortium modalities, group rules, and boundaries (S11)."""

from mcp.consortium.models import (
    ConsortiumSegment,
    GroupRulesInfo,
    InvalidConsortiumParameterError,
    ModalityNotFoundError,
)

CONSORTIUM_CATALOG: dict[ConsortiumSegment, GroupRulesInfo] = {
    ConsortiumSegment.REAL_ESTATE: GroupRulesInfo(
        segment=ConsortiumSegment.REAL_ESTATE,
        display_name="Consórcio Imobiliário",
        min_credit=150000.0,
        max_credit=1500000.0,
        allowed_terms_months=[120, 180, 240],
        total_admin_fee_pct=0.18,
        reserve_fund_pct=0.02,
        max_embedded_bid_pct=0.30,
        description=(
            "Aquisição de imóveis residenciais, comerciais, terrenos e reformas com "
            "prazos estendidos e custo financeiro planejado sem juros bancários."
        ),
    ),
    ConsortiumSegment.AUTOMOTIVE: GroupRulesInfo(
        segment=ConsortiumSegment.AUTOMOTIVE,
        display_name="Consórcio de Veículos",
        min_credit=30000.0,
        max_credit=250000.0,
        allowed_terms_months=[36, 48, 60, 72, 84],
        total_admin_fee_pct=0.14,
        reserve_fund_pct=0.02,
        max_embedded_bid_pct=0.30,
        description=(
            "Compra de automóveis novos e seminovos, utilitários e motocicletas com "
            "parcelas fixas sem incidência de juros bancários."
        ),
    ),
    ConsortiumSegment.SERVICES: GroupRulesInfo(
        segment=ConsortiumSegment.SERVICES,
        display_name="Consórcio de Serviços & Reformas",
        min_credit=10000.0,
        max_credit=60000.0,
        allowed_terms_months=[12, 24, 36, 48],
        total_admin_fee_pct=0.16,
        reserve_fund_pct=0.015,
        max_embedded_bid_pct=0.20,
        description=(
            "Planejamento financeiro para reformas residenciais, festas, viagens, cirurgias, "
            "procedimentos estéticos e cursos de especialização."
        ),
    ),
}


def get_all_modalities() -> list[GroupRulesInfo]:
    """Return all active consortium segments and group rules."""
    return list(CONSORTIUM_CATALOG.values())


def get_group_rules(modality: ConsortiumSegment | str) -> GroupRulesInfo:
    """Lookup group rules by modality identifier.

    Args:
        modality: Segment enum or string.

    Returns:
        GroupRulesInfo model.

    Raises:
        ModalityNotFoundError: If modality does not exist.
    """
    try:
        segment = ConsortiumSegment(modality)
    except ValueError:
        raise ModalityNotFoundError(str(modality)) from None

    if segment not in CONSORTIUM_CATALOG:
        raise ModalityNotFoundError(str(modality))
    return CONSORTIUM_CATALOG[segment]


def validate_consortium_request(
    modality: ConsortiumSegment | str,
    credit_amount: float,
    term_months: int,
    embedded_bid_pct: float = 0.0,
) -> GroupRulesInfo:
    """Validate consortium simulation parameters against group rules.

    Args:
        modality: Target segment.
        credit_amount: Requested credit in BRL.
        term_months: Requested duration in months.
        embedded_bid_pct: Proposed embedded bid ratio.

    Returns:
        Validated GroupRulesInfo.

    Raises:
        ModalityNotFoundError: If segment is invalid.
        InvalidConsortiumParameterError: If any parameter violates group limits.
    """
    rules = get_group_rules(modality)

    if credit_amount < rules.min_credit:
        raise InvalidConsortiumParameterError(
            f"Carta de crédito de R$ {credit_amount:,.2f} é inferior ao mínimo "
            f"de R$ {rules.min_credit:,.2f} para o {rules.display_name}."
        )

    if credit_amount > rules.max_credit:
        raise InvalidConsortiumParameterError(
            f"Carta de crédito de R$ {credit_amount:,.2f} excede o limite máximo "
            f"de R$ {rules.max_credit:,.2f} para o {rules.display_name}."
        )

    if term_months not in rules.allowed_terms_months:
        terms_str = ", ".join(f"{t}m" for t in rules.allowed_terms_months)
        raise InvalidConsortiumParameterError(
            f"Prazo de {term_months} meses não permitido para {rules.display_name}. "
            f"Prazos disponíveis para o grupo: {terms_str}."
        )

    if embedded_bid_pct < 0.0:
        raise InvalidConsortiumParameterError("Percentual de lance não pode ser negativo.")

    if embedded_bid_pct > rules.max_embedded_bid_pct:
        max_pct = rules.max_embedded_bid_pct * 100
        raise InvalidConsortiumParameterError(
            f"Lance embutido de {embedded_bid_pct * 100:.1f}% excede o limite "
            f"máximo permitido de {max_pct:.0f}% para {rules.display_name}."
        )

    return rules
