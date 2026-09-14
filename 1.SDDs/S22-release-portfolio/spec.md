# Spec — S22 · Release / Portfolio

> **Domain:** Consolidation & Delivery · **Quarter:** Q4 · **Depends on:** S00–S21 (Complete ATLAS Catalog)

## 1. Goal

Consolidate the complete ATLAS Banking GenAI Copilot into a verified, production-ready Release Candidate (v1.0.0), validating end-to-end Definition of Done compliance across all 22 SDDs, generating the final comparative evaluation scorecard, ensuring strict security clearance (100% synthetic data, no leaked secrets), and publishing the public technical portfolio documentation, Architecture Decision Records (ADRs), and video demonstration scripts.

## 2. Context

Per `constitution.md` and `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, S22 represents the culmination of the 4-quarter Individual Development Plan (PDI) for the Senior GenAI Software Engineer specialization. It marks the transition from ongoing development to a reproducible, publicly referenceable portfolio project. This phase seals the repository with full governance, traceability between requirements and test evidence, clean demonstration scripts, and technical dissemination assets.

## 3. In scope

- Release Candidate preparation (semantic versioning `v1.0.0`, tag, release notes).
- End-to-End Definition of Done Audit:
  - Verification that every SDD (S00 to S22) has completed `spec.md`, `plan.md`, `tasks.md`, and signed-off `verify.md`.
  - All CI workflows passing (unit tests, contract tests, security scans, evaluation gates, IaC checks).
- Final Comparative Agent Evaluation Scorecard:
  - Benchmark run across all golden datasets (`golden_intents.json`, `golden_questions.json`, `golden_conversations.json`).
  - Scorecard publication comparing baseline vs. final performance (Intent Accuracy, Groundedness, Retrieval Recall, Latency, Tool Precision, Safety).
- Public Portfolio & Security Sanitization:
  - Pre-release security audit confirming 100% synthetic customer data and zero real credentials, API keys, or proprietary data in git history.
  - Finalization of Architecture Decision Records (`docs/adr/`) and technical runbooks (`docs/runbooks/`).
- Technical Content & Demo Assets:
  - End-to-end interactive demo walkthrough and recording script (`docs/portfolio/demo_script.md`).
  - Video series curriculum alignment with the 20 planned YouTube/LinkedIn episodes.
  - Project `README.md` update with badges, architectural diagrams, quickstart guide, and portfolio summary.

## 4. Out of scope

- Ongoing feature development or architectural redesigns (all feature scope is frozen at S21).
- Commercial deployment or live customer onboarding.
- Cloud hosting billing execution (AWS alternative is finalized as verified IaC in S21).

## 5. Requirements

- **R1. Traceability & DoD Sign-off:** Every item in the SDD catalog (S00 through S22) must have all tasks checked and all evidence verified in `verify.md`.
- **R2. Comprehensive Test Suite Execution:** The entire automated test pyramid (unit, contract, integration, adversarial, and IaC) must execute and pass with 0 failures:
  - `pytest 4.tests/` >= 80% code coverage.
  - `python -m evals.runner` meeting all quality thresholds (Intent >= 90%, Groundedness >= 90%, Recall >= 85%, Safety = 100%).
  - `terraform validate` and `checkov` passing.
- **R3. Zero Real Data / Secret Clearance:** Run automated credential and PII scanners (`gitleaks`, `trufflehog`) across repository history, ensuring zero private keys, tokens, or non-synthetic data exist.
- **R4. Consolidated Architecture Decision Records:** Ensure all critical technical choices made throughout Q1–Q4 are documented as finalized ADRs in `docs/adr/`.
- **R5. Portfolio Showcase & Documentation:** The root `README.md` and `docs/portfolio/` must provide a comprehensive showcase detailing the problem statement, system architecture, local-first design, interactive demo flow, and links to technical deep-dives.
- **R6. Release Tagging & Changelog:** Publish `CHANGELOG.md` detailing the delivery milestones across Q1–Q4, tagging Git release `v1.0.0`.

## 6. Acceptance criteria

- 100% of tasks across S00–S22 have signed-off evidence checklists.
- CI pipeline is completely green across linting, typing, unit/integration tests, evals, security, and Terraform plan.
- Automated secret and PII scan confirms zero leaks in git history.
- The final evaluation scorecard report (`evals/reports/final_scorecard_v1.0.0.md`) proves that ATLAS meets all target metrics.
- Complete documentation, demo script, and quickstart guide allow any engineer to clone and spin up the full stack in under 5 minutes.
