"""MCP service catalog and sample queries metadata endpoints (S03/S08)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1", tags=["Menus"])


class SampleQuerySchema(BaseModel):
    label: str = Field(..., description="Query button display label")
    prompt: str = Field(..., description="Prompt template containing optional {CUST_ID}")
    description: str = Field(..., description="Explanation of query functionality")


class MCPMenuItemSchema(BaseModel):
    id: str = Field(..., description="Unique MCP service identifier")
    mcpName: str = Field(..., description="Official MCP display name")
    port: int = Field(..., description="Microservice local port")
    icon: str = Field(..., description="Lucide icon identifier")
    title: str = Field(..., description="Category display title")
    description: str = Field(..., description="Functional description")
    sampleQueries: list[SampleQuerySchema] = Field(
        default_factory=list, description="Curated sample prompts"
    )


MCP_CATALOG: list[MCPMenuItemSchema] = [
    MCPMenuItemSchema(
        id="customer",
        mcpName="Customer MCP",
        port=8001,
        icon="Users",
        title="Clientes & Contas",
        description=(
            "Consulta cadastral com dados mascarados LGPD, saldos consolidados e "
            "histórico de crédito."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Consultar Saldo e Contas",
                prompt="Qual é o saldo da conta corrente e investimentos do cliente {CUST_ID}?",
                description="Exibe saldos e status das contas bancárias vinculadas.",
            ),
            SampleQuerySchema(
                label="Perfil e Score de Crédito",
                prompt=(
                    "Apresente o perfil cadastral e a pontuação de score de crédito do cliente "
                    "{CUST_ID}."
                ),
                description="Exibe renda presumida, faixa de risco e segmento bancário.",
            ),
            SampleQuerySchema(
                label="Extrato Recente",
                prompt="Mostre as últimas movimentações e extrato bancário do cliente {CUST_ID}.",
                description="Lista transações financeiras recentes registradas.",
            ),
        ],
    ),
    MCPMenuItemSchema(
        id="loan",
        mcpName="Loan MCP",
        port=8002,
        icon="Calculator",
        title="Crédito & Empréstimos",
        description=(
            "Cálculo de CET regulatório, tabela Price e SAC, análise de margem consignável e juros."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Crédito Pessoal (R$ 25k em 36x)",
                prompt=(
                    "Simule um empréstimo pessoal de R$ 25.000 em 36 parcelas para o cliente "
                    "{CUST_ID}."
                ),
                description="Calcula CET anual, parcela mensal e custo efetivo total.",
            ),
            SampleQuerySchema(
                label="Financiamento Imobiliário SAC",
                prompt=(
                    "Simule um financiamento imobiliário de R$ 350.000 em 240 meses tabela SAC "
                    "para {CUST_ID}."
                ),
                description="Apresenta amortização decrescente e primeira parcela.",
            ),
            SampleQuerySchema(
                label="Crédito Auto com Carência",
                prompt=(
                    "Simule financiamento de veículo no valor de R$ 60.000 em 48 meses com "
                    "60 dias de carência para {CUST_ID}."
                ),
                description="Projeta impacto da carência nas parcelas subsequentes.",
            ),
        ],
    ),
    MCPMenuItemSchema(
        id="insurance",
        mcpName="Insurance MCP",
        port=8003,
        icon="ShieldCheck",
        title="Seguros & Proteção",
        description=(
            "Cotação multirrisco de seguros de vida, residencial e auto com regras de subscrição."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Seguro de Vida Individual",
                prompt=(
                    "Faça uma cotação de seguro de vida com cobertura de R$ 500.000 para "
                    "o cliente {CUST_ID}."
                ),
                description="Calcula prêmio mensal com IOF e coberturas inclusas.",
            ),
            SampleQuerySchema(
                label="Seguro Residencial Completo",
                prompt=(
                    "Cotar seguro residencial para imóvel de R$ 600.000 com danos elétricos "
                    "e incêndio para {CUST_ID}."
                ),
                description="Projeta franquia e coberturas patrimoniais.",
            ),
            SampleQuerySchema(
                label="Seguro Auto Premium",
                prompt=(
                    "Simule cotação de seguro automóvel para veículo avaliado em "
                    "R$ 90.000 para {CUST_ID}."
                ),
                description="Compara opções Essencial, Prata e Ouro.",
            ),
        ],
    ),
    MCPMenuItemSchema(
        id="consortium",
        mcpName="Consortium MCP",
        port=8004,
        icon="Building2",
        title="Consórcios Imóveis & Auto",
        description=(
            "Simulação de cotas de consórcios, fundo de reserva, taxas de administração "
            "e lances livres."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Consórcio Imobiliário (R$ 300k)",
                prompt=(
                    "Simule uma cota de consórcio imobiliário de R$ 300.000 em 180 meses "
                    "para {CUST_ID}."
                ),
                description="Exibe taxa administrativa mensal e parcela livre de juros.",
            ),
            SampleQuerySchema(
                label="Consórcio Automóvel (R$ 80k)",
                prompt=(
                    "Simule consórcio de automóvel com crédito de R$ 80.000 em 72 meses "
                    "para {CUST_ID}."
                ),
                description="Demonstra parcelas e cenário com lance livre de 20%.",
            ),
            SampleQuerySchema(
                label="Cenário com Lance Embutido",
                prompt=(
                    "Como funciona a oferta de lance livre de 30% no consórcio de imóveis "
                    "para {CUST_ID}?"
                ),
                description="Explica regras de contemplação e abatimento do saldo.",
            ),
        ],
    ),
    MCPMenuItemSchema(
        id="tariff",
        mcpName="Tariff MCP & RAG",
        port=8005,
        icon="FileText",
        title="Tarifas & Normas BACEN",
        description=(
            "Resoluções CMN/Bacen (3.919 e 4.949), tabela oficial de tarifas e direitos "
            "do consumidor."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Saques Gratuitos (Res. 3.919)",
                prompt=(
                    "Quantos saques gratuitos por mês o correntista tem direito segundo o BACEN?"
                ),
                description="Busca regulatória no corpus com citação normativa oficial.",
            ),
            SampleQuerySchema(
                label="Tabela de Tarifas de DOC/TED/PIX",
                prompt=(
                    "Qual é a tarifa oficial para emissão de extrato presencial e "
                    "transferências no ATLAS?"
                ),
                description="Verifica tabela de tarifas parametrizada do banco.",
            ),
            SampleQuerySchema(
                label="Direito a Pacote Essencial Gratuito",
                prompt=(
                    "Quais serviços bancários são obrigados a serem gratuitos pelo Banco Central?"
                ),
                description="Cita a lista de serviços essenciais sem cobrança de tarifa.",
            ),
        ],
    ),
    MCPMenuItemSchema(
        id="ticket",
        mcpName="Ticket MCP (HITL)",
        port=8006,
        icon="AlertCircle",
        title="Chamados & Suporte (HITL)",
        description=(
            "Abertura de chamados com governança estrita Human-in-the-Loop e token de confirmação."
        ),
        sampleQueries=[
            SampleQuerySchema(
                label="Contestação de Compra no Cartão",
                prompt=(
                    "Abra um chamado de contestação de compra de R$ 450,00 no cartão "
                    "para o cliente {CUST_ID}."
                ),
                description="Dispara proposta preliminar exigindo confirmação humana.",
            ),
            SampleQuerySchema(
                label="Aumento Emergencial de Limite",
                prompt=(
                    "Abra um chamado solicitando revisão emergencial de limite de crédito "
                    "para {CUST_ID}."
                ),
                description="Gera proposta com token de validação de 2 etapas.",
            ),
            SampleQuerySchema(
                label="Suporte a Falha de Transação",
                prompt="Registrar chamado de instabilidade no aplicativo para o cliente {CUST_ID}.",
                description="Gera protocolo de atendimento sob auditoria imutável.",
            ),
        ],
    ),
]


@router.get(
    "/mcp-menus",
    response_model=list[MCPMenuItemSchema],
    summary="List MCP services and menu items",
    description=(
        "Returns metadata, active ports, and sample prompt queries for all supported MCP "
        "microservices."
    ),
)
async def list_mcp_menus() -> list[MCPMenuItemSchema]:
    return MCP_CATALOG
