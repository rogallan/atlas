# Tasks — S21 · Terraform AWS

- [ ] Write the Architectural Equivalence Matrix in `infra/terraform/MAPPING.md` documenting Local vs. AWS service mappings.
- [ ] Create reusable Network module in `infra/terraform/modules/network/` (VPC, public/private subnets, NAT Gateway, security groups).
- [ ] Create reusable Compute module in `infra/terraform/modules/compute/` (ECS cluster, Fargate task definition, ALB, target groups).
- [ ] Create reusable Data module in `infra/terraform/modules/data/` (S3 knowledge bucket with SSE-S3 encryption, OpenSearch Serverless vector collection).
- [ ] Create reusable Security/IAM module in `infra/terraform/modules/security_iam/` (ECS task execution role, least-privilege task role, Secrets Manager).
- [ ] Create reusable Observability module in `infra/terraform/modules/observability/` (CloudWatch Log Group, metric alarms, X-Ray tracing).
- [ ] Assemble root Terraform configuration (`main.tf`, `variables.tf`, `outputs.tf`, `environments/dev.tfvars`).
- [ ] Produce monthly cloud budget and cost estimate document in `docs/architecture/aws_cost_estimate.md`.
- [ ] Execute IaC quality gates (`terraform fmt -check`, `terraform validate`, and static security scanning).
- [ ] Execute `terraform plan` generating a complete, error-free execution plan for the `dev` environment.

## Definition of Done

- All tasks above are complete and merged.
- Terraform code is fully modular, parameterized, and formatted.
- `terraform validate` and `terraform plan` run cleanly with zero syntax or resource dependency errors.
- Static security scan (`checkov` or `trivy`) passes without critical or high vulnerabilities.
- Architectural Equivalence Matrix and Cost Estimation documents are approved and versioned.
