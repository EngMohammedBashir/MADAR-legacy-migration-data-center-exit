# MADAR Legacy Lab

## Purpose

This directory contains the representative source workload used to make Phase 03 a real migration exercise rather than an empty infrastructure demo.

The workload is intentionally small enough to run on a constrained laptop but complete enough to expose the kinds of dependencies that matter during migration: application runtime, relational state, operational files, scheduled processing, credentials/configuration, network listeners and recovery artifacts.

## Implemented workload

```text
MADAR-LEGACY-01 (VMware)
├── Ubuntu Server 24.04.4 LTS
├── Flask 3.1.3 shipment application / TCP 8080
├── PostgreSQL 16.14
│   ├── database: madar_legacy
│   └── application role: madar_app
├── deterministic synthetic dataset
│   ├── 10 customers
│   ├── 50 shipments
│   └── 150 shipment events
├── operational exports/reports/manifests
└── scheduled report job
```

No real customer or personal data is used.

## Data model

### Customers

```text
customer_id, company_name, region
```

### Shipments

```text
shipment_id, customer_id, origin, destination, status, created_at, updated_at
```

### Shipment events

```text
event_id, shipment_id, event_type, event_time
```

The application write path updates shipment state and inserts a matching shipment event transactionally.

## Why deterministic data matters

The seed is intentionally reproducible. Migration validation needs a known manifest of business state rather than a vague statement that "the database looks fine."

Accepted source baseline:

```text
Customers        10
Shipments        50
Shipment events  150
```

A controlled write-path exercise changed a representative shipment and inserted a new event; the deterministic seed was then rerun so migration started from the known baseline again.

## Operational state outside PostgreSQL

The VM also produces operational CSV/report artifacts. These are included deliberately so the migration cannot be reduced to "move the database" or "move the Flask code." File count/content integrity is protected with SHA-256 baselines and later replatformed toward S3.

## Scheduled/background processing

A Linux scheduled job queries PostgreSQL and generates a timestamped operations report without an interactive user session. This creates a real dependency on:

```text
scheduler -> DB credentials/connectivity -> query -> local output path -> log
```

The dependency must be revalidated/reconfigured after migration.

## Source recovery discipline

The lab created and validated:

- PostgreSQL custom-format backups,
- operational-file archive/integrity evidence,
- PostgreSQL configuration backup before CDC changes,
- a final PostgreSQL logical dump before the VM Import/Export image was exported.

Binary backups are excluded from Git.

## Migration relevance

The lab exposed multiple logical migration dispositions inside one VM:

```text
Ubuntu + Flask      -> rehost to EC2
PostgreSQL          -> replatform to RDS through DMS
Operational files   -> replatform to S3
Scheduled job       -> retain/reconfigure to target dependencies
```

It also produced a real hypervisor-migration preparation problem: the original VMware guest used `ens33`; the final VM Import/Export image was prepared and reboot-tested with `eth0` + DHCP plus EC2-relevant ENA/NVMe driver readiness.

## Directory purpose

- `app/` — source application, schema/seed and UI assets.
- `scripts/` — scheduled/background workload logic.

Implementation/build history lives in `docs/source-application-build.md` and `docs/source-lab-build-log.md`. Current migration execution lives in `CURRENT-STATE.md` and `docs/07-vm-import-execution-guide.md`.