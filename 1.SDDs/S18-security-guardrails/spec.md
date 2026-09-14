# Spec — S18 · Security Guardrails

> **Domain:** Security & Governance · **Quarter:** Q3 · **Depends on:** S01 (Python Toolchain), S03 (FastAPI Gateway), S04 (Ollama Provider), S14 (Agent Graph)

## 1. Goal

Implement a comprehensive GenAI security defense-in-depth framework for the ATLAS banking copilot, addressing threat modeling, prompt injection defenses (direct user jailbreaks and indirect document injection), synthetic PII masking/sanitization in logs, least privilege enforcement for MCP tools, secret protection, and automated adversarial red-teaming test suites.

## 2. Context

Per `architecture.md`, `constitution.md` (Principle 2: "Security by default"), and the PDI catalog in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, banking conversational copilots face unique threat vectors: attackers attempting to hijack agent instructions, exfiltrate synthetic customer datasets, manipulate credit simulations, execute unapproved ticket actions, or leak secrets through logs and system prompts. S18 establishes formal security guardrails surrounding inputs, outputs, tool invocations, and observability pipelines.

## 3. In scope

- Formal Threat Model document (`docs/security/threat_model.md`) mapping OWASP Top 10 for LLM Applications (Prompt Injection, Insecure Output Handling, Sensitive Information Disclosure, Tool Abuse, Denial of Service).
- Input Security Guardrail (Prompt Injection & Jailbreak Filter):
  - Pattern and heuristic detection for prompt overrides, jailbreaks (e.g. DAN, roleplay bypasses), and delimiter manipulation.
  - Indirect prompt injection sanitization on retrieved RAG document chunks before injecting into prompt context.
- Output Security Guardrail:
  - Toxic / offensive content filter.
  - Secret and token scanner preventing internal system prompts, API keys, or raw SQL/credentials from leaking to the frontend.
- Data Privacy & Log Sanitization:
  - Structured log sanitizer masking sensitive identifiers (synthetic CPF/document numbers, account numbers, tokens).
- MCP Tool Least Privilege Policy:
  - Tool invocation authorization checks ensuring read-only tools cannot mutate state, and state-changing actions cannot execute without signed confirmation tokens.
- Adversarial Red-Teaming Test Suite (`tests/security/test_adversarial.py`) evaluating defensive robustness against automated attacks.

## 4. Out of scope

- Physical infrastructure hardening or AWS cloud IAM provisioning (represented via Terraform in S21).
- Corporate identity federation (OAuth2 / SAML / Active Directory) — uses simulated authentication per project scope.
- Hardware-level HSM or external KMS integrations.

## 5. Requirements

- **R1. Input Injection Defense:** Every incoming message must pass through a pre-execution security filter. Queries attempting to override system instructions or alter agent personas must be neutralized, returning a standardized security refusal.
- **R2. Indirect Prompt Injection Defense:** Text chunks retrieved from external documents (RAG) must be sanitized and isolated using secure prompt delimiters (e.g., XML `<context>` tags) with explicit instructions telling the LLM to ignore any meta-instructions found inside document bodies.
- **R3. Output Secret & Prompt Leakage Prevention:** The post-execution guardrail must inspect model responses, stripping out leaked system prompts, simulated bearer tokens, or internal error tracebacks before sending payloads to the Gateway.
- **R4. Log Sanitization:** Any log emitted by the application must automatically mask synthetic Brazilian sensitive numbers (e.g. CPF formatted as `***.***.123-**`, account numbers masked, bearer tokens redacted).
- **R5. Tool Least-Privilege & Boundary Enforcement:** MCP tool invocations must be bound to validated caller contexts. Unapproved actions must be blocked deterministically before reaching MCP execution layers.
- **R6. Adversarial Benchmark & Red Team Coverage:** Provide a dedicated test suite with at least 25 automated adversarial attack vectors (direct injection, indirect RAG injection, data exfiltration attempts, social engineering) achieving a 100% defense success rate.

## 6. Acceptance criteria

- 100% of tested direct prompt injection and jailbreak payloads in the adversarial test suite are successfully detected and blocked.
- Retrieved documents containing simulated malicious prompt instructions fail to hijack the model's behavior.
- Application logs contain zero unmasked synthetic CPFs, account numbers, or bearer tokens.
- Output filter guarantees that internal system prompts or secrets are never returned in `/v1/chat` responses.
- The threat model documentation (`docs/security/threat_model.md`) is approved and versioned.
