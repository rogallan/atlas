"""Data models, request/response contracts, and exceptions for MCP Tariff Server (S12)."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ChannelType(StrEnum):
    """Canais de prestação de serviços bancários."""

    DIGITAL = "digital"  # Mobile Banking / Internet Banking
    ATM = "atm"  # Terminal de Autoatendimento eletrônico
    BRANCH_COUNTER = "branch_counter"  # Atendimento presencial em guichê de caixa


class ServiceFeeItem(BaseModel):
    """Item tarifário padronizado conforme taxonomia da Resolução CMN nº 3.919/2010."""

    model_config = ConfigDict(extra="ignore")

    service_code: str = Field(description="Identificador único do serviço (ex: 'withdrawal')")
    service_name: str = Field(description="Nome regulatório ou comercial do serviço")
    channel: ChannelType = Field(description="Canal de atendimento utilizado")
    unit_price: float = Field(ge=0.0, description="Preço unitário avulso em BRL")
    is_essential_service: bool = Field(
        description="Indica se faz parte do pacote de serviços essenciais gratuitos"
    )
    monthly_free_quota: int | None = Field(
        default=None, description="Quantidade mensal gratuita assegurada pelo BACEN"
    )
    regulatory_basis: str = Field(
        default="Resolução CMN nº 3.919/2010",
        description="Norma de referência legal do Banco Central / CMN",
    )
    effective_date: str = Field(
        default="2024-01-01", description="Data de vigência da tabela de tarifas (AAAA-MM-DD)"
    )


class TariffPackage(BaseModel):
    """Pacote de serviços de conta corrente e regras de isenção por relacionamento."""

    model_config = ConfigDict(extra="ignore")

    package_id: str = Field(description="Identificador único do pacote")
    name: str = Field(description="Nome comercial do pacote de serviços")
    monthly_price: float = Field(ge=0.0, description="Tarifa mensal de manutenção em BRL")
    included_services: dict[str, int] = Field(
        description="Mapeamento de código de serviço para quantidade mensal inclusa"
    )
    waiver_conditions: str | None = Field(
        default=None, description="Regra de isenção por investimentos, salário ou gastos"
    )
    target_segment: str | None = Field(
        default=None, description="Segmento de clientes alvo (retail, prime, private, all)"
    )
    regulatory_basis: str = Field(
        default="Resolução CMN nº 3.919/2010",
        description="Fundamento regulatório do pacote padronizado",
    )


class QuotaCheckResult(BaseModel):
    """Resultado da avaliação de franquia mensal e cálculo de tarifa de serviço avulso."""

    model_config = ConfigDict(extra="ignore")

    service_code: str = Field(description="Código do serviço consultado")
    service_name: str = Field(description="Nome do serviço consultado")
    channel: ChannelType = Field(description="Canal de atendimento considerado")
    used_count: int = Field(ge=0, description="Quantidade de transações já realizadas no mês")
    free_quota_limit: int = Field(ge=0, description="Limite gratuito mensal concedido")
    is_within_free_quota: bool = Field(
        description="Verdadeiro se a operação ainda estiver dentro da franquia gratuita"
    )
    chargeable_units: int = Field(
        ge=0, description="Quantidade de operações excedentes sujeitas a cobrança"
    )
    unit_fee: float = Field(ge=0.0, description="Tarifa unitária cobrada por operação excedente")
    total_charge: float = Field(ge=0.0, description="Valor total a ser cobrado da operação em BRL")
    regulatory_basis: str = Field(
        default="Resolução CMN nº 3.919/2010",
        description="Base legal da gratuidade dos serviços essenciais",
    )


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------


class GetServiceFeeInput(BaseModel):
    """Parâmetros de entrada para get_service_fee."""

    model_config = ConfigDict(extra="ignore")

    service_code: str = Field(
        min_length=2,
        max_length=64,
        description="Código do serviço (ex: 'withdrawal', 'statement_30d', 'ted_transfer')",
    )
    channel: ChannelType = Field(
        default=ChannelType.DIGITAL,
        description="Canal de prestação ('digital', 'atm', 'branch_counter')",
    )


class CheckEssentialServicesQuotaInput(BaseModel):
    """Parâmetros de entrada para check_essential_services_quota."""

    model_config = ConfigDict(extra="ignore")

    service_code: str = Field(
        min_length=2,
        max_length=64,
        description="Código do serviço essencial (ex: 'withdrawal', 'statement_30d')",
    )
    used_count: int = Field(
        ge=0,
        description="Quantidade de transações do serviço já efetuadas no mês corrente",
    )
    channel: ChannelType = Field(
        default=ChannelType.ATM,
        description="Canal a ser considerado ('digital', 'atm', 'branch_counter')",
    )


class ComparePackagesInput(BaseModel):
    """Parâmetros de entrada para compare_packages."""

    model_config = ConfigDict(extra="ignore")

    customer_segment: str | None = Field(
        default=None,
        description="Filtro opcional por segmento ('retail', 'prime', 'private')",
    )


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class MCPTariffError(Exception):
    """Base exception for MCP Tariff errors."""

    def __init__(self, message: str, code: int = -32000) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ServiceNotFoundError(MCPTariffError):
    """Raised when a service code is not found in the tariff table."""

    def __init__(self, service_code: str, channel: str | None = None) -> None:
        ch_msg = f" para o canal '{channel}'" if channel else ""
        super().__init__(
            f"Serviço bancário '{service_code}' não encontrado na tabela de tarifas{ch_msg}.",
            code=-32001,
        )


class PackageNotFoundError(MCPTariffError):
    """Raised when a tariff package is not found."""

    def __init__(self, package_id: str) -> None:
        super().__init__(
            f"Pacote de tarifas '{package_id}' não encontrado no catálogo.",
            code=-32002,
        )


class InvalidTariffParameterError(MCPTariffError):
    """Raised when tariff lookup parameters are invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=-32003)
