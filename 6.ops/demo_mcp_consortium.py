"""Interactive CLI demo for ATLAS MCP Consortium Server (S11).

Usage:
    uv run python 6.ops/demo_mcp_consortium.py
    uv run python 6.ops/demo_mcp_consortium.py --segment real_estate --credit 300000 --term 180 --bid 0.25
    uv run python 6.ops/demo_mcp_consortium.py --segment automotive --credit 90000 --term 60 --bid 0.20
"""

import argparse
import sys

from mcp.consortium.models import ConsortiumSegment, ConsortiumSimulationResult
from mcp.consortium.server import create_consortium_server


def main() -> None:
    reconfigure_fn = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_fn) and sys.stdout.encoding.lower() != "utf-8":
        try:
            reconfigure_fn(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Consortium Server Demo")
    parser.add_argument(
        "--segment",
        "-s",
        default="automotive",
        choices=["real_estate", "automotive", "services"],
        help="Consortium segment (default: automotive)",
    )
    parser.add_argument(
        "--credit",
        "-c",
        type=float,
        default=80000.0,
        help="Desired letter of credit in BRL (default: 80000.0)",
    )
    parser.add_argument(
        "--term",
        "-t",
        type=int,
        default=60,
        help="Contract duration in months (default: 60)",
    )
    parser.add_argument(
        "--bid",
        "-b",
        type=float,
        default=0.20,
        help="Simulated embedded bid ratio (default: 0.20 for 20%%)",
    )
    args = parser.parse_args()

    server = create_consortium_server()

    print("=" * 70)
    print(">>> ATLAS MCP CONSORTIUM SERVER — INTERACTIVE DEMO (S11)")
    print("=" * 70)

    # 1. Initialize Server & List Tools
    print("\n[STEP 1] Initializing MCP Consortium Server and listing capabilities...")
    init_resp = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    server_info = init_resp.get("result", {}).get("serverInfo", {})
    print(f"  [OK] Server: {server_info.get('name')} v{server_info.get('version')}")

    tools_resp = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"  [OK] Registered MCP Tools ({len(tools)}):")
    for tool in tools:
        print(f"       - {tool['name']}: {tool['description'][:65]}...")

    # 2. List Modalities
    print("\n[STEP 2] Querying active consortium catalog (list_consortium_modalities)...")
    modalities = server.tools.list_consortium_modalities()
    for mod in modalities:
        terms_str = "/".join(str(t) for t in mod.allowed_terms_months)
        print(
            f"  - [{mod.segment:<12}] {mod.display_name:<30} "
            f"Faixa: R$ {mod.min_credit:>8,.0f} a R$ {mod.max_credit:>9,.0f} "
            f"| Prazos: {terms_str}m | Taxa Adm: {mod.total_admin_fee_pct * 100:.1f}%"
        )

    # 3. Query Group Rules
    target_segment = ConsortiumSegment(args.segment)
    print(f"\n[STEP 3] Inspecting group rules for '{target_segment.value}'...")
    rules = server.tools.get_consortium_group_rules(target_segment)
    print(f"  [OK] Modalidade:           {rules.display_name}")
    print(f"  [OK] Taxa Administração:   {rules.total_admin_fee_pct * 100:.1f}% total")
    print(f"  [OK] Fundo de Reserva:     {rules.reserve_fund_pct * 100:.1f}% total")
    print(f"  [OK] Lance Embutido Máx:   Até {rules.max_embedded_bid_pct * 100:.0f}% da carta")
    print(f"  [OK] Prazos do Grupo:      {rules.allowed_terms_months} meses")

    # 4. Run Simulation
    print(
        f"\n[STEP 4] Simulating consortium quota for R$ {args.credit:,.2f} em {args.term}m "
        f"com lance de {args.bid * 100:.1f}%..."
    )

    try:
        quote: ConsortiumSimulationResult = server.tools.simulate_consortium(
            modality=target_segment,
            credit_amount=args.credit,
            term_months=args.term,
            embedded_bid_pct=args.bid,
        )

        print("\n" + "=" * 70)
        print(f" RESULTADO DA SIMULAÇÃO — {quote.display_name.upper()}")
        print("=" * 70)
        print(f"  Modalidade:         {quote.display_name} ({quote.segment})")
        print(f"  Carta de Crédito:   R$ {quote.credit_amount:,.2f}")
        print(f"  Prazo Contratado:   {quote.term_months} meses")
        print("-" * 70)
        print("  COMPOSIÇÃO DA PARCELA MENSAL (Sem Lance):")
        print(f"    - Fundo Comum:        R$ {quote.installments.common_fund_amount:>10,.2f}")
        print(f"    - Taxa Administração: R$ {quote.installments.admin_fee_amount:>10,.2f}")
        print(f"    - Fundo de Reserva:   R$ {quote.installments.reserve_fund_amount:>10,.2f}")
        print(f"    = PARCELA MENSAL:     R$ {quote.installments.monthly_total:>10,.2f}")
        print("-" * 70)
        print(f"  Custo Total Nominal:    R$ {quote.total_payable_amount:>10,.2f}")
        print(f"  Total de Encargos:      R$ {quote.total_fees_amount:>10,.2f}")
        print(f"  Custo Financeiro Total: {quote.total_cost_percentage:.2f}% (Sem juros bancários)")

        if quote.simulated_bid_amount:
            print("-" * 70)
            print("  PROJEÇÃO DE LANCE EMBUTIDO:")
            print(
                f"    - Lance Ofertado:     R$ {quote.simulated_bid_amount:>10,.2f} "
                f"({args.bid * 100:.1f}%)"
            )
            if quote.net_credit_with_embedded_bid:
                print(
                    f"    - Crédito Líquido:    R$ {quote.net_credit_with_embedded_bid:>10,.2f}"
                )
            if quote.post_bid_installment_estimate:
                print(
                    f"    - Nova Parcela Reduz: R$ {quote.post_bid_installment_estimate:>10,.2f} "
                    f"/ mês"
                )

        print("-" * 70)
        print(f"  AVISO LEGAL OBRIGATÓRIO:\n  \"{quote.disclaimer}\"")
        print("=" * 70)
        print("[SUCCESS] Demonstração concluída com sucesso!\n")

    except Exception as exc:
        print(f"\n[ERROR] Falha ao simular consórcio: {exc}")


if __name__ == "__main__":
    main()
