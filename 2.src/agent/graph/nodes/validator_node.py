"""Validator / Critic Node: Enforces grounding, policy guardrails, and HITL action controls."""

import logging
import re
from typing import ClassVar

from agent.graph.state import AgentState, AgentStep
from agent.router.models import IntentType

logger = logging.getLogger("atlas.agent.graph.validator_node")


class ValidatorNode:
    """Evaluates candidate outputs against factual evidence, HITL policies, and compliance rules."""

    POLICY_FORBIDDEN_TERMS: ClassVar[list[str]] = [
        r"\bprometo\s+rentabilidade\b",
        r"\bgarantia\s+de\s+lucro\b",
        r"\bcriptomoeda\b",
        r"\bpirâmide\b",
        r"\bespeculação\s+agressiva\b",
    ]

    def __init__(self) -> None:
        self._compiled_policy_rules = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.POLICY_FORBIDDEN_TERMS
        ]

    def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("validator_node")
        state.current_step = AgentStep.VALIDATOR

        # 1. Policy & Compliance Check
        for regex in self._compiled_policy_rules:
            if regex.search(state.user_message):
                logger.warning(
                    "Policy rule triggered on session '%s': matched pattern '%s'",
                    state.session_id,
                    regex.pattern,
                )
                state.error_message = (
                    "Solicitação bloqueada pela conformidade bancária: "
                    "não são permitidas promessas de rentabilidade ou ativos não regulados."
                )
                state.security_blocked = True
                return state

        # 2. Grounding Verification (for Knowledge intents)
        if state.intent_decision and state.intent_decision.intent == IntentType.KNOWLEDGE:
            has_evidence = False
            for out in state.tool_outputs:
                if out.get("tool") == "rag_retrieval" and out.get("has_sufficient_evidence"):
                    has_evidence = True
                    break

            if not has_evidence and not state.retrieved_context:
                logger.warning(
                    "Validator detected ungrounded knowledge response for session '%s'",
                    state.session_id,
                )
                state.is_grounded = False
                state.error_message = (
                    "Não foram localizadas evidências suficientes no acervo regulatório "
                    "para fundamentar uma resposta precisa e fidedigna."
                )
                return state

        # 3. Action Check (Human-in-the-Loop Guardrail)
        if state.requires_human_confirmation:
            logger.info(
                "Validator confirmed HITL interception for session '%s'",
                state.session_id,
            )

        logger.info(
            "Validator passed for session '%s' (grounded=%s, requires_hitl=%s)",
            state.session_id,
            state.is_grounded,
            state.requires_human_confirmation,
        )

        return state
