"""Standalone HTTP and Server-Sent Events (SSE) server for MCP Consortium Server (S11)."""

import argparse
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

import uvicorn
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from mcp.consortium.models import MCPConsortiumError
from mcp.consortium.server import ConsortiumMCPServer, create_consortium_server

logger = logging.getLogger("atlas.mcp.consortium.http")

app = FastAPI(
    title="ATLAS MCP Consortium Server",
    description="Model Context Protocol Server for Consortium Exploration & Quota Simulation (S11)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_instance: ConsortiumMCPServer = create_consortium_server()


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Health check endpoint confirming consortium service availability."""
    return {"status": "ok", "service": "atlas-mcp-consortium", "version": "1.0.0"}


@app.get("/tools", tags=["MCP Tools"])
def list_available_tools() -> dict[str, Any]:
    """Return list of advertised MCP tools with JSON schemas."""
    return {"tools": server_instance.get_tool_definitions()}


@app.post("/tools/{tool_name}", tags=["MCP Tools"])
def call_tool_rest(
    tool_name: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Direct REST invocation of an MCP consortium tool."""
    args = payload or {}
    try:
        result = server_instance.execute_tool(tool_name, args)
        if isinstance(result, list):
            return {
                "result": [
                    item.model_dump() if hasattr(item, "model_dump") else item for item in result
                ]
            }
        if hasattr(result, "model_dump"):
            return {"result": result.model_dump()}
        return {"result": result}
    except MCPConsortiumError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": exc.message}
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error executing tool %s via REST", tool_name)
        raise HTTPException(status_code=500, detail={"code": -32603, "message": str(exc)}) from exc


@app.post("/mcp/jsonrpc", tags=["MCP JSON-RPC"])
def jsonrpc_endpoint(
    request: dict[str, Any] = Body(...),  # noqa: B008
) -> dict[str, Any]:
    """Standard JSON-RPC 2.0 endpoint for MCP clients."""
    return server_instance.handle_request(request)


@app.get("/sse", tags=["MCP SSE"])
async def sse_endpoint() -> StreamingResponse:
    """Server-Sent Events (SSE) transport endpoint conforming to MCP specification."""
    session_id = str(uuid.uuid4())

    async def event_generator() -> AsyncIterator[str]:
        yield f"event: endpoint\ndata: /mcp/jsonrpc?session_id={session_id}\n\n"
        yield f": connected session {session_id}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def main() -> None:
    """CLI launcher for the HTTP / SSE server."""
    parser = argparse.ArgumentParser(description="Run ATLAS MCP Consortium Server via HTTP / SSE")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=8004, help="Port to listen on (default: 8004)"
    )
    args = parser.parse_args()

    banner = f"""
============================================================
>>> ATLAS MCP Consortium Server (HTTP / SSE Transport)
    URL:      http://{args.host}:{args.port}
    Tools:    http://{args.host}:{args.port}/tools
    Docs:     http://{args.host}:{args.port}/docs
    Health:   http://{args.host}:{args.port}/health
============================================================
"""
    print(banner)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
