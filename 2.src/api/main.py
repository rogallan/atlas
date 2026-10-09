"""FastAPI Gateway main application entrypoint (S03)."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import (
    ALLOWED_ORIGINS,
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
)
from api.routes.chat import router as chat_router
from api.routes.customers import router as customers_router
from api.routes.health import router as health_router
from api.routes.sessions import router as sessions_router
from api.schemas import ErrorDetail, ErrorEnvelope


def create_app() -> FastAPI:
    """Build and configure the FastAPI Gateway application."""
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # 1. CORS & ngrok integration middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Session-ID",
            "ngrok-skip-browser-warning",
        ],
        expose_headers=["Content-Type"],
    )

    # 2. Standardized error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        detail: Any = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code", "HTTP_ERROR"))
            message = str(detail.get("message", detail))
            details = detail.get("details")
        else:
            code = "HTTP_ERROR"
            message = str(detail)
            details = None

        envelope = ErrorEnvelope(error=ErrorDetail(code=code, message=message, details=details))
        return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid request payload structure or parameters.",
                details=exc.errors(),
            )
        )
        status_code = getattr(
            status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return JSONResponse(
            status_code=status_code,
            content=envelope.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred.",
                details=str(exc) if app.debug else None,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=envelope.model_dump(),
        )

    # 3. Register route blueprints
    app.include_router(health_router)
    app.include_router(sessions_router)
    app.include_router(chat_router)
    app.include_router(customers_router)

    return app


app = create_app()
