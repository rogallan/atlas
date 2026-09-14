# Spec — S17 · Harness / Evals

> **Domain:** Quality & Evaluation · **Quarter:** Q3 · **Depends on:** S01 (Python Toolchain), S04 (Ollama Provider), S05 (Intent Router), S06/S07 (RAG), S08–S13 (MCP Servers), S14 (Agent Graph)

## 1. Goal

Build an automated evaluation harness and regression testing framework for the ATLAS copilot, establishing curated golden datasets, multi-turn golden conversations, metric collectors (Retrieval Recall/MRR, Groundedness/Faithfulness, Tool Selection Accuracy, Latency), and CI quality gates to systematically prevent regressions in prompts, models, or agent graph logic.

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 4 & 5: "Evidence before claims" and "Tests before release"), and the PDI plan in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, GenAI applications cannot rely on intuition or manual spot-checks. The Harness / Evals framework provides quantitative, reproducible scorecards comparing agent versions, prompt adjustments, and local model updates (e.g. swapping Ollama quantized checkpoints) against standardized benchmarks.

## 3. In scope

- Evaluation Harness runner CLI (`python -m evals.runner` or pytest-evals plugin).
- Curated Datasets:
  - `golden_intents.json`: Baseline intent classification queries (S05).
  - `golden_questions.json`: Regulatory and public knowledge RAG benchmarks (S07).
  - `golden_conversations.json`: Multi-turn conversational scenarios covering customer queries, credit/insurance simulations, ticket creation approval, and adversarial prompts.
- Quantitative Metrics:
  - Retrieval: Context Recall@k, Context Precision@k, MRR.
  - Generation: Faithfulness / Groundedness (detecting hallucinations), Answer Relevance.
  - Agentic: Tool Selection Precision/Recall, Parameter Extraction Accuracy, Action Safety (blocking unconfirmed state changes).
  - Performance: End-to-end latency, tokens generated, time-to-first-token.
- Comparative Scorecards & Reports: Markdown and JSON summary reports generated after every benchmark run.
- CI/CD Quality Gate: Automated evaluation step failing the build if accuracy or groundedness drops below target thresholds.

## 4. Out of scope

- Real-time online production observability, tracing, and log ingestion (covered in S19 Observability).
- Red-team prompt injection generation and penetration attack suites (covered in S18 Security Guardrails).
- Human feedback annotator UI / crowdsourcing platform.

## 5. Requirements

- **R1. Local-First Evaluation Runner:** The harness must run completely in the local environment using the local Ollama provider or mocked determinism fixtures without cloud dependencies.
- **R2. Comprehensive Golden Conversations:** Golden datasets must represent realistic banking relationship manager dialogues across all 5 intents and all domain services (loan, insurance, consortium, tariff, ticket).
- **R3. Automated Metric Calculation:** Implement programmatic evaluators:
  - *Groundedness Evaluator:* Measures the percentage of factual claims in answers that are directly substantiated by retrieved context chunks or tool returns.
  - *Tool Selection Evaluator:* Compares actual MCP tool calls against expected tool signatures and parameter values.
  - *Safety Guardrail Evaluator:* Verifies that 100% of state-changing ticket actions pause for human approval.
- **R4. Deterministic Scoring & Versioning:** Evaluation datasets must be versioned in `evals/data/`. Scoring formulas must be deterministic and reproducible across repeated runs with identical model seeds.
- **R5. Quality Gate Enforcement:** Provide a threshold checker that exits with a non-zero code if:
  - Intent Accuracy < 90%
  - Retrieval Recall@k < 85%
  - Groundedness Score < 90%
  - Safety / HITL Confirmation < 100%
- **R6. Executive Scorecard Output:** Generate comparative markdown reports (`evals/reports/scorecard_YYYYMMDD.md`) summarizing metric benchmarks, passing rates, and failure regressions.

## 6. Acceptance criteria

- Evaluation runner executes all benchmark suites via a single terminal command.
- Quality gate correctly identifies and fails deliberate regressions (e.g. injected hallucinations, invalid tool calls).
- Baseline execution on current codebase produces a complete scorecard meeting or exceeding defined thresholds.
- Multi-turn golden conversations validate state retention and human-in-the-loop action workflows.
