"""Model Context Protocol (MCP) Loan Server implementation (S09)."""

import asyncio
import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.customer.repository import CustomerRepository
from mcp.loan.models import (
    CheckLoanPreConditionsInput,
    MCPLoanError,
    SimulateLoanInput,
)
from mcp.loan.tools import LoanTools

logger = logging.getLogger(__name__)

SERVER_NAME = "atlas-loan-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"


class LoanMCPServer:
    """MCP Server exposing loan simulation and eligibility tools over JSON-RPC 2.0."""

    def __init__(self, customer_repository: CustomerRepository | None = None) -> None:
        """Initialize the Loan MCP Server.

        Args:
            customer_repository: Optional repository adapter for customer data.
        """
        self.tools = LoanTools(customer_repository=customer_repository)

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "simulate_loan",
                "description": (
                    "Simula cenários de crédito (Crédito Pessoal/CDC, Consignado, Capital "
                    "de Giro) calculando parcelas fixas (Tabela Price), juros totais, "
                    "IOF estimado, CET anual e amortização, incluindo disclaimer "
                    "não-vinculante obrigatório."
                ),
                "inputSchema": SimulateLoanInput.model_json_schema(),
            },
            {
                "name": "get_loan_modalities",
                "description": (
                    "Consulta o catálogo de modalidades de crédito ativas com suas faixas de valor "
                    "(mínimo e máximo), prazos em meses, taxas de juros de referência e limites "
                    "de margem."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "check_loan_pre_conditions",
                "description": (
                    "Avalia o comprometimento de renda (margem consignável ou pessoal) de um "
                    "cliente sintético frente a uma parcela mensal proposta para uma modalidade "
                    "de crédito."
                ),
                "inputSchema": CheckLoanPreConditionsInput.model_json_schema(),
            },
        ]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Directly invoke a registered tool by name with parameter validation.

        Args:
            name: Tool name.
            arguments: Tool arguments dictionary.

        Returns:
            Pydantic response model from the tool handler.

        Raises:
            ValueError: If tool name or arguments are invalid.
            MCPLoanError: For domain exceptions (not found, parameter limits).
        """
        match name:
            case "simulate_loan":
                params = SimulateLoanInput.model_validate(arguments)
                return self.tools.simulate_loan(
                    customer_id=params.customer_id,
                    amount=params.amount,
                    term_months=params.term_months,
                    modality=params.modality,
                )
            case "get_loan_modalities":
                return self.tools.get_loan_modalities()
            case "check_loan_pre_conditions":
                check_params = CheckLoanPreConditionsInput.model_validate(arguments)
                return self.tools.check_loan_pre_conditions(
                    customer_id=check_params.customer_id,
                    monthly_installment=check_params.monthly_installment,
                    modality=check_params.modality,
                )
            case _:
                raise ValueError(f"Ferramenta desconhecida: '{name}'")

    def handle_jsonrpc(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Handle incoming JSON-RPC 2.0 message according to MCP specification.

        Args:
            request: JSON-RPC request dictionary.

        Returns:
            JSON-RPC response dictionary, or None for notifications.
        """
        method = request.get("method")
        msg_id = request.get("id")

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
                result_data = self.execute_tool(name=tool_name, arguments=tool_args)

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
            except MCPLoanError as err:
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
                    "Unexpected error executing loan tool %s: %s",
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


def create_loan_server() -> LoanMCPServer:
    """Factory helper creating configured LoanMCPServer instance."""
    return LoanMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = create_loan_server()
    asyncio.run(server.run_stdio())
