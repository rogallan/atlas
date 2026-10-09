"""Typed MCP tool handlers for banking tariff queries and quota checks (S12)."""

import logging

from mcp.tariff.catalog import get_tariff_item, list_packages
from mcp.tariff.models import (
    ChannelType,
    InvalidTariffParameterError,
    QuotaCheckResult,
    ServiceFeeItem,
    TariffPackage,
)

logger = logging.getLogger(__name__)


class TariffTools:
    """Implementations of MCP tools for tariff lookup, essential quotas, and package comparison."""

    def get_service_fee(
        self,
        service_code: str,
        channel: ChannelType = ChannelType.DIGITAL,
    ) -> ServiceFeeItem:
        """Lookup unit price, regulatory basis, and channel breakdown for a service.

        Args:
            service_code: Service identifier (e.g. 'withdrawal', 'statement_30d', 'ted_transfer').
            channel: Transaction channel ('digital', 'atm', 'branch_counter').

        Returns:
            ServiceFeeItem with unit price and regulatory metadata.

        Raises:
            ServiceNotFoundError: If service is not recognized.
        """
        return get_tariff_item(service_code=service_code, channel=channel)

    def list_tariff_packages(self) -> list[TariffPackage]:
        """List all active account tariff packages and their monthly maintenance pricing.

        Returns:
            List of TariffPackage models.
        """
        return list_packages()

    def check_essential_services_quota(
        self,
        service_code: str,
        used_count: int,
        channel: ChannelType = ChannelType.ATM,
    ) -> QuotaCheckResult:
        """Evaluate if a transaction is within BACEN Res. 3.919 free monthly quota.

        Args:
            service_code: Essential service code (e.g. 'withdrawal', 'statement_30d').
            used_count: Quantity of transactions already completed in the current calendar month.
            channel: Service channel.

        Returns:
            QuotaCheckResult with fee computation and compliance diagnostics.

        Raises:
            InvalidTariffParameterError: If used_count is negative.
            ServiceNotFoundError: If service_code is invalid.
        """
        if used_count < 0:
            raise InvalidTariffParameterError(
                f"Quantidade utilizada não pode ser negativa. Recebido: {used_count}"
            )

        tariff_item = get_tariff_item(service_code=service_code, channel=channel)
        quota_limit = tariff_item.monthly_free_quota or 0

        # Current transaction would be (used_count + 1)
        next_count = used_count + 1
        is_within_free_quota = next_count <= quota_limit

        if is_within_free_quota:
            chargeable_units = 0
            unit_fee = 0.0
            total_charge = 0.0
        else:
            chargeable_units = 1
            unit_fee = tariff_item.unit_price
            total_charge = tariff_item.unit_price

        return QuotaCheckResult(
            service_code=tariff_item.service_code,
            service_name=tariff_item.service_name,
            channel=channel,
            used_count=used_count,
            free_quota_limit=quota_limit,
            is_within_free_quota=is_within_free_quota,
            chargeable_units=chargeable_units,
            unit_fee=unit_fee,
            total_charge=total_charge,
            regulatory_basis=tariff_item.regulatory_basis,
        )

    def compare_packages(
        self,
        customer_segment: str | None = None,
    ) -> list[TariffPackage]:
        """Compare available account packages and waiver rules, filtered by customer segment.

        Args:
            customer_segment: Optional segment name ('retail', 'prime', 'private').

        Returns:
            List of matching TariffPackage models.
        """
        return list_packages(target_segment=customer_segment)
