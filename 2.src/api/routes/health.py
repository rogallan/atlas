"""Health check endpoint for liveness and readiness probes (S03)."""

import time

from fastapi import APIRouter

from api.config import API_VERSION
from api.schemas import HealthResponse

router = APIRouter(tags=["Health"])
START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness and readiness health check",
    description="Returns current service status, API version, and runtime uptime in seconds.",
)
async def get_health() -> HealthResponse:
    uptime = max(0.0, round(time.time() - START_TIME, 2))
    return HealthResponse(
        status="ok",
        version=API_VERSION,
        uptime_seconds=uptime,
    )
