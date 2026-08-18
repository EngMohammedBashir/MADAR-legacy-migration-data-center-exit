# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has an aging shipment-management estate that must be understood, protected and migrated before data-center exit. This phase treats migration as an **engineering engagement**, not an EC2 deployment exercise.

> The VMware environment is a representative lab of MADAR's pre-existing legacy estate. It exists so migration decisions, failure modes and validation can be measured safely.

## Current status

**Source workload baseline and recoverability point complete. Formal discovery is next. No paid AWS target resources have been created.**

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── 2 vCPU / 2560 MB RAM
├── PostgreSQL 16.14
├── Flask 3.1.3 / HTTP 8080
├── 10 customers / 50 shipments / 150 events
├── Operational CSV exports + SHA-256 manifest
├── Scheduled operations report via cron
└── Verified pre-migration DB + file backups
```

## What has been proven

- PostgreSQL-backed application read path works.
- Transactional application write path works: shipment update + event insert commit together.
- The controlled write proof was removed by deterministic reseeding; the migration baseline returned to `10 / 50 / 150`.
- Operational source files are generated from workload data and protected by SHA-256 baseline verification.
- A scheduled Linux job queries PostgreSQL and generates timestamped operations reports without an interactive session.
- Source timezone is explicitly `Asia/Riyadh` and NTP is active.
- PostgreSQL custom-format backup is readable with `pg_restore --list`.
- Operational-file archive is inspectable and checksum-verifiable.

## Source workload model

```text
Windows operations host
        |
        | HTTP / SSH
        v
MADAR-LEGACY-01 (VMware)
        |
   +----+-----------+----------------+
   |                |                |
Flask API       PostgreSQL      Operational files
   |                ^                ^
   | PATCH/GET      |                |
   +----------------+        scheduled report
                                  ^
                                  |
                                cron
```

The compact lab deliberately co-locates logical roles on one VM because of local hardware constraints. The migration assessment will reason about component statefulness and dependencies rather than pretending the lab topology is a production topology.

## Application paths

```text
GET   /
GET   /api/health
GET   /api/summary
GET   /api/customers
GET   /api/shipments
GET   /api/shipments/<id>/events
PATCH /api/shipments/<id>/status
```

The PATCH path validates status, updates the shipment, inserts the matching event and commits both operations transactionally.

## Data and integrity baseline

Deterministic source data:

```text
Customers:        10
Shipments:        50
Shipment events: 150
```

Operational artifacts include shipment export/report CSVs, a SHA-256 source manifest, timestamped scheduled reports and job logs. Pre-migration database and file backups are kept local and verified before migration work.

## Security discipline

- normal DB workload identity is `madar_app`, not a PostgreSQL superuser,
- secrets are not committed,
- unattended `psql` uses a protected user `.pgpass` rather than a password embedded in cron,
- `.venv`, `.env`, keys, credentials and backup artifacts remain outside Git,
- the lab credential exposed during interactive construction should be rotated before final portfolio publication,
- binary evidence is reviewed before public upload.

## Engineering lifecycle

`Discovery → Inventory → Dependency Mapping → Assessment → Migration Strategy → Target Design → Readiness → Migration → Validation → Cutover → Rollback Validation → Optimization → Cleanup`

### Current gate

We are at **Discovery**. MGN, DMS, rehost/replatform decisions and the final AWS target are intentionally not selected as foregone conclusions. They will be justified from the dependency inventory and statefulness assessment.

## Repository map

- `CURRENT-STATE.md` — start here each session.
- `legacy-lab/app/` — source application, schema, deterministic seed and UI.
- `legacy-lab/scripts/` — source scheduled-job implementation.
- `runbooks/source-lab-operations.md` — operator command/runbook reference.
- `checklists/phase03-master-checklist.md` — implementation and validation progress.
- `evidence/README.md` — evidence index and capture policy.
- `docs/03-discovery-assessment.md` — discovery/assessment workspace.
- `docs/04-migration-strategy.md` — migration decisions after discovery.
- `docs/05-target-architecture.md` — AWS target after assessment.
- `docs/06-validation-plan.md` — reconciliation and functional validation.
- `decisions/` — ADRs.
- `terraform/` — AWS IaC only after target approval.

## Success criteria

Success is not "AWS resources exist." The project must prove source understanding, reproducible target infrastructure, data/file reconciliation, application behavior, scheduled processing, recoverability, cutover acceptance, rollback logic, security/observability checks, cost discipline and cleanup.

## Integrity rule

MADAR is fictional. Tests, code, failures, outputs, decisions and evidence are technically authentic. Controlled exercises are labeled as such and are never represented as real production incidents.
