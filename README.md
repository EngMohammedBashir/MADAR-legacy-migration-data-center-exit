# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has already established an AWS foundation and validated a cloud-native event-driven workload. The company now faces a different problem: its core shipment-management estate still depends on aging infrastructure in the legacy data center.

This phase treats migration as an **engineering engagement**, not as an EC2 deployment exercise.

> The VMware environment built for this project is a representative lab of MADAR's pre-existing legacy estate. It is created now so the migration can be executed and measured safely; the company story does not claim that the legacy estate appeared after AWS adoption.

## Current status

**Source lab active — database, deterministic data and working shipment application are now implemented. AWS target selection remains intentionally on hold until source discovery is complete.**

Current verified source baseline:

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── 2 vCPU / 2560 MB RAM
├── PostgreSQL 16.14
├── Flask 3.1.3
├── Customers: 10
├── Shipments: 50
├── Shipment events: 150
└── HTTP application: port 8080
```

Remaining source-lab work includes operational files, SHA-256 manifesting, background processing, an application write-path proof, source aggregates, snapshot/backup and formal dependency discovery.

## Mission

Plan and execute a controlled migration of a representative MADAR logistics workload from a VMware-based legacy environment toward AWS while preserving application behavior, data integrity, operational recoverability, and a credible rollback path.

## Business pressure

MADAR's legacy environment is becoming harder to justify because of aging infrastructure, growth, operational overhead, weak recovery confidence, deployment friction, and an eventual data-center exit requirement.

The migration team must answer a harder question than "how do we move a server?":

**What should move, what should change, what should remain temporarily, what should be retired, and how can MADAR prove that cutover is safe?**

## Representative source estate

```text
Windows host / operations user
              |
              | HTTP / SSH
              v
       VMware Legacy Lab
              |
       MADAR-LEGACY-01
              |
     +--------+---------+
     |        |         |
 Flask App PostgreSQL  Operational Files
     |        |             [NEXT]
     +--- scheduled/background job [NEXT]
```

The physical lab is intentionally compact enough to run on limited local hardware. Multiple logical legacy roles coexist on one VM. Documentation distinguishes **logical production roles** from the **representative lab topology**.

## Working legacy application

The source workload is a real PostgreSQL-backed Flask application rather than a static mock UI.

Implemented application paths:

```text
GET /
GET /api/health
GET /api/summary
GET /api/customers
GET /api/shipments
GET /api/shipments/<id>/events
```

The browser dashboard provides working Dashboard, Shipments, Customers and System Status views plus shipment search and a workflow timeline.

The application deliberately has **no mock-data fallback**. If PostgreSQL is unavailable, the dependency failure is surfaced instead of fabricating a healthy-looking source system.

## Reproducible source data

The repository contains:

```text
legacy-lab/app/schema.sql
legacy-lab/app/seed_data.py
legacy-lab/app/requirements.txt
```

The corrected seed generator uses fixed timestamps and workflow-consistent shipment events. Its intended reproducible baseline is:

```text
Customers:        10
Shipments:        50
Shipment events: 150
```

Before freezing the final pre-migration baseline, the VM will rerun this corrected repository version and independently revalidate the counts.

## Security and dependency discipline

- normal workload access uses `madar_app`, not the PostgreSQL superuser,
- the DB password is supplied through `MADAR_DB_PASSWORD`, not committed in source,
- `.env`, key material and local virtual environments are ignored,
- Ubuntu's PEP 668 protection was respected; Python dependencies use `.venv`,
- paid AWS resources have not been created yet.

## Engineering lifecycle

`Discovery → Inventory → Dependency Mapping → Assessment → Migration Strategy → Target Design → Readiness → Migration → Validation → Cutover → Rollback Validation → Optimization → Cleanup`

## Success is not "AWS resources exist"

The phase is complete only when important claims have evidence, including:

- source workload works before migration,
- source data baseline is recorded,
- dependencies are understood,
- migration strategy is justified per component,
- target infrastructure is reproducible,
- migrated data is reconciled,
- application behavior is validated,
- cutover criteria are satisfied,
- rollback/abort conditions are defined and exercised where practical,
- security and observability controls are checked,
- cost and quotas are reviewed,
- temporary cloud resources are destroyed,
- residual resources are checked.

## Repository map

- `CURRENT-STATE.md` — **start here each session**.
- `docs/01-business-case.md` — why MADAR is exiting the legacy environment.
- `docs/02-source-estate.md` — logical estate and representative VMware lab.
- `docs/03-discovery-assessment.md` — inventory and dependency assessment.
- `docs/04-migration-strategy.md` — component-level strategy and trade-offs.
- `docs/05-target-architecture.md` — target architecture after assessment.
- `docs/06-validation-plan.md` — integrity and functional validation.
- `docs/source-lab-build-log.md` — VM, storage, network, patching and runtime build record.
- `docs/source-application-build.md` — PostgreSQL, schema, seed, Python isolation and Flask application record.
- `checklists/phase03-master-checklist.md` — implementation and validation progress.
- `decisions/` — architecture decision records.
- `runbooks/` — repeatable operational procedures.
- `evidence/README.md` — evidence index and capture status.
- `legacy-lab/app/` — reproducible source application, schema and seed code.
- `terraform/` — AWS Infrastructure as Code only after target design is approved.

## Cost discipline

Paid AWS resources should exist only during intentional implementation/test windows. Prepare locally first, deploy when ready, validate aggressively, capture evidence, then destroy and verify cleanup.

## Integrity rule

MADAR is fictional. Tests, code, failures, outputs, decisions and evidence must be technically authentic. Controlled failures must be labeled as controlled exercises; they must not be presented as real production incidents.
