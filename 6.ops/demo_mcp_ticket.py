"""Interactive CLI demo for ATLAS MCP Ticket Server (S13).

Usage:
    uv run python 6.ops/demo_mcp_ticket.py
    uv run python 6.ops/demo_mcp_ticket.py --reject
    uv run python 6.ops/demo_mcp_ticket.py --customer-id CUST-002 --category limit_increase
"""

import argparse
import json
import sys

from mcp.ticket.models import ActionRejectedError, TicketCategory, TicketPriority
from mcp.ticket.server import create_ticket_server


def main() -> None:
    reconfigure_fn = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_fn) and sys.stdout.encoding.lower() != "utf-8":
        try:
            reconfigure_fn(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Ticket Server Demo (S13)")
    parser.add_argument(
        "--customer-id",
        "-c",
        default="CUST-001",
        help="Target synthetic customer ID (default: CUST-001)",
    )
    parser.add_argument(
        "--category",
        default="contestation",
        choices=[c.value for c in TicketCategory],
        help="Ticket category (default: contestation)",
    )
    parser.add_argument(
        "--title",
        default="Contestação de lançamento duplicado",
        help="Ticket subject title",
    )
    parser.add_argument(
        "--description",
        default="Cliente identificou cobrança duplicada de R$ 149,90 no cartão de débito.",
        help="Detailed ticket description",
    )
    parser.add_argument(
        "--priority",
        default="high",
        choices=[p.value for p in TicketPriority],
        help="Priority level (default: high)",
    )
    parser.add_argument(
        "--reject",
        action="store_true",
        help="Simulate human operator rejecting the ticket draft",
    )
    parser.add_argument(
        "--idempotency-key",
        default="demo-idem-key-001",
        help="Client idempotency key for deduplication",
    )
    args = parser.parse_args()

    server = create_ticket_server()

    print("=" * 70)
    print(">>> ATLAS MCP TICKET SERVER — INTERACTIVE DEMO (S13)")
    print("=" * 70)

    # 1. Initialize Server & List Tools
    print("\n[STEP 1] Initializing MCP Ticket Server and listing capabilities...")
    tools = server.get_tool_definitions()
    print(f"[OK] {len(tools)} tools registered:")
    for t in tools:
        print(f"  - {t['name']}: {t['description'][:80]}...")

    # 2. Phase 1: Prepare Ticket Draft (Human-in-the-Loop)
    print("\n[STEP 2] Phase 1: Invoking 'prepare_ticket' (Draft Preparation)...")
    draft = server.execute_tool(
        "prepare_ticket",
        {
            "customer_id": args.customer_id,
            "category": args.category,
            "title": args.title,
            "description": args.description,
            "priority": args.priority,
            "idempotency_key": args.idempotency_key,
        },
    )
    print("[OK] Ticket draft prepared successfully!")
    print(f"  Token:      {draft.confirmation_token}")
    print(f"  Customer:   {draft.customer_id}")
    print(f"  Category:   {draft.category.value}")
    print(f"  Priority:   {draft.priority.value}")
    print(f"  Expires At: {draft.expires_at.isoformat()}")
    print(f"  Human Card: {draft.summary_for_human}")

    # 3. Phase 2: Confirmation / Rejection
    if args.reject:
        print("\n[STEP 3] Simulating Human Operator REJECTION...")
        try:
            server.execute_tool(
                "confirm_and_create_ticket",
                {
                    "confirmation_token": draft.confirmation_token,
                    "approved_by_user": False,
                    "operator_id": "manager_001",
                },
            )
        except ActionRejectedError as exc:
            print(f"[BLOCKED AS EXPECTED] Guardrail stopped creation: {exc.message}")
    else:
        print("\n[STEP 3] Human Operator Confirms Action: 'confirm_and_create_ticket'...")
        ticket = server.execute_tool(
            "confirm_and_create_ticket",
            {
                "confirmation_token": draft.confirmation_token,
                "approved_by_user": True,
                "idempotency_key": args.idempotency_key,
                "operator_id": "manager_001",
            },
        )
        print("[OK] Ticket committed to persistent store!")
        print(f"  Ticket ID:  {ticket.ticket_id}")
        print(f"  Status:     {ticket.status.value}")
        print(f"  Operator:   {ticket.operator_id}")
        print(f"  Created At: {ticket.created_at.isoformat()}")

        # 4. Idempotency test
        print("\n[STEP 4] Testing Idempotency Protection (Re-submitting same key)...")
        # Prepare a new draft with same key
        draft2 = server.execute_tool(
            "prepare_ticket",
            {
                "customer_id": args.customer_id,
                "category": args.category,
                "title": args.title,
                "description": args.description,
                "idempotency_key": args.idempotency_key,
            },
        )
        ticket_replayed = server.execute_tool(
            "confirm_and_create_ticket",
            {
                "confirmation_token": draft2.confirmation_token,
                "approved_by_user": True,
                "idempotency_key": args.idempotency_key,
            },
        )
        print(f"[OK] Returned Ticket ID: {ticket_replayed.ticket_id}")
        assert ticket_replayed.ticket_id == ticket.ticket_id
        print("  -> Idempotency validated: No duplicate ticket generated!")

    # 5. List Customer Tickets
    print(f"\n[STEP 5] Querying customer ticket history for '{args.customer_id}'...")
    history = server.execute_tool(
        "list_customer_tickets",
        {"customer_id": args.customer_id},
    )
    print(f"[OK] Found {len(history)} ticket(s):")
    for t in history:
        print(f"  - [{t.ticket_id}] {t.category.value}: '{t.title}' ({t.status.value})")

    # 6. Audit Trail Verification
    print("\n[STEP 6] Inspecting Security Audit Trail...")
    events = server.tools.audit.get_events()
    print(f"[OK] Recorded {len(events)} structured audit event(s):")
    for ev in events:
        print(
            f"  [{ev['timestamp']}] Event: {ev['event']} | Approved: {ev['approved_by_human']} | Ticket: {ev.get('ticket_id')}"
        )

    print("\n" + "=" * 70)
    print(">>> DEMO COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
