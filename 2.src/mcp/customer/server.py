"""Model Context Protocol (MCP) Customer Server implementation (S08)."""

import asyncio
import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.customer.auth import AuthContext, SecurityManager
from mcp.customer.models import (
    GetCustomerAccountsInput,
    GetCustomerProfileInput,
    GetCustomerSummaryInput,
    GetFinancialHistoryInput,
    MCPCustomerError,
)
from mcp.customer.repository import CustomerRepository
from mcp.customer.tools import CustomerTools

logger = logging.getLogger(__name__)

SERVER_NAME = "atlas-customer-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"


class CustomerMCPServer:
    """MCP Server exposing read-only customer tools over JSON-RPC 2.0."""

    def __init__(
        self,
        repository: CustomerRepository | None = None,
        security_manager: SecurityManager | None = None,
    ) -> None:
        """Initialize the MCP Customer Server.

        Args:
            repository: Optional repository adapter.
            security_manager: Optional security and audit manager.
        """
        self.tools = CustomerTools(
            repository=repository,
            security_manager=security_manager,
        )

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "get_customer_profile",
                "description": (
                    "Consulta o perfil cadastral sintético, segmento bancário, score de crédito "
                    "e classificação de risco de um cliente."
                ),
                "inputSchema": GetCustomerProfileInput.model_json_schema(),
            },
            {
                "name": "get_customer_accounts",
                "description": (
                    "Lista todas as contas correntes, poupanças e investimentos ativas de um "
                    "cliente com seus respectivos saldos em BRL."
                ),
                "inputSchema": GetCustomerAccountsInput.model_json_schema(),
            },
            {
                "name": "get_financial_history",
                "description": (
                    "Retorna o histórico cronológico de transações e eventos financeiros recentes "
                    "(Pix, parcelas de empréstimo, depósitos, etc.) de um cliente."
                ),
                "inputSchema": GetFinancialHistoryInput.model_json_schema(),
            },
            {
                "name": "get_customer_summary",
                "description": (
                    "Gera um briefing gerencial consolidado do cliente, agregando perfil, contas, "
                    "saldo total, contratos ativos e eventos recentes."
                ),
                "inputSchema": GetCustomerSummaryInput.model_json_schema(),
            },
        ]

    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        auth_context: AuthContext | None = None,
    ) -> Any:
        """Directly invoke a registered tool by name with parameter validation.

        Args:
            name: Tool name.
            arguments: Tool arguments dictionary.
            auth_context: Optional security credentials.

        Returns:
            Pydantic response model from the tool handler.

        Raises:
            ValueError: If tool name or arguments are invalid.
            MCPCustomerError: For domain exceptions (not found, unauthorized).
        """
        match name:
            case "get_customer_profile":
                params = GetCustomerProfileInput.model_validate(arguments)
                return self.tools.get_customer_profile(
                    customer_id=params.customer_id,
                    auth_context=auth_context,
                )
            case "get_customer_accounts":
                acc_params = GetCustomerAccountsInput.model_validate(arguments)
                return self.tools.get_customer_accounts(
                    customer_id=acc_params.customer_id,
                    auth_context=auth_context,
                )
            case "get_financial_history":
                hist_params = GetFinancialHistoryInput.model_validate(arguments)
                return self.tools.get_financial_history(
                    customer_id=hist_params.customer_id,
                    limit=hist_params.limit,
                    auth_context=auth_context,
                )
            case "get_customer_summary":
                sum_params = GetCustomerSummaryInput.model_validate(arguments)
                return self.tools.get_customer_summary(
                    customer_id=sum_params.customer_id,
                    auth_context=auth_context,
                )
            case _:
                raise ValueError(f"Ferramenta desconhecida: '{name}'")

    def handle_jsonrpc(
        self,
        request: dict[str, Any],
        auth_context: AuthContext | None = None,
    ) -> dict[str, Any] | None:
        """Handle incoming JSON-RPC 2.0 message according to MCP specification.

        Args:
            request: JSON-RPC request dictionary.
            auth_context: Operator authorization context.

        Returns:
            JSON-RPC response dictionary, or None for notifications.
        """
        method = request.get("method")
        msg_id = request.get("id")

        # Ignore notifications without id
        if method == "notifications/initialized":
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                },
            }

        if method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.get_tool_definitions()},
            }

        if method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})

            try:
                result_data = self.execute_tool(
                    name=tool_name,
                    arguments=tool_args,
                    auth_context=auth_context,
                )

                # Format payload as JSON text content
                if hasattr(result_data, "model_dump"):
                    payload_json = json.dumps(result_data.model_dump(), default=str)
                elif isinstance(result_data, list):
                    dumped = [
                        item.model_dump() if hasattr(item, "model_dump") else item
                        for item in result_data
                    ]
                    payload_json = json.dumps(dumped, default=str)
                else:
                    payload_json = json.dumps(result_data, default=str)

                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": payload_json}],
                        "isError": False,
                    },
                }

            except (ValidationError, ValueError) as err:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Erro de validação: {err}"}],
                        "isError": True,
                    },
                }
            except MCPCustomerError as err:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": err.message}],
                        "isError": True,
                    },
                }
            except Exception as err:
                logger.error(
                    "Unexpected error executing tool %s: %s",
                    tool_name,
                    err,
                    exc_info=True,
                )
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Erro interno: {err}"}],
                        "isError": True,
                    },
                }

        # Unknown method
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Método não encontrado: '{method}'",
            },
        }

    async def run_stdio(self) -> None:
        """Run standard stdio event loop processing JSON-RPC messages line-by-line."""
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break

            text = line.decode("utf-8").strip()
            if not text:
                continue

            try:
                req_obj = json.loads(text)
                resp_obj = self.handle_jsonrpc(req_obj)
                if resp_obj is not None:
                    sys.stdout.write(json.dumps(resp_obj) + "\n")
                    sys.stdout.flush()
            except Exception as exc:
                logger.error("Failed processing stdio request: %s", exc)


def create_customer_server() -> CustomerMCPServer:
    """Factory helper creating configured CustomerMCPServer instance."""
    return CustomerMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = create_customer_server()
    asyncio.run(server.run_stdio())
