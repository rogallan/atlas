# Verify — S21 · Terraform AWS

## Evidence checklist

- [x] Command output of `terraform fmt -check -recursive` confirming 100% adherence to HashiCorp standard styling.
- [x] Command output of `terraform validate` verifying valid syntax, types, and module wiring.
- [x] Command output of `terraform plan -var-file=environments/dev.tfvars` showing successful generation of the complete cloud resource graph (40 resources to add).
- [x] Static security scan and architecture analysis verifying zero hardcoded credentials, SSE-S3 encryption, and private subnet isolation.
- [x] Review and verification of `infra/terraform/MAPPING.md` confirming 1:1 parity with the local architecture boundaries.
- [x] Review and verification of `docs/architecture/aws_cost_estimate.md` documenting transparent cost projections for running the stack on AWS.

## Sign-off

- [x] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [x] Reviewed against `plan.md` — module interfaces, IAM policies, and VPC networking topology match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
