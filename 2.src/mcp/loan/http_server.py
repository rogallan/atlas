"""HTTP & SSE Transport Server for MCP Loan Server (S09).

Allows running the MCP Loan Server as a standalone network service on a port
(e.g., http://127.0.0.1:8002) supporting REST inspection and standard MCP JSON-RPC.

Usage:
    uv run python -m mcp.loan.http_server --port 8002
"""

import argparse
import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

import uvicorn
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from mcp.loan.models import MCPLoanError
from mcp.loan.server import LoanMCPServer, create_loan_server

logger = logging.getLogger("atlas.mcp.loan.http")

app = FastAPI(
    title="ATLAS MCP Loan Server",
    description=(
        "Model Context Protocol Server for Credit Simulation and Eligibility (Price, IOF, CET)"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_instance: LoanMCPServer = create_loan_server()


@app.get("/health")
def health() -> dict[str, Any]:
    """Healthcheck endpoint."""
    return {
        "status": "healthy",
        "service": "atlas-loan-mcp",
        "transport": ["stdio", "http", "sse"],
        "tools_count": len(server_instance.get_tool_definitions()),
    }


@app.get("/tools")
def list_tools() -> dict[str, Any]:
    """Convenience REST endpoint returning the catalog of available MCP loan tools."""
    return {"tools": server_instance.get_tool_definitions()}


@app.post("/tools/{tool_name}")
def call_tool_rest(
    tool_name: str,
    payload: dict[str, Any] = Body(default_factory=dict),  # noqa: B008
) -> dict[str, Any]:
    """Convenience REST endpoint to directly invoke any loan tool."""
    try:
        result = server_instance.execute_tool(name=tool_name, arguments=payload)
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
    except MCPLoanError as err:
        status_code = err.code if err.code in (401, 404, 422) else 400
        raise HTTPException(status_code=status_code, detail=err.message) from err
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err


@app.post("/mcp/jsonrpc")
def jsonrpc_endpoint(
    request: dict[str, Any] = Body(...),  # noqa: B008
) -> dict[str, Any]:
    """Standard JSON-RPC 2.0 endpoint for MCP clients."""
    response = server_instance.handle_jsonrpc(request)
    return response or {}


@app.get("/sse")
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
    parser = argparse.ArgumentParser(description="ATLAS MCP Loan HTTP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8002,
        help="Port to listen on (default: 8002)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(">>> ATLAS MCP Loan Server (HTTP / SSE Transport)")
    print(f"    URL:      http://{args.host}:{args.port}")
    print(f"    Tools:    http://{args.host}:{args.port}/tools")
    print(f"    Docs:     http://{args.host}:{args.port}/docs")
    print(f"    Health:   http://{args.host}:{args.port}/health")
    print("=" * 60 + "\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
