# Phase 03 — Current State

**Status: REHOST VALIDATED — DATABASE REPLATFORM IN PROGRESS**  
**Region: us-east-1**

## Executive state

The VMware rehost path is complete and validated. The exported VMDK was uploaded to private S3 staging, converted by EC2 VM Import/Export into an AMI, launched as EC2, and validated at OS, network, filesystem, PostgreSQL, database and application levels.

The project has now entered Stage 2: replatforming PostgreSQL from the migrated EC2 host to Amazon RDS for PostgreSQL using AWS DMS Full Load + CDC.

## Stage 1 — VMware -> EC2: COMPLETE

```text
VMware MADAR-LEGACY-01
  -> clean streamOptimized VMDK
  -> private S3 staging
  -> EC2 VM Import/Export
  -> AMI ami-0cbd2e9ec0d6f9168
  -> EC2 i-051336c5f304a5319
```

Import task:

```text
ImportTaskId  import-ami-48f44651b4c75774t
Status        completed
AMI           ami-0cbd2e9ec0d6f9168
Snapshot      snap-0920a020c47fb6447
Architecture  x86_64
Virtualization hvm
ENA           enabled
Root volume   25 GiB
```

Migrated EC2:

```text
Name          MADAR-LEGACY-EC2
Instance      i-051336c5f304a5319
Type          t3.small
Private IP    172.31.3.142
VPC           vpc-015017581b8954e61
Subnet        subnet-04e63af31360b080a / us-east-1a
Source SG     sg-0589383abcc3ebbbc
```

Post-import validation succeeded:

- Ubuntu 24.04.4 / kernel 6.8.0-138 / x86_64 booted successfully.
- `eth0` acquired VPC DHCP networking.
- SSH administration succeeded.
- LVM/ext4 root filesystem mounted correctly.
- PostgreSQL 16.14 is enabled and active.
- `madar_legacy` exists.
- Tables: `customers`, `shipments`, `shipment_events`.
- Baseline counts preserved: **10 / 50 / 150**.
- `systemctl --failed` returned zero failed units.
- Flask application was manually restarted with its required environment credential and returned healthy database connectivity and the expected summary counts.

## Stage 2 — PostgreSQL -> RDS with DMS: ACTIVE

### Source preparation

PostgreSQL logical replication support was enabled:

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
```

PostgreSQL was configured to listen for VPC-local migration traffic and `pg_hba.conf` permits SCRAM authentication for the lab VPC range. A dedicated DMS database login was created and connectivity to `madar_legacy` over the EC2 private address was validated.

**Secrets are intentionally not recorded in this repository.**

### Network controls

Dedicated migration security groups:

```text
DMS SG       sg-085569e2731850c8a  (madar-dms-sg)
RDS SG       sg-093756a8cabaad407  (madar-rds-sg)
Source SG    sg-0589383abcc3ebbbc  (madar-legacy-migration-sg)
```

Ingress design:

```text
DMS SG -> TCP/5432 -> EC2 source PostgreSQL
DMS SG -> TCP/5432 -> RDS target PostgreSQL
```

PostgreSQL is not opened to `0.0.0.0/0` for migration.

### RDS target — AVAILABLE

```text
Identifier  madar-postgres-target
Engine      PostgreSQL 16.14
Class       db.t3.micro
Storage     20 GiB gp3
Public      false
Multi-AZ    false (lab/cost decision)
Endpoint    madar-postgres-target.cgx64cygc3mj.us-east-1.rds.amazonaws.com
SG          sg-093756a8cabaad407
```

The RDS subnet group spans `us-east-1a` and `us-east-1b`.

### DMS IAM prerequisite — RESOLVED

The first DMS replication-subnet-group request failed because `dms-vpc-role` was not configured. This was treated as an IAM/service prerequisite rather than a networking failure.

Created/configured:

```text
Role          dms-vpc-role
Trusted       dms.amazonaws.com
Policy        AmazonDMSVPCManagementRole
```

After the role and AWS-managed policy were attached, the same subnet-group operation succeeded.

### DMS subnet group — COMPLETE

```text
Identifier  madar-dms-subnets
VPC         vpc-015017581b8954e61
AZs         us-east-1a, us-east-1b
Status      Complete
Network     IPv4
```

### DMS replication instance — PROVISIONING

```text
Identifier  madar-dms-repl
Class       dms.t3.small
Engine      3.6.1
Storage     20 GiB
Public      false
Multi-AZ    false
SG          sg-085569e2731850c8a
Status      creating (last observed state)
```

Do not claim the DMS replication instance is available until the AWS API reports `available`.

## Evidence checkpoint

Latest completed screenshot checkpoint:

```text
18-rds-postgresql-target-available.png
```

Next capture only after the DMS replication instance reports `available`:

```text
19-dms-replication-instance-available.png
```

Planned evidence sequence after that:

```text
20  source endpoint connection success
21  target endpoint connection success
22  DMS full load completed
23  CDC replication proof
24  final data reconciliation
```

## Next gate

```text
1. Wait for madar-dms-repl -> available
2. Capture evidence 19
3. Create DMS source endpoint for EC2 PostgreSQL
4. Create DMS target endpoint for RDS PostgreSQL
5. Test both endpoint connections
6. Create Full Load + CDC replication task
7. Run initial load
8. Reconcile customers / shipments / shipment_events
9. Generate a controlled source-side change
10. Prove CDC applies it to RDS
11. Record cutover/rollback evidence
12. Continue operational-file replatform track to S3
13. Perform security/cost review and cleanup temporary migration resources
```

## Current stop rule

Do not cut the application over to RDS merely because RDS is `available`. Database migration is accepted only after DMS endpoint tests succeed, initial data reconciles, CDC is demonstrated, and rollback remains possible.