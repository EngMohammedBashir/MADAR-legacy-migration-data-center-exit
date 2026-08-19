# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has a representative legacy shipment-management workload hosted on VMware. This phase demonstrates a controlled data-center-exit workflow: discover the source, protect recoverability, troubleshoot a blocked migration path, rehost the machine into AWS, validate business state, then replatform PostgreSQL to a managed database with low-downtime replication.

> MADAR is fictional. The workload, commands, failures, AWS behavior, troubleshooting and evidence are technically authentic lab work.

## Executive summary

The source VMware VM runs Ubuntu 24.04.4, Flask and PostgreSQL 16.14. The original rehost path used AWS Transform / Application Migration Service (MGN). Block replication reached 25/25 GiB and Ready for testing, but the service-managed conversion stage attempted an `m5.large`, which the account's Free Plan rejected. CloudTrail isolated the failing `RunInstances` request and AWS Transform confirmed that conversion-server sizing was not customer-configurable.

The project therefore pivoted to **EC2 VM Import/Export** rather than upgrading the account merely to force the lab through. That fallback is now complete: the clean VMware VMDK was staged in private S3, imported into an AMI, launched as EC2, and validated successfully.

The project is now executing **database replatforming from EC2 PostgreSQL to Amazon RDS for PostgreSQL using AWS DMS Full Load + CDC**.

## Current architecture

```text
STAGE 1 — REHOST (COMPLETE)

VMware MADAR-LEGACY-01
        |
        | clean streamOptimized VMDK
        v
private Amazon S3 staging
        |
        | EC2 VM Import/Export
        v
AMI ami-0cbd2e9ec0d6f9168
        |
        v
EC2 i-051336c5f304a5319 / t3.small
Ubuntu + Flask + PostgreSQL 16.14
private IP 172.31.3.142
        |
        | validated: boot/network/filesystem/DB/app
        v
baseline preserved: 10 customers / 50 shipments / 150 events

STAGE 2 — DATABASE REPLATFORM (IN PROGRESS)

EC2 PostgreSQL 16.14
        |
        | TCP 5432 restricted to DMS SG
        v
AWS DMS replication instance
madar-dms-repl / dms.t3.small
        |
        | Full Load + CDC
        v
Amazon RDS PostgreSQL 16.14
madar-postgres-target / db.t3.micro / private

STAGE 3 — FILE REPLATFORM (NEXT)

Operational CSV/reports
        |
        | validated transfer + SHA-256 verification
        v
Amazon S3
```

## Rehost result

VM Import/Export completed successfully:

```text
Import task    import-ami-48f44651b4c75774t
AMI            ami-0cbd2e9ec0d6f9168
Snapshot       snap-0920a020c47fb6447
Architecture   x86_64
Virtualization HVM
ENA            enabled
Root           25 GiB EBS
```

The imported AMI was launched as `MADAR-LEGACY-EC2` (`i-051336c5f304a5319`) using `t3.small` in the lab VPC. SSH succeeded and the migrated host preserved the expected Linux storage layout and application/database state.

Validation after rehost:

- Ubuntu 24.04.4 booted on AWS.
- `eth0` obtained VPC DHCP configuration.
- SSH administration succeeded.
- LVM/ext4 filesystems mounted correctly.
- PostgreSQL 16.14 was enabled and active.
- `madar_legacy` existed with the expected schema.
- Counts reconciled to **10 customers / 50 shipments / 150 shipment events**.
- zero failed systemd units were reported.
- Flask health returned database connected after loading the application credential into the runtime environment.

This distinction matters: **an AMI reaching `available` was not treated as migration success; the workload itself had to prove it still worked.**

## Database replatform design

The source PostgreSQL instance was prepared for logical change replication:

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
```

A dedicated DMS database principal was created and private-VPC PostgreSQL connectivity was tested. Credentials are intentionally excluded from Git.

Network access is SG-to-SG rather than Internet-wide:

```text
DMS SG  sg-085569e2731850c8a
   |-- TCP/5432 --> source EC2 SG sg-0589383abcc3ebbbc
   `-- TCP/5432 --> target RDS SG sg-093756a8cabaad407
```

The RDS target is already available:

```text
Identifier  madar-postgres-target
Engine      PostgreSQL 16.14
Class       db.t3.micro
Storage     20 GiB gp3
Public      false
Endpoint    madar-postgres-target.cgx64cygc3mj.us-east-1.rds.amazonaws.com
```

The DMS replication subnet group spans `us-east-1a` and `us-east-1b` and reports `Complete`. The replication instance `madar-dms-repl` uses `dms.t3.small`, DMS engine 3.6.1, private networking, and was last observed provisioning. The repository will not claim it is available until AWS reports that state.

## A useful DMS failure and its resolution

The first `CreateReplicationSubnetGroup` request failed with an IAM error stating that `dms-vpc-role` was not configured properly.

Rather than changing subnets or opening network access, the prerequisite was fixed at the correct layer:

```text
AWS DMS
   |
   | sts:AssumeRole
   v
dms-vpc-role
   |
   `-- AmazonDMSVPCManagementRole
```

After configuring trust for `dms.amazonaws.com` and attaching the AWS-managed VPC management policy, the same subnet-group request succeeded. This is retained as evidence of distinguishing **IAM control-plane failure** from **data-plane network failure**.

## Why the earlier MGN failure matters

MGN itself successfully replicated the source blocks. The failure happened later in a different compute role:

```text
MGN replication server     configurable
MGN target EC2             configurable
MGN conversion server      service-managed; not customer-configurable
```

CloudTrail showed the conversion server requesting `m5.large`; the account rejected that instance type under its plan. The target `t3.small` was therefore not the failing resource. MGN resources were cleaned and the migration strategy was deliberately changed.

See `decisions/ADR-002-mgn-free-plan-blocker-and-vm-import-fallback.md`.

## Engineering decisions demonstrated

- preserve an independent PostgreSQL recovery artifact before migration,
- validate hypervisor-to-EC2 boot, ENA/NVMe, GRUB and network compatibility before export,
- use private S3 staging and an IAM service role for VM Import/Export,
- diagnose managed-service failures using CloudTrail rather than repeated retries,
- keep source and target PostgreSQL on the same major/minor version for this lab migration,
- use a private RDS target rather than exposing the database publicly,
- restrict PostgreSQL migration traffic to the DMS security group,
- enable PostgreSQL logical replication before CDC,
- separate rehost success from database replatform success,
- use deterministic row counts and a controlled CDC change as acceptance evidence,
- treat temporary migration infrastructure and AWS credits as real operational cost.

## Evidence checkpoints

The evidence set is intentionally sequential. The latest completed checkpoint is:

```text
18-rds-postgresql-target-available.png
```

Next planned captures:

```text
19-dms-replication-instance-available.png
20-source-endpoint-connection-success.png
21-target-endpoint-connection-success.png
22-dms-full-load-completed.png
23-cdc-replication-proof.png
24-final-data-reconciliation.png
```

Evidence is captured only after the corresponding state is actually observed.

## Validation philosophy

A migration is not successful because an AWS resource says `Available`.

The acceptance chain is:

```text
machine boot
  -> network
  -> administration
  -> filesystem
  -> PostgreSQL service
  -> database/schema/data
  -> application health
  -> DMS source/target connectivity
  -> full-load reconciliation
  -> CDC proof
  -> cutover readiness
  -> rollback viability
```

## Security and cost discipline

- no VM image, database dump, secret, `.env`, `.pgpass` or private key is committed to Git,
- S3 VM-import staging is private,
- service integrations use IAM roles rather than static AWS credentials,
- RDS is not publicly accessible,
- PostgreSQL 5432 is not opened to the Internet for DMS,
- lab resources use intentionally small single-AZ sizing where HA is not the experiment's objective,
- temporary migration resources will be removed after their evidence purpose is complete.

## What this project demonstrates to a reviewer

This is not a diagram-only migration project. It demonstrates source discovery, VMware/Linux administration, PostgreSQL recovery and replication concepts, AWS MGN experimentation, CloudTrail troubleshooting, IAM service roles, S3 staging, EC2 VM Import/Export, EC2 validation, RDS provisioning, DMS networking and IAM prerequisites, security-group design, deterministic reconciliation, CDC planning, rollback thinking, and cost-aware engineering.

The failed MGN route remains documented because production engineering is not a sequence of perfect screenshots. The useful skill is identifying the failing layer, proving why it failed, protecting recoverability, and changing the migration mechanism without losing control of risk.

## Repository map

- `CURRENT-STATE.md` — exact live execution state and next gate.
- `docs/01-business-case.md` — business reason for the migration.
- `docs/02-source-estate.md` — logical estate and representative lab topology.
- `docs/03-discovery-assessment.md` — verified source dependencies and assessment.
- `docs/04-migration-strategy.md` — staged rehost/replatform strategy.
- `docs/05-target-architecture.md` — target boundaries, security and sizing.
- `docs/06-validation-plan.md` — acceptance and reconciliation criteria.
- `docs/07-vm-import-execution-guide.md` — VM Import/Export execution details.
- `docs/08-interview-guide.md` — recruiter/interview explanation and likely questions.
- `runbooks/migration-day-runbook.md` — ordered execution/rollback/cleanup procedure.
- `checklists/phase03-master-checklist.md` — implementation and evidence progress.
- `evidence/README.md` — evidence catalog and capture rules.
- `decisions/` — architecture decision records and migration pivots.
- `legacy-lab/` — representative source application and scheduled workload.
- `terraform/` — IaC position and future target infrastructure scope.

For the exact current execution state, see `CURRENT-STATE.md`.