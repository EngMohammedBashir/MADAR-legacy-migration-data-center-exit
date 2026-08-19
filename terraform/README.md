# Terraform — AWS Target Infrastructure

## Current position

Terraform remains part of the Phase 03 infrastructure strategy, but it is **not used to drive the current asynchronous VM Import/Export task**.

The project intentionally uses:

```text
AWS CLI / CloudShell
├── private S3 VM-import staging
├── vmimport IAM service role
├── VMDK upload
└── EC2 ImportImage task

Terraform (next)
├── repeatable target VPC/subnets
├── security groups
├── imported-AMI EC2 launch configuration where appropriate
├── RDS networking/target
└── other stable target infrastructure worth managing as code
```

## Why the split exists

Terraform is excellent for desired-state infrastructure. VM Import/Export is an asynchronous migration workflow that starts from a large external artifact and eventually produces an AMI. Treating that conversion task as ordinary long-lived infrastructure would add complexity without improving the migration proof.

The CLI-first workflow also made the permission boundaries explicit:

- local Windows AWS CLI uploads the local VMDK,
- AWS CloudShell provisions/inspects AWS-side prerequisites,
- `vmimport` is a dedicated service role,
- `iam:PassRole` is verified before the import task,
- Terraform can consume the resulting AMI only after the import succeeds.

## IaC guardrails

When target Terraform is added:

- no secrets in `.tf`, variables, plans or committed state,
- `.terraform/`, state, lock/plan artifacts follow repository policy,
- run `terraform fmt`, `terraform validate`, and review `terraform plan`,
- avoid creating paid/stateful resources before the current migration gate needs them,
- review public exposure and IAM scope,
- tag resources for ownership/cleanup,
- prefer explicit variables/outputs rather than hidden console state,
- destroy short-lived lab resources after acceptance unless retention is intentional,
- separately check service-created resources that Terraform does not own.

## Planned target scope

Terraform should be introduced after the imported AMI is proven, because the exact EC2 target/network requirements are then known from evidence rather than assumption.

Likely modules/resources:

```text
network
├── VPC
├── application subnet
├── private DB subnets
├── route tables / IGW as required
└── security groups

compute
└── imported-AMI EC2 target

database
├── DB subnet group
└── RDS PostgreSQL
```

## Engineering rule

IaC is a tool for reproducibility, not a requirement to force every migration API call into Terraform. The project chooses the tool that best matches the lifecycle of the resource/workflow.