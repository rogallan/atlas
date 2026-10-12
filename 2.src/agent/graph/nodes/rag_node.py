"""RAG Node: Dispatches regulatory & knowledge queries to S07 RAG service (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep
from rag.retrieval.service import RAGRetrievalService

logger = logging.getLogger("atlas.agent.graph.rag_node")


class RAGNode:
    """Executes vector retrieval and grounded synthesis for knowledge inquiries."""

    def __init__(self, service: RAGRetrievalService | None = None) -> None:
        self.service = service or RAGRetrievalService()

    async def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("rag_node")
        state.current_step = AgentStep.RAG

        query = state.user_message.strip()
        logger.info("RAG node executing query for session '%s': '%s'", state.session_id, query)

        try:
            grounded = await self.service.retrieve_and_answer(query)
            # Store raw retrieved passages in state.retrieved_context
            state.retrieved_context = [
                {
                    "chunk_id": cit.chunk_id,
                    "title": cit.source_title,
                    "section": cit.section_title or "",
                    "quote": cit.excerpt,
                    "norm": cit.norm_reference or "",
                }
                for cit in grounded.citations
            ]

            # Store citations for downstream synthesis
            state.citations = [cit.model_dump() for cit in grounded.citations]

            # Register tool output
            state.tool_outputs.append(
                {
                    "tool": "rag_retrieval",
                    "answer": grounded.answer,
                    "has_sufficient_evidence": grounded.has_sufficient_evidence,
                    "confidence_score": grounded.confidence_score,
                    "disclaimer": grounded.disclaimer,
                }
            )

            # Check if evidence was sufficient
            state.is_grounded = grounded.has_sufficient_evidence

        except Exception as exc:
            logger.exception("Error executing RAG retrieval in session '%s'", state.session_id)
            state.error_message = f"Falha na consulta ao acervo regulatório: {exc}"
            state.is_grounded = False

        return state
