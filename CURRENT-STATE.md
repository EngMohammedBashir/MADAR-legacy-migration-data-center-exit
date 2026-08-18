# Phase 03 — Current State

**Status:** SOURCE LAB BUILD — DATABASE + APPLICATION + DETERMINISTIC DATA READY  
**AWS paid-resource window:** NOT STARTED  
**Current objective:** complete the remaining source-side operational-file/background-job work, capture the full pre-migration baseline, create a snapshot/backup point, then begin formal discovery before selecting the AWS target.

## Story position

MADAR already had a traditional estate before its AWS journey. Phase 01 established cloud foundations. Phase 02 proved a new event-driven cloud-native workload. Phase 03 now models and proves the remaining shipment-management estate so MADAR can approach data-center exit as a measured migration engagement rather than an EC2 deployment exercise.

## Local lab constraint and topology

The Windows lab host has approximately 8 GB RAM and an Intel Core i3-N305. The representative estate therefore uses one lightweight VMware VM carrying several logical legacy roles rather than pretending to run a full multi-server enterprise estate locally.

```text
Windows 11 host
      |
      | VMware NAT / SSH / HTTP
      v
MADAR-LEGACY-01
      |
      +-- Ubuntu Server 24.04.4 LTS
      +-- Flask shipment application
      +-- PostgreSQL 16.14
      +-- operational files       [NEXT]
      +-- scheduled/background job [NEXT]
```

## Source VM foundation — verified

- VMware Workstation Pro 26H1.
- VM: `MADAR-LEGACY-01`.
- Ubuntu Server 24.04.4 LTS.
- 2 vCPU.
- 2560 MB RAM.
- 25 GB dynamically allocated virtual disk.
- VMware NAT networking.
- Guest interface observed as `ens33`, `192.168.14.128/24` during the current session.
- OpenSSH active and remote administration from Windows verified.
- Guided LVM layout corrected from roughly 11.5 GB root capacity to approximately 23 GB usable root filesystem.
- Ubuntu packages patched; required reboot completed; post-reboot validation passed.

## Runtime and database — verified

Installed and verified:

- Python 3.12.3,
- pip 24.0,
- PostgreSQL 16.14,
- `postgresql-contrib`,
- PostgreSQL systemd service active.

Database implementation:

- application role: `madar_app`,
- application database: `madar_legacy`,
- tables: `customers`, `shipments`, `shipment_events`,
- application account owns the application database/schema objects rather than using the PostgreSQL superuser for normal workload access.

The repository now includes a reproducible `schema.sql` under `legacy-lab/app/`.

## Python dependency isolation — verified

Ubuntu 24.04 rejected a direct system-wide `pip install` because the base interpreter is externally managed under PEP 668. The lab deliberately did **not** bypass that protection with `--break-system-packages`.

Instead:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

Application dependencies are isolated in `.venv` and pinned in `legacy-lab/app/requirements.txt`:

- Flask 3.1.3,
- psycopg2-binary 2.9.12.

`.venv/` remains excluded by `.gitignore`.

## Deterministic source dataset — verified

A Python seed generator now produces a reproducible fictional logistics dataset.

Baseline size:

```text
Customers:        10
Shipments:        50
Shipment events: 150
```

The repository seed implementation uses a fixed base timestamp and records every workflow stage reached by a shipment. Ten shipments exist at each workflow depth, so the event total is deterministically:

```text
10 * (1 + 2 + 3 + 4 + 5) = 150 events
```

The database itself was queried independently and confirmed the `10 / 50 / 150` row counts.

## Legacy shipment application — verified

A lightweight Flask application now provides a real source workload backed by PostgreSQL rather than mock data.

Implemented endpoints:

```text
GET /
GET /api/health
GET /api/summary
GET /api/customers
GET /api/shipments
GET /api/shipments/<id>/events
```

The dashboard provides:

- live shipment/customer KPIs,
- shipment inventory,
- search/filter behavior,
- customer view,
- system/database health view,
- shipment detail panel,
- workflow timeline.

The dashboard is reachable from the Windows host on the representative source address at port `8080` while the Flask process is running.

## Trustworthy failure behavior

The application does **not** fall back to mock shipment data when PostgreSQL is unavailable. Database connectivity is a real dependency and `/api/health` returns a degraded/error response when that dependency cannot be reached.

This is intentional: migration evidence must prove the real source/target dependency chain, not a visually healthy UI backed by fabricated fallback values.

## Secret handling

The database password is not committed to source code. The current lab process receives it through the `MADAR_DB_PASSWORD` environment variable.

The repository ignores `.env`, key material, local virtual environments and other common secret-bearing paths.

The current lab credential should be rotated before final public portfolio publication because it was exposed during the interactive build session; the repository itself does not contain that secret.

## Evidence captured locally so far

- `madar-legacy-vm-system-baseline.png`
- `madar-legacy-vm-network-ssh.png`
- `madar-lvm-storage-expanded.png`
- `madar-base-os-patched.png`
- `madar-post-reboot-validation.png`
- `madar-runtime-postgresql-installed.png`
- `madar-postgresql-database-role-created.png`
- `madar-postgresql-schema-created.png`
- `madar-python-venv-psycopg2-ready.png`
- `madar-deterministic-dataset-baseline.png`
- `madar-application-dashboard.png`

These filenames are documented in the evidence index. Binary screenshots remain local until intentionally uploaded and reviewed for secrets/unrelated desktop information.

## Repository implementation added in this milestone

```text
legacy-lab/app/
├── README.md
├── app.py
├── requirements.txt
├── schema.sql
├── seed_data.py
├── templates/
│   └── dashboard.html
└── static/
    ├── css/
    │   └── style.css
    └── images/
        └── madar-hero-truck.png   # local lab asset; repository upload pending provenance review
```

## Exact next action

1. Synchronize the local VM seed script with the repository's corrected fully deterministic version and rerun it.
2. Reconfirm `10 / 50 / 150` and one delivered shipment timeline after reseeding.
3. Create the operational-file area with deterministic shipment-linked artifacts.
4. Generate and verify a SHA-256 manifest plus file count/size baseline.
5. Configure and demonstrate one scheduled/background operation.
6. Demonstrate the application write path rather than only direct SQL writes/read-only UI behavior.
7. Capture representative aggregates in addition to row counts.
8. Create a pre-migration VM/database backup or snapshot point.
9. Inventory compute, processes, ports, configuration, database, filesystem, job, identity and network dependencies.
10. Draw the dependency map.
11. Only after discovery/assessment, approve the migration strategy and AWS target architecture.

## Important hold point

**Do not run Terraform apply yet.**

The target architecture remains intentionally undecided until the source workload, dependencies and migration evidence requirements are fully understood.

## Exit criteria for source-lab stage

- VM boots reliably. ✅
- workload is reachable and functional. ✅
- database contains deterministic seed records. ✅, with local reseed to corrected fixed-timestamp generator still required.
- operational files exist and can be checksummed. ⏳
- scheduled/background operation is demonstrated. ⏳
- inventory and dependencies are documented. ⏳
- full baseline counts/checksums are captured. ⏳
- snapshot/backup point exists before migration changes. ⏳

## Blockers

None currently. The remaining work is source-lab completion and discovery, not an infrastructure blocker.
