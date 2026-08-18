# Phase 03 — Current State

**Status:** DISCOVERY + ASSESSMENT + TARGET DESIGN COMPLETE — PRE-MIGRATION READINESS IN PROGRESS  
**AWS paid-resource window:** NOT STARTED  
**Current objective:** finish zero-cost readiness and enter the migration session with an approved target, ordered runbook, validation gates and cleanup plan.

## Verified source estate

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── 2 vCPU / ~2.4 GiB RAM
├── PostgreSQL 16.14
├── Flask 3.1.3 on port 8080
├── Customers: 10
├── Shipments: 50
├── Shipment events: 150
├── Operational CSV exports/reports
├── Daily scheduled operations report at 02:00 Asia/Riyadh
└── Pre-migration database + file/config backups
```

## Completed engineering gates

### Source baseline and recoverability

- deterministic baseline restored to `10 customers / 50 shipments / 150 shipment events`,
- source write path proven transactionally and then reset,
- operational-file SHA-256 baseline verified,
- scheduled cron processing proven,
- PostgreSQL custom-format pre-migration dump verified,
- operational-file recovery archive verified,
- PostgreSQL configuration copied before DMS-related changes to:
  `/home/madaradmin/madar-backups/postgresql-16-main-before-dms`.

### Discovery and dependency assessment

Discovery verified:

- 2 vCPU / ~2.4 GiB RAM,
- ~23 GiB root filesystem with ~5.4 GiB used during discovery,
- Flask/Python listener on `0.0.0.0:8080`,
- PostgreSQL listener on `127.0.0.1:5432`,
- SSH on TCP 22,
- active PostgreSQL, cron and SSH services,
- VMware NAT source network `192.168.14.128/24`,
- application -> PostgreSQL dependency,
- cron -> PostgreSQL -> local report-file dependency.

The workload is treated as several logical components rather than one indivisible VM.

### Approved migration strategy

```text
Ubuntu + Flask -------- AWS MGN -------------> EC2
PostgreSQL 16 --------- AWS DMS Full+CDC ----> RDS PostgreSQL
Operational files ----- validated transfer --> S3
Scheduled job ---------- reconfigure --------> target DB/storage path
Target protection ------ AWS Backup ----------> where useful after cutover
```

MGN rehosts the machine/runtime. DMS replatforms and synchronizes database data. They solve different migration concerns and are intentionally used together.

### Approved lab target

- Region: `us-east-1`.
- VPC: `10.30.0.0/16`.
- Public application subnet: `10.30.1.0/24`.
- Private DB subnets: `10.30.11.0/24`, `10.30.12.0/24`.
- EC2 target candidate: `t3.small`.
- RDS PostgreSQL: small burstable class, Single-AZ; `db.t3.micro` candidate subject to execution-time availability.
- DMS: minimum suitable capacity, Full Load + CDC.
- S3 for operational files.
- No NAT Gateway, no ALB and no Multi-AZ RDS for this short-lived migration proof.

### DMS / CDC source readiness

Verified:

```text
PostgreSQL version          16.14
wal_level                   replica
max_replication_slots       10
max_wal_senders             10
config file                 /etc/postgresql/16/main/postgresql.conf
```

`wal_level=replica` is intentionally retained before AWS execution. DMS Premigration Assessment will be used first to record the AWS-native readiness finding, then required source changes will be applied and reassessed before Full Load + CDC.

### MGN source connectivity

Outbound HTTPS from the VMware source to an AWS MGN-related regional S3 endpoint in `us-east-1` was verified. HTTP 403 from the unauthenticated bucket request confirmed AWS network reachability; no AWS migration resources were created by this check.

## Cost posture

The AWS paid-resource window has **not started**. Preparation intentionally avoids running EC2/RDS/DMS/MGN target resources while planning is still in progress.

Execution principles:

- check cost/credits immediately before creation,
- create resources only when needed,
- target a short migration sprint (roughly three hours where practical),
- treat AWS credits as real money,
- capture evidence before deletion,
- aggressively clean temporary resources after acceptance.

## AWS-native automation preference

Before giving a long sequence of manual commands, evaluate whether AWS provides a suitable managed assessment, agent or automation. Prefer the AWS-native option when it materially reduces toil and is affordable. Manual source changes remain appropriate where AWS cannot perform the change safely.

Examples: DMS Premigration Assessment, MGN replication workflow and post-cutover AWS Backup.

## Exact next actions

1. Finalize the secure temporary connectivity design from AWS DMS to the local PostgreSQL source; do not expose PostgreSQL publicly.
2. At migration-session start, check credits/cost and quotas.
3. Create AWS foundation in the order defined in `runbooks/migration-day-runbook.md`.
4. Run DMS Premigration Assessment before CDC remediation and capture the finding.
5. Remediate/reassess PostgreSQL logical-replication readiness.
6. Execute DMS Full Load + CDC and prove a live source change arrives in RDS.
7. Execute MGN test/cutover workflow for the Ubuntu/Flask runtime.
8. Transfer operational files to S3 and verify integrity.
9. Validate application, data, files and scheduled processing.
10. Cut over only after reconciliation passes; preserve source until acceptance.
11. Apply target backup protection where useful.
12. Clean paid temporary resources and record actual cost/credit delta.

## Important hold point

**Do not create paid AWS migration resources until the migration session explicitly starts.**

The repository is now prepared to move from zero-cost readiness into controlled AWS execution.
