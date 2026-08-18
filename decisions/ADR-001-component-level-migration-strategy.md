# ADR-001 — Component-Level Migration Strategy

- **Status:** Accepted
- **Date:** 2026-08-18
- **Scope:** Phase 03 — Legacy Migration & Data Center Exit

## Context

Source discovery found a representative Ubuntu VM containing a Flask application, PostgreSQL 16, local operational files, a cron-driven reporting job and SSH administration. PostgreSQL currently listens only on loopback, while Flask listens on TCP 8080. The reporting job queries PostgreSQL and writes CSV output to the local filesystem.

Treating the VM as a single migration unit would preserve avoidable coupling and would not meet the phase objective of demonstrating both data-center exit and justified modernization.

## Decision

Use a component-level migration strategy:

- **Application/Ubuntu:** rehost to Amazon EC2, with AWS Application Migration Service (MGN) as the execution candidate.
- **PostgreSQL:** replatform to Amazon RDS for PostgreSQL, with AWS Database Migration Service (DMS) as the migration/synchronization candidate subject to readiness checks.
- **Operational files:** replatform to Amazon S3 using a controlled transfer and checksum-based validation.
- **Scheduled report:** preserve behavior first, then modestly replatform its database/output dependencies after target validation.
- **Administration:** prefer AWS Systems Manager Session Manager for the target rather than relying on inbound SSH.

## Rationale

This separates stateless-ish runtime concerns from stateful database and file concerns while limiting simultaneous application change. It creates clear validation boundaries and demonstrates that migration tooling is selected according to workload component rather than for résumé visibility.

## Consequences

### Positive

- managed PostgreSQL reduces database host administration,
- S3 removes operational files from local VM disk,
- application rehost limits code change during migration,
- independent validation is possible for app, DB and files,
- rollback can preserve the source until acceptance.

### Trade-offs

- more migration paths must be coordinated,
- application DB configuration changes from localhost to an RDS endpoint,
- the scheduled job must be reconfigured for target dependencies,
- DMS and MGN introduce temporary migration resources/cost and connectivity requirements,
- cutover ordering matters because DB and file state must remain consistent enough for acceptance.

## Rejected alternatives

1. **Rehost everything to one EC2 instance:** fastest but preserves DB/local-file coupling and operational burden.
2. **Immediate application refactor:** excessive change for a migration phase and makes failures harder to attribute.
3. **Immediate container/serverless rewrite:** same problem; modernization scope would dominate migration scope.
4. **DMS only:** cannot migrate the application/OS runtime.
5. **MGN only:** does not create the desired managed RDS database target.

## Validation required before final acceptance

- source/target database counts and aggregates,
- representative record comparison,
- application health/read/write behavior,
- file count and checksum/content validation,
- scheduled report execution on target dependencies,
- target management/security checks,
- documented cutover and rollback result.
