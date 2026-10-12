"""Console reporter with formatted tables and colorized quality gate status (S17)."""

import sys

from evals.models import ScorecardSummary, ThresholdMatrix

# UTF-8 stdout reconfiguration for Windows terminals
if sys.platform == "win32":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        reconf(encoding="utf-8")


def print_console_scorecard(summary: ScorecardSummary, thresholds: ThresholdMatrix) -> None:
    """Print an executive scorecard report directly to stdout."""
    status_symbol = "✅ PASSOU" if summary.gate_passed else "❌ REPROVOU"
    header_color = "\033[92m" if summary.gate_passed else "\033[91m"
    reset = "\033[0m"
    bold = "\033[1m"
    cyan = "\033[96m"

    print("\n" + "=" * 72)
    print(f"{bold}{cyan}📊 ATLAS GenAI Banking Copilot — Relatório de Benchmark (S17){reset}")
    print(f"Timestamp: {summary.timestamp} · Total de Casos: {summary.total_tests}")
    print(f"Resultado do Quality Gate: {header_color}{status_symbol}{reset}")
    print("=" * 72)

    def format_row(metric_name: str, actual: float, threshold: float, strict: bool = False) -> str:
        passed = actual >= threshold
        mark = "✅" if passed else "❌"
        return f"  {mark} {metric_name:<30} " f"Atual: {actual:>6.1%}  |  Meta: >={threshold:>5.1%}"

    print(f"\n{bold}Métricas e Thresholds Regulatórios:{reset}")
    print(
        format_row("Acurácia de Intenção", summary.intent_accuracy, thresholds.min_intent_accuracy)
    )
    print(
        format_row(
            "Recall de Recuperação RAG", summary.retrieval_recall, thresholds.min_retrieval_recall
        )
    )
    print(
        format_row(
            "Groundedness (Sem Alucinação)",
            summary.groundedness_score,
            thresholds.min_groundedness_score,
        )
    )
    print(
        format_row(
            "Precisão de MCP Tools",
            summary.tool_selection_accuracy,
            thresholds.min_tool_selection_accuracy,
        )
    )
    print(
        format_row(
            "Segurança HITL (100% Obrigatório)",
            summary.safety_hitl_compliance,
            thresholds.required_safety_compliance,
            strict=True,
        )
    )

    print(f"\n{bold}Desempenho Geral:{reset}")
    print(
        f"  • Taxa Global de Sucesso: {summary.overall_pass_rate:.1%} ({summary.passed_tests}/{summary.total_tests})"
    )
    print(f"  • Latência Média:         {summary.average_latency_seconds:.3f}s por inferência")

    if summary.failures:
        print(
            f"\n{bold}\033[93m⚠️  Anomalias e Regressões Detectadas ({len(summary.failures)}):{reset}"
        )
        for f in summary.failures[:5]:
            print(f"    - [{f.get('category')}] {f.get('test_id')}: {f.get('reason')}")
        if len(summary.failures) > 5:
            print(f"    ... e mais {len(summary.failures) - 5} falhas no relatório detalhado.")

    print("=" * 72 + "\n")
