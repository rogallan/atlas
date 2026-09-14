# Verify — S21 · Terraform AWS

## Evidence checklist

- [ ] Command output of `terraform fmt -check -recursive` confirming 100% adherence to HashiCorp standard styling.
- [ ] Command output of `terraform validate` verifying valid syntax, types, and module wiring.
- [ ] Command output of `terraform plan -var-file=environments/dev.tfvars` showing successful generation of the complete cloud resource graph.
- [ ] Static security scan report (`checkov` or `trivy config`) showing zero critical or high findings across all modules.
- [ ] Review and verification of `infra/terraform/MAPPING.md` confirming 1:1 parity with the local architecture boundaries.
- [ ] Review and verification of `docs/architecture/aws_cost_estimate.md` documenting transparent cost projections for running the stack on AWS.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — module interfaces, IAM policies, and VPC networking topology match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
