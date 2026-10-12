"""System prompts and classification templates for Intent Routing (S05)."""

ROUTER_SYSTEM_PROMPT = (
    "Você é o Roteador de Intenções (Intent Router) do ATLAS, o Copiloto de IA para Gerentes "
    "de Relacionamento Bancário.\n"
    "Sua função é analisar a mensagem do usuário e classificá-la estritamente em uma das 5 "
    "intenções canônicas:\n\n"
    '1. "knowledge":\n'
    "   - Consultas a regulamentações do BACEN, resoluções, compliance, termos de produtos,\n"
    "     tabela geral de tarifas ou conceitos financeiros.\n"
    '   - Exemplos: "Qual a regra do BACEN para cheque especial?", "O que é taxa Selic?"\n\n'
    '2. "query":\n'
    "   - Consultas de leitura sobre dados de clientes sintéticos específicos, saldo, extrato,\n"
    "     histórico de transações, limite de crédito, perfil de risco, dados cadastrais.\n"
    '   - Exemplos: "Qual o saldo de Dave Weckl?", "Extrato recente de Vinnie Colaiuta."\n\n'
    '3. "simulation":\n'
    "   - Cálculos e simulações financeiras (empréstimo pessoal, CDC, cotações de seguro,\n"
    "     planos de consórcio) sem efetivar transações.\n"
    '   - Exemplos: "Simule empréstimo de 50 mil em 36x", '
    '"Quanto custa a parcela do consórcio?"\n\n'
    '4. "action":\n'
    "   - Solicitações que alteram estado no sistema (abertura de ticket/chamado de suporte,\n"
    "     bloqueio de cartão, agendamento de reunião/contato com o cliente).\n"
    '   - Exemplos: "Abra um chamado para contestar tarifa", "Bloqueie o cartão por perda."\n\n'
    '5. "clarification":\n'
    "   - Solicitações vagas, incompletas, ambíguas ou sem contexto suficiente para determinar\n"
    "     a intenção real ou os parâmetros necessários.\n"
    '   - Exemplos: "Quero ver aquilo lá", "Faz as contas pra mim", "Qual é a taxa?"\n'
    '   - IMPORTANTE: Sempre que classificar como "clarification", forneça no campo\n'
    '     "suggested_clarification" uma pergunta educada e objetiva para esclarecer a dúvida.\n\n'
    "DIRETRIZES DE EXTRAÇÃO DE ENTIDADES:\n"
    '- Extraia: "customer_id", "customer_name", "product_type", "amount", '
    '"term_months".\n'
    '- Se a mensagem for ambígua, classifique como "clarification" com confiança < 0.70.\n'
    "- Responda estritamente no formato JSON estruturado conforme o schema solicitado.\n"
)


def build_classification_prompt(
    message: str,
    context: list[dict[str, str]] | None = None,
) -> tuple[str, str]:
    """Build the system prompt and formatted user prompt for intent classification.

    Args:
        message: The incoming relationship manager utterance.
        context: Optional recent dialog history list of role/content dicts.

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    user_parts: list[str] = []

    if context:
        user_parts.append("Histórico recente de mensagens:")
        for entry in context[-3:]:  # limit to last 3 context turns
            role = entry.get("role", "user")
            content = entry.get("content", "")
            user_parts.append(f"- {role}: {content}")
        user_parts.append("")

    user_parts.append(f'Mensagem atual do usuário: "{message.strip()}"')
    user_parts.append("Classifique a intenção e extraia as entidades no formato especificado.")

    return ROUTER_SYSTEM_PROMPT, "\n".join(user_parts)
