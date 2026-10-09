"""MCP Ticket Server exposing JSON-RPC 2.0 stdio protocol (S13)."""

import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.ticket.models import (
    ConfirmAndCreateTicketInput,
    GetTicketInput,
    ListCustomerTicketsInput,
    MCPTicketError,
    PrepareTicketInput,
)
from mcp.ticket.tools import TicketTools

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "atlas-mcp-ticket"
SERVER_VERSION = "1.0.0"


class TicketMCPServer:
    """Model Context Protocol server for customer service ticket lifecycle management."""

    def __init__(self, tools: TicketTools | None = None) -> None:
        self.tools = tools or TicketTools()

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "prepare_ticket",
                "description": (
                    "Fase 1 (Human-in-the-Loop): Valida os dados da solicitação, cria um rascunho "
                    "de chamado pendente e gera um confirmation_token criptográfico de uso único "
                    "com TTL de 10 minutos. Nenhuma alteração definitiva ocorre nesta etapa."
                ),
                "inputSchema": PrepareTicketInput.model_json_schema(),
            },
            {
                "name": "confirm_and_create_ticket",
                "description": (
                    "Fase 2 (Human-in-the-Loop): Executa a abertura definitiva do chamado bancário "
                    "apenas mediante aprovação humana explícita (approved_by_user=True). Requer "
                    "token válido, não expirado e não utilizado. Suporta chave de idempotência."
                ),
                "inputSchema": ConfirmAndCreateTicketInput.model_json_schema(),
            },
            {
                "name": "get_ticket",
                "description": (
                    "Consulta os detalhes, status de resolução, operador responsável e histórico "
                    "de um chamado de atendimento a partir do ticket_id."
                ),
                "inputSchema": GetTicketInput.model_json_schema(),
            },
            {
                "name": "list_customer_tickets",
                "description": (
                    "Lista todos os chamados de atendimento associados a um determinado cliente, "
                    "ordenados do mais recente para o mais antigo."
                ),
                "inputSchema": ListCustomerTicketsInput.model_json_schema(),
            },
        ]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Directly invoke a registered tool by name with parameter validation."""
        try:
            if name == "prepare_ticket":
                inp = PrepareTicketInput(**arguments)
                return self.tools.prepare_ticket(
                    customer_id=inp.customer_id,
                    category=inp.category,
                    title=inp.title,
                    description=inp.description,
                    priority=inp.priority,
                    operator_id=inp.operator_id,
                    idempotency_key=inp.idempotency_key,
                )
            elif name == "confirm_and_create_ticket":
                inp_confirm = ConfirmAndCreateTicketInput(**arguments)
                return self.tools.confirm_and_create_ticket(
                    confirmation_token=inp_confirm.confirmation_token,
                    approved_by_user=inp_confirm.approved_by_user,
                    idempotency_key=inp_confirm.idempotency_key,
                    operator_id=inp_confirm.operator_id,
                )
            elif name == "get_ticket":
                inp_get = GetTicketInput(**arguments)
                return self.tools.get_ticket(ticket_id=inp_get.ticket_id)
            elif name == "list_customer_tickets":
                inp_list = ListCustomerTicketsInput(**arguments)
                return self.tools.list_customer_tickets(customer_id=inp_list.customer_id)
            else:
                raise MCPTicketError(f"Unknown tool: '{name}'", code=-32601)
        except ValidationError as e:
            raise MCPTicketError(
                f"Validation error: {e}",
                code=-32602,
                data={"errors": e.errors(include_url=False)},
            ) from e

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process incoming JSON-RPC 2.0 request and generate compliant response."""
        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if request.get("jsonrpc") != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Invalid JSON-RPC request"},
            }

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "version": SERVER_VERSION,
                        },
                        "capabilities": {"tools": {}},
                    },
                }

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_tool_definitions()},
                }

            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = self.execute_tool(tool_name, arguments)

                if isinstance(result, list):
                    dumped = [
                        item.model_dump(mode="json")
                        if hasattr(item, "model_dump")
                        else item
                        for item in result
                    ]
                elif hasattr(result, "model_dump"):
                    dumped = result.model_dump(mode="json")
                else:
                    dumped = result

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(dumped, ensure_ascii=False, indent=2),
                            }
                        ]
                    },
                }

            elif method == "ping":
                return {"jsonrpc": "2.0", "id": req_id, "result": {}}

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: '{method}'"},
                }

        except MCPTicketError as err:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": err.code,
                    "message": err.message,
                    "data": err.data,
                },
            }
        except Exception as exc:
            logger.exception("Unexpected error processing JSON-RPC request")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": f"Internal error: {exc}"},
            }

    def run_stdio(self) -> None:
        """Run the MCP server in stdio mode, processing JSON-RPC lines from stdin."""
        logger.info("Starting %s v%s stdio transport...", SERVER_NAME, SERVER_VERSION)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error: Invalid JSON"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def create_ticket_server(tools: TicketTools | None = None) -> TicketMCPServer:
    """Factory creating configured TicketMCPServer instance."""
    return TicketMCPServer(tools=tools)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_ticket_server().run_stdio()
