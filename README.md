# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

This repository is an evidence-driven AWS migration case study: a representative MADAR logistics workload is moved from VMware to EC2, validated, then its PostgreSQL database is replatformed to Amazon RDS using AWS DMS Full Load + CDC.

> MADAR is fictional. The workload, commands, failures, AWS behavior, troubleshooting and validation are technically authentic lab work.

## Executive outcome

```text
Stage 1 — VMware -> EC2 Rehost                 PASS
Stage 2 — EC2 PostgreSQL -> RDS via DMS       PASS
Stage 3 — Operational files -> S3             NEXT
Cutover / closeout                            NEXT
```

The project deliberately preserves failures that changed engineering decisions rather than rewriting the story as a perfect demo.

## End-to-end architecture

```text
LEGACY
VMware MADAR-LEGACY-01
Ubuntu 24.04.4 + Flask + PostgreSQL 16.14
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
Ubuntu + Flask + PostgreSQL
        |
        | AWS DMS Full Load + CDC
        v
private Amazon RDS PostgreSQL 16.14
madar-postgres-target / db.t3.micro
```

## Stage 1 — VMware to EC2: validated

The original rehost attempt used AWS Transform / Application Migration Service (MGN). Initial block replication completed at `25 / 25 GiB`, but the MGN test-launch conversion stage attempted to launch a service-managed `m5.large`; the account plan rejected that instance type. CloudTrail identified the exact `RunInstances` failure, and the project pivoted to EC2 VM Import/Export instead of repeatedly retrying the wrong layer.

The VMware guest was prepared for the hypervisor move:

- BIOS/GRUB and GPT/LVM/ext4 topology verified,
- ENA and NVMe driver readiness verified,
- VMware-specific `ens33` dependence removed,
- `eth0` + DHCP validated after reboot,
- SSH and PostgreSQL enabled at boot,
- independent PostgreSQL custom-format recovery dump created and inspected,
- first OVF export rejected after detecting an attached installer ISO,
- clean second export verified as `streamOptimized` VMDK.

VM Import/Export result:

```text
ImportTaskId   import-ami-48f44651b4c75774t
Status         completed
AMI            ami-0cbd2e9ec0d6f9168
Snapshot       snap-0920a020c47fb6447
Architecture   x86_64
Virtualization HVM
ENA            enabled
```

The AMI was launched as `MADAR-LEGACY-EC2` and accepted only after workload validation:

```text
Ubuntu boot                  PASS
EC2 status checks            PASS
eth0 / VPC DHCP              PASS
NVMe + LVM/ext4              PASS
SSH administration           PASS
PostgreSQL 16.14             active / enabled
Failed systemd units         0
Initial DB counts            10 / 50 / 150
Flask /api/health            status=ok, database=connected
Flask /api/summary           expected business counts
```

## Stage 2 — PostgreSQL to RDS with AWS DMS: validated

### CDC source readiness

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
```

PostgreSQL was made reachable over the private VPC path while AWS Security Groups kept TCP/5432 restricted. A dedicated DMS database login was used for migration connectivity.

### Security model

```text
Source EC2 SG  sg-0589383abcc3ebbbc
DMS SG         sg-085569e2731850c8a
RDS SG         sg-093756a8cabaad407

DMS SG -> TCP/5432 -> EC2 source
DMS SG -> TCP/5432 -> RDS target
EC2 SG -> TCP/5432 -> RDS for validation/cutover testing
```

No Internet-wide PostgreSQL ingress was used.

### RDS target

```text
Identifier  madar-postgres-target
Engine      PostgreSQL 16.14
Class       db.t3.micro
Storage     20 GiB gp3
Public      false
Status      available
```

### DMS infrastructure

The first DMS replication-subnet-group request failed because `dms-vpc-role` was not configured correctly. The fix was applied at the IAM layer:

```text
DMS service
   -> sts:AssumeRole
   -> dms-vpc-role
   -> AmazonDMSVPCManagementRole
```

After the prerequisite was repaired:

```text
DMS subnet group   Complete / us-east-1a + us-east-1b
Replication node   madar-dms-repl
Class              dms.t3.small
Engine             3.6.1
Private IP         172.31.13.46
Status             available
```

### Endpoint troubleshooting

Source endpoint test:

```text
madar-postgres-source | successful
```

Target endpoint initially failed with:

```text
no pg_hba.conf entry ... no encryption
```

That error proved network reachability because PostgreSQL itself returned the rejection. The DMS target endpoint was changed to `ssl-mode=require`.

The next failure became:

```text
password authentication failed for user "postgres"
```

This narrowed the remaining issue to credentials. After synchronizing the RDS and DMS target credentials, the final result was:

```text
madar-postgres-target | successful
```

The troubleshooting progression is intentional evidence of diagnosing IAM, network/TLS and authentication as separate layers.

## Full Load + CDC result

DMS task:

```text
Identifier        madar-full-load-cdc
Migration type    full-load-and-cdc
FullLoadProgress  100%
TablesLoaded      3
TablesLoading     0
TablesErrored     0
```

Per-table initial load:

```text
public.customers         10 rows   Table completed
public.shipments         50 rows   Table completed
public.shipment_events   150 rows  Table completed
```

An independent SQL query against RDS confirmed the same initial baseline.

## CDC proof

After Full Load, a unique record was inserted into the **source EC2 PostgreSQL**:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

Without restarting or rerunning Full Load, the record appeared automatically on RDS through PostgreSQL logical WAL and AWS DMS CDC.

Final RDS reconciliation:

```text
customers         11
shipments         50
shipment_events   150
```

This is the critical proof that the database migration handled both initial state and subsequent changes.

## Important command guides

Do not memorize every command; understand why each layer exists. The repository keeps reproducible commands with explanations in:

- `docs/07-vm-import-execution-guide.md` — VMware guest preparation, S3 staging, IAM `vmimport`, `PassRole`, `ImportImage`, AMI/EC2 validation.
- `docs/09-dms-rds-execution-guide.md` — PostgreSQL logical replication, SG design, RDS, `dms-vpc-role`, DMS endpoints, TLS troubleshooting, Full Load, CDC and reconciliation.
- `runbooks/migration-day-runbook.md` — ordered execution, acceptance, rollback and cleanup flow.

## Evidence sequence

The completed database-migration evidence sequence is:

```text
18-rds-postgresql-target-available.png
19-dms-replication-instance-available.png
20-source-endpoint-connection-success.png
21-target-endpoint-connection-success.png
22-dms-full-load-completed.png
23-cdc-replication-proof.png
24-final-data-reconciliation.png
```

See `evidence/README.md` for captions, security review rules and the intended evidence folder structure.

## What this demonstrates to a reviewer

This phase demonstrates more than service familiarity:

- source discovery and recoverability before migration,
- VMware/Linux administration,
- hypervisor-to-EC2 compatibility reasoning,
- AWS MGN experimentation and CloudTrail root-cause analysis,
- IAM service roles and `PassRole`,
- S3 staging and EC2 VM Import/Export,
- EC2 workload and database reconciliation,
- PostgreSQL WAL/logical replication concepts,
- private Amazon RDS design,
- AWS DMS networking and IAM prerequisites,
- SG-to-SG database access,
- TLS/authentication troubleshooting,
- Full Load + CDC execution,
- controlled change validation,
- rollback and cleanup discipline.

The engineering story is not "I clicked migrate." It is: **I identified the source state, protected recovery, isolated real managed-service blockers, changed the migration mechanism deliberately, proved the rehost, replatformed the database, and validated data continuity with a controlled CDC change.**

## Security and cost discipline

- no VM image, database dump, secret, `.env`, `.pgpass` or private key is committed,
- the VM-import S3 staging area is private,
- RDS is private,
- PostgreSQL 5432 is not exposed to the Internet,
- target DMS connection requires TLS,
- single-AZ/small classes are explicitly lab/cost choices rather than production HA recommendations,
- temporary migration resources are inventoried for cleanup after final evidence/cutover decisions.

## Repository map

- `CURRENT-STATE.md` — exact live state and next gate.
- `docs/01-business-case.md` — business motivation.
- `docs/02-source-estate.md` — source inventory.
- `docs/03-discovery-assessment.md` — dependencies and assessment.
- `docs/04-migration-strategy.md` — staged strategy.
- `docs/05-target-architecture.md` — target boundaries/security.
- `docs/06-validation-plan.md` — acceptance gates and outcomes.
- `docs/07-vm-import-execution-guide.md` — VMware -> EC2 command guide.
- `docs/08-interview-guide.md` — recruiter/interview narrative.
- `docs/09-dms-rds-execution-guide.md` — EC2 PostgreSQL -> RDS DMS command guide.
- `runbooks/migration-day-runbook.md` — ordered execution/rollback/cleanup procedure.
- `checklists/phase03-master-checklist.md` — progress and closeout checklist.
- `evidence/README.md` — screenshot/evidence catalog.
- `decisions/` — architecture decision records.
- `legacy-lab/` — representative source application/workload.
- `terraform/` — IaC position and future infrastructure scope.