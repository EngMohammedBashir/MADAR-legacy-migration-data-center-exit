# Phase 03 Evidence Index

Evidence should prove engineering claims, not merely show that AWS Console pages exist.

## Planned source evidence

- virtualization/local lab preflight,
- legacy VM running,
- shipment application functional,
- representative database records/counts,
- operational files present,
- SHA-256 source manifest,
- scheduled/background job result,
- dependency/configuration evidence.

## Planned migration evidence

- approved source/target architecture diagrams,
- Terraform plan/apply summary,
- migration/synchronization result,
- database reconciliation,
- file checksum reconciliation,
- target application functional test,
- monitoring/security validation,
- cutover decision,
- rollback exercise/result,
- controlled failure exercise if performed.

## Planned closeout evidence

- Terraform destroy summary,
- residual-resource checks,
- cost review result,
- clean repository state.

## Screenshot naming convention

Use descriptive lowercase names such as:

`source-db-baseline.png`

`file-checksum-reconciliation.png`

`cutover-target-smoke-test.png`

Avoid screenshots containing credentials, tokens, unnecessary account identifiers, email addresses, or unrelated desktop information.

## Evidence quality rule

Prefer command output or a focused screenshot that directly supports one claim. Ten decorative console screenshots are weaker than three pieces of evidence that prove integrity, recovery and cleanup.
