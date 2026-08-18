# Phase 03 — Current State

**Status: PRE-MIGRATION READY — WAITING FOR AWS EXECUTION WINDOW**  
**AWS paid-resource window: NOT STARTED**

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
└── Verified pre-migration DB + file/config backups
```

## Completed readiness

- deterministic database baseline restored and verified,
- transactional application write path proven,
- scheduled background processing proven,
- source operational-file SHA-256 baseline verified,
- PostgreSQL custom-format pre-migration dump verified,
- PostgreSQL configuration backed up before DMS/CDC changes,
- source compute/runtime/network/filesystem/service dependencies discovered,
- component-level migration strategy approved,
- target VPC/subnet/security direction approved,
- source outbound HTTPS reachability to AWS `us-east-1` verified,
- PostgreSQL CDC baseline inspected,
- migration-day runbook, validation, rollback, screenshot and cleanup plans prepared,
- paid AWS migration resources intentionally not started during preparation.

## Final staged migration strategy

```text
STAGE 1 — REHOST
VMware MADAR-LEGACY-01
      |
      | AWS MGN
      v
EC2: Ubuntu + Flask + PostgreSQL + files

STAGE 2 — REPLATFORM DATABASE
EC2 PostgreSQL
      |
      | AWS DMS Full Load + CDC
      v
RDS PostgreSQL

STAGE 3 — REPLATFORM FILES
Small operational CSV/reports
      |
      | validated copy
      v
Amazon S3
```

This sequence deliberately avoids building direct DMS connectivity from AWS into the VMware NAT address. MGN first places the server inside AWS; DMS then migrates PostgreSQL from the EC2 intermediate source to private RDS.

## AWS target direction

- Region: `us-east-1`.
- VPC: `10.30.0.0/16`.
- Application subnet: `10.30.1.0/24`.
- Private DB subnets: `10.30.11.0/24`, `10.30.12.0/24`.
- EC2 target candidate: `t3.small`.
- RDS PostgreSQL: small burstable Single-AZ class, finalized at execution.
- DMS: minimum suitable replication capacity for Full Load + CDC.
- S3: operational files.
- AWS Backup: evaluated post-cutover for useful target protection.
- No NAT Gateway, ALB or Multi-AZ RDS for this short-lived migration proof.

## DMS / CDC baseline

```text
PostgreSQL version          16.14
wal_level                   replica
max_replication_slots       10
max_wal_senders             10
config file                 /etc/postgresql/16/main/postgresql.conf
```

`wal_level=replica` remains intentionally unchanged before execution. After the MGN EC2 source is available, DMS Premigration Assessment will be run first, the AWS-native finding captured, required logical-replication remediation applied to the EC2 PostgreSQL source, and the assessment rerun before Full Load + CDC.

## File-transfer decision

The representative file estate is tiny, so a simple validated transfer to S3 is appropriate. AWS DataSync was evaluated and rejected for this lab as unnecessary overhead. For a large independent file estate, DataSync would be a primary AWS-native option to evaluate rather than relying on MGN as a bulk-file migration mechanism.

## Cost posture

The AWS paid-resource window has not started. At execution:

1. check credits/cost and quotas,
2. record start time,
3. create only resources required for the current stage,
4. capture evidence immediately at defined gates,
5. remove temporary resources after acceptance,
6. record actual credit/cost delta.

AWS credits are treated as real money.

## AWS-native automation preference

Before introducing long manual command sequences, first evaluate AWS-native assessments, agents and managed workflows. Prefer them when they materially reduce toil and are affordable. Manual source changes are reserved for work the AWS service cannot safely perform automatically.

## Exact next actions when execution begins

```text
1. Billing/credits + quota check
2. Minimal VPC/network/security foundation
3. MGN initialize + agent
4. MGN replication -> EC2 test target
5. Validate Flask + PostgreSQL on EC2
6. Create private RDS + minimum DMS capacity
7. DMS Premigration Assessment
8. Fix/reassess CDC readiness on EC2 PostgreSQL
9. DMS Full Load + CDC
10. Prove live shipment/event replication
11. Transfer small operational files -> S3 + SHA-256 validation
12. Point Flask -> RDS and validate
13. Cutover + acceptance
14. AWS Backup where useful
15. Cleanup + final cost evidence
```

## Hold point

**STOP HERE until the AWS execution window intentionally begins.**

No paid migration resource needs to be created during the remaining preparation period.
