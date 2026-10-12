"""Deterministic synthetic banking dataset generator (S02).

This generator produces completely simulated and fictitious customer profiles,
accounts, products, contracts, events, and aggregated history using a fixed seed.
"""

import hashlib
import json
import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from data.models import (
    Account,
    AccountStatus,
    AccountType,
    Contract,
    ContractStatus,
    Customer,
    CustomerHistory,
    CustomerSegment,
    FinancialEvent,
    FinancialEventType,
    Product,
    ProductCategory,
    SyntheticDataset,
)

SYNTHETIC_DISCLAIMER: str = (
    "DISCLAIMER: 100% SYNTHETIC DATA. This dataset is entirely fictitious and simulated "
    "for testing and evaluation in the ATLAS Banking Copilot project. No real individual, "
    "account, bank, or transaction data is contained herein."
)

FAMOUS_DRUMMERS: list[str] = [
    "Dave Weckl",
    "Vinnie Colaiuta",
    "Dennis Chambers",
    "Buddy Rich",
    "Steve Gadd",
    "Thomas Lang",
    "Mike Portnoy",
    "Neil Peart",
    "John Bonham",
    "Stewart Copeland",
    "Danny Carey",
    "Ginger Baker",
    "Keith Moon",
    "Gene Krupa",
    "Billy Cobham",
    "Bernard Purdie",
    "Simon Phillips",
    "Tony Williams",
    "Jeff Porcaro",
    "Terry Bozzio",
    "Chad Smith",
    "Gavin Harrison",
    "Jojo Mayer",
    "Virgil Donati",
    "Ian Paice",
]

PRODUCTS_CATALOG: list[dict[str, Any]] = [
    {
        "id": "PROD-LOAN-PERSONAL",
        "name": "Crédito Pessoal Flex",
        "category": ProductCategory.LOAN,
        "description": "Empréstimo pessoal com taxa pré-fixada e parcelamento em até 48x.",
        "min_credit_score": 500,
        "base_rate_or_fee": Decimal("2.49"),
    },
    {
        "id": "PROD-LOAN-PAYROLL",
        "name": "Crédito Consignado Atlas",
        "category": ProductCategory.LOAN,
        "description": "Empréstimo com desconto em folha e taxas reduzidas.",
        "min_credit_score": 400,
        "base_rate_or_fee": Decimal("1.65"),
    },
    {
        "id": "PROD-INS-LIFE",
        "name": "Seguro Vida Tranquila",
        "category": ProductCategory.INSURANCE,
        "description": "Cobertura abrangente para morte acidental, invalidez e auxílio funeral.",
        "min_credit_score": 300,
        "base_rate_or_fee": Decimal("45.00"),
    },
    {
        "id": "PROD-INS-AUTO",
        "name": "Seguro Auto Protegido",
        "category": ProductCategory.INSURANCE,
        "description": "Proteção veicular contra colisão, furto e terceiros.",
        "min_credit_score": 450,
        "base_rate_or_fee": Decimal("180.00"),
    },
    {
        "id": "PROD-CON-AUTO",
        "name": "Consórcio Auto Sonho",
        "category": ProductCategory.CONSORTIUM,
        "description": "Cartas de crédito automotivo com taxa de administração competitiva.",
        "min_credit_score": 400,
        "base_rate_or_fee": Decimal("12.00"),
    },
    {
        "id": "PROD-CON-HOME",
        "name": "Consórcio Imobiliário Atlas",
        "category": ProductCategory.CONSORTIUM,
        "description": "Planejamento para aquisição de imóveis sem juros bancários tradicionais.",
        "min_credit_score": 550,
        "base_rate_or_fee": Decimal("15.00"),
    },
    {
        "id": "PROD-TAR-BASIC",
        "name": "Pacote Tarifário Essencial",
        "category": ProductCategory.TARIFF,
        "description": "Cesta básica de serviços bancários conforme normativo Bacen.",
        "min_credit_score": 0,
        "base_rate_or_fee": Decimal("0.00"),
    },
    {
        "id": "PROD-TAR-PRIME",
        "name": "Pacote Prime Exclusivo",
        "category": ProductCategory.TARIFF,
        "description": "Atendimento preferencial, transferências ilimitadas e isenções parciais.",
        "min_credit_score": 700,
        "base_rate_or_fee": Decimal("69.90"),
    },
]


class SyntheticDataGenerator:
    """Deterministic generator for synthetic banking data."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

    def generate(self, customer_count: int = 25) -> SyntheticDataset:
        """Generate a complete synthetic dataset."""
        # 1. Products
        products = [Product(**p) for p in PRODUCTS_CATALOG]
        products_by_id = {p.id: p for p in products}

        # 2. Customers
        customers: list[Customer] = []
        segments: list[CustomerSegment] = list(CustomerSegment)

        base_date = date(2023, 1, 1)

        for i in range(1, customer_count + 1):
            full_name = FAMOUS_DRUMMERS[(i - 1) % len(FAMOUS_DRUMMERS)]
            name_parts = full_name.split()
            first_name = name_parts[0]
            last_name = name_parts[-1]
            cust_id = f"CUST-{i:04d}"
            email_handle = f"{first_name.lower()}.{last_name.lower()}{i}"
            email = f"{email_handle}@simulado.atlas.local"
            doc_raw = f"SYNTHETIC-CPF-{i:06d}"
            doc_hash = hashlib.sha256(doc_raw.encode("utf-8")).hexdigest()[:16]

            segment: CustomerSegment = self.rng.choice(segments)
            if segment == CustomerSegment.PRIVATE:
                score = self.rng.randint(780, 990)
                income = Decimal(str(self.rng.randint(25000, 80000)))
            elif segment == CustomerSegment.PRIME:
                score = self.rng.randint(620, 850)
                income = Decimal(str(self.rng.randint(10000, 24000)))
            elif segment == CustomerSegment.CORPORATE_SMB:
                score = self.rng.randint(580, 880)
                income = Decimal(str(self.rng.randint(18000, 60000)))
            else:
                score = self.rng.randint(350, 700)
                income = Decimal(str(self.rng.randint(2200, 9500)))

            days_offset = self.rng.randint(0, 700)
            created_at = base_date + timedelta(days=days_offset)

            customers.append(
                Customer(
                    id=cust_id,
                    name=full_name,
                    email=email,
                    document_hash=doc_hash,
                    segment=segment,
                    credit_score=score,
                    income_monthly=income,
                    created_at=created_at,
                )
            )

        # 3. Accounts
        accounts: list[Account] = []
        account_seq = 1

        for cust in customers:
            # Each customer has at least 1 checking account
            acc_id = f"ACC-{account_seq:04d}"
            account_seq += 1
            balance = Decimal(str(self.rng.randint(500, 45000) + self.rng.randint(0, 99) / 100))
            accounts.append(
                Account(
                    id=acc_id,
                    customer_id=cust.id,
                    type=AccountType.CHECKING,
                    status=AccountStatus.ACTIVE,
                    currency="BRL",
                    balance=balance,
                    opened_at=cust.created_at,
                )
            )

            # Some customers also have savings or investment accounts
            if self.rng.random() > 0.4:
                acc_sav_id = f"ACC-{account_seq:04d}"
                account_seq += 1
                sav_balance = Decimal(
                    str(self.rng.randint(1000, 120000) + self.rng.randint(0, 99) / 100)
                )
                accounts.append(
                    Account(
                        id=acc_sav_id,
                        customer_id=cust.id,
                        type=AccountType.SAVINGS,
                        status=AccountStatus.ACTIVE,
                        currency="BRL",
                        balance=sav_balance,
                        opened_at=cust.created_at + timedelta(days=10),
                    )
                )

        accounts_by_customer: dict[str, list[Account]] = {}
        for acc in accounts:
            accounts_by_customer.setdefault(acc.customer_id, []).append(acc)

        # 4. Contracts
        contracts: list[Contract] = []
        contract_seq = 1

        for cust in customers:
            # Assign tariff package contract
            tariff_prod = (
                products_by_id["PROD-TAR-PRIME"]
                if cust.segment in (CustomerSegment.PRIME, CustomerSegment.PRIVATE)
                else products_by_id["PROD-TAR-BASIC"]
            )
            ctr_id = f"CTR-{contract_seq:04d}"
            contract_seq += 1
            contracts.append(
                Contract(
                    id=ctr_id,
                    customer_id=cust.id,
                    product_id=tariff_prod.id,
                    status=ContractStatus.ACTIVE,
                    principal_amount=None,
                    installment_amount=tariff_prod.base_rate_or_fee,
                    start_date=cust.created_at,
                    terms={"plan": tariff_prod.name},
                )
            )

            # Assign optional loan or insurance contract
            if cust.credit_score >= 600 and self.rng.random() > 0.5:
                loan_prod = products_by_id["PROD-LOAN-PERSONAL"]
                principal = Decimal(str(self.rng.randint(5000, 40000)))
                installment = Decimal(str(round(principal / 24 * Decimal("1.15"), 2)))
                ctr_id = f"CTR-{contract_seq:04d}"
                contract_seq += 1
                contracts.append(
                    Contract(
                        id=ctr_id,
                        customer_id=cust.id,
                        product_id=loan_prod.id,
                        status=ContractStatus.ACTIVE,
                        principal_amount=principal,
                        installment_amount=installment,
                        start_date=cust.created_at + timedelta(days=30),
                        end_date=cust.created_at + timedelta(days=30 + 720),
                        terms={
                            "rate_monthly_pct": float(loan_prod.base_rate_or_fee),
                            "terms_months": 24,
                        },
                    )
                )

        # 5. Financial Events (Transactions)
        events: list[FinancialEvent] = []
        event_seq = 1
        event_ref_time = datetime(2026, 10, 1, 10, 0, 0, tzinfo=UTC)

        for acc in accounts:
            # Generate 2 to 6 realistic transactions per account
            tx_count = self.rng.randint(2, 6)
            for j in range(tx_count):
                evt_id = f"EVT-{event_seq:05d}"
                event_seq += 1
                event_types: list[FinancialEventType] = list(FinancialEventType)
                evt_type: FinancialEventType = self.rng.choice(event_types)
                amount = Decimal(str(self.rng.randint(20, 2500) + self.rng.randint(0, 99) / 100))
                evt_time = event_ref_time - timedelta(days=j * 5, hours=self.rng.randint(1, 12))
                description = f"Simulação de transação {evt_type.value} na conta {acc.id}"

                events.append(
                    FinancialEvent(
                        id=evt_id,
                        account_id=acc.id,
                        type=evt_type,
                        amount=amount,
                        timestamp=evt_time,
                        description=description,
                    )
                )

        # 6. Aggregated Customer Histories
        events_by_account: dict[str, list[FinancialEvent]] = {}
        for ev in events:
            events_by_account.setdefault(ev.account_id, []).append(ev)

        histories: list[CustomerHistory] = []
        for cust in customers:
            cust_accs = accounts_by_customer.get(cust.id, [])
            total_balance = sum((a.balance for a in cust_accs), Decimal("0"))
            cust_contracts = [c for c in contracts if c.customer_id == cust.id]
            total_borrowed = sum(
                (c.principal_amount for c in cust_contracts if c.principal_amount is not None),
                Decimal("0"),
            )
            cust_events_count = sum(len(events_by_account.get(a.id, [])) for a in cust_accs)

            if cust.credit_score >= 750:
                risk = "LOW"
            elif cust.credit_score >= 550:
                risk = "MEDIUM"
            else:
                risk = "HIGH"

            histories.append(
                CustomerHistory(
                    customer_id=cust.id,
                    total_balance=total_balance,
                    active_contracts_count=len(cust_contracts),
                    total_borrowed=total_borrowed,
                    credit_risk_tier=risk,
                    last_activity_date=date(2026, 10, 1),
                    events_count=cust_events_count,
                )
            )

        return SyntheticDataset(
            version="1.0.0",
            seed=self.seed,
            generated_at="2026-10-06T00:00:00Z",
            disclaimer=SYNTHETIC_DISCLAIMER,
            customers=customers,
            accounts=accounts,
            products=products,
            contracts=contracts,
            financial_events=events,
            histories=histories,
        )


def export_dataset(dataset: SyntheticDataset) -> tuple[str, str]:
    """Serialize dataset to JSON and compute its deterministic SHA-256 hash."""

    # Custom encoder for Decimals, dates, and datetimes
    def default_serializer(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, date | datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    json_str = json.dumps(
        dataset.model_dump(), indent=2, default=default_serializer, sort_keys=True
    )
    digest = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    return json_str, digest
