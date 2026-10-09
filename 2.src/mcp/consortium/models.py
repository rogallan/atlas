"""Data models, request/response contracts, and exceptions for MCP Consortium Server (S11)."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONSORTIUM_DISCLAIMER = (
    "Simulação de consórcio baseada em dados puramente sintéticos e regras fictícias. "
    "A contemplação depende exclusivamente de sorteio ou lance em assembleia e não é "
    "garantida em data específica."
)


class ConsortiumSegment(StrEnum):
    """Segmentos e categorias de consórcio."""

    REAL_ESTATE = "real_estate"
    AUTOMOTIVE = "automotive"
    SERVICES = "services"


class GroupRulesInfo(BaseModel):
    """Regras de grupo, faixas de crédito e taxas de uma modalidade de consórcio."""

    model_config = ConfigDict(extra="ignore")

    segment: ConsortiumSegment = Field(description="Segmento do consórcio")
    display_name: str = Field(description="Nome comercial da modalidade")
    min_credit: float = Field(gt=0.0, description="Carta de crédito mínima em BRL")
    max_credit: float = Field(gt=0.0, description="Carta de crédito máxima em BRL")
    allowed_terms_months: list[int] = Field(description="Prazos em meses disponíveis para o grupo")
    total_admin_fee_pct: float = Field(
        gt=0.0, description="Taxa de administração total do período (ex: 0.15 para 15%)"
    )
    reserve_fund_pct: float = Field(
        gt=0.0, description="Taxa de fundo de reserva total (ex: 0.02 para 2%)"
    )
    max_embedded_bid_pct: float = Field(
        ge=0.0, le=1.0, description="Percentual máximo permitido de lance embutido (ex: 0.30)"
    )
    description: str = Field(description="Descrição da modalidade e bens/serviços elegíveis")


class ConsortiumInstallmentBreakdown(BaseModel):
    """Composição detalhada da parcela mensal de consórcio."""

    model_config = ConfigDict(extra="ignore")

    common_fund_amount: float = Field(
        gt=0.0, description="Fundo comum mensal (valor destinado à compra do bem)"
    )
    admin_fee_amount: float = Field(
        gt=0.0, description="Taxa de administração mensal da administradora"
    )
    reserve_fund_amount: float = Field(
        ge=0.0, description="Fundo de reserva mensal para inadimplência do grupo"
    )
    monthly_total: float = Field(gt=0.0, description="Valor integral da parcela mensal em BRL")


class ConsortiumSimulationResult(BaseModel):
    """Resultado detalhado de simulação de cota de consórcio com lances e disclaimer."""

    model_config = ConfigDict(extra="ignore")

    segment: ConsortiumSegment = Field(description="Segmento de consórcio cotado")
    display_name: str = Field(description="Nome comercial da modalidade")
    credit_amount: float = Field(gt=0.0, description="Valor nominal da carta de crédito em BRL")
    term_months: int = Field(ge=1, description="Prazo contratado em meses")
    installments: ConsortiumInstallmentBreakdown = Field(
        description="Composição detalhada da parcela mensal"
    )
    total_payable_amount: float = Field(
        gt=0.0, description="Custo total nominal a ser pago no período em BRL"
    )
    total_fees_amount: float = Field(
        ge=0.0, description="Total de taxas pagas (administração + fundo de reserva)"
    )
    total_cost_percentage: float = Field(
        ge=0.0, description="Percentual total de encargo financeiro sobre o crédito"
    )
    simulated_bid_amount: float | None = Field(
        default=None, description="Valor monetário do lance ofertado se simulado"
    )
    net_credit_with_embedded_bid: float | None = Field(
        default=None, description="Crédito líquido recebido após desconto do lance embutido"
    )
    post_bid_installment_estimate: float | None = Field(
        default=None, description="Estimativa de nova parcela reduzida após quitação de lance"
    )
    disclaimer: str = Field(
        default=DEFAULT_CONSORTIUM_DISCLAIMER,
        description="Aviso legal mandatório de não-garantia de contemplação",
    )


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------


class GetConsortiumGroupRulesInput(BaseModel):
    """Parâmetros de entrada para get_consortium_group_rules."""

    model_config = ConfigDict(extra="ignore")

    modality: ConsortiumSegment = Field(
        description="Segmento de consórcio (ex: 'real_estate', 'automotive', 'services')",
    )


class SimulateConsortiumInput(BaseModel):
    """Parâmetros de entrada para simulate_consortium."""

    model_config = ConfigDict(extra="ignore")

    modality: ConsortiumSegment = Field(
        description="Segmento do consórcio ('real_estate', 'automotive', 'services')",
    )
    credit_amount: float = Field(
        gt=0.0,
        description="Valor da carta de crédito pretendida em BRL",
    )
    term_months: int = Field(
        ge=1,
        description="Prazo desejado em meses (deve constar nos prazos permitidos do grupo)",
    )
    embedded_bid_pct: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Percentual de lance embutido simulado (ex: 0.20 para 20%)",
    )


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class MCPConsortiumError(Exception):
    """Base exception for MCP Consortium errors."""

    def __init__(self, message: str, code: int = -32000) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ModalityNotFoundError(MCPConsortiumError):
    """Raised when a consortium segment/modality is unknown."""

    def __init__(self, modality: str) -> None:
        super().__init__(
            f"Segmento de consórcio '{modality}' não encontrado no catálogo.",
            code=-32001,
        )


class InvalidConsortiumParameterError(MCPConsortiumError):
    """Raised when credit value, term, or bid violates group rules."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=-32002)
