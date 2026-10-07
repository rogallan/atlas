# Synthetic Customer Data & History (S02)

> ⚠️ **DISCLAIMER: 100% SYNTHETIC & FICTITIOUS DATA**
> All data stored or generated in this directory is **100% synthetic and fictitious**. It is designed solely for local testing, simulation, and evaluation of the ATLAS Banking Copilot. **No real customer, CPF/CNPJ, bank account, institution, or transaction history** is ever accessed, stored, or derived.

## Entity Model & Schema

- **Customer:** Fictitious demographic and segmentation profile (`retail`, `prime`, `private`, `corporate_smb`).
- **Account:** Checking and savings accounts linked to customers with simulated balances.
- **Product:** Catalog of banking products (`loan`, `insurance`, `consortium`, `tariff`).
- **Contract:** Active or pending contracts between customers and products.
- **FinancialEvent:** Simulated ledger events (`pix_in`, `pix_out`, `salary_deposit`, `bill_payment`, etc.).
- **CustomerHistory:** Pre-aggregated metrics (total balance, risk tier, activity summary) for rapid MCP lookup.

## Reproducibility

The dataset is generated deterministically using a fixed pseudo-random seed (`42`).
To regenerate the dataset:

```bash
uv run python -m data.generate
```

Verification parameters and checksums are recorded in `fixtures/manifest.json`.
