"""In-memory structured catalog of banking service fees, packages, and quotas (S12)."""

from mcp.tariff.models import (
    ChannelType,
    PackageNotFoundError,
    ServiceFeeItem,
    ServiceNotFoundError,
    TariffPackage,
)

# ---------------------------------------------------------------------------
# Tariff items catalog indexed by (service_code, channel)
# ---------------------------------------------------------------------------

TARIFF_ITEMS_CATALOG: dict[tuple[str, ChannelType], ServiceFeeItem] = {
    # 1. Saques (withdrawal)
    ("withdrawal", ChannelType.ATM): ServiceFeeItem(
        service_code="withdrawal",
        service_name="Saque em Terminal de Autoatendimento",
        channel=ChannelType.ATM,
        unit_price=2.90,
        is_essential_service=True,
        monthly_free_quota=4,
    ),
    ("withdrawal", ChannelType.BRANCH_COUNTER): ServiceFeeItem(
        service_code="withdrawal",
        service_name="Saque em Guichê de Caixa Presencial",
        channel=ChannelType.BRANCH_COUNTER,
        unit_price=3.80,
        is_essential_service=True,
        monthly_free_quota=4,
    ),
    ("withdrawal", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="withdrawal",
        service_name="Saque Digital / Saque Sem Cartão via App",
        channel=ChannelType.DIGITAL,
        unit_price=2.90,
        is_essential_service=True,
        monthly_free_quota=4,
    ),
    # 2. Extratos 30 dias (statement_30d)
    ("statement_30d", ChannelType.ATM): ServiceFeeItem(
        service_code="statement_30d",
        service_name="Extrato Mensal dos Últimos 30 Dias (Terminal)",
        channel=ChannelType.ATM,
        unit_price=2.20,
        is_essential_service=True,
        monthly_free_quota=2,
    ),
    ("statement_30d", ChannelType.BRANCH_COUNTER): ServiceFeeItem(
        service_code="statement_30d",
        service_name="Extrato Mensal dos Últimos 30 Dias (Guichê)",
        channel=ChannelType.BRANCH_COUNTER,
        unit_price=3.20,
        is_essential_service=True,
        monthly_free_quota=2,
    ),
    ("statement_30d", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="statement_30d",
        service_name="Consulta de Extrato via Internet / Mobile Banking",
        channel=ChannelType.DIGITAL,
        unit_price=0.00,
        is_essential_service=True,
        monthly_free_quota=9999,
    ),
    # 3. Transferências internas (internal_transfer)
    ("internal_transfer", ChannelType.ATM): ServiceFeeItem(
        service_code="internal_transfer",
        service_name="Transferência Entre Contas da Própria Instituição (ATM)",
        channel=ChannelType.ATM,
        unit_price=1.90,
        is_essential_service=True,
        monthly_free_quota=2,
    ),
    ("internal_transfer", ChannelType.BRANCH_COUNTER): ServiceFeeItem(
        service_code="internal_transfer",
        service_name="Transferência Entre Contas na Própria Instituição (Guichê)",
        channel=ChannelType.BRANCH_COUNTER,
        unit_price=4.20,
        is_essential_service=True,
        monthly_free_quota=2,
    ),
    ("internal_transfer", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="internal_transfer",
        service_name="Transferência Entre Contas na Própria Instituição (Digital)",
        channel=ChannelType.DIGITAL,
        unit_price=0.00,
        is_essential_service=True,
        monthly_free_quota=9999,
    ),
    # 4. TED (ted_transfer)
    ("ted_transfer", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="ted_transfer",
        service_name="Transferência Eletrônica Disponível (TED Digital)",
        channel=ChannelType.DIGITAL,
        unit_price=0.00,
        is_essential_service=False,
        monthly_free_quota=0,
    ),
    ("ted_transfer", ChannelType.ATM): ServiceFeeItem(
        service_code="ted_transfer",
        service_name="Transferência Eletrônica Disponível (TED Terminal)",
        channel=ChannelType.ATM,
        unit_price=11.00,
        is_essential_service=False,
        monthly_free_quota=0,
    ),
    ("ted_transfer", ChannelType.BRANCH_COUNTER): ServiceFeeItem(
        service_code="ted_transfer",
        service_name="Transferência Eletrônica Disponível (TED Guichê)",
        channel=ChannelType.BRANCH_COUNTER,
        unit_price=19.50,
        is_essential_service=False,
        monthly_free_quota=0,
    ),
    # 5. PIX (pix_transfer)
    ("pix_transfer", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="pix_transfer",
        service_name="Transferência Instantânea PIX (Pessoa Física)",
        channel=ChannelType.DIGITAL,
        unit_price=0.00,
        is_essential_service=True,
        monthly_free_quota=9999,
        regulatory_basis="Resolução BCB nº 1/2020",
    ),
    ("pix_transfer", ChannelType.ATM): ServiceFeeItem(
        service_code="pix_transfer",
        service_name="Transferência Instantânea PIX via Terminal",
        channel=ChannelType.ATM,
        unit_price=0.00,
        is_essential_service=True,
        monthly_free_quota=9999,
        regulatory_basis="Resolução BCB nº 1/2020",
    ),
    # 6. 2ª Via de Cartão (card_reissue)
    ("card_reissue", ChannelType.DIGITAL): ServiceFeeItem(
        service_code="card_reissue",
        service_name="Fornecimento de 2ª Via de Cartão de Débito (Pedido App)",
        channel=ChannelType.DIGITAL,
        unit_price=12.00,
        is_essential_service=False,
        monthly_free_quota=0,
    ),
    ("card_reissue", ChannelType.BRANCH_COUNTER): ServiceFeeItem(
        service_code="card_reissue",
        service_name="Fornecimento de 2ª Via de Cartão de Débito (Guichê)",
        channel=ChannelType.BRANCH_COUNTER,
        unit_price=15.00,
        is_essential_service=False,
        monthly_free_quota=0,
    ),
}

# ---------------------------------------------------------------------------
# Tariff packages catalog
# ---------------------------------------------------------------------------

TARIFF_PACKAGES_CATALOG: dict[str, TariffPackage] = {
    "essential_free": TariffPackage(
        package_id="essential_free",
        name="Serviços Essenciais Gratuitos (BACEN)",
        monthly_price=0.00,
        included_services={
            "withdrawal": 4,
            "statement_30d": 2,
            "internal_transfer": 2,
            "check_leaf": 10,
        },
        waiver_conditions="Gratuito por determinação legal da Resolução CMN nº 3.919/2010.",
        target_segment="all",
    ),
    "package_classic": TariffPackage(
        package_id="package_classic",
        name="Pacote Clássico Padronizado I",
        monthly_price=29.90,
        included_services={
            "withdrawal": 8,
            "statement_30d": 4,
            "internal_transfer": 4,
            "ted_transfer": 2,
        },
        waiver_conditions=(
            "Isenção total com investimentos a partir de R$ 30.000 ou fatura mensal de "
            "cartão de crédito a partir de R$ 2.000."
        ),
        target_segment="retail",
    ),
    "package_prime": TariffPackage(
        package_id="package_prime",
        name="Pacote Prime Especial Padronizado III",
        monthly_price=59.90,
        included_services={
            "withdrawal": 15,
            "statement_30d": 10,
            "internal_transfer": 20,
            "ted_transfer": 5,
        },
        waiver_conditions=(
            "Isenção total com investimentos a partir de R$ 100.000 ou portabilidade de salário."
        ),
        target_segment="prime",
    ),
    "package_private": TariffPackage(
        package_id="package_private",
        name="Pacote Private Banking Exclusivo",
        monthly_price=0.00,
        included_services={
            "withdrawal": 9999,
            "statement_30d": 9999,
            "internal_transfer": 9999,
            "ted_transfer": 9999,
        },
        waiver_conditions=(
            "Isenção contratual automática para clientes do segmento Private Banking (> R$ 1M)."
        ),
        target_segment="private",
    ),
}


def get_tariff_item(service_code: str, channel: ChannelType) -> ServiceFeeItem:
    """Retrieve tariff item by service code and transaction channel.

    Args:
        service_code: Service identifier.
        channel: ChannelType enum.

    Returns:
        ServiceFeeItem.

    Raises:
        ServiceNotFoundError: If service code is not recognized for that channel.
    """
    key = (service_code, channel)
    if key in TARIFF_ITEMS_CATALOG:
        return TARIFF_ITEMS_CATALOG[key]

    # Try fallback to ATM or Digital if channel not explicitly mapped
    for fallback_channel in [ChannelType.ATM, ChannelType.DIGITAL, ChannelType.BRANCH_COUNTER]:
        fb_key = (service_code, fallback_channel)
        if fb_key in TARIFF_ITEMS_CATALOG:
            return TARIFF_ITEMS_CATALOG[fb_key]

    raise ServiceNotFoundError(service_code=service_code, channel=channel.value)


def list_packages(target_segment: str | None = None) -> list[TariffPackage]:
    """Return tariff packages, optionally filtered by customer segment.

    Args:
        target_segment: Optional segment name ('retail', 'prime', 'private', 'all').

    Returns:
        List of matching TariffPackage models.
    """
    packages = list(TARIFF_PACKAGES_CATALOG.values())
    if not target_segment:
        return packages

    norm_seg = target_segment.lower()
    return [p for p in packages if p.target_segment in (norm_seg, "all")]


def get_package_info(package_id: str) -> TariffPackage:
    """Retrieve package details by identifier.

    Args:
        package_id: Unique package ID.

    Returns:
        TariffPackage model.

    Raises:
        PackageNotFoundError: If package does not exist.
    """
    if package_id not in TARIFF_PACKAGES_CATALOG:
        raise PackageNotFoundError(package_id)
    return TARIFF_PACKAGES_CATALOG[package_id]
