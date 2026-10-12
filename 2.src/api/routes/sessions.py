"""Session management endpoint (S03)."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status

from api.auth import require_manager_auth
from api.schemas import CreateSessionRequest, SessionResponse

router = APIRouter(prefix="/v1", tags=["Sessions"])


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversational session",
    description="Initializes a new correlated conversation session for the relationship manager.",
)
async def create_session(
    payload: CreateSessionRequest | None = None,
    manager_id: str = Depends(require_manager_auth),
) -> SessionResponse:
    session_id = str(uuid.uuid4())
    now_iso = datetime.now(UTC).isoformat()
    effective_manager_id = payload.manager_id if payload else manager_id

    return SessionResponse(
        session_id=session_id,
        created_at=now_iso,
        manager_id=effective_manager_id,
    )
