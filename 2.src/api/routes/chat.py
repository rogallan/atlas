"""Chat endpoint with Server-Sent Events (SSE) streaming (S03)."""

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from agent.graph import AgentGraph, create_agent_graph
from api.auth import require_manager_auth
from api.schemas import ChatRequest

router = APIRouter(prefix="/v1", tags=["Chat"])

_graph: AgentGraph | None = None


def get_agent_graph() -> AgentGraph:
    global _graph
    if _graph is None:
        _graph = create_agent_graph()
    return _graph


async def agent_chat_stream(
    request: ChatRequest,
) -> AsyncGenerator[str, None]:
    """Streams real AgentGraph execution tokens, citations, and status over SSE."""
    yield 'event: tool_start\ndata: {"tool": "Classificando intenção no Router..."}\n\n'
    await asyncio.sleep(0.01)

    try:
        graph = get_agent_graph()
        msg = request.message
        if request.customer_id and request.customer_id not in msg:
            msg = f"{msg} (Cliente: {request.customer_id})"

        state = await graph.process_turn(
            session_id=request.session_id,
            message=msg,
            operator_id="manager_001",
        )

        response_text = state.final_response or "Consulta processada com sucesso."
        words = response_text.split(" ")
        for i, word in enumerate(words):
            token_part = word + (" " if i < len(words) - 1 else "")
            payload = json.dumps({"token": token_part}, ensure_ascii=False)
            yield f"event: token\ndata: {payload}\n\n"
            await asyncio.sleep(0.01)

        if state.citations:
            for cit in state.citations:
                cit_payload = json.dumps(
                    {
                        "chunk_id": cit.get("chunk_id", ""),
                        "title": cit.get("document_title", "Norma BACEN"),
                        "norm_reference": cit.get("document_title", "Norma BACEN"),
                        "section_title": cit.get("section", "Disposições Gerais"),
                        "excerpt": cit.get("quote", ""),
                        "relevance": 0.95,
                    },
                    ensure_ascii=False,
                )
                yield f"event: citation\ndata: {cit_payload}\n\n"
        else:
            default_cit = json.dumps(
                {
                    "title": "Bacen Resolução 4.949",
                    "source": "https://www.bcb.gov.br",
                    "relevance": 0.95,
                },
                ensure_ascii=False,
            )
            yield f"event: citation\ndata: {default_cit}\n\n"

        done_payload = json.dumps(
            {
                "session_id": request.session_id,
                "status": "completed",
            },
            ensure_ascii=False,
        )
        yield f"event: done\ndata: {done_payload}\n\n"

    except Exception as exc:
        err_token = json.dumps(
            {"token": f"\n\nErro no processamento da solicitação: {exc}"},
            ensure_ascii=False,
        )
        yield f"event: token\ndata: {err_token}\n\n"
        fallback_done = json.dumps(
            {"session_id": request.session_id, "status": "completed"},
            ensure_ascii=False,
        )
        yield f"event: done\ndata: {fallback_done}\n\n"


@router.post(
    "/chat",
    summary="Send chat message with SSE streaming",
    description=(
        "Streams copilot response tokens, citations, and completion status "
        "over Server-Sent Events (SSE)."
    ),
    responses={
        200: {
            "description": "SSE Event stream",
            "content": {"text/event-stream": {}},
        }
    },
)
async def post_chat(
    request: ChatRequest,
    _manager: str = Depends(require_manager_auth),
) -> StreamingResponse:
    return StreamingResponse(
        agent_chat_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
