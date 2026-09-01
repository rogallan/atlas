# Plan — S02 · Synthetic Customer Base

## 1. Approach

Define the entity schemas first (as typed models), then build a deterministic generator on top of
them, then validate the output with schema/consistency tests.

## 2. Entity model (high level)

- **Customer** — id, name (synthetic), segment, since-date.
- **Account** — id, customer_id, type, balance, opened_at.
- **Product** — id, name, category (loan/insurance/consortium/tariff plan).
- **Contract** — id, customer_id, product_id, status, terms.
- **FinancialEvent** — id, account_id, type, amount, timestamp.
- **History** — aggregated view joining events over time for a given customer.

Relationships: Customer 1—N Account, Customer 1—N Contract, Account 1—N FinancialEvent.

## 3. Generation strategy

- Use a seeded random generator (e.g., Python's `random.Random(seed)` or a library like Faker with
  a fixed seed) so output is reproducible.
- Store the seed and generation parameters alongside the dataset (e.g., in a `manifest.json`).
- Persist the dataset as versioned files (e.g., JSON/CSV or a local SQLite file) under `src/data/`.

## 4. Test strategy

- **Schema tests:** every generated record validates against its typed model (e.g., Pydantic).
- **Consistency tests:** referential integrity (every `Account.customer_id` refers to an existing
  Customer, etc.), no duplicate IDs, no negative balances unless intentionally modeled.
- **Reproducibility test:** generating twice with the same seed yields identical output (hash
  comparison).

## 5. Risks & mitigations

- **Risk:** the dataset accidentally resembles a real institution/customer. **Mitigation:** use
  clearly fictitious naming conventions and review before merging.
- **Risk:** schema drifts as later MCP servers need new fields. **Mitigation:** version the schema
  and document changes in `docs/adr/`.
