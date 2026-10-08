"""Interactive CLI demonstration for MCP Loan Server (S09).

Usage:
    uv run python 6.ops/demo_mcp_loan.py
    uv run python 6.ops/demo_mcp_loan.py --amount 25000 --term 36 --customer CUST-0008
    uv run python 6.ops/demo_mcp_loan.py --modality payroll_loan
    uv run python 6.ops/demo_mcp_loan.py --list
"""

import argparse
import sys

from mcp.loan.models import LoanModality
from mcp.loan.server import create_loan_server


def main() -> None:
    reconfigure_fn = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_fn) and sys.stdout.encoding.lower() != "utf-8":
        try:
            reconfigure_fn(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="ATLAS MCP Loan Server Demo")
    parser.add_argument(
        "--customer",
        "-c",
        default="CUST-0001",
        help="Synthetic customer identifier (default: CUST-0001 - Dave Weckl)",
    )
    parser.add_argument(
        "--amount",
        "-a",
        type=float,
        default=10000.0,
        help="Loan principal amount in BRL (default: 10000.0)",
    )
    parser.add_argument(
        "--term",
        "-t",
        type=int,
        default=24,
        help="Financing term in months (default: 24)",
    )
    parser.add_argument(
        "--modality",
        "-m",
        default="personal_credit",
        choices=["personal_credit", "payroll_loan", "working_capital"],
        help="Credit modality (personal_credit, payroll_loan, working_capital)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available loan modalities and benchmark interest rates",
    )
    args = parser.parse_args()

    server = create_loan_server()

    if args.list:
        print("\n=== Catalogo de Modalidades de Credito (get_loan_modalities) ===\n")
        modalities = server.execute_tool("get_loan_modalities", {})
        for m in modalities:
            print(f"[*] {m.display_name} ({m.modality.value})")
            print(f"    Faixa de Valor: R$ {m.min_amount:,.2f} ate R$ {m.max_amount:,.2f}")
            print(f"    Prazo:          {m.min_term_months} a {m.max_term_months} meses")
            print(f"    Taxa de Juros:  {m.monthly_interest_rate * 100:.2f}% a.m. ({m.annual_interest_rate * 100:.2f}% a.a.)")
            print(f"    Margem Maxima:  {m.max_debt_income_ratio * 100:.0f}% da renda")
            print(f"    Descricao:      {m.description}\n")
        return

    print("\n" + "=" * 60)
    print(">>> ATLAS MCP Loan Server -- Demonstracao de Simulacao")
    print(f"    Cliente:    {args.customer}")
    print(f"    Modalidade: {args.modality}")
    print(f"    Valor:      R$ {args.amount:,.2f} em {args.term} parcelas")
    print("=" * 60 + "\n")

    try:
        # 1. Simulação completa
        print("[1/2] Executando 'simulate_loan' (Tabela Price, IOF, CET)...")
        sim_result = server.execute_tool(
            "simulate_loan",
            {
                "customer_id": args.customer,
                "amount": args.amount,
                "term_months": args.term,
                "modality": args.modality,
            },
        )

        print(f"\n   Produto:               {sim_result.modality_display_name}")
        print(f"   Valor Solicitado:      R$ {sim_result.requested_amount:,.2f}")
        print(f"   IOF Estimado:          R$ {sim_result.estimated_iof:,.2f}")
        print(f"   Prazo:                 {sim_result.term_months} meses")
        print(f"   Parcela Mensal (PMT):  R$ {sim_result.monthly_installment:,.2f}")
        print(f"   Taxa Nominal:          {sim_result.monthly_interest_rate * 100:.2f}% a.m. ({sim_result.annual_interest_rate * 100:.2f}% a.a.)")
        print(f"   CET Anualizado:        {sim_result.annual_cet * 100:.2f}% a.a.")
        print(f"   Total de Juros:        R$ {sim_result.total_interest:,.2f}")
        print(f"   Total a Pagar:         R$ {sim_result.total_amount_payable:,.2f}\n")

        # Margem de renda
        if sim_result.customer_monthly_income:
            income = sim_result.customer_monthly_income
            ratio_pct = (sim_result.debt_to_income_ratio or 0) * 100
            limit_pct = sim_result.margin_limit_ratio * 100
            status_margin = "[OK - Dentro da margem]" if sim_result.is_within_margin else "[ALERTA - Excede margem]"
            print(f"   Renda Mensal do Cliente: R$ {income:,.2f}")
            print(f"   Comprometimento de Renda: {ratio_pct:.1f}% (Limite: {limit_pct:.0f}%) {status_margin}\n")

        # Cronograma de amortização
        print("   Resumo do Cronograma de Amortizacao (Tabela Price):")
        print("   Mes |   Parcela   |    Juros    | Amortizacao | Saldo Devedor")
        print("   ----+-------------+-------------+-------------+--------------")
        for item in sim_result.schedule_summary:
            print(
                f"   {item.month:3d} | R$ {item.installment:8.2f} | R$ {item.interest:8.2f} "
                f"| R$ {item.amortization:8.2f} | R$ {item.remaining_balance:10.2f}"
            )
        print()

        # 2. Avaliação de pré-condições
        print("[2/2] Executando 'check_loan_pre_conditions'...")
        check_result = server.execute_tool(
            "check_loan_pre_conditions",
            {
                "customer_id": args.customer,
                "monthly_installment": sim_result.monthly_installment,
                "modality": args.modality,
            },
        )
        print(f"   Status Elegibilidade: {'APROVADO NA MARGEM' if check_result.is_eligible else 'REPROVADO NA MARGEM'}")
        print(f"   Parecer: \"{check_result.message}\"\n")

        print("------------------------------------------------------------")
        print(f"AVISO CONSTITUCIONAL: \"{sim_result.disclaimer}\"")
        print("------------------------------------------------------------\n")
        print("[SUCCESS] Simulacao MCP concluida com sucesso!\n")

    except Exception as exc:
        print(f"\n[ERROR] Falha na execucao: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
