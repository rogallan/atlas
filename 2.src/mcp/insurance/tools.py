"""Typed MCP tool handlers for insurance catalog and quote simulation (S10)."""

import logging
from datetime import UTC, datetime

from mcp.customer.repository import CustomerRepository
from mcp.insurance.calculator import calculate_insurance_premium
from mcp.insurance.catalog import get_all_products, get_product_info, validate_insurance_request
from mcp.insurance.models import (
    DEFAULT_INSURANCE_DISCLAIMER,
    CoverageItem,
    CoverageNotFoundError,
    InsuranceProductInfo,
    InsuranceQuoteResult,
)

logger = logging.getLogger(__name__)


class InsuranceTools:
    """Implementations of MCP tools for insurance exploration and simulation."""

    def __init__(self, customer_repository: CustomerRepository | None = None) -> None:
        self.customer_repo = customer_repository or CustomerRepository()

    def list_insurance_products(self) -> list[InsuranceProductInfo]:
        """List all active synthetic insurance products with limits and available coverages.

        Returns:
            List of InsuranceProductInfo models.
        """
        return get_all_products()

    def get_coverage_details(self, product_id: str) -> list[CoverageItem]:
        """Retrieve the catalog of coverages, indemnity limits, and deductibles for a product.

        Args:
            product_id: Target insurance product identifier.

        Returns:
            List of CoverageItem models for the product.

        Raises:
            ProductNotFoundError: If product_id does not exist.
        """
        product = get_product_info(product_id)
        return product.available_coverages

    def simulate_insurance_quote(
        self,
        product_id: str,
        insured_capital: float,
        customer_id: str | None = None,
        optional_coverages: list[str] | None = None,
    ) -> InsuranceQuoteResult:
        """Simulate a deterministic, non-binding insurance quote with actuarial premises.

        Args:
            product_id: Target insurance product identifier.
            insured_capital: Desired insured capital in BRL.
            customer_id: Optional synthetic customer ID for risk profiling.
            optional_coverages: Optional list of additional coverage codes.

        Returns:
            InsuranceQuoteResult with premium breakdown, premises, and disclaimer.

        Raises:
            ProductNotFoundError: If product_id is invalid.
            InvalidInsuranceParameterError: If insured_capital is outside boundaries.
            CoverageNotFoundError: If any optional coverage code is invalid.
        """
        product = validate_insurance_request(product_id, insured_capital)
        optional_codes = set(optional_coverages or [])

        # Validate that all requested optional coverages exist in the product catalog
        available_coverage_map = {cov.code: cov for cov in product.available_coverages}

        for code in optional_codes:
            if code not in available_coverage_map:
                raise CoverageNotFoundError(coverage_code=code, product_id=product_id)

        # Assemble selected coverages (all mandatory + requested optional)
        selected_coverages: list[CoverageItem] = []
        for cov in product.available_coverages:
            if cov.is_mandatory or cov.code in optional_codes:
                selected_coverages.append(cov)

        # Extract customer profile data if available
        customer_age: int | None = None
        customer_segment: str | None = None

        if customer_id:
            customer = self.customer_repo.get_customer(customer_id)
            if customer:
                current_year = datetime.now(UTC).date().year
                relationship_years = max(1, current_year - customer.created_at.year)
                # Synthetic age estimate: base 32 + tenure
                customer_age = 32 + relationship_years * 2
                customer_segment = customer.segment.value
            else:
                logger.warning(
                    "Customer ID %s provided for quote simulation not found.", customer_id
                )

        # Compute premium
        quote_calc = calculate_insurance_premium(
            insured_capital=insured_capital,
            selected_coverages=selected_coverages,
            product_info=product,
            customer_age=customer_age,
            customer_segment=customer_segment,
        )

        return InsuranceQuoteResult(
            customer_id=customer_id,
            product_id=product.product_id,
            product_name=product.name,
            category=product.category,
            insured_capital=insured_capital,
            included_coverages=selected_coverages,
            monthly_premium=quote_calc["monthly_premium"],
            annual_premium=quote_calc["annual_premium"],
            net_monthly_premium=quote_calc["net_monthly_premium"],
            estimated_iof=quote_calc["estimated_iof"],
            iof_rate=quote_calc["iof_rate"],
            underwriting_premises=quote_calc["underwriting_premises"],
            disclaimer=DEFAULT_INSURANCE_DISCLAIMER,
        )
