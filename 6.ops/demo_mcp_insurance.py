"""Interactive CLI demo for ATLAS MCP Insurance Server (S10).

Usage:
    uv run python 6.ops/demo_mcp_insurance.py
    uv run python 6.ops/demo_mcp_insurance.py --customer CUST-0001 --product life_individual --capital 200000
    uv run python 6.ops/demo_mcp_insurance.py --product home_complete --capital 500000 --coverages theft_robbery,electrical_damage
"""

import argparse
import sys

from mcp.customer.repository import CustomerRepository
from mcp.insurance.models import InsuranceQuoteResult
from mcp.insurance.server import create_insurance_server


def main() -> None:
    reconfigure_fn = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_fn) and sys.stdout.encoding.lower() != "utf-8":
        try:
            reconfigure_fn(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Insurance Server Demo")
    parser.add_argument(
        "--customer",
        "-c",
        default="CUST-0001",
        help="Synthetic customer identifier (default: CUST-0001 - Dave Weckl)",
    )
    parser.add_argument(
        "--product",
        "-p",
        default="life_individual",
        help="Insurance product ID (default: life_individual)",
    )
    parser.add_argument(
        "--capital",
        "-k",
        type=float,
        default=150000.0,
        help="Desired insured capital in BRL (default: 150000.0)",
    )
    parser.add_argument(
        "--coverages",
        default="critical_illness,accidental_disability",
        help="Comma-separated optional coverage codes (e.g. critical_illness,accidental_disability)",
    )
    args = parser.parse_args()

    repo = CustomerRepository()
    server = create_insurance_server(customer_repository=repo)

    print("=" * 70)
    print(">>> ATLAS MCP INSURANCE SERVER — INTERACTIVE DEMO (S10)")
    print("=" * 70)

    # 1. MCP Initialization & Tools List
    print("\n[STEP 1] Initializing MCP Insurance Server and listing capabilities...")
    init_resp = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    server_info = init_resp.get("result", {}).get("serverInfo", {})
    print(f"  [OK] Server: {server_info.get('name')} v{server_info.get('version')}")

    tools_resp = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"  [OK] Registered MCP Tools ({len(tools)}):")
    for tool in tools:
        print(f"       - {tool['name']}: {tool['description'][:65]}...")

    # 2. List Products
    print("\n[STEP 2] Querying active insurance catalog (list_insurance_products)...")
    products = server.tools.list_insurance_products()
    for prod in products:
        print(
            f"  - [{prod.product_id}] {prod.name:<32} "
            f"Faixa: R$ {prod.min_capital:>8,.0f} a R$ {prod.max_capital:>9,.0f} "
            f"| IOF: {prod.iof_rate * 100:.2f}%"
        )

    # 3. Customer Context
    print(f"\n[STEP 3] Inspecting customer profile for {args.customer}...")
    customer = repo.get_customer(args.customer)
    if customer:
        print(f"  [OK] Nome:        {customer.name}")
        print(f"  [OK] Segmento:    {customer.segment.value.upper()}")
        print(f"  [OK] Score:       {customer.credit_score}")
        print(f"  [OK] Renda:       R$ {float(customer.income_monthly):,.2f}")
    else:
        print(f"  [WARN] Cliente {args.customer} não encontrado no banco sintético.")

    # 4. Coverage details
    print(f"\n[STEP 4] Querying coverage rules for product '{args.product}'...")
    try:
        coverages = server.tools.get_coverage_details(args.product)
        for cov in coverages:
            status = "[OBRIGAT]" if cov.is_mandatory else "[OPCIONAL]"
            print(
                f"  {status:<10} {cov.name:<32} "
                f"LMI: R$ {cov.max_indemnity_limit:>10,.0f} | Taxa: {cov.rate_factor * 10000:.1f} bps"
            )
            if cov.deductible_info:
                print(f"             Regra/Franquia: {cov.deductible_info}")
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        return

    # 5. Quote Simulation
    optional_list = [c.strip() for c in args.coverages.split(",") if c.strip()]
    print(
        f"\n[STEP 5] Simulating insurance quote for R$ {args.capital:,.2f} "
        f"com opcionais: {optional_list}..."
    )

    try:
        quote: InsuranceQuoteResult = server.tools.simulate_insurance_quote(
            customer_id=args.customer,
            product_id=args.product,
            insured_capital=args.capital,
            optional_coverages=optional_list,
        )

        print("\n" + "=" * 70)
        print(f" RESULTADO DA COTAÇÃO — {quote.product_name.upper()}")
        print("=" * 70)
        print(f"  Produto:            {quote.product_name} ({quote.product_id})")
        print(f"  Capital Segurado:   R$ {quote.insured_capital:,.2f}")
        print(f"  Cliente:            {quote.customer_id or 'Não informado'}")
        print("-" * 70)
        print("  COBERTURAS CONTRATADAS:")
        for cov in quote.included_coverages:
            mand = "Básica" if cov.is_mandatory else "Adicional"
            print(f"    - {cov.name:<34} [{mand}] LMI: R$ {cov.max_indemnity_limit:,.2f}")
        print("-" * 70)
        print(f"  Prêmio Líquido:     R$ {quote.net_monthly_premium:>10,.2f} / mês")
        print(f"  IOF Mensal:         R$ {quote.estimated_iof:>10,.2f} ({quote.iof_rate*100:.2f}%)")
        print(f"  PRÊMIO TOTAL MÊS:   R$ {quote.monthly_premium:>10,.2f} / mês")
        print(f"  PRÊMIO TOTAL ANO:   R$ {quote.annual_premium:>10,.2f} / ano (à vista c/ 5% desc.)")
        print("-" * 70)
        print("  PREMISSAS ATUARIAIS:")
        for k, v in quote.underwriting_premises.items():
            print(f"    * {k}: {v}")
        print("-" * 70)
        print(f"  DISCLAIMER OBRIGATÓRIO:\n  \"{quote.disclaimer}\"")
        print("=" * 70)
        print("[SUCCESS] Demonstração concluída com sucesso!\n")

    except Exception as exc:
        print(f"\n[ERROR] Falha ao simular cotação: {exc}")


if __name__ == "__main__":
    main()
