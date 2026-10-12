"""FastAPI observability middleware for correlation propagation, metrics, and logs (S19)."""

import time

from fastapi import APIRouter, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse

from ops.context import correlation_context
from ops.logger import get_logger
from ops.metrics import get_prometheus_metrics, record_http_request

logger = get_logger("gateway")
metrics_router = APIRouter(tags=["Observability"])


@metrics_router.get("/metrics", summary="Export Prometheus metrics")
async def prometheus_metrics() -> Response:
    """Expose application metrics in Prometheus text exposition format."""
    payload, content_type = get_prometheus_metrics()
    return Response(content=payload, media_type=content_type)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware capturing request timing, correlating trace contexts, and recording metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        correlation_id = request.headers.get("x-correlation-id") or request.headers.get(
            "X-Correlation-ID"
        )
        session_id = request.headers.get("x-session-id") or request.headers.get("X-Session-ID")

        with correlation_context(correlation_id=correlation_id, session_id=session_id) as (
            cid,
            sid,
        ):
            start_time = time.perf_counter()
            path = request.url.path
            method = request.method

            try:
                response = await call_next(request)
                duration = time.perf_counter() - start_time
                status_code = response.status_code

                # Inject correlation ID into response headers
                response.headers["X-Correlation-ID"] = cid

                # Record Prometheus metrics (skip scraping /metrics itself to avoid recursion)
                if path != "/metrics":
                    record_http_request(
                        method=method,
                        endpoint=path,
                        status_code=status_code,
                        duration_seconds=duration,
                    )
                    logger.info(
                        "HTTP request completed",
                        method=method,
                        path=path,
                        status_code=status_code,
                        duration_ms=round(duration * 1000, 2),
                    )

                return response

            except Exception as exc:
                duration = time.perf_counter() - start_time
                record_http_request(
                    method=method,
                    endpoint=path,
                    status_code=500,
                    duration_seconds=duration,
                )
                logger.error(
                    "HTTP request failed with unhandled exception",
                    method=method,
                    path=path,
                    error=str(exc),
                    duration_ms=round(duration * 1000, 2),
                )
                raise
