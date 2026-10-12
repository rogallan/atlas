# ADR 0007: Human-in-the-Loop (HITL) Critical Action Approval Pattern

## Status
Accepted

## Date
2026-10-10

## Context
Per `constitution.md` (Principle 2: Security by Default; Principle 3: Explicit Tools) and banking compliance standards, an autonomous AI agent must **never** execute high-impact, state-changing operations without affirmative human authorization.

Sensitive operational domains in ATLAS:
1. Support ticket creation, cancellation, or modification.
2. Credit card or account limit increases.
3. Formal dispute registration or financial transaction staging.

## Decision
Implemented a deterministic two-turn **Human-in-the-Loop (HITL) Action Card Pattern**:
1. **Stage 1 — Intent Detection & Staging:**
   - Agent router identifies an `action` intent.
   - The agent prepares an execution draft payload (tool arguments, affected customer ID, action impact summary).
   - Generates a cryptographically secure, time-bounded confirmation token (`confirmation_token`).
   - The response flags `requires_human_confirmation: True`, pauses graph execution, and renders an interactive HITL card on the frontend.
2. **Stage 2 — Affirmative Confirmation or Cancellation:**
   - The user must explicitly approve or reject the action.
   - On approval: Frontend posts back the `confirmation_token` with approval flag.
   - On rejection: Action is dropped, audit log records refusal, and no tool executes.
   - Graph verifies token authenticity and executes the tool only upon valid human approval.

## Consequences
- **Positive:**
  - 100% compliance with safety quality gates (`Safety / HITL Compliance = 100%`).
  - Total prevention of unauthorized state mutation or agent hallucination side effects.
  - Full audit trail: Every confirmed or rejected action is logged with user session metadata.
- **Negative / Mitigations:**
  - Requires a two-step conversational round-trip for action execution.
  - Necessary trade-off for regulatory security and banking risk governance.
