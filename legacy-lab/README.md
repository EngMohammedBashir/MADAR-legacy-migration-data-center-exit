# MADAR Legacy Lab — Pre-Cloud Baseline Representation

## Purpose

This directory contains the **reproducible lab representation of MADAR's pre-cloud legacy shipment workload** used by Phase 03.

The transformation narrative assumes that the legacy estate exists before Phase 01. When Phase 03 required a source that could actually be discovered, protected, migrated, cut over and validated, this VMware workload was constructed to represent that inherited estate.

Therefore two timelines coexist without contradiction:

```text
Business / architecture story:
Pre-Cloud Legacy Estate -> Phase 01 -> Phase 02 -> Phase 03 migration

Lab implementation chronology:
Phase 03 preparation -> build representative VMware source -> baseline -> migrate
```

The workload is intentionally small enough to run on constrained hardware but complete enough to expose migration-relevant dependencies: application runtime, relational state, operational files, scheduled processing, credentials/configuration, network listeners and recovery artifacts.

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

No real customer or personal data is used. The single-VM topology is a migration lab constraint, not a claim about a literal production data center.

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

The VM also produces operational CSV/report artifacts. These are included deliberately so the migration cannot be reduced to "move the database" or "move the Flask code." File count/content integrity was protected with SHA-256 baselines and later replatformed to S3.

## Scheduled/background processing

A Linux scheduled job queries PostgreSQL and generates a timestamped operations report without an interactive user session. This creates a dependency chain:

```text
scheduler -> DB credentials/connectivity -> query -> output path -> log
```

## Source recovery discipline

The lab created and validated PostgreSQL custom-format backups, operational-file archive/integrity evidence, PostgreSQL configuration backup before CDC changes, and a final PostgreSQL logical dump before VM Import/Export. Binary backups are excluded from Git.

## Migration disposition

```text
Ubuntu + Flask      -> rehost to EC2
PostgreSQL          -> replatform to RDS through DMS
Operational files   -> replatform to S3
Scheduled job       -> retain/reconfigure to target dependencies
```

The lab also produced a real hypervisor-migration preparation problem: the original VMware guest used `ens33`; the final VM Import/Export image was prepared and reboot-tested with `eth0` + DHCP plus EC2-relevant ENA/NVMe driver readiness.

## Directory purpose

- `app/` — representative source application, schema/seed and UI assets.
- `scripts/` — scheduled/background workload logic.

Implementation/build history lives in `docs/source-application-build.md` and `docs/source-lab-build-log.md`. Those build records prove reproducibility; they do not redefine the scenario's pre-cloud chronology.
