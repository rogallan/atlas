# Spec — S15 · React Chat

> **Domain:** Product / FrontEnd · **Quarter:** Q3 · **Depends on:** S03 (FastAPI Gateway), S07 (RAG Retrieval), S08–S13 (MCP Servers), S14 (Agent Graph)

## 1. Goal

Build a modern, responsive React conversational user interface (React Chat) that connects bank relationship managers to the ATLAS copilot via the FastAPI Gateway (S03), providing real-time Server-Sent Events (SSE) streaming, interactive simulation cards, transparent citation/source drawers, controlled tool execution indicators, and an explicit human confirmation workflow for state-changing actions.

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 2, 4, 5: "Security by default", "Evidence before claims", "Tests before release"), and the lab environment in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, the front boundary is deployed externally on **Vercel** and connects to the local development environment via an **ngrok** tunnel (S16). The frontend represents the manager's primary touchpoint: it must render streamed text incrementally, display verifiable documentary sources, clearly present complex calculations (loans, insurance, consortium), and gate actions (e.g. ticket creation) with explicit user approval buttons.

## 3. In scope

- React SPA application (built with Vite + TypeScript).
- Real-time conversational interface with SSE streaming support (`POST /v1/chat`).
- Session management (`POST /v1/sessions` and local storage correlation).
- RAG Citation Drawer: interactive badges displaying norm references, article numbers, and source excerpts.
- Controlled Tool Status Badges: transparent status indicators (e.g., "Consultando perfil do cliente...", "Calculando simulação de crédito...") without exposing internal secrets or backend credentials.
- Financial Simulation Cards:
  - Loan Card (monthly installment, CET, amortization breakdown, disclaimer).
  - Insurance Card (coverages, deductibles, premium with IOF).
  - Consortium Card (common fund, admin fee, reserve fund, bid scenarios).
- Human-in-the-Loop Action Confirmation Card: interactive UI card with explicit "Confirmar" and "Cancelar" buttons for state-changing actions (S13 tickets).
- Robust Error Handling & Loading States: graceful connection retries, network offline banners, and standardized error messaging.
- Automated component tests and end-to-end Cypress/Playwright smoke tests.

## 4. Out of scope

- Backend business logic or direct database connections (all data passes through S03 FastAPI Gateway).
- Real authentication/SSO providers (uses simulated bearer token configured in S03).
- Direct Ollama or MCP communication from the browser.

## 5. Requirements

- **R1. Streaming UX:** Consume `POST /v1/chat` SSE stream and render markdown text incrementally with smooth auto-scroll.
- **R2. Citation & Source Grounding UI:** Whenever the response includes RAG citations, display clickable citation chips that open a detail drawer showing the exact Central Bank document title, norm reference, and excerpt.
- **R3. Simulation Cards:** Render structured data payloads as dedicated UI cards rather than raw markdown tables, displaying the mandatory non-binding simulation disclaimer prominently.
- **R4. Human-in-the-Loop Action Confirmation:** When an action proposal is returned by the agent (`requires_human_confirmation == True`), render an interactive card requiring the manager to click "Confirmar" or "Cancelar". The action is only dispatched upon user interaction.
- **R5. Tool Execution Transparency:** Display clean progress indicators indicating which capability is actively running, without leaking sensitive payload details.
- **R6. Error Resilience:** Display clear, friendly feedback when the backend is unreachable, ngrok tunnel is closed, or the request times out.

## 6. Acceptance criteria

- Conversational stream displays chunks progressively without freezing or UI jitter.
- Clicking a citation chip opens the source viewer displaying verifiable document metadata.
- Simulation outputs for loan, insurance, and consortium display dedicated formatted cards with disclaimers.
- Action confirmation workflow prompts the user and sends an approval event only after the button click.
- Automated frontend tests (unit + E2E) verify streaming, card rendering, and error state behavior.
