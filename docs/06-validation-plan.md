# Migration Validation Plan

## Principle

A migration is not trusted because an AMI exists, an EC2 instance reaches `running`, or an RDS instance reports `available`. Validation compares target state against the recorded source baseline and proves workload behavior plus data continuity.

## Source baseline

```text
Customers        10
Shipments        50
Shipment events  150
Database         madar_legacy
PostgreSQL       16.14
Tables           customers / shipments / shipment_events
```

An independent PostgreSQL custom-format dump exists and was validated with `pg_restore -l`.

## Gate 1 — VM import artifact: PASS

Validated before import:

- clean VMware export contains no attached installer ISO,
- VMDK is `streamOptimized`,
- S3 object size matches the local VMDK,
- staging bucket is private,
- `vmimport` trusts `vmie.amazonaws.com`,
- required S3/image permissions exist,
- operator `iam:PassRole` simulation returned `allowed`.

## Gate 2 — ImportImage task: PASS

Recorded result:

```text
ImportTaskId  import-ami-48f44651b4c75774t
Status        completed
AMI           ami-0cbd2e9ec0d6f9168
Snapshot      snap-0920a020c47fb6447
```

## Gate 3 — EC2 boot acceptance: PASS

Validated:

```text
EC2 running + status checks
 -> Ubuntu boot
 -> eth0 / DHCP
 -> default route
 -> SSH
 -> NVMe-backed disk
 -> LVM/ext4 activation
 -> zero failed systemd units
```

## Gate 4 — OS and service reconciliation: PASS

- Ubuntu 24.04.4 / kernel 6.8.0-138 / x86_64,
- PostgreSQL 16.14 enabled and active,
- Flask/application files present,
- expected cron configuration preserved.

## Gate 5 — Database reconciliation on imported EC2: PASS

```text
customers         10
shipments         50
shipment_events   150
```

Expected tables and database `madar_legacy` were present.

## Gate 6 — Application validation: PASS

Observed:

```text
/api/health
status       ok
database     connected

/api/summary
customers    10
shipments    50
events       150
```

The Flask process did not auto-start because the legacy application was not managed by systemd; it was manually started with its runtime DB credential. This is recorded as a post-migration operational improvement, not hidden as a migration failure.

## Gate 7 — DMS/RDS database replatform: PASS

### CDC readiness

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
```

PostgreSQL was made VPC-reachable on TCP/5432, with `pg_hba.conf` and SG controls restricting authenticated access.

### RDS target

```text
PostgreSQL  16.14
Class       db.t3.micro
Public      false
Status      available
```

### DMS infrastructure

```text
Replication instance  madar-dms-repl
dms class              dms.t3.small
Status                 available
Private IP             172.31.13.46
```

### Endpoint gates

```text
Source endpoint  successful
Target endpoint  successful
```

Troubleshooting accepted as evidence:

- `dms-vpc-role` missing/misconfigured -> repaired IAM trust and attached `AmazonDMSVPCManagementRole`,
- target rejected unencrypted connection -> target endpoint changed to `ssl-mode=require`,
- target then rejected password -> credential synchronized,
- final target connection -> `successful`.

### Full Load gate

```text
FullLoadProgress  100
TablesLoaded      3
TablesLoading     0
TablesErrored     0

customers         10
shipments         50
shipment_events   150
```

An independent SQL query against RDS confirmed the same initial counts.

### CDC gate

Controlled source-side change:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

Without rerunning Full Load, RDS contained the same row and `customers` became `11`.

Final RDS reconciliation:

```text
customers         11
shipments         50
shipment_events   150
```

This is direct evidence that Full Load established the initial state and CDC propagated a later change.

## Gate 8 — File validation: PENDING

- source file count recorded,
- target object count must match expected scope,
- SHA-256/content validation required,
- naming/prefix structure must be accepted.

## Cutover gate: PENDING

Stage 2 data migration passed, but an application cutover is a separate decision.

Before final cutover:

```text
CDC caught up
 -> final reconciliation
 -> securely configure Flask for RDS
 -> validate health/read/write
 -> explicitly continue or abort
 -> retain rollback anchor until acceptance
```

## Operational/security validation

Passed so far:

- RDS is private,
- PostgreSQL migration paths are SG-to-SG,
- no `0.0.0.0/0 -> 5432` rule used,
- target DMS connection uses TLS,
- secrets are excluded from Git,
- rollback source/recovery artifacts remain available.

Remaining:

- final cutover secret handling,
- monitoring/operational improvements,
- resource cleanup,
- cost/credit review.

## Evidence sequence

Completed through database replatform:

```text
18-rds-postgresql-target-available.png
19-dms-replication-instance-available.png
20-source-endpoint-connection-success.png
21-target-endpoint-connection-success.png
22-dms-full-load-completed.png
23-cdc-replication-proof.png
24-final-data-reconciliation.png
```

## Pass/fail rule

Unexplained differences are failures until reconciled or explicitly accepted. A successful AWS resource state never substitutes for workload/data validation.