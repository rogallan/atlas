"""Chat endpoint with Server-Sent Events (SSE) streaming (S03)."""

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.auth import require_manager_auth
from api.schemas import ChatRequest

router = APIRouter(prefix="/v1", tags=["Chat"])


async def simulated_chat_stream(
    request: ChatRequest,
) -> AsyncGenerator[str, None]:
    """Generates simulated streaming SSE chunks for S03 before agent integration (S05/S14)."""
    context_prefix = (
        f"Contexto do cliente {request.customer_id} carregado. " if request.customer_id else ""
    )

    sample_tokens = [
        "Olá, ",
        "gerente! ",
        context_prefix,
        "Recebi sua mensagem: ",
        f'"{request.message}". ',
        "Estou processando ",
        "a consulta através ",
        "do Gateway FastAPI ",
        "do ATLAS.",
    ]

    for token in sample_tokens:
        if token:
            payload = json.dumps({"token": token}, ensure_ascii=False)
            yield f"event: token\ndata: {payload}\n\n"
            await asyncio.sleep(0.02)

    citation_payload = json.dumps(
        {
            "title": "Bacen Resolução 4.949",
            "source": "https://www.bcb.gov.br",
            "relevance": 0.95,
        },
        ensure_ascii=False,
    )
    yield f"event: citation\ndata: {citation_payload}\n\n"
    await asyncio.sleep(0.01)

    done_payload = json.dumps(
        {
            "session_id": request.session_id,
            "status": "completed",
        },
        ensure_ascii=False,
    )
    yield f"event: done\ndata: {done_payload}\n\n"


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
        simulated_chat_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
