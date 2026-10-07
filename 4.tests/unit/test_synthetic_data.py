"""Unit tests for the synthetic customer database (S02).

Validates schema constraints, referential integrity, determinism/reproducibility,
and compliance with the 100% synthetic data principle.
"""

import json
from decimal import Decimal
from pathlib import Path

from data.generator import (
    SYNTHETIC_DISCLAIMER,
    SyntheticDataGenerator,
    export_dataset,
)
from data.models import SyntheticDataset


def test_dataset_generation_and_schema_validation() -> None:
    """Validate that the generator produces a valid SyntheticDataset model."""
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate(customer_count=10)

    assert isinstance(dataset, SyntheticDataset)
    assert len(dataset.customers) == 10
    assert len(dataset.accounts) >= 10
    assert len(dataset.products) >= 6
    assert len(dataset.contracts) >= 10
    assert len(dataset.financial_events) > 0
    assert len(dataset.histories) == 10


def test_referential_integrity() -> None:
    """Ensure all foreign key references between entities are strictly valid."""
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate(customer_count=20)

    customer_ids = {c.id for c in dataset.customers}
    account_ids = {a.id for a in dataset.accounts}
    product_ids = {p.id for p in dataset.products}

    # 1. Accounts reference valid Customers
    for account in dataset.accounts:
        assert (
            account.customer_id in customer_ids
        ), f"Account {account.id} references invalid customer {account.customer_id}"
        assert account.balance >= Decimal("0"), f"Account {account.id} has negative balance"

    # 2. Contracts reference valid Customers and Products
    for contract in dataset.contracts:
        assert (
            contract.customer_id in customer_ids
        ), f"Contract {contract.id} references invalid customer {contract.customer_id}"
        assert (
            contract.product_id in product_ids
        ), f"Contract {contract.id} references invalid product {contract.product_id}"

    # 3. Financial Events reference valid Accounts
    for event in dataset.financial_events:
        assert (
            event.account_id in account_ids
        ), f"Event {event.id} references invalid account {event.account_id}"
        assert event.amount > Decimal("0"), f"Event {event.id} must have positive amount"

    # 4. Histories reference valid Customers
    for history in dataset.histories:
        assert (
            history.customer_id in customer_ids
        ), f"History references invalid customer {history.customer_id}"
        assert history.credit_risk_tier in {"LOW", "MEDIUM", "HIGH"}


def test_reproducibility_deterministic_seed() -> None:
    """Ensure running generation twice with the same seed yields byte-identical output."""
    gen1 = SyntheticDataGenerator(seed=42)
    ds1 = gen1.generate(customer_count=15)
    json1, hash1 = export_dataset(ds1)

    gen2 = SyntheticDataGenerator(seed=42)
    ds2 = gen2.generate(customer_count=15)
    json2, hash2 = export_dataset(ds2)

    assert json1 == json2, "Generated JSON outputs must be byte-identical for identical seed"
    assert hash1 == hash2, "Computed SHA-256 hashes must be identical"

    # Running with different seed must differ
    gen3 = SyntheticDataGenerator(seed=99)
    ds3 = gen3.generate(customer_count=15)
    _, hash3 = export_dataset(ds3)

    assert hash1 != hash3, "Different seeds must produce distinct outputs"


def test_synthetic_privacy_invariants() -> None:
    """Verify that all records comply with the 100% fictitious data guarantee."""
    generator = SyntheticDataGenerator(seed=42)
    dataset = generator.generate(customer_count=25)

    assert dataset.disclaimer == SYNTHETIC_DISCLAIMER

    for cust in dataset.customers:
        # Check simulated domain
        assert cust.email.endswith(
            "@simulado.atlas.local"
        ), f"Customer email {cust.email} must use simulated local domain"
        # Check simulated CPF hash format
        assert len(cust.document_hash) == 16, "Document hash must be simulated 16-char hex"
        assert 0 <= cust.credit_score <= 1000, "Credit score must be between 0 and 1000"


def test_persisted_fixture_matches_manifest() -> None:
    """Validate that the persisted synthetic_customers.json matches manifest.json."""
    fixtures_dir = Path(__file__).parents[2] / "2.src" / "data" / "fixtures"
    dataset_path = fixtures_dir / "synthetic_customers.json"
    manifest_path = fixtures_dir / "manifest.json"

    assert dataset_path.exists(), f"Missing fixture at {dataset_path}"
    assert manifest_path.exists(), f"Missing manifest at {manifest_path}"

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)

    parsed_dataset = SyntheticDataset.model_validate(data)
    _, current_hash = export_dataset(parsed_dataset)

    assert manifest["sha256"] == current_hash, "Manifest SHA-256 must match persisted dataset"
    assert len(parsed_dataset.customers) == manifest["customer_count"]


def test_generate_script_execution() -> None:
    """Verify that generate.main executes properly and writes fixtures."""
    from data.generate import main

    # Calling main should regenerate without errors
    main()
    fixtures_dir = Path(__file__).parents[2] / "2.src" / "data" / "fixtures"
    assert (fixtures_dir / "synthetic_customers.json").exists()
    assert (fixtures_dir / "manifest.json").exists()
