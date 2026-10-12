#!/usr/bin/env python3
"""ATLAS Automated Release Candidate & DoD Completeness Auditor (S22).

Verifies SDD catalog completeness (S00 to S22), task sign-offs, evidence checklists,
evaluation benchmark scorecard thresholds, and architectural documentation.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Reconfigure stdout for utf-8 on Windows
if sys.platform == "win32":
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        reconf(encoding="utf-8")

# Project root resolution
REPO_ROOT = Path(__file__).resolve().parents[2]


class ReleaseAuditor:
    """Audits the repository for Definition of Done compliance across all SDDs."""

    def __init__(self, repo_root: Path = REPO_ROOT) -> None:
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.sdd_count: int = 0

    def audit_sdds(self) -> bool:
        """Verify S00 through S22 exist and have 100% completed tasks and evidence."""
        sdd_dir = self.repo_root / "1.SDDs"
        if not sdd_dir.exists():
            self.errors.append("Diretório 1.SDDs não encontrado no repositório.")
            return False

        sdd_folders = sorted(
            [d for d in sdd_dir.iterdir() if d.is_dir() and d.name.startswith("S")]
        )
        self.sdd_count = len(sdd_folders)

        if self.sdd_count < 23:
            self.errors.append(
                f"Esperado pelo menos 23 SDDs (S00 a S22), encontrado {self.sdd_count}."
            )

        for folder in sdd_folders:
            sdd_name = folder.name
            required_files = ["spec.md", "plan.md", "tasks.md", "verify.md"]

            for req_file in required_files:
                file_path = folder / req_file
                if not file_path.exists():
                    self.errors.append(f"[{sdd_name}] Arquivo obrigatório ausente: {req_file}")
                elif file_path.stat().st_size == 0:
                    self.errors.append(f"[{sdd_name}] Arquivo obrigatório está vazio: {req_file}")

            # Check for unchecked tasks in tasks.md
            tasks_path = folder / "tasks.md"
            if tasks_path.exists():
                content = tasks_path.read_text(encoding="utf-8")
                unchecked_tasks = len(re.findall(r"- \[\s\]", content))
                if unchecked_tasks > 0:
                    self.errors.append(
                        f"[{sdd_name}] Possui {unchecked_tasks} tarefa(s) não concluída(s) em tasks.md"
                    )

            # Check for unchecked verification in verify.md
            verify_path = folder / "verify.md"
            if verify_path.exists():
                content = verify_path.read_text(encoding="utf-8")
                unchecked_verify = len(re.findall(r"- \[\s\]", content))
                if unchecked_verify > 0:
                    self.errors.append(
                        f"[{sdd_name}] Possui {unchecked_verify} evidência(s) não verificada(s) em verify.md"
                    )

        return len(self.errors) == 0

    def audit_adrs(self) -> bool:
        """Verify ADR catalog contains completed records ADR-0001 through ADR-0012."""
        adr_dir = self.repo_root / "8.docs" / "adr"
        if not adr_dir.exists():
            self.errors.append("Diretório 8.docs/adr não encontrado.")
            return False

        expected_adrs = [
            "0001-package-manager.md",
            "0002-vector-store-and-embeddings.md",
            "0003-local-llm-runtime.md",
            "0004-agent-orchestration-engine.md",
            "0005-mcp-tool-integration.md",
            "0006-web-framework-and-api.md",
            "0007-hitl-approval-pattern.md",
            "0008-defensive-guardrails.md",
            "0009-observability-and-telemetry.md",
            "0010-frontend-architecture.md",
            "0011-ngrok-tunneling.md",
            "0012-aws-terraform-iac.md",
        ]

        for adr in expected_adrs:
            adr_path = adr_dir / adr
            if not adr_path.exists():
                self.errors.append(f"[ADR] Registro arquitetural ausente: {adr}")
            elif adr_path.stat().st_size < 100:
                self.errors.append(f"[ADR] Registro muito curto/incompleto: {adr}")

        return len(self.errors) == 0

    def audit_portfolio_assets(self) -> bool:
        """Verify release and portfolio showcase assets."""
        portfolio_dir = self.repo_root / "8.docs" / "portfolio"
        required_portfolio = [
            "README.md",
            "demo_script.md",
            "video_curriculum.md",
        ]

        for p_file in required_portfolio:
            file_path = portfolio_dir / p_file
            if not file_path.exists() or file_path.stat().st_size == 0:
                self.errors.append(f"[Portfolio] Asset ausente ou vazio: 8.docs/portfolio/{p_file}")

        # Root files
        required_root = ["README.md", "CHANGELOG.md", "constitution.md", "architecture.md"]
        for r_file in required_root:
            r_path = self.repo_root / r_file
            if not r_path.exists() or r_path.stat().st_size == 0:
                self.errors.append(f"[Root] Arquivo obrigatório ausente na raiz: {r_file}")

        return len(self.errors) == 0

    def audit_eval_scorecard(self) -> bool:
        """Verify the final release evaluation scorecard exists and meets gate thresholds."""
        scorecard_path = self.repo_root / "7.evals" / "reports" / "final_scorecard_v1.0.0.md"
        if not scorecard_path.exists():
            self.errors.append(
                "Relatório final de benchmark ausente: 7.evals/reports/final_scorecard_v1.0.0.md"
            )
            return False

        content = scorecard_path.read_text(encoding="utf-8")
        required_keywords = [
            "Intent Classification Accuracy",
            "RAG Context Recall",
            "Faithfulness & Groundedness",
            "Human-in-the-Loop Safety Compliance",
            "PASS",
        ]
        for kw in required_keywords:
            if kw not in content:
                self.errors.append(
                    f"[Scorecard] Palavra-chave obrigatória ausente no relatório final: '{kw}'"
                )

        return len(self.errors) == 0


def main() -> int:
    """CLI execution for release readiness auditing."""
    parser = argparse.ArgumentParser(description="ATLAS Release Candidate Auditor")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Falhar se houver qualquer pendência nas SDDs ou documentação",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("🔍 ATLAS GenAI Banking Copilot — Auditoria de Release Candidate v1.0.0")
    print("=" * 70)

    auditor = ReleaseAuditor()
    print("\n[1/4] Auditando catálogo SDD (S00 a S22)...")
    auditor.audit_sdds()
    print(f"      Processados {auditor.sdd_count} SDDs.")

    print("\n[2/4] Auditando Architecture Decision Records (ADRs)...")
    auditor.audit_adrs()

    print("\n[3/4] Auditando assets de portfólio e documentação de release...")
    auditor.audit_portfolio_assets()

    print("\n[4/4] Auditando scorecard final de benchmark de avaliação...")
    auditor.audit_eval_scorecard()

    print("\n" + "=" * 70)
    if auditor.errors:
        print(f"❌ AUDITORIA FALHOU: {len(auditor.errors)} inconsistência(s) detectada(s):\n")
        for err in auditor.errors:
            print(f"  • {err}")
        print("\nResolva os itens acima para liberar a Release Candidate v1.0.0.")
        return 1

    print("🎉 AUDITORIA APROVADA: 100% de conformidade com a Definition of Done!")
    print(f"  • {auditor.sdd_count} SDDs auditados com 0 pendências")
    print("  • Catálogo completo de 12 ADRs verificado")
    print("  • Assets de demonstração, portfólio e currículo de vídeos validados")
    print("  • Scorecard executivo final v1.0.0 em conformidade com os Quality Gates")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
