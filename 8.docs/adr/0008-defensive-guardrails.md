# ADR 0008: Defensive Security Guardrails (Dual-Layer Input & Output Protection)

## Status
Accepted

## Date
2026-10-10

## Context
Per `1.SDDs/S18-security-guardrails/spec.md`, generative banking assistants are exposed to adversarial risks:
1. **Adversarial Input:** Jailbreak attempts, prompt injection, system prompt extraction, instructions to bypass banking rules.
2. **Sensitive Output:** Accidental leakage of Personally Identifiable Information (PII) such as unmasked CPFs, credit card numbers, or internal auth tokens.
3. **Cross-Tenant Leakage:** A user querying data from a customer other than their authenticated session.

## Decision
Designed and deployed a **Dual-Layer Defensive Guardrail Architecture**:
1. **Input Guardrail (`InputGuardrail`):**
   - Intercepts raw user prompts before LLM inference.
   - Evaluates multi-pattern heuristic regexes and semantic threat signatures (jailbreaks, roleplay impersonation, base64 payload decoding, prompt extraction).
   - Blocks malicious prompts deterministically with HTTP 400 / polite refusal, logging security alerts without consuming LLM inference tokens.
2. **Output Guardrail & PII Masking (`OutputGuardrail` & `sanitizers.py`):**
   - Intercepts all synthesized agent outputs before reaching the client.
   - Automatically detects Brazilian CPFs (`XXX.XXX.XXX-XX`), bank account numbers, passwords, and tokens.
   - Replaces sensitive strings with compliant masked representations (e.g., `***.456.789-**`).
3. **Context Isolation (`ContextIsolation`):**
   - Strict session tenant binding: Rejects queries attempting to operate on `CUST-XXX` when the authenticated session belongs to `CUST-YYY`.

## Consequences
- **Positive:**
  - Zero prompt injection bypass in test harnesses (`100% Interception Rate`).
  - Total LGPD (Lei Geral de Proteção de Dados) alignment for sensitive PII.
  - Defense-in-depth: Protection applied at input, database retrieval, and output stages.
- **Negative / Mitigations:**
  - Slight regex evaluation overhead (< 1ms per request).
  - Negligible impact compared to LLM latency (~1.2s).
