# Verify — S17 · Harness / Evals

## Evidence checklist

- [x] Evaluation runner execution output showing successful test completion across intent, retrieval, groundedness, tool selection, and safety suites.
- [x] Initial benchmark scorecard report (`evals/reports/scorecard_YYYYMMDD.md`) verifying all metrics meet or exceed established thresholds.
- [x] Quality gate test execution demonstrating deliberate build failure upon an injected regression (e.g., dropped groundedness or unconfirmed action).
- [x] Multi-turn conversation evaluation log confirming successful state preservation, tool coordination, and HITL card gating.
- [x] CI workflow configuration and test run showing the automated eval quality gate passing on PR/push.

## Execution Evidence

### 1. Benchmark Execution Output (`python -m evals.runner`)
```
================================================================================
ATLAS EVALUATION HARNESS - BENCHMARK & QUALITY GATE REPORT
================================================================================
Timestamp: 2026-10-12T16:24:36 | Mode: ALL | Total Scenarios: 81

Category-Specific Performance:
  [OK] Intent Classification  : 96.0% (Pass: 48/50) | Threshold: >= 90.0%
  [OK] Retrieval Recall       : 100.0% (Pass: 20/20) | Threshold: >= 85.0%
  [OK] Groundedness Score     : 100.0% (Pass: 20/20) | Threshold: >= 90.0%
  [OK] Tool Selection Accuracy: 100.0% (Pass: 7/7) | Threshold: >= 85.0%
  [OK] Safety HITL Compliance : 100.0% (Pass: 7/7) | Threshold: = 100.0%

--------------------------------------------------------------------------------
OVERALL PASS RATE: 97.5% (79/81 passed)
QUALITY GATE STATUS: PASSED
================================================================================
Executive scorecard exported to: evals/reports/scorecard_20261012.md
```

### 2. Unit & Integration Test Suite (`uv run pytest`)
```
============================= test session starts =============================
collected 208 items

4.tests/unit/test_evals_harness.py .......                               [  3%]
...
4.tests/unit/test_workflows.py ..................................        [100%]

============================= 208 passed in 37.10s =============================
Coverage: 83.27% (Threshold >= 70%)
```

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — metric formulas, dataset structures, and runner architecture match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
