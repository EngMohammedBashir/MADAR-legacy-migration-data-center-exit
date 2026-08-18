# Phase 03 Evidence Index

Evidence proves engineering claims; screenshots are not collected merely for decoration.

## Source evidence captured locally

Earlier foundation/runtime evidence:

```text
madar-legacy-vm-system-baseline.png
madar-legacy-vm-network-ssh.png
madar-lvm-storage-expanded.png
madar-base-os-patched.png
madar-post-reboot-validation.png
madar-runtime-postgresql-installed.png
madar-postgresql-database-role-created.png
madar-postgresql-schema-created.png
madar-python-venv-psycopg2-ready.png
madar-deterministic-dataset-baseline.png
madar-application-dashboard.png
```

Latest source-baseline/recoverability evidence:

```text
madar-source-files-sha256-baseline.png
madar-server-timezone-riyadh.png
madar-cron-background-job-verified.png
madar-application-write-path-verified.png
madar-source-baseline-restored.png
madar-pre-migration-db-backup-verified-v2.png
madar-pre-migration-files-backup-verified.png
```

If the combined `pre-migration-snapshot.sha256` manifest is executed and verified, capture:

```text
madar-final-pre-migration-snapshot.png
```

Binary screenshots remain local until individually reviewed for credentials, unrelated desktop content and image provenance.

## What the evidence now proves

- representative VMware source VM and Ubuntu runtime exist,
- network/SSH administration path works,
- PostgreSQL and isolated Python runtime are functional,
- deterministic database baseline is `10 / 50 / 150`,
- real PostgreSQL-backed dashboard is reachable,
- operational CSV files exist and baseline SHA-256 checks return `OK`,
- server timezone is `Asia/Riyadh` with NTP active,
- cron executed the report job without an interactive shell,
- application PATCH write path updated a shipment and inserted a matching event transactionally,
- deterministic seed restored the migration baseline after the controlled write test,
- custom-format PostgreSQL backup can be inspected by `pg_restore --list`,
- operational-file archive contents can be listed,
- database/file backup integrity is protected with SHA-256 verification.

## Evidence still required before target selection

- representative source database aggregates,
- compute/runtime/process/port inventory,
- application/database/filesystem/job/identity/network dependency inventory,
- dependency map,
- assessment and migration-disposition evidence.

## Planned migration evidence

- approved source/target architecture diagrams,
- Terraform plan/apply summary,
- migration/synchronization result,
- database reconciliation,
- file checksum reconciliation,
- target application functional test,
- monitoring/security validation,
- cutover decision and rollback result,
- controlled failure exercise if performed.

## Quality and security rules

Prefer focused command output plus an independent source-of-truth check. Avoid screenshots containing credentials, tokens, unnecessary identifiers or unrelated desktop information. Never publish `.pgpass`, secret-bearing environment files, private keys, or local backup artifacts containing sensitive real data.
