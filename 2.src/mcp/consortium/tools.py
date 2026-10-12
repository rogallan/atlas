"""Typed MCP tool handlers for consortium catalog and simulation (S11)."""

import logging

from mcp.consortium.calculator import calculate_consortium_quota
from mcp.consortium.catalog import (
    get_all_modalities,
    get_group_rules,
    validate_consortium_request,
)
from mcp.consortium.models import (
    DEFAULT_CONSORTIUM_DISCLAIMER,
    ConsortiumSegment,
    ConsortiumSimulationResult,
    GroupRulesInfo,
)

logger = logging.getLogger(__name__)


class ConsortiumTools:
    """Implementations of MCP tools for consortium exploration and quota simulation."""

    def list_consortium_modalities(self) -> list[GroupRulesInfo]:
        """List all active consortium segments, limits, fee rates, and allowed terms.

        Returns:
            List of GroupRulesInfo models.
        """
        return get_all_modalities()

    def get_consortium_group_rules(
        self,
        modality: ConsortiumSegment,
    ) -> GroupRulesInfo:
        """Retrieve group rules, administration fee, and bid parameters for a segment.

        Args:
            modality: Target consortium segment ('real_estate', 'automotive', 'services').

        Returns:
            GroupRulesInfo for the requested segment.

        Raises:
            ModalityNotFoundError: If segment is invalid.
        """
        return get_group_rules(modality)

    def simulate_consortium(
        self,
        modality: ConsortiumSegment,
        credit_amount: float,
        term_months: int,
        embedded_bid_pct: float = 0.0,
    ) -> ConsortiumSimulationResult:
        """Simulate a deterministic consortium quota with fee breakdown and bid options.

        Args:
            modality: Target consortium segment.
            credit_amount: Desired letter of credit amount in BRL.
            term_months: Contract duration in months.
            embedded_bid_pct: Optional embedded bid percentage (e.g. 0.20 for 20%).

        Returns:
            ConsortiumSimulationResult with installment components, totals, and disclaimer.

        Raises:
            ModalityNotFoundError: If segment is invalid.
            InvalidConsortiumParameterError: If any parameter violates group limits.
        """
        rules = validate_consortium_request(
            modality=modality,
            credit_amount=credit_amount,
            term_months=term_months,
            embedded_bid_pct=embedded_bid_pct,
        )

        calc = calculate_consortium_quota(
            credit_amount=credit_amount,
            term_months=term_months,
            rules=rules,
            embedded_bid_pct=embedded_bid_pct,
        )

        return ConsortiumSimulationResult(
            segment=rules.segment,
            display_name=rules.display_name,
            credit_amount=credit_amount,
            term_months=term_months,
            installments=calc["installments"],
            total_payable_amount=calc["total_payable_amount"],
            total_fees_amount=calc["total_fees_amount"],
            total_cost_percentage=calc["total_cost_percentage"],
            simulated_bid_amount=calc["simulated_bid_amount"],
            net_credit_with_embedded_bid=calc["net_credit_with_embedded_bid"],
            post_bid_installment_estimate=calc["post_bid_installment_estimate"],
            disclaimer=DEFAULT_CONSORTIUM_DISCLAIMER,
        )
