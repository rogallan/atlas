# Spec — S13 · MCP Ticket Server

> **Domain:** MCP · **Quarter:** Q2 · **Depends on:** S01 (Python Toolchain), S02 (Synthetic Customer Base), S08 (MCP Customer Server)

## 1. Goal

Implement a typed Model Context Protocol (MCP) server managing the lifecycle of synthetic customer service tickets (tickets de atendimento / chamados de suporte), enforcing state-changing action policies, strict human confirmation (Human-in-the-Loop), full audit logging, and idempotency to prevent duplicate ticket creation.

## 2. Context

Per `architecture.md`, `constitution.md` (Principles 2 & 3: "Security by default" and "Explicit tools"), and the PDI operation map ("Ticket: MCP + aprovação"), opening a service ticket or initiating an operational request is a state-altering action. The copilot must never autonomously execute a ticket creation without explicit human approval from the relationship manager. The Ticket Server enforces a two-phase action pattern (Draft/Prepare → User Confirmation → Execute), assigns idempotent transaction tokens, maintains an audit trail, and records the resolution status in the synthetic database.

## 3. In scope

- MCP Server conforming to the Model Context Protocol specification.
- Typed action & query tools:
  - `prepare_ticket(customer_id: str, category: str, title: str, description: str, priority: str)`: Validates request data, generates a pending ticket draft, and returns a confirmation payload with a cryptographic `confirmation_token`.
  - `confirm_and_create_ticket(confirmation_token: str, approved_by_user: bool)`: Executes ticket creation only when `approved_by_user == True` with a valid, non-expired confirmation token.
  - `get_ticket(ticket_id: str)`: Returns current status, timestamps, operator, and ticket details.
  - `list_customer_tickets(customer_id: str)`: Returns tickets opened for a given synthetic customer.
- Idempotency protection (idempotency key prevents duplicate tickets upon network retries).
- Security Guardrail: Explicit rejection and audit logging of any attempt to execute ticket creation without valid human approval.
- Contract tests verifying the approval workflow, token expiration, idempotency, and schema compliance.

## 4. Out of scope

- Direct integration with third-party ticketing systems (Jira, ServiceNow, Zendesk).
- Automated customer messaging (SMS/WhatsApp) regarding ticket updates.
- Simulations of credit or insurance products (handled in S09, S10, and S11).

## 5. Requirements

- **R1. MCP Compliance:** Expose tools following standard MCP JSON-RPC protocol over stdio / local HTTP SSE transport.
- **R2. Human-in-the-Loop (Mandatory Approval):** State modification is forbidden in a single step. The system must prepare a proposal, receive human confirmation via `confirm_and_create_ticket`, and reject any direct unconfirmed creation.
- **R3. Idempotency:** Each ticket creation must be tagged with an `idempotency_key` (derived from token or provided by client). Multiple submissions with identical keys must return the original ticket without creating duplicates.
- **R4. Confirmation Token Expiration:** The `confirmation_token` generated during preparation must have a configurable TTL (e.g. 10 minutes) and become single-use once consumed or rejected.
- **R5. Full Audit Trail:** Every ticket event (preparation, approval, rejection, completion) must emit a structured audit log containing `operator_id`, `customer_id`, `ticket_id`, timestamp, and approval status.
- **R6. Categorization Taxonomy:** Validate ticket categories (e.g., `contestation`, `card_maintenance`, `limit_increase`, `general_inquiry`) and priority levels (`low`, `medium`, `high`, `urgent`).

## 6. Acceptance criteria

- MCP Ticket Server advertises `prepare_ticket`, `confirm_and_create_ticket`, `get_ticket`, and `list_customer_tickets` with complete JSON schemas.
- Attempting to execute `confirm_and_create_ticket` with `approved_by_user == False` or without an active token blocks creation and logs the rejection.
- Re-sending identical creation requests with the same idempotency key returns the existing ticket ID without spawning extra tickets.
- All lifecycle events generate structured audit records verifying that human approval preceded execution.
