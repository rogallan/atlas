"""Router Node: Inspects inputs for injection and routes to proper intent (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep
from agent.guardrails.injection import PromptInjectionDetector
from agent.router.models import IntentResult, IntentType
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

        # 2. Fast-path lexical detection for standard banking keywords (0ms response)
        msg_low = state.user_message.lower()
        fast_intent: IntentType | None = None
        if any(w in msg_low for w in ["chamado", "contest", "tkn_", "confirmar", "cancelar"]):
            fast_intent = IntentType.ACTION
        elif any(w in msg_low for w in ["saldo", "extrato", "conta", "perfil", "transaç"]):
            fast_intent = IntentType.QUERY
        elif any(w in msg_low for w in ["simul", "empréstimo", "seguro", "consórcio"]):
            fast_intent = IntentType.SIMULATION
        elif any(w in msg_low for w in ["bacen", "cmn", "resolução", "saque"]):
            fast_intent = IntentType.KNOWLEDGE

        if fast_intent is not None:
            state.intent_decision = IntentResult(
                intent=fast_intent,
                confidence=0.95,
                reasoning="Classificação de alta confiança por fast-path bancário.",
            )
            logger.info(
                "Router node fast-path intent='%s' for session '%s'",
                fast_intent.value,
                state.session_id,
            )
            return state

        # 3. Intent Classification via LLM Router with timeout guard
        try:
            import asyncio

            decision = await asyncio.wait_for(
                self.router.route(state.user_message),
                timeout=5.0,
            )
        except Exception as exc:
            logger.warning("Router LLM timeout or error: %s. Using clarification.", exc)
            decision = IntentResult(
                intent=IntentType.CLARIFICATION,
                confidence=0.5,
                reasoning="Requisição ambígua ou modelo local lento.",
            )

        state.intent_decision = decision
        return state
