"""Fallback Node: Handles step limits, security blocks, and unexpected errors gracefully (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep

logger = logging.getLogger("atlas.agent.graph.fallback_node")


class FallbackNode:
    """Terminates failed, ungrounded, or looped execution with courteous explanations."""

    def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("fallback_node")
        state.current_step = AgentStep.FALLBACK

        logger.warning(
            "Fallback node entered for session '%s' (blocked=%s, steps=%d/%d, error='%s')",
            state.session_id,
            state.security_blocked,
            state.step_count,
            state.max_steps,
            state.error_message,
        )

        if state.security_blocked:
            detail = state.error_message or "Comando incompatível com políticas operacionais."
            state.final_response = (
                "🛡️ **Requisição Interrompida por Segurança**\n\n"
                f"A mensagem violou as diretrizes de conformidade bancária.\nDetalhe: {detail}"
            )
        elif state.step_count >= state.max_steps:
            state.final_response = (
                "⚠️ **Limite de Etapas de Execução Atingido**\n\n"
                "O processamento da sua solicitação atingiu o limite anti-loop do grafo. "
                "Por favor, reformule sua pergunta de maneira mais específica."
            )
        elif not state.is_grounded:
            state.final_response = (
                "🔍 **Informação Não Confirmada na Base Normativa**\n\n"
                "Não foi possível localizar fundamentação documental segura nos normativos "
                "para responder com precisão. Recomendamos consultar a equipe de compliance."
            )
        else:
            default_err = "Instabilidade transitória na consulta. Por favor, tente novamente."
            err_msg = state.error_message or default_err
            state.final_response = (
                f"ℹ️ **Não foi possível concluir a operação no momento**\n\n{err_msg}"
            )

        return state
