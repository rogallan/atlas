"""Data repository adapter querying the synthetic customer dataset (S08)."""

import json
import logging
from pathlib import Path

from data.generator import SyntheticDataGenerator
from data.models import (
    Account,
    Contract,
    Customer,
    CustomerHistory,
    FinancialEvent,
    SyntheticDataset,
)

logger = logging.getLogger(__name__)

DEFAULT_FIXTURE_PATH = (
    Path(__file__).parent.parent.parent / "data" / "fixtures" / "synthetic_customers.json"
)


class CustomerRepository:
    """In-memory indexed repository for synthetic customer records."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        """Initialize and populate the repository.

        Args:
            fixture_path: Path to the synthetic_customers.json fixture file.
        """
        self.fixture_path = fixture_path or DEFAULT_FIXTURE_PATH
        self._customers: dict[str, Customer] = {}
        self._accounts_by_customer: dict[str, list[Account]] = {}
        self._contracts_by_customer: dict[str, list[Contract]] = {}
        self._events_by_account: dict[str, list[FinancialEvent]] = {}
        self._histories_by_customer: dict[str, CustomerHistory] = {}

        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load data from JSON fixture or generate deterministically as fallback."""
        dataset: SyntheticDataset | None = None

        if self.fixture_path.exists():
            try:
                with open(self.fixture_path, encoding="utf-8") as f:
                    raw_data = json.load(f)
                dataset = SyntheticDataset.model_validate(raw_data)
                logger.info(
                    "Loaded %d synthetic customers from fixture %s",
                    len(dataset.customers),
                    self.fixture_path,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to parse fixture at %s: %s. Generating on-the-fly.",
                    self.fixture_path,
                    exc,
                )

        if dataset is None:
            generator = SyntheticDataGenerator(seed=42)
            dataset = generator.generate(customer_count=25)
            logger.info("Generated %d synthetic customers with seed 42", len(dataset.customers))

        # Index customers
        for cust in dataset.customers:
            self._customers[cust.id] = cust
            self._accounts_by_customer[cust.id] = []
            self._contracts_by_customer[cust.id] = []

        # Index accounts
        for acc in dataset.accounts:
            if acc.customer_id in self._accounts_by_customer:
                self._accounts_by_customer[acc.customer_id].append(acc)
            self._events_by_account[acc.id] = []

        # Index contracts
        for ctr in dataset.contracts:
            if ctr.customer_id in self._contracts_by_customer:
                self._contracts_by_customer[ctr.customer_id].append(ctr)

        # Index financial events
        for evt in dataset.financial_events:
            if evt.account_id in self._events_by_account:
                self._events_by_account[evt.account_id].append(evt)

        # Sort events descending by timestamp
        for acc_id in self._events_by_account:
            self._events_by_account[acc_id].sort(key=lambda e: e.timestamp, reverse=True)

        # Index histories
        for hist in dataset.histories:
            self._histories_by_customer[hist.customer_id] = hist

    def get_customer(self, customer_id: str) -> Customer | None:
        """Retrieve customer by unique identifier."""
        return self._customers.get(customer_id)

    def get_accounts(self, customer_id: str) -> list[Account]:
        """Retrieve all synthetic accounts for a given customer."""
        return list(self._accounts_by_customer.get(customer_id, []))

    def get_events(self, customer_id: str, limit: int = 10) -> list[FinancialEvent]:
        """Retrieve recent financial events across all accounts of a customer."""
        accounts = self.get_accounts(customer_id)
        all_events: list[FinancialEvent] = []
        for acc in accounts:
            all_events.extend(self._events_by_account.get(acc.id, []))

        # Sort all aggregated events descending by timestamp
        all_events.sort(key=lambda e: e.timestamp, reverse=True)
        return all_events[:limit]

    def get_contracts(self, customer_id: str) -> list[Contract]:
        """Retrieve active and past contracts for a customer."""
        return list(self._contracts_by_customer.get(customer_id, []))

    def get_history(self, customer_id: str) -> CustomerHistory | None:
        """Retrieve aggregated historical scorecard for a customer."""
        return self._histories_by_customer.get(customer_id)

    def list_customer_ids(self) -> list[str]:
        """List all indexed customer identifiers."""
        return sorted(self._customers.keys())
