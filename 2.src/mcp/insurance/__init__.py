"""MCP Insurance Server module (S10)."""

from mcp.insurance.calculator import calculate_insurance_premium
from mcp.insurance.catalog import get_all_products, get_product_info
from mcp.insurance.models import (
    CoverageItem,
    InsuranceCategory,
    InsuranceProductInfo,
    InsuranceQuoteResult,
)
from mcp.insurance.server import InsuranceMCPServer, create_insurance_server
from mcp.insurance.tools import InsuranceTools

__all__ = [
    "CoverageItem",
    "InsuranceCategory",
    "InsuranceMCPServer",
    "InsuranceProductInfo",
    "InsuranceQuoteResult",
    "InsuranceTools",
    "calculate_insurance_premium",
    "create_insurance_server",
    "get_all_products",
    "get_product_info",
]
