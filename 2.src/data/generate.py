"""Script to reproducibly generate the ATLAS synthetic customer database (S02)."""

import json
from pathlib import Path

from data.generator import (
    SYNTHETIC_DISCLAIMER,
    SyntheticDataGenerator,
    export_dataset,
)


def main() -> None:
    seed = 42
    output_dir = Path(__file__).parent / "fixtures"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = SyntheticDataGenerator(seed=seed)
    dataset = generator.generate(customer_count=25)

    json_str, sha256_hash = export_dataset(dataset)

    dataset_path = output_dir / "synthetic_customers.json"
    with open(dataset_path, "w", encoding="utf-8") as f:
        f.write(json_str + "\n")

    manifest = {
        "version": dataset.version,
        "seed": seed,
        "customer_count": len(dataset.customers),
        "account_count": len(dataset.accounts),
        "product_count": len(dataset.products),
        "contract_count": len(dataset.contracts),
        "event_count": len(dataset.financial_events),
        "dataset_file": dataset_path.name,
        "sha256": sha256_hash,
        "disclaimer": SYNTHETIC_DISCLAIMER,
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"Generated synthetic dataset: {dataset_path}")
    print(f"SHA-256: {sha256_hash}")
    print(f"Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
