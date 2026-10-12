# ADR 0012: Production Cloud Architecture & Terraform AWS Infrastructure as Code

## Status
Accepted

## Date
2026-10-12

## Context
Per `1.SDDs/S21-terraform-aws/spec.md`, while ATLAS is designed to run locally by default, enterprise deployment requires an officially verified, automated Infrastructure as Code (IaC) path for hosting the backend on Amazon Web Services (AWS), keeping the frontend on Vercel.

Architectural requirements:
1. Complete architectural equivalence with the local stack (FastAPI container, Vector Search, Knowledge storage, Secrets management, Observability).
2. Modular, reusable Terraform design following HashiCorp best practices.
3. Offline testability and dry-run execution without requiring live AWS billing credentials in CI.
4. Detailed, transparent cost model with optimization levers for Dev and Prod environments.

## Decision
Implemented a modular **Terraform AWS** suite under `infra/terraform/`:
1. **Compute:** **AWS ECS Fargate** with Container Insights and Application Load Balancer (ALB) health checks on `/health`.
2. **Data & Vectors:** **AWS OpenSearch Serverless** (`VECTORSEARCH` collection) paired with encrypted **AWS S3** (`SSE-S3 AES256`) for regulatory knowledge documents.
3. **Security:** **AWS Secrets Manager** for credential rotation and dedicated least-privilege IAM Task/Execution roles.
4. **Networking:** Multi-AZ VPC (`us-east-1`), public/private subnets, Elastic IP NAT Gateway, and segregated security groups.
5. **Observability:** **Amazon CloudWatch Logs** (30-day retention) and CloudWatch Metric Alarms for CPU/memory saturation (> 85%).
6. **Cost Modeling:** Comprehensive breakdown documenting Dev (~$222/mo) vs. Prod (~$444/mo) and optimization levers (Savings Plans, Fargate Spot, Single NAT).

## Consequences
- **Positive:**
  - 100% reproducible, audited cloud architecture with `terraform validate` and `terraform plan`.
  - Zero lock-in to local hardware when scaling to production workloads.
  - Complete architectural mapping documented in `infra/terraform/MAPPING.md`.
- **Negative / Mitigations:**
  - Running OpenSearch Serverless and NAT Gateways in AWS incurs ongoing cloud costs (~$200+/mo).
  - Mitigated by keeping local-first development with Ollama/ChromaDB as the default daily development workflow.
