"""Agent Graph orchestrator compiling nodes, edges, and state machine lifecycle (S14)."""

import inspect
import logging
from typing import cast

from agent.graph.edges import (
    route_from_mcp,
    route_from_rag,
    route_from_router,
    route_from_validator,
)
from agent.graph.nodes import (
    ClarificationNode,
    FallbackNode,
    MCPNode,
    RAGNode,
    RouterNode,
    SynthesizerNode,
    ValidatorNode,
)
from agent.graph.state import AgentState, AgentStep

logger = logging.getLogger("atlas.agent.graph.orchestrator")


class AgentGraph:
    """Stateful Agent Graph coordinating conversation turns across RAG and MCP servers."""

    def __init__(
        self,
        router_node: RouterNode | None = None,
        rag_node: RAGNode | None = None,
        mcp_node: MCPNode | None = None,
        clarification_node: ClarificationNode | None = None,
        validator_node: ValidatorNode | None = None,
        synthesizer_node: SynthesizerNode | None = None,
        fallback_node: FallbackNode | None = None,
    ) -> None:
        self.router_node = router_node or RouterNode()
        self.rag_node = rag_node or RAGNode()
        self.mcp_node = mcp_node or MCPNode()
        self.clarification_node = clarification_node or ClarificationNode()
        self.validator_node = validator_node or ValidatorNode()
        self.synthesizer_node = synthesizer_node or SynthesizerNode()
        self.fallback_node = fallback_node or FallbackNode()

    async def _execute_node(self, node: object, state: AgentState) -> AgentState:
        """Execute a node handler supporting both synchronous and asynchronous callables."""
        if callable(node):
            if inspect.iscoroutinefunction(node.__call__):
                res = await node(state)
            else:
                res = node(state)
            return cast(AgentState, res)
        raise TypeError(f"Node '{node}' is not callable.")

    async def process_turn(
        self,
        session_id: str,
        message: str,
        history: list[dict[str, str]] | None = None,
        operator_id: str = "manager_001",
        max_steps: int = 5,
    ) -> AgentState:
        """Execute a complete conversational turn through the compiled state graph.

        Args:
            session_id: Unique chat session ID.
            message: User/operator message.
            history: Previous messages list.
            operator_id: Identifier of relationship manager.
            max_steps: Maximum step limit to prevent infinite loops.

        Returns:
            Final AgentState containing synthesized response, citations, or confirmation cards.
        """
        state = AgentState(
            session_id=session_id,
            user_message=message,
            history=history or [],
            operator_id=operator_id,
            max_steps=max_steps,
        )

        logger.info(
            "AgentGraph starting turn for session '%s' with max_steps=%d",
            session_id,
            max_steps,
        )

        # 1. Initial Step: Router Node
        state = await self._execute_node(self.router_node, state)
        next_step = route_from_router(state)

        # 2. State Machine Loop
        while next_step != AgentStep.END:
            # Enforce step limit
            if state.step_count >= state.max_steps and next_step != AgentStep.FALLBACK:
                logger.warning(
                    "Step limit reached (%d/%d) in session '%s', forcing FallbackNode",
                    state.step_count,
                    state.max_steps,
                    session_id,
                )
                next_step = AgentStep.FALLBACK

            if next_step == AgentStep.RAG:
                state = await self._execute_node(self.rag_node, state)
                next_step = route_from_rag(state)

            elif next_step == AgentStep.MCP:
                state = await self._execute_node(self.mcp_node, state)
                next_step = route_from_mcp(state)

            elif next_step == AgentStep.CLARIFICATION:
                state = await self._execute_node(self.clarification_node, state)
                next_step = AgentStep.END

            elif next_step == AgentStep.VALIDATOR:
                state = await self._execute_node(self.validator_node, state)
                next_step = route_from_validator(state)

            elif next_step == AgentStep.SYNTHESIZER:
                state = await self._execute_node(self.synthesizer_node, state)
                next_step = AgentStep.END

            elif next_step == AgentStep.FALLBACK:
                state = await self._execute_node(self.fallback_node, state)
                next_step = AgentStep.END

            else:
                logger.error(
                    "Unknown next step '%s' encountered in session '%s'",
                    next_step,
                    session_id,
                )
                state = await self._execute_node(self.fallback_node, state)
                next_step = AgentStep.END

        logger.info(
            "AgentGraph finished turn for session '%s': %d steps, nodes visited: %s",
            session_id,
            state.step_count,
            " -> ".join(state.node_history),
        )

        return state


def create_agent_graph() -> AgentGraph:
    """Factory creating fully wired AgentGraph instance."""
    return AgentGraph()
