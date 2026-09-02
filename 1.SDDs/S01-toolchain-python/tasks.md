# S01 — Project Setup & Python Toolchain · Tasks

Source: Quarter 1 (Foundation) of the IDP.

- [ ] **Create the repository structure** (`SDDs/`, `docs/`, `src/` with the
      `api/`, `agent/`, `rag/`, `mcp/`, `providers/`, `data/` subfolders
      aligned with S00's `architecture.md`).
- [ ] **Choose and configure a dependency manager** (`uv` or `poetry`), with a
      versioned lockfile; record the decision as an ADR.
- [ ] **Configure lint, formatter, and typing** (`ruff` + `mypy`) via
      `pyproject.toml`, with `mypy` in strict mode for `src/`.
- [ ] **Configure `pre-commit`** with `ruff format`, `ruff check --fix`, and
      `mypy` hooks, validated locally.
- [ ] **Configure the test environment** (`pytest` + `pytest-asyncio` +
      `pytest-cov`), with an example smoke test passing and an initial minimum
      coverage defined.
- [ ] **Create the base `Dockerfile`** (multi-stage) that successfully builds
      the Python application's image.
- [ ] **Create a minimal CI pipeline** that runs lint + type check + tests on
      every push/PR.
- [ ] **Document the local setup** in `README.md` (step by step: clone,
      install dependencies, enable pre-commit, run tests).
