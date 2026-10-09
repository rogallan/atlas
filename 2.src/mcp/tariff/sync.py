"""Consistency verification helper synchronizing MCP Tariff table with RAG corpus (S12)."""

import logging
from pathlib import Path
from typing import Any

from mcp.tariff.catalog import TARIFF_ITEMS_CATALOG, TARIFF_PACKAGES_CATALOG
from mcp.tariff.models import ChannelType

logger = logging.getLogger(__name__)

DEFAULT_RAG_DOCUMENT_PATH = (
    Path(__file__).resolve().parents[3] / "8.docs" / "knowledge" / "tabela_tarifas_bancarias.md"
)


def verify_tariff_rag_consistency(
    document_path: Path | None = None,
) -> dict[str, Any]:
    """Verify that MCP Tariff catalog entries align with RAG documentary knowledge.

    Args:
        document_path: Optional custom path to tabela_tarifas_bancarias.md.

    Returns:
        Dictionary with synchronization audit results and detected discrepancies.
    """
    doc_file = document_path or DEFAULT_RAG_DOCUMENT_PATH
    if not doc_file.exists():
        logger.warning("RAG documentary file not found at %s", doc_file)
        return {
            "is_consistent": False,
            "document_path": str(doc_file),
            "errors": [f"Document not found: {doc_file}"],
        }

    content = doc_file.read_text(encoding="utf-8")
    mismatches: list[str] = []

    # 1. Verify Regulatory Basis reference
    expected_norm = "Resolução CMN nº 3.919/2010"
    if expected_norm not in content:
        mismatches.append(f"Expected reference '{expected_norm}' not found in RAG document.")

    # 2. Check essential withdrawal quota (Art. 2º III - até quatro saques)
    atm_withdrawal = TARIFF_ITEMS_CATALOG.get(("withdrawal", ChannelType.ATM))
    if not atm_withdrawal or atm_withdrawal.monthly_free_quota != 4:
        mismatches.append("MCP withdrawal free quota is not 4.")
    if "quatro saques" not in content.lower():
        mismatches.append("RAG document does not mention 'quatro saques'.")

    # 3. Check essential statement quota (Art. 2º IV - até dois extratos)
    atm_statement = TARIFF_ITEMS_CATALOG.get(("statement_30d", ChannelType.ATM))
    if not atm_statement or atm_statement.monthly_free_quota != 2:
        mismatches.append("MCP statement_30d free quota is not 2.")
    if "dois extratos" not in content.lower():
        mismatches.append("RAG document does not mention 'dois extratos'.")

    # 4. Check essential internal transfer quota (Art. 2º VI - até duas transferências)
    atm_transfer = TARIFF_ITEMS_CATALOG.get(("internal_transfer", ChannelType.ATM))
    if not atm_transfer or atm_transfer.monthly_free_quota != 2:
        mismatches.append("MCP internal_transfer free quota is not 2.")
    if "duas transferências" not in content.lower():
        mismatches.append("RAG document does not mention 'duas transferências'.")

    # 5. Check zero-cost essential package
    essential_pkg = TARIFF_PACKAGES_CATALOG.get("essential_free")
    if not essential_pkg or essential_pkg.monthly_price != 0.0:
        mismatches.append("Essential free package price is not R$ 0.00.")

    is_consistent = len(mismatches) == 0
    return {
        "is_consistent": is_consistent,
        "document_path": str(doc_file),
        "checked_rules": [
            "Resolução CMN nº 3.919/2010",
            "4 saques mensais gratuitos",
            "2 extratos mensais gratuitos",
            "2 transferências internas mensais gratuitas",
            "Pacote de serviços essenciais a R$ 0,00",
        ],
        "mismatches": mismatches,
    }
