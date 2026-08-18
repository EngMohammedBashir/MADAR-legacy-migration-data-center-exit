# Phase 03 — Current State

**Status:** SOURCE LAB BASELINE + RECOVERABILITY COMPLETE — DISCOVERY NEXT  
**AWS paid-resource window:** NOT STARTED  
**Current objective:** freeze the pre-migration source evidence, inventory dependencies, draw the dependency map, then assess migration dispositions before approving an AWS target.

## Verified source estate

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── 2 vCPU / 2560 MB RAM
├── PostgreSQL 16.14
├── Flask 3.1.3 on port 8080
├── Customers: 10
├── Shipments: 50
├── Shipment events: 150
├── Operational CSV exports/reports
├── Daily scheduled operations report
└── Pre-migration database + file backups
```

The representative lab remains intentionally compact: multiple logical legacy roles coexist on one VMware VM because the local host is resource constrained. Documentation distinguishes the lab topology from a real multi-server production estate.

## Completed in the latest milestone

### Deterministic source baseline

The corrected repository seed was synchronized to the VM and rerun. PostgreSQL independently reconfirmed `10 customers / 50 shipments / 150 shipment events`.

### Operational files and integrity

The source now includes deterministic shipment-linked operational artifacts under `~/madar-legacy-data/`:

- `exports/shipments_export.csv`,
- `reports/shipment_status_report.csv`,
- timestamped operations reports,
- `manifests/source-sha256.txt`,
- background-job logs.

The source manifest was verified with `sha256sum -c`; both baseline source files returned `OK`. File count and byte sizes were also recorded.

### Scheduled/background processing

`generate_operations_report.sh` queries PostgreSQL, writes a timestamped status report, and logs success. A controlled two-minute cron schedule produced reports at consecutive two-minute intervals without interactive execution, proving the scheduled dependency. The retained lab schedule was then changed to daily at `02:00`.

The server timezone is explicitly `Asia/Riyadh`; NTP synchronization is active.

### Application write path

The Flask application now exposes:

```text
PATCH /api/shipments/<id>/status
```

The endpoint validates status, updates the shipment, inserts the matching shipment event, and commits both operations transactionally. A controlled proof changed shipment 3 from `IN_TRANSIT` to `DELIVERED` and created event 151. PostgreSQL independently verified both writes.

After evidence capture, the deterministic seed was rerun. The migration baseline was restored to `10 / 50 / 150`, and shipment 3 returned to `IN_TRANSIT`.

### Pre-migration recoverability point

Database backup:

```text
~/madar-backups/madar_legacy_pre_migration.dump
```

The custom-format PostgreSQL dump was opened successfully with `pg_restore --list` and SHA-256 verified.

Operational-file backup:

```text
~/madar-backups/madar_operational_files_pre_migration.tar.gz
```

The archive contents were listed successfully and SHA-256 verified. Database and file backups remain local; secrets and local backup artifacts are not committed.

## Security posture

- normal workload DB identity is `madar_app`, not the PostgreSQL superuser,
- application secrets are not committed,
- the interactive application process currently receives `MADAR_DB_PASSWORD` through its environment,
- the unattended PostgreSQL client job uses the user's protected `.pgpass` (`0600`) rather than embedding a password in cron,
- `.venv`, `.env`, keys, credentials and local backup artifacts must remain outside Git,
- the lab credential exposed during the interactive build should be rotated before final portfolio publication.

## Evidence captured locally in this milestone

In addition to the earlier VM/runtime/application screenshots:

```text
madar-source-files-sha256-baseline.png
madar-server-timezone-riyadh.png
madar-cron-background-job-verified.png
madar-application-write-path-verified.png
madar-source-baseline-restored.png
madar-pre-migration-db-backup-verified-v2.png
madar-pre-migration-files-backup-verified.png
```

A final combined snapshot-manifest screenshot should be captured if/when the combined manifest command is executed. Binary screenshots remain local until reviewed for secrets and unrelated desktop information.

## Repository implementation now includes

```text
legacy-lab/app/                 # Flask app, schema, deterministic seed, UI
legacy-lab/scripts/             # scheduled operations report script
runbooks/source-lab-operations.md
checklists/phase03-master-checklist.md
evidence/README.md
```

## Exact next action

1. Inventory compute/runtime and systemd/process state.
2. Inventory listening ports and network dependencies.
3. Inventory application configuration without exposing secrets.
4. Inventory PostgreSQL/database dependencies.
5. Inventory filesystem paths and operational-file dependencies.
6. Inventory cron/scheduled jobs.
7. Inventory identities/credentials by role, not secret value.
8. Record DNS/external integration assumptions.
9. Capture representative source aggregates needed for later reconciliation.
10. Draw the source dependency map.
11. Classify statefulness/criticality and evaluate migration disposition per component.
12. Only then approve the AWS target and migration services.

## Important hold point

**Do not run Terraform apply and do not select MGN/DMS/other migration tooling as a foregone conclusion yet.** Discovery evidence comes first; the migration strategy must follow the workload dependencies rather than lead them.

## Source-lab exit criteria

- VM boots reliably. ✅
- workload is reachable and functional. ✅
- deterministic DB baseline is verified. ✅
- operational files exist and are checksummed. ✅
- scheduled/background operation is demonstrated. ✅
- application read and write paths are demonstrated. ✅
- pre-migration database/file recoverability point exists. ✅
- inventory and dependencies are documented. ⏳
- representative aggregates are frozen for later reconciliation. ⏳
- dependency map is documented. ⏳

## Blockers

None. The project is deliberately paused at the discovery/assessment gate before AWS target implementation.
