"""Interactive CLI demonstration for MCP Customer Server (S08).

Usage:
    uv run python 6.ops/demo_mcp_customer.py
    uv run python 6.ops/demo_mcp_customer.py --customer CUST-0002
    uv run python 6.ops/demo_mcp_customer.py --list
"""

import argparse
import json
import sys

from mcp.customer.auth import AuthContext
from mcp.customer.server import create_customer_server


def main() -> None:
    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Customer Server Demo")
    parser.add_argument(
        "--customer",
        "-c",
        default="CUST-0001",
        help="Synthetic customer identifier (default: CUST-0001 - Dave Weckl)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available MCP tools and JSON Schemas",
    )
    parser.add_argument(
        "--role",
        "-r",
        default="relationship_manager",
        help="Simulated operator role (relationship_manager, analyst, admin, intern)",
    )
    args = parser.parse_args()

    server = create_customer_server()

    if args.list:
        print("\n=== Catalogo de Ferramentas MCP Registradas (tools/list) ===\n")
        tools = server.get_tool_definitions()
        for t in tools:
            print(f"[*] Ferramenta: {t['name']}")
            print(f"    Descricao:  {t['description']}")
            props = list(t["inputSchema"].get("properties", {}).keys())
            print(f"    Parametros: {props}\n")
        return

    auth_context = AuthContext(operator_id="OP-CLI-DEMO", role=args.role)

    print("\n" + "=" * 55)
    print(">>> ATLAS MCP Customer Server -- Demonstracao")
    print(f"    Operador: {auth_context.operator_id} | Perfil: {auth_context.role}")
    print(f"    Consultando Cliente: {args.customer}")
    print("=" * 55 + "\n")

    try:
        # 1. Profile
        print("[1/4] Executando 'get_customer_profile'...")
        profile = server.execute_tool(
            "get_customer_profile",
            {"customer_id": args.customer},
            auth_context=auth_context,
        )
        print(f"   Nome: {profile.full_name} | Segmento: {profile.segment.value.upper()}")
        print(f"   Renda Mensal: R$ {profile.monthly_income:,.2f}")
        print(f"   Score: {profile.credit_score} ({profile.credit_score_range}) | Risco: {profile.risk_rating}")
        print(f"   Anos de Relacionamento: {profile.relationship_years} anos\n")

        # 2. Accounts
        print("[2/4] Executando 'get_customer_accounts'...")
        accounts = server.execute_tool(
            "get_customer_accounts",
            {"customer_id": args.customer},
            auth_context=auth_context,
        )
        print(f"   Contas encontradas: {len(accounts)}")
        for acc in accounts:
            print(f"   - Conta {acc.account_number} ({acc.account_type.upper()}): R$ {acc.balance:,.2f} {acc.currency} [{acc.status}]")
        print()

        # 3. Financial History
        print("[3/4] Executando 'get_financial_history' (limite=3)...")
        history = server.execute_tool(
            "get_financial_history",
            {"customer_id": args.customer, "limit": 3},
            auth_context=auth_context,
        )
        print(f"   Ultimas {len(history)} transacoes:")
        for evt in history:
            print(f"   - [{evt.event_date[:10]}] {evt.category.upper()}: R$ {evt.amount:,.2f} -- {evt.description}")
        print()

        # 4. Summary
        print("[4/4] Executando 'get_customer_summary' (Briefing 360)...")
        summary = server.execute_tool(
            "get_customer_summary",
            {"customer_id": args.customer},
            auth_context=auth_context,
        )
        print(f"   Saldo Total Consolidado: R$ {summary.total_balance:,.2f}")
        print(f"   Contratos Ativos: {summary.active_contracts_count}")
        print(f"   Briefing do Gerente: \"{summary.relationship_notes}\"\n")

        # Audit logs inspection
        audit_entries = server.tools.security.audit_log
        print(f"[AUDIT] Trilha de Auditoria Gerada ({len(audit_entries)} eventos registrados):")
        for log in audit_entries:
            print(f"   [OK] [{log.timestamp[11:19]}] tool={log.tool} status={log.status} correlation_id={log.correlation_id[:8]}...")

        print("\n[SUCCESS] Consulta via MCP executada com sucesso!\n")

    except Exception as exc:
        print(f"\n[ERROR] Erro na execucao do MCP: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
