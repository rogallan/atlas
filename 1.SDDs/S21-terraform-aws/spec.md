# Spec — S21 · Terraform AWS

> **Domain:** Cloud Infrastructure & IaC · **Quarter:** Q4 · **Depends on:** S01 (Python Toolchain), S03 (FastAPI Gateway), S06/S07 (Vector DB/RAG), S08–S13 (MCP Servers), S19 (Observability), S20 (Docker Local Stack)

## 1. Goal

Provide an equivalent, production-ready cloud infrastructure path on Amazon Web Services (AWS) using modular Terraform (Infrastructure as Code - IaC), modeling the complete ATLAS local stack (network, container compute, vector storage, IAM least-privilege, secrets, and cloud observability) while keeping the frontend hosted externally on Vercel.

## 2. Context

Per `architecture.md`, `constitution.md`, and the PDI catalog in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, ATLAS develops local-first, but includes an explicit architectural cloud path. S21 models the mapping matrix (*Local-first $\leftrightarrow$ AWS*): running the containerized FastAPI Gateway and MCP servers on AWS ECS Fargate, vector indexing on managed OpenSearch Serverless / Qdrant on EC2, secrets managed via AWS Secrets Manager, least-privilege IAM roles, and observability via CloudWatch and AWS X-Ray, validated deterministically through `terraform plan` quality gates.

## 3. In scope

- Architectural Equivalence Matrix (`infra/terraform/MAPPING.md`) detailing the exact translation of local components to AWS services.
- Modular Terraform configuration (`infra/terraform/modules/`):
  - `network`: Multi-AZ VPC, public/private subnets, NAT Gateways, Security Groups.
  - `compute`: ECS Cluster, Fargate task definitions for Gateway and MCP servers, Application Load Balancer (ALB) with SSL/TLS and health checks.
  - `data`: S3 bucket for Central Bank document corpus; OpenSearch Serverless / managed Vector storage.
  - `security_iam`: Task execution roles, task roles with strict least privilege, and Secrets Manager integration.
  - `observability`: CloudWatch Log Groups with retention policies, CloudWatch Alarms, and AWS X-Ray tracing integration.
- Multi-environment support (e.g. `dev`, `staging`) using Terraform workspaces or environment-specific `.tfvars`.
- Static analysis & quality gates: `terraform fmt`, `terraform validate`, and security scanning with `trivy` or `checkov`.
- Automated validation via `terraform plan` without requiring live cloud deployment credentials.
- Estimated monthly cloud budget and cost estimation document (`docs/architecture/aws_cost_estimate.md`).

## 4. Out of scope

- Direct automated `terraform apply` creating billable resources during local development.
- Hosting or deploying the React Chat frontend on AWS (it remains deployed on Vercel per architecture design).
- Proprietary closed-source AWS Bedrock dependencies (the architecture maintains LLM flexibility; compute provisions containerized LLM/inference endpoints or managed endpoints).

## 5. Requirements

- **R1. Modular Architecture:** All infrastructure resources must be isolated into reusable, documented Terraform modules (`network`, `compute`, `data`, `security_iam`, `observability`).
- **R2. Parity with Local Architecture:** The AWS design must strictly mirror the local design:
  - Gateway & MCP containers -> ECS Fargate behind ALB.
  - Local Vector Store -> Amazon OpenSearch Serverless (Vector Search collection) or dedicated container.
  - Document files -> Amazon S3 with SSE-S3 encryption and versioning.
  - Local structured logs/traces -> Amazon CloudWatch Logs + X-Ray.
- **R3. Least Privilege IAM:** Tasks must not use wildcard permissions (`"Action": "*"`). Separate ECS Task Execution Role (pulling images, reading secrets) from Task Role (S3 read-only for RAG, vector store access).
- **R4. Secure Ingress & Network Isolation:** Containers must reside exclusively within private subnets with no public IPs. Ingress is managed strictly through the ALB with TLS.
- **R5. IaC Quality Gates:** Terraform code must pass formatting (`terraform fmt -check`), syntax validation (`terraform validate`), and static security compliance without warnings.
- **R6. Cost Modeling & Estimation:** Provide a transparent, documented budget estimate detailing the running cost breakdown per service for small/medium bank copilot workloads.

## 6. Acceptance criteria

- `terraform validate` and `terraform fmt -check` pass cleanly with zero errors.
- `terraform plan` executes successfully against a mock/dev configuration, generating a complete, predictable resource execution graph.
- Automated security scanning (`trivy config` or `checkov`) passes without high or critical findings.
- The Architectural Equivalence Matrix (`MAPPING.md`) and Cost Estimation document (`aws_cost_estimate.md`) are complete, reviewed, and versioned.
