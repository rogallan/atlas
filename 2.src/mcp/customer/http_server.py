"""HTTP & SSE Transport Server for MCP Customer Server (S08).

Allows running the MCP Customer Server as a standalone network service on a port
(e.g., http://127.0.0.1:8001) supporting REST inspection and standard MCP JSON-RPC.

Usage:
    uv run python -m mcp.customer.http_server --port 8001
"""

import argparse
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from mcp.customer.auth import AuthContext
from mcp.customer.models import MCPCustomerError
from mcp.customer.server import CustomerMCPServer, create_customer_server

logger = logging.getLogger("atlas.mcp.customer.http")

app = FastAPI(
    title="ATLAS MCP Customer Server",
    description="Model Context Protocol Server for Synthetic Banking Customer Queries",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared in-process server instance
server_instance: CustomerMCPServer = create_customer_server()


@app.get("/health")
def health() -> dict[str, Any]:
    """Healthcheck endpoint."""
    return {
        "status": "healthy",
        "service": "atlas-customer-mcp",
        "transport": ["stdio", "http", "sse"],
        "tools_count": len(server_instance.get_tool_definitions()),
    }


@app.get("/tools")
def list_tools() -> dict[str, Any]:
    """Convenience REST endpoint returning the catalog of available MCP tools."""
    return {"tools": server_instance.get_tool_definitions()}


@app.post("/tools/{tool_name}")
def call_tool_rest(
    tool_name: str,
    payload: dict[str, Any] = Body(default_factory=dict),  # noqa: B008
    operator_id: str = Query("OP-HTTP-USER", description="Simulated operator ID"),  # noqa: B008
    role: str = Query("relationship_manager", description="Simulated operator role"),  # noqa: B008
) -> dict[str, Any]:
    """Convenience REST endpoint to directly invoke any customer tool."""
    auth_ctx = AuthContext(operator_id=operator_id, role=role)
    try:
        result = server_instance.execute_tool(
            name=tool_name,
            arguments=payload,
            auth_context=auth_ctx,
        )
        if hasattr(result, "model_dump"):
            return {"result": result.model_dump()}
        if isinstance(result, list):
            return {
                "result": [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in result
                ]
            }
        return {"result": result}
    except MCPCustomerError as err:
        status_code = err.code if err.code in (401, 404) else 400
        raise HTTPException(status_code=status_code, detail=err.message) from err
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


@app.post("/mcp/jsonrpc")
def jsonrpc_endpoint(
    request: dict[str, Any] = Body(...),  # noqa: B008
    operator_id: str = Query("OP-MCP-CLIENT"),  # noqa: B008
    role: str = Query("relationship_manager"),  # noqa: B008
) -> dict[str, Any]:
    """Standard JSON-RPC 2.0 endpoint for MCP clients."""
    auth_ctx = AuthContext(operator_id=operator_id, role=role)
    response = server_instance.handle_jsonrpc(request, auth_context=auth_ctx)
    return response or {}


@app.get("/sse")
async def sse_endpoint() -> StreamingResponse:
    """Server-Sent Events (SSE) transport endpoint conforming to MCP specification."""
    session_id = str(uuid.uuid4())

    async def event_generator() -> AsyncIterator[str]:
        # 1. Send endpoint event notifying client where to post messages
        yield f"event: endpoint\ndata: /mcp/jsonrpc?session_id={session_id}\n\n"
        # 2. Keep connection open with heartbeat comment
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
    parser = argparse.ArgumentParser(description="ATLAS MCP Customer HTTP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(">>> ATLAS MCP Customer Server (HTTP / SSE Transport)")
    print(f"    URL:      http://{args.host}:{args.port}")
    print(f"    Tools:    http://{args.host}:{args.port}/tools")
    print(f"    Docs:     http://{args.host}:{args.port}/docs")
    print(f"    Health:   http://{args.host}:{args.port}/health")
    print("=" * 60 + "\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
