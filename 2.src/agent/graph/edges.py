"""Conditional routing edge functions for Agent Graph state machine (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep
from agent.router.models import IntentType

logger = logging.getLogger("atlas.agent.graph.edges")


def route_from_router(state: AgentState) -> AgentStep:
    """Determine next node after Router Node evaluation."""
    if state.security_blocked:
        return AgentStep.FALLBACK

    if state.step_count >= state.max_steps:
        return AgentStep.FALLBACK

    if not state.intent_decision:
        return AgentStep.FALLBACK

    intent = state.intent_decision.intent
    if intent == IntentType.KNOWLEDGE:
        return AgentStep.RAG
    if intent in (IntentType.QUERY, IntentType.SIMULATION, IntentType.ACTION):
        return AgentStep.MCP
    return AgentStep.CLARIFICATION


def route_from_rag(state: AgentState) -> AgentStep:
    """Route from RAG retrieval to Validator/Critic node."""
    if state.step_count >= state.max_steps:
        return AgentStep.FALLBACK
    return AgentStep.VALIDATOR


def route_from_mcp(state: AgentState) -> AgentStep:
    """Route from MCP domain tools to Validator/Critic node."""
    if state.step_count >= state.max_steps:
        return AgentStep.FALLBACK
    return AgentStep.VALIDATOR


def route_from_validator(state: AgentState) -> AgentStep:
    """Route from Validator node based on compliance, grounding, and HITL state."""
    if state.step_count >= state.max_steps:
        return AgentStep.FALLBACK

    if state.security_blocked:
        return AgentStep.FALLBACK

    if not state.is_grounded:
        return AgentStep.FALLBACK

    return AgentStep.SYNTHESIZER


def route_from_terminal(state: AgentState) -> AgentStep:
    """Terminal routing function marking completion."""
    return AgentStep.END
