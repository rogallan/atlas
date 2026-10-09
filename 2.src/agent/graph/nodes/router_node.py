"""Router Node: Inspects inputs for injection and routes to proper intent (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep
from agent.guardrails.injection import PromptInjectionDetector
from agent.router.models import IntentType
from agent.router.router import IntentRouter

logger = logging.getLogger("atlas.agent.graph.router_node")


class RouterNode:
    """Evaluates security guardrails and delegates to S05 Intent Router."""

    def __init__(
        self,
        router: IntentRouter | None = None,
        injection_detector: PromptInjectionDetector | None = None,
    ) -> None:
        self.router = router or IntentRouter()
        self.injection_detector = injection_detector or PromptInjectionDetector()

    async def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("router_node")
        state.current_step = AgentStep.ROUTER

        # 1. Prompt Injection & Jailbreak Guardrail check
        is_suspicious, reason = self.injection_detector.check_input(state.user_message)
        if is_suspicious:
            logger.warning(
                "Security guardrail triggered on session '%s': %s",
                state.session_id,
                reason,
            )
            state.security_blocked = True
            state.error_message = reason
            return state

        # 2. Intent Classification via S05 Intent Router
        decision = await self.router.route(state.user_message)

        # Fallback to lexical heuristics if LLM was unavailable (confidence == 0.0)
        if decision.confidence == 0.0:
            msg_low = state.user_message.lower()
            if any(w in msg_low for w in ["chamado", "contest", "tkn_", "confirmar", "cancelar"]):
                decision.intent = IntentType.ACTION
                decision.confidence = 0.85
            elif any(w in msg_low for w in ["saldo", "extrato", "conta", "perfil", "transaç"]):
                decision.intent = IntentType.QUERY
                decision.confidence = 0.85
            elif any(w in msg_low for w in ["simul", "empréstimo", "seguro", "consórcio"]):
                decision.intent = IntentType.SIMULATION
                decision.confidence = 0.85
            elif any(w in msg_low for w in ["bacen", "cmn", "resolução", "saque"]):
                decision.intent = IntentType.KNOWLEDGE
                decision.confidence = 0.85

        state.intent_decision = decision
        logger.info(
            "Router node classified intent='%s' (conf=%.2f) for session '%s'",
            decision.intent.value,
            decision.confidence,
            state.session_id,
        )

        return state
