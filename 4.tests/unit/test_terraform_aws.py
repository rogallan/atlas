"""Automated Unit Tests for S21 Terraform AWS Infrastructure as Code (IaC)."""

import shutil
import subprocess
from pathlib import Path


def test_terraform_mapping_document_structure() -> None:
    """Verify that MAPPING.md documents the complete Local to AWS equivalence matrix."""
    mapping_path = Path("infra/terraform/MAPPING.md")
    assert mapping_path.exists(), "infra/terraform/MAPPING.md must exist"

    content = mapping_path.read_text(encoding="utf-8")
    assert "FastAPI Gateway (Docker)" in content
    assert "Amazon ECS Fargate" in content
    assert "OpenSearch Serverless" in content
    assert "Amazon S3" in content
    assert "AWS Secrets Manager" in content
    assert "AWS X-Ray" in content


def test_terraform_cost_estimate_document() -> None:
    """Verify that aws_cost_estimate.md documents monthly OpEx projections."""
    cost_path = Path("docs/architecture/aws_cost_estimate.md")
    assert cost_path.exists(), "docs/architecture/aws_cost_estimate.md must exist"

    content = cost_path.read_text(encoding="utf-8")
    assert "ECS Fargate" in content
    assert "NAT Gateway" in content
    assert "OpenSearch Serverless" in content
    assert "Optimization Levers" in content


def test_terraform_module_structure() -> None:
    """Verify that all 5 Terraform modules contain main.tf, variables.tf, and outputs.tf."""
    base_dir = Path("infra/terraform/modules")
    modules = ["network", "compute", "data", "security_iam", "observability"]

    for mod in modules:
        mod_dir = base_dir / mod
        assert mod_dir.is_dir(), f"Module directory {mod_dir} must exist"
        assert (mod_dir / "main.tf").exists(), f"{mod}/main.tf must exist"
        assert (mod_dir / "variables.tf").exists(), f"{mod}/variables.tf must exist"
        assert (mod_dir / "outputs.tf").exists(), f"{mod}/outputs.tf must exist"


def test_terraform_environments_and_root_files() -> None:
    """Verify root composition files and environment tfvars exist."""
    root_dir = Path("infra/terraform")
    assert (root_dir / "main.tf").exists()
    assert (root_dir / "variables.tf").exists()
    assert (root_dir / "outputs.tf").exists()
    assert (root_dir / "environments" / "dev.tfvars").exists()
    assert (root_dir / "environments" / "staging.tfvars").exists()


def test_terraform_cli_fmt_and_validate() -> None:
    """Execute terraform fmt -check and terraform validate if terraform CLI is installed."""
    terraform_bin = shutil.which("terraform")
    if not terraform_bin:
        return

    # Check formatting
    fmt_res = subprocess.run(
        [terraform_bin, "fmt", "-check", "-recursive", "infra/terraform"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert fmt_res.returncode == 0, (
        f"Terraform formatting failed: {fmt_res.stdout} {fmt_res.stderr}"
    )

    # Check validation
    val_res = subprocess.run(
        [terraform_bin, "-chdir=infra/terraform", "validate"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert val_res.returncode == 0, f"Terraform validate failed: {val_res.stdout} {val_res.stderr}"
