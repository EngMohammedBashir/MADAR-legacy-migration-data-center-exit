# Terraform — AWS Target Infrastructure

**Implementation hold:** target architecture is not approved yet.

Terraform configuration belongs here after discovery and the migration-strategy ADR identify the required AWS target.

## Guardrails

- Infrastructure as Code for reproducibility.
- No secrets in variables or state committed to Git.
- `.terraform/`, local state and generated plans must remain untracked.
- Run `terraform fmt` and `terraform validate` before apply.
- Review the plan for paid/stateful resources.
- Review public exposure and IAM scope.
- Tag resources for project ownership and cleanup without legacy `Portfolio` tagging.
- Prefer short-lived lab infrastructure.
- Destroy after evidence/validation unless a specific test requires persistence.
- Verify residual resources after destroy, including service-created resources not managed by Terraform.

## Why this directory is intentionally empty of resources

Choosing AWS resources before understanding the legacy workload would reverse the engineering process. Phase 03 begins with discovery, not with `terraform apply`.
