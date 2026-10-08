"""MCP Insurance Server exposing JSON-RPC 2.0 stdio protocol (S10)."""

import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.customer.repository import CustomerRepository
from mcp.insurance.models import (
    GetCoverageDetailsInput,
    MCPInsuranceError,
    SimulateInsuranceQuoteInput,
)
from mcp.insurance.tools import InsuranceTools

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "atlas-mcp-insurance"
SERVER_VERSION = "1.0.0"


class InsuranceMCPServer:
    """Model Context Protocol server for insurance exploration and simulation."""

    def __init__(self, customer_repository: CustomerRepository | None = None) -> None:
        self.tools = InsuranceTools(customer_repository=customer_repository)

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "list_insurance_products",
                "description": (
                    "Lista produtos de seguro ativos (Vida, Residencial, Prestamista, Proteção "
                    "de Cartão) com categorias, limites de capital e resumo de coberturas."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_coverage_details",
                "description": (
                    "Consulta coberturas detalhadas, limites máximos de indenização (LMI) "
                    "e franquias/carências de um produto de seguro específico."
                ),
                "inputSchema": GetCoverageDetailsInput.model_json_schema(),
            },
            {
                "name": "simulate_insurance_quote",
                "description": (
                    "Simula cotação determinística de seguro (prêmio mensal, anual com "
                    "desconto, IOF estimado e premissas atuariais) com disclaimer obrigatório."
                ),
                "inputSchema": SimulateInsuranceQuoteInput.model_json_schema(),
            },
        ]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Directly invoke a registered tool by name with parameter validation.

        Args:
            name: Tool name identifier.
            arguments: Tool parameters dictionary.

        Returns:
            Pydantic model or list of models.

        Raises:
            MCPInsuranceError: If tool is unknown or parameter validation fails.
        """
        try:
            if name == "list_insurance_products":
                return self.tools.list_insurance_products()

            if name == "get_coverage_details":
                validated = GetCoverageDetailsInput(**arguments)
                return self.tools.get_coverage_details(product_id=validated.product_id)

            if name == "simulate_insurance_quote":
                validated_quote = SimulateInsuranceQuoteInput(**arguments)
                return self.tools.simulate_insurance_quote(
                    customer_id=validated_quote.customer_id,
                    product_id=validated_quote.product_id,
                    insured_capital=validated_quote.insured_capital,
                    optional_coverages=validated_quote.optional_coverages,
                )

            raise MCPInsuranceError(f"Tool '{name}' desconhecida.", code=-32601)

        except ValidationError as exc:
            msg = f"Parâmetros inválidos para a ferramenta '{name}': {exc}"
            raise MCPInsuranceError(msg, code=-32602) from exc

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a single JSON-RPC 2.0 request and return the response."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if not method:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Requisição inválida: 'method' ausente."},
            }

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                        "capabilities": {"tools": {"listChanged": False}},
                    },
                }

            if method == "ping":
                return {"jsonrpc": "2.0", "id": req_id, "result": {}}

            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_tool_definitions()},
                }

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32602,
                            "message": "Parâmetro 'name' obrigatório em tools/call.",
                        },
                    }

                raw_result = self.execute_tool(tool_name, arguments)

                if isinstance(raw_result, list):
                    serialized_content = [item.model_dump() for item in raw_result]
                elif hasattr(raw_result, "model_dump"):
                    serialized_content = raw_result.model_dump()
                else:
                    serialized_content = raw_result

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    serialized_content, ensure_ascii=False, indent=2
                                ),
                            }
                        ],
                        "isError": False,
                    },
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Método '{method}' não suportado."},
            }

        except MCPInsuranceError as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": exc.code, "message": exc.message},
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erro interno inesperado no MCP Insurance Server.")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Erro interno: {exc}"},
            }


def create_insurance_server(
    customer_repository: CustomerRepository | None = None,
) -> InsuranceMCPServer:
    """Factory creating an InsuranceMCPServer instance."""
    return InsuranceMCPServer(customer_repository=customer_repository)


def main() -> None:
    """Run the MCP Insurance Server reading JSON-RPC 2.0 lines from stdin."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = create_insurance_server()

    for line in sys.stdin:
        line_clean = line.strip()
        if not line_clean:
            continue

        try:
            req = json.loads(line_clean)
            resp = server.handle_request(req)
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "JSON inválido."},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
