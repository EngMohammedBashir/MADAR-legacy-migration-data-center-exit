# Target Architecture

**Status: NOT YET APPROVED**

This file intentionally does not pretend the target has already been selected.

## Design rule

Target architecture follows source discovery and migration-strategy selection.

Candidate AWS building blocks may include VPC networking, EC2, managed database services, object/file storage, load balancing, Systems Manager, CloudWatch, IAM, backup capabilities and migration tooling — but inclusion requires an identified workload need.

## Required architecture views

When approved, document:

1. **Source view** — what exists before migration.
2. **Migration-path view** — how data/application state moves.
3. **Target view** — runtime after cutover.
4. **Failure/rollback view** — what happens when cutover is aborted.
5. **Security boundaries** — public/private exposure, IAM and network controls.
6. **Operations view** — logs, metrics, backup/recovery and access path.

## Target design questions

- Does the application need a public endpoint at this phase?
- Is a load balancer justified for one temporary lab instance?
- Is NAT Gateway cost justified, or can the design avoid it?
- Should the database remain on the application host for a pure rehost, or is managed DB replatforming justified?
- Do operational files require filesystem semantics or can they become objects?
- What target state creates useful modernization without hiding the migration lesson?

## Cost guardrail

Prefer architectures that can be created and destroyed within the same lab session. Avoid always-on paid components unless the test specifically requires them.
