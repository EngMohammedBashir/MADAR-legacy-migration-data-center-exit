# Phase 03 Evidence Index

Evidence exists to prove engineering claims. Screenshots are not collected as decoration, and planned evidence is not described as completed evidence.

## Evidence naming rule

Use ordered, descriptive names so a reviewer can follow the migration chronologically without opening every file blindly.

```text
NN-short-engineering-fact.png
```

Do not publish screenshots that expose passwords, private keys, session tokens, shell history containing secrets, or unrelated desktop content.

## Source baseline evidence

Representative local evidence includes:

```text
madar-legacy-vm-system-baseline.png
madar-legacy-vm-network-ssh.png
madar-lvm-storage-expanded.png
madar-base-os-patched.png
madar-runtime-postgresql-installed.png
madar-deterministic-dataset-baseline.png
madar-application-dashboard.png
madar-source-files-sha256-baseline.png
madar-cron-background-job-verified.png
madar-application-write-path-verified.png
madar-source-baseline-restored.png
madar-pre-migration-db-backup-verified-v2.png
madar-pre-migration-files-backup-verified.png
```

These prove the original VMware workload, deterministic `10 / 50 / 150` database baseline, application behavior and recoverability before migration.

## MGN experiment evidence

Retain evidence showing:

```text
MGN source server -> 25/25 GiB replicated
MGN status -> Healthy / Ready for testing
MGN launch history -> snapshot success / conversion failure
CloudTrail RunInstances -> m5.large Conversion Server
AWS Transform response -> conversion-server type not configurable
EC2 -> replication server terminated
MGN -> zero active source servers after cleanup
EBS/Snapshot -> residual resources cleaned
```

This supports the ADR that the visible `t3.small` target was not the failing resource.

## VM Import/Export evidence

Completed engineering checkpoints include:

```text
03-vmimport-role-trust.png
04-vmimport-role-permissions.png
05-vm-import-converting-09-percent.png
06-vm-import-updating-43-percent.png
07-vm-import-booting-62-percent.png
08-vm-import-completed-ami-created.png
09-imported-ami-available.png
10-ec2-imported-vm-running.png
11-ec2-status-checks-passed.png
12-ssh-success-migrated-ubuntu.png
13-post-migration-workload-validation.png
14-rehost-database-validation-pass.png
15-flask-running-on-migrated-ec2.png
16-migrated-application-api-validation-pass.png
17-postgresql-cdc-ready.png
```

Important facts represented by this group:

- the import role has a service trust relationship and explicit permissions,
- the asynchronous VM Import task progressed through conversion/update/boot phases,
- import completed with an AMI and EBS snapshot,
- imported EC2 booted and passed AWS status checks,
- Linux networking changed from VMware `192.168.14.x` to VPC `172.31.x.x`,
- NVMe/LVM/filesystem state survived the hypervisor move,
- PostgreSQL 16.14 remained healthy,
- initial `10 / 50 / 150` data reconciled,
- Flask health/summary passed after runtime configuration was restored,
- source PostgreSQL was prepared for logical CDC.

## DMS / RDS evidence — COMPLETED THROUGH CDC

### 18 — RDS target available

```text
18-rds-postgresql-target-available.png
```

Should show the private RDS PostgreSQL target in `available` state with the intended instance class/version. The target is PostgreSQL 16.14 on `db.t3.micro`, `PubliclyAccessible=false`.

### 19 — DMS replication instance available

```text
19-dms-replication-instance-available.png
```

Captured facts:

```text
Class       dms.t3.small
Private IP  172.31.13.46
Status      available
```

This proves the private DMS compute node was provisioned successfully after fixing the `dms-vpc-role` prerequisite.

### 20 — Source endpoint connection successful

```text
20-source-endpoint-connection-success.png
```

Expected/captured fact:

```text
madar-postgres-source | Failure=None | Status=successful
```

This proves DMS can connect to PostgreSQL on the migrated EC2 source.

### 21 — Target endpoint connection successful

```text
21-target-endpoint-connection-success.png
```

Expected/captured fact:

```text
madar-postgres-target | Failure=None | Status=successful
```

Troubleshooting evidence before the successful screenshot is also valuable in documentation:

```text
failure 1: no encryption
fix:      DMS target endpoint ssl-mode=require

failure 2: password authentication failed
fix:      synchronize RDS/DMS target credentials

final:    successful
```

Do not publish a screenshot containing the actual password or a command line that exposes it.

### 22 — DMS Full Load completed

```text
22-dms-full-load-completed.png
```

Important facts:

```text
FullLoadProgress  100
Status            running
TablesLoaded      3
TablesLoading     0
TablesErrored     0

customers         Table completed   10
shipments         Table completed   50
shipment_events   Table completed   150
```

`running` after 100% is expected because this is a `full-load-and-cdc` task; DMS remains active to capture changes.

### 23 — CDC replication proof

```text
23-cdc-replication-proof.png
```

Controlled source change:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

The same row appeared in RDS **without rerunning Full Load**, proving CDC from source WAL through DMS to the target.

### 24 — Final data reconciliation

```text
24-final-data-reconciliation.png
```

Final RDS counts:

```text
customers         11
shipments         50
shipment_events   150
```

This is the final Stage 2 data-integrity checkpoint after the controlled CDC insert.

## Screenshot placement guidance

Recommended repository layout if the actual image files are added from the workstation:

```text
evidence/
├── vm-import/
│   ├── 03-vmimport-role-trust.png
│   ├── 04-vmimport-role-permissions.png
│   ├── ...
│   └── 17-postgresql-cdc-ready.png
└── dms-rds/
    ├── 18-rds-postgresql-target-available.png
    ├── 19-dms-replication-instance-available.png
    ├── 20-source-endpoint-connection-success.png
    ├── 21-target-endpoint-connection-success.png
    ├── 22-dms-full-load-completed.png
    ├── 23-cdc-replication-proof.png
    └── 24-final-data-reconciliation.png
```

The connected GitHub text interface used during this session can update Markdown and code files but does not provide a general binary-image upload action. Therefore this index records the exact intended filenames/locations; the screenshot binaries themselves should be copied into those paths from the workstation before final portfolio publication.

## Evidence still required

### File/cutover/closeout

- S3 operational-file integrity validation,
- final application cutover decision,
- Flask-to-RDS validation if an actual DB cutover is executed,
- rollback proof where practical,
- cleanup/residual-resource review,
- actual cost/credit delta,
- final RTO/RPO narrative.

## Quality and security rules

- never publish credentials, tokens, `.pgpass`, `.env`, private keys or raw session credentials,
- never publish shell history showing database passwords,
- VM images and database backups remain outside Git,
- review screenshots for account-sensitive identifiers and unrelated desktop content,
- crop evidence to the engineering fact being demonstrated,
- preserve failures and status messages when they explain a decision,
- never mark a planned gate as passed merely because a command was started.