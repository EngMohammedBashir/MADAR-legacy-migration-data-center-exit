# Phase 03 Evidence Index

Evidence should prove engineering claims, not merely show that AWS Console pages exist.

## Source evidence captured locally

The following focused screenshots have been captured during the source-lab build using the agreed `madar-...` naming convention:

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

These currently remain local binary evidence until each image is reviewed for secrets, unrelated desktop information and image provenance before upload.

### What the current evidence proves

- representative VMware VM exists and is correctly identified,
- Ubuntu guest resources and storage baseline were inspected,
- SSH/network administration path works,
- LVM root filesystem expansion persisted,
- base OS patching/reboot succeeded,
- Python/PostgreSQL runtime dependencies are installed,
- PostgreSQL application role/database/schema exist,
- isolated Python venv and PostgreSQL driver work,
- PostgreSQL independently confirms the source dataset counts,
- the real PostgreSQL-backed MADAR shipment dashboard is reachable and functional.

## Source evidence still required

- corrected fully deterministic seed rerun proof,
- application write-path proof,
- deterministic operational files present,
- source file count and total size,
- SHA-256 source manifest,
- scheduled/background job result,
- representative database aggregates,
- dependency/configuration inventory,
- pre-migration snapshot/backup proof.

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

Use descriptive lowercase names prefixed with `madar-`, for example:

```text
madar-source-db-baseline.png
madar-file-checksum-reconciliation.png
madar-cutover-target-smoke-test.png
```

Avoid screenshots containing credentials, tokens, unnecessary account identifiers, email addresses, or unrelated desktop information.

## Evidence quality rule

Prefer command output or a focused screenshot that directly supports one claim. Ten decorative screenshots are weaker than three pieces of evidence that prove integrity, recovery and cleanup.

## Integrity rule

A screenshot is not accepted merely because the UI looks healthy. Where possible, pair visual application evidence with an independent source-of-truth check such as PostgreSQL counts, hashes, service state, or an HTTP health result.
