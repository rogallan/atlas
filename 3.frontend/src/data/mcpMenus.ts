import { CustomerSummary, MCPMenuItem } from '../types/api';

export const SYNTHETIC_CUSTOMERS: CustomerSummary[] = [
  {
    id: 'CUST-0001',
    name: 'Roberto Carlos Santos',
    segment: 'PRIME',
    monthly_income: 14500,
    credit_score: 820,
    active_account: '0001-92837-1',
  },
  {
    id: 'CUST-0002',
    name: 'Beatriz Almeida Silveira',
    segment: 'PRIVATE',
    monthly_income: 38000,
    credit_score: 910,
    active_account: '0001-44129-8',
  },
  {
    id: 'CUST-0003',
    name: 'Carlos Eduardo Oliveira',
    segment: 'RETAIL',
    monthly_income: 4200,
    credit_score: 640,
    active_account: '0105-18234-0',
  },
  {
    id: 'CUST-0004',
    name: 'Mariana Duarte Souza',
    segment: 'PRIME',
    monthly_income: 16800,
    credit_score: 790,
    active_account: '0001-77291-5',
  },
  {
    id: 'CUST-0005',
    name: 'Lucas Ferreira Lima',
    segment: 'RETAIL',
    monthly_income: 5500,
    credit_score: 670,
    active_account: '0210-99412-3',
  },
  {
    id: 'CUST-0006',
    name: 'Juliana Pires Martins',
    segment: 'PRIVATE',
    monthly_income: 45000,
    credit_score: 935,
    active_account: '0001-10394-2',
  },
  {
    id: 'CUST-0007',
    name: 'Thiago Mendes Ramos',
    segment: 'CORPORATE',
    monthly_income: 82000,
    credit_score: 880,
    active_account: '0001-55102-7',
  },
  {
    id: 'CUST-0008',
    name: 'Fernanda Nogueira Costa',
    segment: 'RETAIL',
    monthly_income: 3900,
    credit_score: 590,
    active_account: '0315-77210-4',
  },
];

export const MCP_MENU_ITEMS: MCPMenuItem[] = [
  {
    id: 'customer',
    mcpName: 'Customer MCP',
    port: 8001,
    icon: 'Users',
    title: 'Clientes & Contas',
    description: 'Consulta cadastral com dados mascarados LGPD, saldos consolidados e histórico de crédito.',
    sampleQueries: [
      {
        label: 'Consultar Saldo e Contas',
        prompt: 'Qual é o saldo da conta corrente e investimentos do cliente {CUST_ID}?',
        description: 'Exibe saldos e status das contas bancárias vinculadas.',
      },
      {
        label: 'Perfil e Score de Crédito',
        prompt: 'Apresente o perfil cadastral e a pontuação de score de crédito do cliente {CUST_ID}.',
        description: 'Exibe renda presumida, faixa de risco e segmento bancário.',
      },
      {
        label: 'Extrato Recente',
        prompt: 'Mostre as últimas movimentações e extrato bancário do cliente {CUST_ID}.',
        description: 'Lista transações financeiras recentes registradas.',
      },
    ],
  },
  {
    id: 'loan',
    mcpName: 'Loan MCP',
    port: 8002,
    icon: 'Calculator',
    title: 'Crédito & Empréstimos',
    description: 'Cálculo de CET regulatório, tabela Price e SAC, análise de margem consignável e juros.',
    sampleQueries: [
      {
        label: 'Crédito Pessoal (R$ 25k em 36x)',
        prompt: 'Simule um empréstimo pessoal de R$ 25.000 em 36 parcelas para o cliente {CUST_ID}.',
        description: 'Calcula CET anual, parcela mensal e custo efetivo total.',
      },
      {
        label: 'Financiamento Imobiliário SAC',
        prompt: 'Simule um financiamento imobiliário de R$ 350.000 em 240 meses tabela SAC para {CUST_ID}.',
        description: 'Apresenta amortização decrescente e primeira parcela.',
      },
      {
        label: 'Crédito Auto com Carência',
        prompt: 'Simule financiamento de veículo no valor de R$ 60.000 em 48 meses com 60 dias de carência para {CUST_ID}.',
        description: 'Projeta impacto da carência nas parcelas subsequentes.',
      },
    ],
  },
  {
    id: 'insurance',
    mcpName: 'Insurance MCP',
    port: 8003,
    icon: 'ShieldCheck',
    title: 'Seguros & Proteção',
    description: 'Cotação multirrisco de seguros de vida, residencial e auto com regras de subscrição.',
    sampleQueries: [
      {
        label: 'Seguro de Vida Individual',
        prompt: 'Faça uma cotação de seguro de vida com cobertura de R$ 500.000 para o cliente {CUST_ID}.',
        description: 'Calcula prêmio mensal com IOF e coberturas inclusas.',
      },
      {
        label: 'Seguro Residencial Completo',
        prompt: 'Cotar seguro residencial para imóvel de R$ 600.000 com danos elétricos e incêndio para {CUST_ID}.',
        description: 'Projeta franquia e coberturas patrimoniais.',
      },
      {
        label: 'Seguro Auto Premium',
        prompt: 'Simule cotação de seguro automóvel para veículo avaliado em R$ 90.000 para {CUST_ID}.',
        description: 'Compara opções Essencial, Prata e Ouro.',
      },
    ],
  },
  {
    id: 'consortium',
    mcpName: 'Consortium MCP',
    port: 8004,
    icon: 'Building2',
    title: 'Consórcios Imóveis & Auto',
    description: 'Simulação de cotas de consórcios, fundo de reserva, taxas de administração e lances livres.',
    sampleQueries: [
      {
        label: 'Consórcio Imobiliário (R$ 300k)',
        prompt: 'Simule uma cota de consórcio imobiliário de R$ 300.000 em 180 meses para {CUST_ID}.',
        description: 'Exibe taxa administrativa mensal e parcela livre de juros.',
      },
      {
        label: 'Consórcio Automóvel (R$ 80k)',
        prompt: 'Simule consórcio de automóvel com crédito de R$ 80.000 em 72 meses para {CUST_ID}.',
        description: 'Demonstra parcelas e cenário com lance livre de 20%.',
      },
      {
        label: 'Cenário com Lance Embutido',
        prompt: 'Como funciona a oferta de lance livre de 30% no consórcio de imóveis para {CUST_ID}?',
        description: 'Explica regras de contemplação e abatimento do saldo.',
      },
    ],
  },
  {
    id: 'tariff',
    mcpName: 'Tariff MCP & RAG',
    port: 8005,
    icon: 'FileText',
    title: 'Tarifas & Normas BACEN',
    description: 'Resoluções CMN/Bacen (3.919 e 4.949), tabela oficial de tarifas e direitos do consumidor.',
    sampleQueries: [
      {
        label: 'Saques Gratuitos (Res. 3.919)',
        prompt: 'Quantos saques gratuitos por mês o correntista tem direito segundo o BACEN?',
        description: 'Busca regulatória no corpus com citação normativa oficial.',
      },
      {
        label: 'Tabela de Tarifas de DOC/TED/PIX',
        prompt: 'Qual é a tarifa oficial para emissão de extrato presencial e transferências no ATLAS?',
        description: 'Verifica tabela de tarifas parametrizada do banco.',
      },
      {
        label: 'Direito a Pacote Essencial Gratuito',
        prompt: 'Quais serviços bancários são obrigados a serem gratuitos pelo Banco Central?',
        description: 'Cita a lista de serviços essenciais sem cobrança de tarifa.',
      },
    ],
  },
  {
    id: 'ticket',
    mcpName: 'Ticket MCP (HITL)',
    port: 8006,
    icon: 'AlertCircle',
    title: 'Chamados & Suporte (HITL)',
    description: 'Abertura de chamados com governança estrita Human-in-the-Loop e token de confirmação.',
    sampleQueries: [
      {
        label: 'Contestação de Compra no Cartão',
        prompt: 'Abra um chamado de contestação de compra de R$ 450,00 no cartão para o cliente {CUST_ID}.',
        description: 'Dispara proposta preliminar exigindo confirmação humana.',
      },
      {
        label: 'Aumento Emergencial de Limite',
        prompt: 'Abra um chamado solicitando revisão emergencial de limite de crédito para {CUST_ID}.',
        description: 'Gera proposta com token de validação de 2 etapas.',
      },
      {
        label: 'Suporte a Falha de Transação',
        prompt: 'Registrar chamado de instabilidade no aplicativo para o cliente {CUST_ID}.',
        description: 'Gera protocolo de atendimento sob auditoria imutável.',
      },
    ],
  },
];
