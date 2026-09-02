# S01 — Project Setup & Python Toolchain · Verification

## Acceptance criteria (Definition of Done for this item)

- [ ] The `src/{api,agent,rag,mcp,providers,data}` structure exists and is
      aligned with S00's `architecture.md`.
- [ ] `pyproject.toml` (or equivalent) is versioned, with a committed
      dependency lockfile.
- [ ] Running lint locally (`ruff check .`) returns no errors on the project's
      initial skeleton.
- [ ] Running type check locally (`mypy src/`) returns no errors on the
      initial skeleton.
- [ ] `pre-commit run --all-files` passes with no failures.
- [ ] `pytest --cov` runs successfully, with at least 1 passing test and a
      coverage report being generated.
- [ ] `docker build .` completes successfully from the base `Dockerfile`.
- [ ] The CI workflow runs automatically on a test push/PR and all steps
      (lint, type check, tests) finish green.
- [ ] `README.md` documents the local setup step by step, and someone new to
      the project can reproduce the environment by following only those
      instructions.

## How to verify

1. Clone the repository into a clean folder and follow only the `README.md`
   to set up the environment — with no prior knowledge of the project.
2. Run, in this order: `ruff check .`, `mypy src/`, `pytest --cov`,
   `docker build .`.
3. Open a test PR (e.g., changing a comment) and confirm CI triggers and
   completes successfully.
4. Mark this item as complete in the IDP checklist (section 14) only after
   the 3 steps above are confirmed.
