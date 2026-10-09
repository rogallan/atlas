"""Interactive CLI demo for ATLAS MCP Tariff Server (S12).

Usage:
    uv run python 6.ops/demo_mcp_tariff.py
    uv run python 6.ops/demo_mcp_tariff.py --service withdrawal --channel branch_counter --used 4
    uv run python 6.ops/demo_mcp_tariff.py --service statement_30d --channel atm --used 2
"""

import argparse
import sys

from mcp.tariff.models import ChannelType
from mcp.tariff.server import create_tariff_server
from mcp.tariff.sync import verify_tariff_rag_consistency


def main() -> None:
    reconfigure_fn = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_fn) and sys.stdout.encoding.lower() != "utf-8":
        try:
            reconfigure_fn(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Tariff Server Demo")
    parser.add_argument(
        "--service",
        "-s",
        default="withdrawal",
        help="Service code (default: withdrawal)",
    )
    parser.add_argument(
        "--channel",
        "-c",
        default="atm",
        choices=["digital", "atm", "branch_counter"],
        help="Channel type (default: atm)",
    )
    parser.add_argument(
        "--used",
        "-u",
        type=int,
        default=4,
        help="Number of transactions already performed in the month (default: 4)",
    )
    parser.add_argument(
        "--segment",
        default=None,
        help="Customer segment filter for packages (e.g. retail, prime, private)",
    )
    args = parser.parse_args()

    server = create_tariff_server()

    print("=" * 70)
    print(">>> ATLAS MCP TARIFF SERVER — INTERACTIVE DEMO (S12)")
    print("=" * 70)

    # 1. Initialize Server & List Tools
    print("\n[STEP 1] Initializing MCP Tariff Server and listing capabilities...")
    init_resp = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    server_info = init_resp.get("result", {}).get("serverInfo", {})
    print(f"  [OK] Server: {server_info.get('name')} v{server_info.get('version')}")

    tools_resp = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tools_resp.get("result", {}).get("tools", [])
    print(f"  [OK] Registered MCP Tools ({len(tools)}):")
    for tool in tools:
        print(f"       - {tool['name']}: {tool['description'][:65]}...")

    # 2. Get Service Fee
    target_channel = ChannelType(args.channel)
    print(f"\n[STEP 2] Querying unit fee for '{args.service}' via '{target_channel.value}'...")
    try:
        fee_item = server.tools.get_service_fee(args.service, target_channel)
        print(f"  [OK] Serviço:          {fee_item.service_name}")
        print(f"  [OK] Canal:            {fee_item.channel.value.upper()}")
        print(f"  [OK] Tarifa Avulsa:    R$ {fee_item.unit_price:,.2f}")
        print(f"  [OK] É Essencial:      {'Sim' if fee_item.is_essential_service else 'Não'}")
        print(f"  [OK] Franquia Grátis:  {fee_item.monthly_free_quota or 0} / mês")
        print(f"  [OK] Base Legal:       {fee_item.regulatory_basis}")
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        return

    # 3. Check Quota
    print(f"\n[STEP 3] Evaluating essential services quota after {args.used} transações...")
    quota_res = server.tools.check_essential_services_quota(
        service_code=args.service,
        used_count=args.used,
        channel=target_channel,
    )
    status_label = "GRATUITO (Dentro da cota)" if quota_res.is_within_free_quota else "TARIFADO"
    print(f"  [STATUS]               {status_label}")
    print(f"  - Já utilizados:       {quota_res.used_count}")
    print(f"  - Limite gratuito:     {quota_res.free_quota_limit}")
    print(f"  - Cobrança nesta op:   R$ {quota_res.total_charge:,.2f}")

    # 4. Compare Packages
    print("\n[STEP 4] Comparing tariff packages and relationship fee waivers...")
    packages = server.tools.compare_packages(customer_segment=args.segment)
    for pkg in packages:
        print(f"\n  * [{pkg.package_id}] {pkg.name}")
        print(f"    Mensalidade:         R$ {pkg.monthly_price:,.2f} / mês")
        print(f"    Serviços Inclusos:   {pkg.included_services}")
        if pkg.waiver_conditions:
            print(f"    Regra de Isenção:    {pkg.waiver_conditions}")

    # 5. Cross-Consistency with RAG Document
    print("\n[STEP 5] Auditing cross-consistency between MCP Catalog & RAG Corpus...")
    audit = verify_tariff_rag_consistency()
    if audit["is_consistent"]:
        print("  [SUCCESS] 100% de consistência confirmada com o documento RAG:")
        for rule in audit["checked_rules"]:
            print(f"    [VERIFIED] {rule}")
    else:
        print("  [WARN] Inconsistências detectadas:")
        for err in audit["mismatches"]:
            print(f"    [DIFF] {err}")

    print("\n" + "=" * 70)
    print("[SUCCESS] Demonstração do MCP Tariff Server concluída com sucesso!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
