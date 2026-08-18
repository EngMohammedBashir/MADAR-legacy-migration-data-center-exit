# Migration Strategy

## Decision summary

Discovery showed that the representative legacy VM contains several logical workload components with different state and operational characteristics. The project will therefore use a **component-level migration strategy**, not a blanket `VM -> EC2` decision.

## Approved strategy

| Source component | Disposition | AWS target | Migration mechanism / approach | Reason |
|---|---|---|---|---|
| Ubuntu + Flask application | Rehost | Amazon EC2 | AWS Application Migration Service (MGN) candidate for execution | Preserves the legacy runtime with minimal application change and demonstrates controlled rehosting |
| PostgreSQL 16 | Replatform | Amazon RDS for PostgreSQL | AWS Database Migration Service (DMS) candidate, subject to connectivity/readiness checks | Separates stateful DB operations from the application host and moves DB operations to a managed service |
| Operational CSV/files | Replatform | Amazon S3 | Controlled file copy/synchronization with checksum validation | Removes dependency on local VM disk and gives durable object storage with simple integrity validation |
| Scheduled report job | Modest replatform | Initially retained with migrated application or moved to an AWS-native scheduler after functional validation | Reconfigure DB endpoint and output destination | Job logic is simple, but its DB and filesystem dependencies must be preserved during cutover |
| SSH administration | Modernize operations | AWS Systems Manager Session Manager where practical | Install/configure SSM management path | Reduces reliance on inbound administrative SSH for the target |

## Why MGN and DMS can both appear

MGN and DMS solve different problems.

```text
MGN = move/rehost the machine/runtime
DMS = migrate/synchronize database data
```

Using DMS for PostgreSQL does not mean MGN is unnecessary for the Flask/Ubuntu runtime. Likewise, using MGN for the server does not by itself produce the desired managed RDS target. The project intentionally separates these concerns.

## Target direction

```text
Representative source                         AWS target

Flask + Ubuntu -------- MGN/rehost ---------> EC2
      |                                      |
      | localhost DB today                   | RDS endpoint after cutover
      v                                      v
PostgreSQL 16 ---------- DMS --------------> RDS PostgreSQL

Operational files ------ validated copy ---> S3

cron/report job -------- reconfigure -------> target DB + target file destination
```

## Alternatives rejected

### Rehost the entire VM and leave PostgreSQL on EC2

Rejected as the final target because it preserves database administration, patching, local-disk coupling and the single-host failure domain. It remains useful only as part of a staged application rehost if required.

### Refactor the Flask application immediately

Rejected for this phase. The objective is migration/data-center exit with controlled modernization, not an application rewrite. Refactoring now would increase variables and weaken migration attribution.

### Replace everything with containers/serverless during migration

Rejected for the same reason: too much simultaneous architectural change for a migration phase whose success must be measured against a known source baseline.

### Use DMS as though it migrates the whole server

Rejected. DMS is a database migration service, not a machine/application migration mechanism.

### Use MGN as though it produces a managed RDS database

Rejected. MGN rehosts servers; it does not replatform PostgreSQL into RDS.

## Cutover principle

The source remains authoritative until target validation passes. Final cutover must reconcile database state, representative records, operational files, application read/write behavior and scheduled processing. Rollback means returning traffic/operations to the preserved source if acceptance criteria fail within the defined window.

## Implementation gate

Before creating migration resources:

1. draw and approve the AWS target architecture,
2. define VPC/subnet/security-group flows,
3. determine how the local VMware source reaches AWS migration endpoints/targets,
4. validate PostgreSQL/DMS prerequisites and endpoint connectivity,
5. define file-transfer mechanism and checksum validation,
6. estimate paid resources and cleanup order,
7. define cutover and rollback triggers.
