# Verify — S02 · Synthetic Customer Base

## Evidence checklist

- [x] Test run showing schema and consistency tests passing (8 unit tests green).
- [x] Reproducibility check: two generation runs with the same seed produce identical output
      (hash comparison recorded: `cac313f4d49688a62aef58b71794ad171060d19ba5938717e90b3eb281fa426a`).
- [x] Manual review confirming no entity resembles a real person or institution:
      all emails end with `@simulado.atlas.local`, doc hashes are simulated 16-hex characters.
- [x] `manifest.json` documenting the seed (42), version (1.0.0), entity counts, and SHA-256 hash.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R5) satisfied.
- [x] Reviewed against `plan.md` — entity model and generation strategy match what was implemented.
- [x] No task in `tasks.md` is checked without corresponding evidence above.

## Execution Evidence Log

1. **Schema & Referential Integrity Tests**:
   - `test_dataset_generation_and_schema_validation`
   - `test_referential_integrity` (Account -> Customer, Contract -> Customer/Product, Event -> Account, History -> Customer)
   - `test_reproducibility_deterministic_seed`
   - `test_synthetic_privacy_invariants`
   - `test_persisted_fixture_matches_manifest`
   - `test_generate_script_execution`
   - Result: `8 passed in 0.60s`, Total coverage: `99.16%`.

2. **Lint & Static Type Check**:
   - `uv run ruff check` -> `All checks passed!`
   - `uv run mypy` -> `Success: no issues found in 14 source files`

3. **Pre-commit Hooks**:
   - `uv run pre-commit run` -> `All hooks passed (trailing-whitespace, end-of-file-fixer, check-added-large-files, ruff, ruff-format, mypy)`.
