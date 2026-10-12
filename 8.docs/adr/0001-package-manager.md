# ADR 0001 — Package and Dependency Manager Selection: uv

- **Status:** Accepted
- **Date:** 2026-10-06
- **Context:** S01 — Project Setup & Python Toolchain
- **Author:** ATLAS Team (bmad-architect)

## 1. Context and Problem Statement

ATLAS requires a robust, reproducible, and modern dependency and environment management toolchain for Python 3.11+. The project integrates several complex components: FastAPI, LangGraph/Agent orchestrators, Ollama client, MCP SDKs, vector database clients, and testing/evaluation harnesses.

We evaluated two candidates recommended by the project specification:
1. **uv** (Astral)
2. **Poetry**

## 2. Decision

We chose **`uv`** as the official dependency, project, and toolchain manager for ATLAS.

## 3. Rationale & Comparison

| Criteria | `uv` | `Poetry` |
|---|---|---|
| **Speed** | 10x–100x faster resolution and installation (written in Rust) | Slower resolver on large dependency graphs |
| **Python Version Management** | Built-in Python installation and management (`uv python install`) | Requires external tools (pyenv, asdf, etc.) |
| **PEP Compliance** | Native adherence to standard `pyproject.toml` (PEP 517, PEP 518, PEP 621) | Custom sections and non-standard dependency specification |
| **Tool Execution** | Replaces `pipx` via `uvx` / `uv run` for linters, formatters, and test runners | Requires `poetry run` with virtualenv overhead |
| **Lockfile Determinism** | Universal `uv.lock` platform-independent resolution | `poetry.lock` |
| **Container & CI Build Speed** | Extremely fast in multi-stage Docker builds with wheel caching | Significantly longer build times in CI |

## 4. Consequences

### Positive
- Unified toolchain: `uv` manages Python versions, virtual environments, package locking, and command execution.
- Deterministic builds across Windows local development, Linux Docker containers, and GitHub Actions CI.
- Compatible with standard tools (`ruff`, `mypy`, `pytest`).

### Negative / Trade-offs
- Newer tool compared to Poetry; teammates unfamiliar with `uv` will need a short onboarding curve (documented in `README.md`).

## 5. References
- S01 Specification: `1.SDDs/S01-toolchain-python/spec.md`
- Astral uv Documentation: https://docs.astral.sh/uv/
