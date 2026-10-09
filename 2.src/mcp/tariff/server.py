"""MCP Tariff Server exposing JSON-RPC 2.0 stdio protocol (S12)."""

import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.tariff.models import (
    CheckEssentialServicesQuotaInput,
    ComparePackagesInput,
    GetServiceFeeInput,
    MCPTariffError,
)
from mcp.tariff.tools import TariffTools

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "atlas-mcp-tariff"
SERVER_VERSION = "1.0.0"


class TariffMCPServer:
    """Model Context Protocol server for banking tariff tables and essential quotas."""

    def __init__(self) -> None:
        self.tools = TariffTools()

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "get_service_fee",
                "description": (
                    "Consulta a tarifa unitária avulsa de um serviço bancário por canal "
                    "(digital, ATM, guichê presencial), com fundamento regulatório BACEN."
                ),
                "inputSchema": GetServiceFeeInput.model_json_schema(),
            },
            {
                "name": "list_tariff_packages",
                "description": (
                    "Lista os pacotes de serviços de conta corrente (Essencial Gratuito, "
                    "Clássico, Prime, Private) com mensalidades e serviços inclusos."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "check_essential_services_quota",
                "description": (
                    "Valida se uma transação (saque, extrato, transferência) está dentro da "
                    "franquia mensal gratuita obrigatória da Resolução CMN nº 3.919/2010."
                ),
                "inputSchema": CheckEssentialServicesQuotaInput.model_json_schema(),
            },
            {
                "name": "compare_packages",
                "description": (
                    "Compara pacotes de tarifas e apresenta regras de isenção total por "
                    "volume de investimentos, portabilidade de salário ou fatura de cartão."
                ),
                "inputSchema": ComparePackagesInput.model_json_schema(),
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
            MCPTariffError: If tool is unknown or parameter validation fails.
        """
        try:
            if name == "get_service_fee":
                validated_fee = GetServiceFeeInput(**arguments)
                return self.tools.get_service_fee(
                    service_code=validated_fee.service_code,
                    channel=validated_fee.channel,
                )

            if name == "list_tariff_packages":
                return self.tools.list_tariff_packages()

            if name == "check_essential_services_quota":
                validated_quota = CheckEssentialServicesQuotaInput(**arguments)
                return self.tools.check_essential_services_quota(
                    service_code=validated_quota.service_code,
                    used_count=validated_quota.used_count,
                    channel=validated_quota.channel,
                )

            if name == "compare_packages":
                validated_comp = ComparePackagesInput(**arguments)
                return self.tools.compare_packages(customer_segment=validated_comp.customer_segment)

            raise MCPTariffError(f"Tool '{name}' desconhecida.", code=-32601)

        except ValidationError as exc:
            msg = f"Parâmetros inválidos para a ferramenta '{name}': {exc}"
            raise MCPTariffError(msg, code=-32602) from exc

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

        except MCPTariffError as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": exc.code, "message": exc.message},
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erro interno inesperado no MCP Tariff Server.")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Erro interno: {exc}"},
            }


def create_tariff_server() -> TariffMCPServer:
    """Factory creating a TariffMCPServer instance."""
    return TariffMCPServer()


def main() -> None:
    """Run the MCP Tariff Server reading JSON-RPC 2.0 lines from stdin."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = create_tariff_server()

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
