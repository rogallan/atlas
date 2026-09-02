# S01 — Project Setup & Python Toolchain

Quarter: Q1 · Category: Foundation
Deliverable: `spec.md` + `plan.md` + `tasks.md` (this item) + a reproducible toolchain in the repository

## 1. Goal

Establish ATLAS's engineering foundation: repository structure, a reproducible
Python environment, automated code quality (lint/format/typing), tests, and a
minimal CI pipeline. This item delivers the base on which all code from S02
onward will be written — no product feature should start before S01 is
complete.

## 2. Context

ATLAS's backend is written mostly in Python (FastAPI, Agent, RAG, MCP,
providers). To sustain a senior-level project over four quarters, the
toolchain needs to be decided once, consistently, instead of growing
organically and generating technical debt.

This item directly follows the `constitution.md` and `architecture.md` defined
in S00: the folder structure created here must reflect the Front/API/Agent/
MCP/RAG/Infra boundaries already documented.

## 3. Scope

1. Repository structure (`SDDs/`, `docs/`, `src/`, and `src/` subfolders
   aligned with the architecture: `api/`, `agent/`, `rag/`, `mcp/`,
   `providers/`, `data/`).
2. Python dependency manager and virtual environment.
3. Lint, formatter, and type checking (e.g., `ruff` for lint/format, `mypy` for
   static typing) configured via `pre-commit`.
4. Test environment (`pytest`) with a defined minimum coverage.
5. Base `Dockerfile` for the Python application.
6. Minimal CI pipeline (lint + type check + tests running on every push/PR).

## 4. Out of scope

- Product code (API routes, agent, RAG, MCP) — that starts at S02+.
- Full Docker Compose with multiple services (Ollama, Vector DB) — that's
  covered in S20 (Docker Local Stack); here it's just the application's base
  `Dockerfile`.
- Cloud deployment CI/CD — that's covered in Q4 (S21/S22).

## 5. Suggested technical decisions

- **Package manager**: `uv` or `poetry` (decision recorded as an ADR in
  `docs/adr/`, with the reasoning behind the choice).
- **Python version**: 3.11+ (modern typing support, async performance).
- **Lint/format**: `ruff` (replaces flake8+black+isort with a single tool).
- **Type checking**: `mypy` in strict mode for the modules under `src/`.
- **Tests**: `pytest` + `pytest-asyncio` (the project uses FastAPI/async from
  S03 onward).
- **Pre-commit**: lint, format, and type-check hooks running before every
  commit.
- **Minimum coverage**: set an initial floor (e.g., 70%) that rises over the
  quarters, without locking Q1 into an unrealistic target.

## 6. Acceptance criteria

- [ ] `src/` structure created and aligned with `architecture.md` (S00).
- [ ] Reproducible Python environment (versioned lockfile, `README` with a
      step-by-step local setup guide).
- [ ] `ruff` and `mypy` configured and running without errors on the initial
      skeleton.
- [ ] `pre-commit` installed and validated locally.
- [ ] `pytest` configured, with at least one example test passing and a
      coverage metric being reported.
- [ ] Base `Dockerfile` builds the application image successfully.
- [ ] Minimal CI pipeline runs lint + type check + tests on every push/PR.
