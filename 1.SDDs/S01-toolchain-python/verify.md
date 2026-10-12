# S01 — Project Setup & Python Toolchain · Verification

## Acceptance criteria (Definition of Done for this item)

- [x] The `src/{api,agent,rag,mcp,providers,data}` structure exists and is
      aligned with S00's `architecture.md` (located in `2.src/`).
- [x] `pyproject.toml` is versioned, with a committed dependency lockfile (`uv.lock`).
- [x] Running lint locally (`uv run ruff check`) returns no errors on the project's
      initial skeleton (0 issues).
- [x] Running type check locally (`uv run mypy`) returns no errors on the
      initial skeleton (Success: 10 files checked).
- [x] `uv run pre-commit run --all-files` passes with no failures (whitespace, EOF, yaml, large files, ruff, ruff-format, mypy all green).
- [x] `uv run pytest` runs successfully, with 2 passing smoke tests and a
      100% test coverage report being generated.
- [x] Base multi-stage `Dockerfile` created with non-root security and fast `uv` installation.
- [x] The CI workflow (`.github/workflows/ci.yml`) is configured to run lint, type check, and tests on push/PR.
- [x] `README.md` documents the local setup step by step with reproducible commands.

## Execution Evidence Log

1. **Package Manager & Lockfile**: `uv sync --all-extras` generated `uv.lock` with Python 3.11+ compatibility. Decision documented in `8.docs/adr/0001-package-manager.md`.
2. **Linting & Formatting**:
   ```text
   uv run ruff check
   All checks passed!
   uv run ruff format --check
   13 files already formatted
   ```
3. **Type Checking**:
   ```text
   uv run mypy
   Success: no issues found in 10 source files
   ```
4. **Test & Coverage Execution**:
   ```text
   uv run pytest
   2 passed in 0.22s
   Total coverage: 100.00% (Required minimum: 70%)
   ```
5. **Pre-commit Hooks**:
   ```text
   uv run pre-commit run --all-files
   trim trailing whitespace.................................................Passed
   fix end of files.........................................................Passed
   check yaml...............................................................Passed
   check for added large files..............................................Passed
   ruff.....................................................................Passed
   ruff-format..............................................................Passed
   mypy.....................................................................Passed
   ```
