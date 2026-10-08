"""In-memory synthetic catalog of insurance products, coverages, and constraints (S10)."""

from mcp.insurance.models import (
    CoverageItem,
    InsuranceCategory,
    InsuranceProductInfo,
    InvalidInsuranceParameterError,
    ProductNotFoundError,
)

INSURANCE_CATALOG: dict[str, InsuranceProductInfo] = {
    "life_individual": InsuranceProductInfo(
        product_id="life_individual",
        name="Seguro de Vida Individual",
        category=InsuranceCategory.LIFE,
        min_capital=20000.0,
        max_capital=1500000.0,
        iof_rate=0.0038,
        description=(
            "Proteção financeira completa para você e seus beneficiários com coberturas "
            "em vida e indenização rápida em casos de sinistro."
        ),
        available_coverages=[
            CoverageItem(
                code="death",
                name="Morte Qualquer Causa",
                description="Indenização aos beneficiários em caso de morte natural ou acidental.",
                is_mandatory=True,
                max_indemnity_limit=1500000.0,
                deductible_info=None,
                rate_factor=0.00035,
            ),
            CoverageItem(
                code="accidental_disability",
                name="Invalidez Permanente por Acidente",
                description="Indenização em caso de perda ou impotência funcional permanente.",
                is_mandatory=False,
                max_indemnity_limit=1500000.0,
                deductible_info=None,
                rate_factor=0.00015,
            ),
            CoverageItem(
                code="critical_illness",
                name="Doenças Graves",
                description="Antecipação de indenização no diagnóstico de câncer, infarto ou AVC.",
                is_mandatory=False,
                max_indemnity_limit=500000.0,
                deductible_info="Carência de 60 dias para diagnóstico após contratação.",
                rate_factor=0.00025,
            ),
            CoverageItem(
                code="funeral_assist",
                name="Assistência Funeral Familiar",
                description="Reembolso de despesas ou prestação direta de serviços de funeral.",
                is_mandatory=False,
                max_indemnity_limit=10000.0,
                deductible_info=None,
                rate_factor=0.00005,
            ),
        ],
    ),
    "home_complete": InsuranceProductInfo(
        product_id="home_complete",
        name="Seguro Residencial Completo",
        category=InsuranceCategory.HOME,
        min_capital=50000.0,
        max_capital=2000000.0,
        iof_rate=0.0738,
        description=(
            "Proteção para casa ou apartamento próprio e alugado contra incêndio, roubo, "
            "danos elétricos e assistência emergencial 24h."
        ),
        available_coverages=[
            CoverageItem(
                code="fire_lightning_explosion",
                name="Incêndio, Queda de Raio e Explosão",
                description="Cobertura da estrutura do imóvel e do conteúdo em eventos de fogo.",
                is_mandatory=True,
                max_indemnity_limit=2000000.0,
                deductible_info=None,
                rate_factor=0.00020,
            ),
            CoverageItem(
                code="theft_robbery",
                name="Roubo e Furto Qualificado",
                description="Subtração de bens do interior da residência mediante arrombamento.",
                is_mandatory=False,
                max_indemnity_limit=400000.0,
                deductible_info="Franquia de 10% dos prejuízos com valor mínimo de R$ 500.",
                rate_factor=0.00030,
            ),
            CoverageItem(
                code="electrical_damage",
                name="Danos Elétricos",
                description="Danos a aparelhos e fiação decorrentes de variações na rede elétrica.",
                is_mandatory=False,
                max_indemnity_limit=150000.0,
                deductible_info="Franquia fixa de R$ 300 por evento indenizável.",
                rate_factor=0.00018,
            ),
            CoverageItem(
                code="plumbing_24h",
                name="Assistência Residencial 24 Horas",
                description=(
                    "Serviços emergenciais de encanador, eletricista, vidraceiro e chaveiro."
                ),
                is_mandatory=False,
                max_indemnity_limit=5000.0,
                deductible_info="Até 4 chamados por ano de vigência.",
                rate_factor=0.00008,
            ),
        ],
    ),
    "credit_life_presta": InsuranceProductInfo(
        product_id="credit_life_presta",
        name="Seguro Prestamista Financeiro",
        category=InsuranceCategory.CREDIT_LIFE,
        min_capital=1000.0,
        max_capital=300000.0,
        iof_rate=0.0038,
        description=(
            "Garante a liquidação ou amortização do saldo devedor de empréstimos e "
            "financiamentos em caso de imprevistos financeiros ou morte."
        ),
        available_coverages=[
            CoverageItem(
                code="loan_death_disability",
                name="Quitação por Morte ou Invalidez Total",
                description="Quitação do saldo devedor remanescente do contrato de crédito.",
                is_mandatory=True,
                max_indemnity_limit=300000.0,
                deductible_info=None,
                rate_factor=0.00045,
            ),
            CoverageItem(
                code="involuntary_unemployment",
                name="Desemprego Involuntário",
                description=(
                    "Pagamento de até 4 parcelas do empréstimo em demissão sem justa causa."
                ),
                is_mandatory=False,
                max_indemnity_limit=30000.0,
                deductible_info="Carência inicial de 30 dias e vínculo CLT mínimo de 12 meses.",
                rate_factor=0.00030,
            ),
        ],
    ),
    "card_protection_plus": InsuranceProductInfo(
        product_id="card_protection_plus",
        name="Proteção de Cartão & Conta Segura",
        category=InsuranceCategory.CARD_PROTECTION,
        min_capital=1000.0,
        max_capital=50000.0,
        iof_rate=0.0738,
        description=(
            "Tranquilidade contra fraudes, perda, coação em transações PIX e furto de bolsa "
            "ou carteira contendo cartões do banco."
        ),
        available_coverages=[
            CoverageItem(
                code="card_fraud_theft",
                name="Fraude e Saque Indevido sob Coação",
                description=(
                    "Reembolso de compras e saques indevidos ocorridos até 72h antes do aviso."
                ),
                is_mandatory=True,
                max_indemnity_limit=50000.0,
                deductible_info=None,
                rate_factor=0.00120,
            ),
            CoverageItem(
                code="pix_under_duress",
                name="Transferência PIX sob Coação",
                description="Ressarcimento de transferências realizadas mediante ameaça física.",
                is_mandatory=False,
                max_indemnity_limit=25000.0,
                deductible_info="Boletim de ocorrência policial obrigatório.",
                rate_factor=0.00080,
            ),
            CoverageItem(
                code="bag_protection",
                name="Bolsa e Documentos Protegidos",
                description="Indenização para reposição da bolsa, documentos pessoais e celular.",
                is_mandatory=False,
                max_indemnity_limit=3000.0,
                deductible_info="Franquia fixa de R$ 150 por evento.",
                rate_factor=0.00050,
            ),
        ],
    ),
}


def get_all_products() -> list[InsuranceProductInfo]:
    """Return all active insurance products in the synthetic catalog."""
    return list(INSURANCE_CATALOG.values())


def get_product_info(product_id: str) -> InsuranceProductInfo:
    """Lookup an insurance product by its identifier.

    Args:
        product_id: Product identifier.

    Returns:
        InsuranceProductInfo model.

    Raises:
        ProductNotFoundError: If product_id does not exist.
    """
    if product_id not in INSURANCE_CATALOG:
        raise ProductNotFoundError(product_id)
    return INSURANCE_CATALOG[product_id]


def validate_insurance_request(
    product_id: str,
    insured_capital: float,
) -> InsuranceProductInfo:
    """Validate requested insurance parameters against catalog boundaries.

    Args:
        product_id: Target product ID.
        insured_capital: Desired insured capital in BRL.

    Returns:
        Validated InsuranceProductInfo.

    Raises:
        ProductNotFoundError: If product_id is invalid.
        InvalidInsuranceParameterError: If insured_capital is outside bounds.
    """
    info = get_product_info(product_id)

    if insured_capital < info.min_capital:
        raise InvalidInsuranceParameterError(
            f"Capital segurado de R$ {insured_capital:,.2f} é inferior ao mínimo "
            f"de R$ {info.min_capital:,.2f} para o produto '{info.name}'."
        )

    if insured_capital > info.max_capital:
        raise InvalidInsuranceParameterError(
            f"Capital segurado de R$ {insured_capital:,.2f} excede o limite máximo "
            f"de R$ {info.max_capital:,.2f} para o produto '{info.name}'."
        )

    return info
