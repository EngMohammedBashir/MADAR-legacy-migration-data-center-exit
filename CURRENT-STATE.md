# Phase 03 — Current State

**Status: VM REHOST COMPLETE — DATABASE REPLATFORM VALIDATED**  
**Region: us-east-1**

## Executive state

Stage 1 and Stage 2 have both passed their technical acceptance gates.

```text
Stage 1  VMware -> EC2 VM rehost                 COMPLETE
Stage 2  EC2 PostgreSQL -> RDS via DMS          COMPLETE
Stage 3  operational file replatform to S3      NEXT
Cutover  application DB switch + closeout       NEXT
```

## Stage 1 — VMware -> EC2: COMPLETE

```text
VMware MADAR-LEGACY-01
  -> clean streamOptimized VMDK
  -> private S3 staging
  -> EC2 VM Import/Export
  -> AMI ami-0cbd2e9ec0d6f9168
  -> EC2 i-051336c5f304a5319
```

Import result:

```text
ImportTaskId   import-ami-48f44651b4c75774t
Status         completed
AMI            ami-0cbd2e9ec0d6f9168
Snapshot       snap-0920a020c47fb6447
Architecture   x86_64
Virtualization HVM
ENA            enabled
```

Migrated EC2 acceptance:

```text
Name          MADAR-LEGACY-EC2
Instance      i-051336c5f304a5319
Type          t3.small
Private IP    172.31.3.142
VPC           vpc-015017581b8954e61
Subnet        subnet-04e63af31360b080a
```

Validated:

- Ubuntu 24.04.4 / kernel 6.8.0-138 / x86_64 booted.
- `eth0` acquired VPC DHCP configuration.
- LVM/ext4 mounted correctly on NVMe-presented EBS storage.
- SSH access succeeded.
- PostgreSQL 16.14 was enabled and active.
- `madar_legacy` and expected tables existed.
- baseline counts matched `10 / 50 / 150`.
- zero failed systemd units.
- Flask `/api/health` returned database connected / status ok.
- Flask `/api/summary` returned the expected business counts.

## Stage 2 — EC2 PostgreSQL -> RDS via AWS DMS: COMPLETE

### Source CDC readiness

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
PostgreSQL listener    TCP/5432 on VPC-reachable interface
DMS login              dedicated and connectivity validated
```

Secrets are not recorded in Git.

### Private network controls

```text
Source EC2 SG  sg-0589383abcc3ebbbc
DMS SG         sg-085569e2731850c8a
RDS SG         sg-093756a8cabaad407
```

Allowed migration paths:

```text
DMS SG  -> TCP/5432 -> source EC2 PostgreSQL
DMS SG  -> TCP/5432 -> target RDS PostgreSQL
EC2 SG  -> TCP/5432 -> RDS for validation/cutover testing
```

No Internet-wide PostgreSQL ingress was used.

### RDS target

```text
Identifier  madar-postgres-target
Engine      PostgreSQL 16.14
Class       db.t3.micro
Storage     20 GiB gp3
Public      false
Endpoint    madar-postgres-target.cgx64cygc3mj.us-east-1.rds.amazonaws.com
Status      available
```

### DMS infrastructure

```text
IAM role        dms-vpc-role
Trust           dms.amazonaws.com
Managed policy  AmazonDMSVPCManagementRole
Subnet group    madar-dms-subnets / Complete / us-east-1a + us-east-1b
Replication     madar-dms-repl
Class           dms.t3.small
Engine          3.6.1
Private IP      172.31.13.46
Status          available
```

The first replication-subnet-group request failed because `dms-vpc-role` was not configured. Fixing IAM trust/policy resolved the request without changing network design.

### Endpoint validation

```text
Source endpoint  madar-postgres-source  successful
Target endpoint  madar-postgres-target  successful
```

Target troubleshooting preserved as an engineering finding:

1. `no pg_hba.conf entry ... no encryption` -> DMS had reached RDS, but target connection needed TLS.
2. target endpoint changed to `ssl-mode=require`.
3. next error became `password authentication failed` -> network/TLS were now healthy; credentials were the remaining layer.
4. RDS credential and endpoint credential were synchronized.
5. target test returned `successful`.

### Full Load + CDC task

```text
Task            madar-full-load-cdc
Migration type  full-load-and-cdc
Status          running after initial load
Full Load       100%
Tables loaded   3
Tables loading  0
Tables errored  0
```

Per-table Full Load:

```text
public.customers         Table completed   10 rows
public.shipments         Table completed   50 rows
public.shipment_events   Table completed   150 rows
```

Independent SQL query against RDS confirmed the same `10 / 50 / 150` baseline.

### CDC proof

A controlled row was inserted into the **source EC2 PostgreSQL** after Full Load:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

Without rerunning Full Load, the same row appeared on RDS and the target customer count became `11`.

Final target reconciliation:

```text
customers         11
shipments         50
shipment_events   150
```

**Stage 2 acceptance: PASS.**

## Evidence checkpoint

Completed evidence sequence through Stage 2:

```text
18-rds-postgresql-target-available.png
19-dms-replication-instance-available.png
20-source-endpoint-connection-success.png
21-target-endpoint-connection-success.png
22-dms-full-load-completed.png
23-cdc-replication-proof.png
24-final-data-reconciliation.png
```

See `evidence/README.md` for captions and publication rules.

## Detailed execution docs

```text
docs/07-vm-import-execution-guide.md  VMware -> EC2
/docs/09-dms-rds-execution-guide.md    EC2 PostgreSQL -> RDS via DMS
```

## Next gate

```text
1. decide whether to perform actual Flask cutover to RDS in this lab
2. if cutting over: move runtime DB secret safely and validate Flask against RDS
3. replatform approved operational files to S3 and validate hashes/counts
4. document explicit continue/rollback decision
5. inventory and clean temporary migration infrastructure
6. review actual AWS cost/credit impact
7. finalize RTO/RPO and lessons learned
8. update the master transformation repository
```

## Stop rule

Do not delete the source/recovery anchors until cutover acceptance is documented. Do not delete DMS before any desired final CDC/cutover evidence is captured.