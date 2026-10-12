"""Clarification Node: Formulates polite follow-up questions for ambiguous prompts (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep

logger = logging.getLogger("atlas.agent.graph.clarification_node")


class ClarificationNode:
    """Interacts with the operator when request lacks critical banking entities or context."""

    def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("clarification_node")
        state.current_step = AgentStep.CLARIFICATION

        reasoning = (
            state.intent_decision.reasoning
            if state.intent_decision
            else "A solicitação necessita de parâmetros adicionais."
        )

        prompt_clarification = (
            "Compreendi a sua solicitação, mas preciso de informações complementares:\n\n"
            f"📌 **Contexto:** {reasoning}\n\n"
            "Poderia informar, por favor:\n"
            "- O identificador do cliente (ex.: `CUST-001`); e/ou\n"
            "- A modalidade bancária (crédito, consórcio, seguro, tarifa) e valor pretendido?"
        )

        state.final_response = prompt_clarification
        logger.info(
            "Clarification node asked follow-up for session '%s'",
            state.session_id,
        )

        return state
