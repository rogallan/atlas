"""Data models, request/response contracts, and exceptions for MCP Insurance Server (S10)."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_INSURANCE_DISCLAIMER = (
    "Cotação de seguro baseada em dados puramente sintéticos e regras fictícias. "
    "Não constitui proposta vinculante ou emissão de apólice."
)


class InsuranceCategory(StrEnum):
    """Categorias regulatórias e comerciais de seguros."""

    LIFE = "life"
    HOME = "home"
    CREDIT_LIFE = "credit_life"
    CARD_PROTECTION = "card_protection"


class CoverageItem(BaseModel):
    """Cobertura individual de um produto de seguro com parâmetros atuariais."""

    model_config = ConfigDict(extra="ignore")

    code: str = Field(description="Identificador único da cobertura (ex: 'death')")
    name: str = Field(description="Nome comercial da cobertura")
    description: str = Field(description="Descrição da garantia e eventos cobertos")
    is_mandatory: bool = Field(description="Indica se a cobertura é básica/obrigatória")
    max_indemnity_limit: float = Field(
        gt=0.0, description="Limite Máximo de Indenização (LMI) em BRL"
    )
    deductible_info: str | None = Field(
        default=None, description="Informações de franquia ou carência"
    )
    rate_factor: float = Field(
        gt=0.0, description="Taxa atuarial base mensal aplicada sobre o capital segurado"
    )


class InsuranceProductInfo(BaseModel):
    """Ficha cadastral e limites de contratação de um produto de seguro."""

    model_config = ConfigDict(extra="ignore")

    product_id: str = Field(description="Identificador único do produto")
    name: str = Field(description="Nome comercial do seguro")
    category: InsuranceCategory = Field(description="Categoria do seguro")
    min_capital: float = Field(gt=0.0, description="Capital segurado mínimo em BRL")
    max_capital: float = Field(gt=0.0, description="Capital segurado máximo em BRL")
    available_coverages: list[CoverageItem] = Field(
        description="Lista de coberturas básicas e adicionais disponíveis"
    )
    description: str = Field(description="Resumo do produto e público-alvo")
    iof_rate: float = Field(
        ge=0.0, description="Alíquota de IOF seguro aplicável (ex: 0.0038 ou 0.0738)"
    )


class InsuranceQuoteResult(BaseModel):
    """Resultado estruturado de cotação de seguro com premissas e disclaimer."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str | None = Field(
        default=None, description="Identificador do cliente sintético consultado"
    )
    product_id: str = Field(description="Identificador do produto cotado")
    product_name: str = Field(description="Nome comercial do produto")
    category: InsuranceCategory = Field(description="Categoria do seguro")
    insured_capital: float = Field(gt=0.0, description="Capital segurado contratado em BRL")
    included_coverages: list[CoverageItem] = Field(
        description="Lista de coberturas inclusas nesta simulação"
    )
    monthly_premium: float = Field(gt=0.0, description="Prêmio mensal total com IOF em BRL")
    annual_premium: float = Field(gt=0.0, description="Prêmio anual com desconto à vista em BRL")
    net_monthly_premium: float = Field(gt=0.0, description="Prêmio líquido mensal antes de IOF")
    estimated_iof: float = Field(ge=0.0, description="Valor estimado de IOF mensal em BRL")
    iof_rate: float = Field(ge=0.0, description="Alíquota aplicada de IOF")
    underwriting_premises: dict[str, Any] = Field(
        default_factory=dict,
        description="Premissas atuariais utilizadas (faixa etária, multiplicador de risco, etc.)",
    )
    disclaimer: str = Field(
        default=DEFAULT_INSURANCE_DISCLAIMER,
        description="Disclaimer obrigatório de simulação não-vinculante",
    )


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------


class GetCoverageDetailsInput(BaseModel):
    """Parâmetros de entrada para get_coverage_details."""

    model_config = ConfigDict(extra="ignore")

    product_id: str = Field(
        min_length=3,
        max_length=64,
        description="Identificador do produto de seguro (ex: 'life_individual')",
    )


class SimulateInsuranceQuoteInput(BaseModel):
    """Parâmetros de entrada para simulate_insurance_quote."""

    model_config = ConfigDict(extra="ignore")

    customer_id: str | None = Field(
        default=None,
        pattern=r"^CUST-\d{4}$",
        description="Identificador do cliente sintético opcional (ex: 'CUST-0001')",
    )
    product_id: str = Field(
        min_length=3,
        max_length=64,
        description="Identificador do produto de seguro (ex: 'life_individual')",
    )
    insured_capital: float = Field(
        gt=0.0,
        description="Capital segurado desejado em BRL",
    )
    optional_coverages: list[str] = Field(
        default_factory=list,
        description="Lista de códigos de coberturas opcionais desejadas (ex: ['critical_illness'])",
    )


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class MCPInsuranceError(Exception):
    """Base exception for MCP Insurance errors."""

    def __init__(self, message: str, code: int = -32000):
        super().__init__(message)
        self.code = code
        self.message = message


class ProductNotFoundError(MCPInsuranceError):
    """Raised when an insurance product is not found in the catalog."""

    def __init__(self, product_id: str):
        super().__init__(
            f"Produto de seguro com identificador '{product_id}' não encontrado no catálogo.",
            code=-32001,
        )


class InvalidInsuranceParameterError(MCPInsuranceError):
    """Raised when insurance quotation parameters violate catalog boundaries."""

    def __init__(self, message: str):
        super().__init__(message, code=-32002)


class CoverageNotFoundError(MCPInsuranceError):
    """Raised when an optional coverage code is invalid for the selected product."""

    def __init__(self, coverage_code: str, product_id: str):
        super().__init__(
            f"Cobertura '{coverage_code}' não existe ou não está disponível "
            f"para o produto '{product_id}'.",
            code=-32003,
        )
