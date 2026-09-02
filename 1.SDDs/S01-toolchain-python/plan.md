# S01 — Project Setup & Python Toolchain · Technical Plan

## 1. Approach

Work in three sequential blocks: (1) folder structure and environment, (2)
automated quality (lint/format/typing/pre-commit), (3) tests + Docker + CI.
Each block ends with a quick verification before moving to the next.

## 2. Block 1 — Structure and environment

```
atlas/
├── src/
│   ├── api/          # (populated starting at S03)
│   ├── agent/         # (populated starting at S05/S14)
│   ├── rag/            # (populated starting at S06/S07)
│   ├── mcp/             # (populated starting at S08+)
│   ├── providers/        # (populated starting at S04)
│   └── data/               # (populated starting at S02)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── pyproject.toml   # dependencies, metadata, ruff/mypy/pytest config
├── uv.lock (or poetry.lock)
├── Dockerfile
└── .pre-commit-config.yaml
```

Each `src/` subfolder gets an empty `__init__.py` at this stage — the real
content arrives together with the corresponding catalog item (S02 → S14).

## 3. Block 2 — Automated quality

- `pyproject.toml` centralizes the configuration for `ruff` (lint + format)
  and `mypy` (strict type checking for everything under `src/`).
- `.pre-commit-config.yaml` runs, in this order: `ruff format`,
  `ruff check --fix`, `mypy`. A failure at any step blocks the commit.
- Record the package-manager choice (`uv` vs. `poetry`) as an ADR in
  `docs/adr/0001-package-manager.md`, with the pros/cons considered.

## 4. Block 3 — Tests, Docker, and CI

- `pytest.ini` (or a section in `pyproject.toml`) configuring
  `pytest-asyncio` in automatic mode, and `pytest-cov` for coverage
  reporting.
- An example test (`tests/unit/test_setup.py`) that simply confirms the
  package imports correctly — it acts as a smoke test for the environment.
- Multi-stage `Dockerfile`: a build stage installs dependencies, a final
  stage copies only what's needed for production (a lean image).
- Minimal CI (GitHub Actions or equivalent): a workflow that runs on every
  push/PR with the steps `ruff check`, `mypy`, `pytest --cov`.

## 5. Risks & mitigation

| Risk | Mitigation |
|---|---|
| Overly strict typing slows down the project early on | Start `mypy` in strict mode only for `src/`, not `tests/`; revisit strictness each quarter |
| Folder structure doesn't scale as MCP/Agent grow | The structure already reflects `architecture.md` (S00); any new module must be justified against that architecture |
| CI becomes slow and discourages frequent commits | Minimal CI runs only lint+type+unit tests; heavy integration/contract tests stay out of the PR CI at this stage |

## 6. Expected output

A repository with a `src/` skeleton, `pyproject.toml`,
`.pre-commit-config.yaml`, `Dockerfile`, `tests/` with a passing smoke test,
and a minimal CI workflow running successfully.
