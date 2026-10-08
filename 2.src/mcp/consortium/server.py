"""MCP Consortium Server exposing JSON-RPC 2.0 stdio protocol (S11)."""

import json
import logging
import sys
from typing import Any

from pydantic import ValidationError

from mcp.consortium.models import (
    GetConsortiumGroupRulesInput,
    MCPConsortiumError,
    SimulateConsortiumInput,
)
from mcp.consortium.tools import ConsortiumTools

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "atlas-mcp-consortium"
SERVER_VERSION = "1.0.0"


class ConsortiumMCPServer:
    """Model Context Protocol server for consortium exploration and simulation."""

    def __init__(self) -> None:
        self.tools = ConsortiumTools()

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP-compliant tool specifications with JSON Schema parameters."""
        return [
            {
                "name": "list_consortium_modalities",
                "description": (
                    "Lista os segmentos de consórcio ativos (Imobiliário, Veículos, Serviços) "
                    "com faixas de crédito, prazos disponíveis e taxas de administração."
                ),
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_consortium_group_rules",
                "description": (
                    "Consulta regras de grupo, taxas (adm e fundo de reserva) e limites de "
                    "lance embutido para uma modalidade específica de consórcio."
                ),
                "inputSchema": GetConsortiumGroupRulesInput.model_json_schema(),
            },
            {
                "name": "simulate_consortium",
                "description": (
                    "Simula cota de consórcio calculando parcelas integrais (fundo comum, "
                    "taxa de administração, fundo de reserva) e cenários de lance embutido, "
                    "com aviso mandatório de não-garantia de contemplação."
                ),
                "inputSchema": SimulateConsortiumInput.model_json_schema(),
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
            MCPConsortiumError: If tool is unknown or parameter validation fails.
        """
        try:
            if name == "list_consortium_modalities":
                return self.tools.list_consortium_modalities()

            if name == "get_consortium_group_rules":
                validated = GetConsortiumGroupRulesInput(**arguments)
                return self.tools.get_consortium_group_rules(modality=validated.modality)

            if name == "simulate_consortium":
                validated_sim = SimulateConsortiumInput(**arguments)
                return self.tools.simulate_consortium(
                    modality=validated_sim.modality,
                    credit_amount=validated_sim.credit_amount,
                    term_months=validated_sim.term_months,
                    embedded_bid_pct=validated_sim.embedded_bid_pct,
                )

            raise MCPConsortiumError(f"Tool '{name}' desconhecida.", code=-32601)

        except ValidationError as exc:
            msg = f"Parâmetros inválidos para a ferramenta '{name}': {exc}"
            raise MCPConsortiumError(msg, code=-32602) from exc

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

        except MCPConsortiumError as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": exc.code, "message": exc.message},
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erro interno inesperado no MCP Consortium Server.")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Erro interno: {exc}"},
            }


def create_consortium_server() -> ConsortiumMCPServer:
    """Factory creating a ConsortiumMCPServer instance."""
    return ConsortiumMCPServer()


def main() -> None:
    """Run the MCP Consortium Server reading JSON-RPC 2.0 lines from stdin."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = create_consortium_server()

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
