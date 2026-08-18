# Target Architecture

**Status: APPROVED FOR LAB EXECUTION — AWS PAID-RESOURCE WINDOW NOT STARTED**

## Design intent

Phase 03 demonstrates a controlled data-center-exit migration rather than rebuilding a production three-tier platform. The target is intentionally right-sized for a short-lived lab and separates the logical workload components discovered on the legacy VM.

## Approved target

```text
Representative VMware source                     AWS target (us-east-1)

Ubuntu + Flask -------- AWS MGN ----------------> EC2 t3.small
      |                                              |
      | localhost DB today                          | RDS endpoint after cutover
      v                                              v
PostgreSQL 16 -------- AWS DMS Full Load + CDC --> RDS PostgreSQL

Operational CSV/reports ---- validated copy ----> Amazon S3

cron/report job ------------- reconfigure ------> target DB / target storage path

Post-cutover protection ------------------------> AWS Backup where justified
```

## Network plan

```text
VPC 10.30.0.0/16
|
+-- Public subnet A      10.30.1.0/24
|   +-- temporary migrated EC2 application target
|
+-- Private DB subnet A  10.30.11.0/24
|
+-- Private DB subnet B  10.30.12.0/24
    +-- RDS DB subnet group
```

An Internet Gateway serves the public lab subnet. NAT Gateway and ALB are deliberately excluded because they do not contribute to the migration hypothesis being tested and would add cost/complexity to a one-instance temporary lab.

The temporary public EC2 exposure is a lab simplification, not the recommended production end state. The production-oriented direction is private compute behind a controlled ingress tier.

## Security boundaries

- EC2 application listener: TCP 8080, restricted to the operator/test source during the lab rather than open Internet access.
- RDS PostgreSQL: TCP 5432, private; access limited to the migrated application security group and the required DMS migration path.
- Target administration should use AWS Systems Manager Session Manager where practical rather than depending on inbound SSH.
- PostgreSQL must never be exposed on `0.0.0.0/0` merely to make DMS work.
- Secrets are not committed to Git.

## Resource sizing

| Resource | Lab selection | Reason |
|---|---|---|
| Region | `us-east-1` | Selected account/console region and low-cost lab target |
| EC2 | `t3.small` candidate | 2 vCPU / 2 GiB, closer to the discovered 2 vCPU / 2.4 GiB source than a 1 GiB micro |
| RDS PostgreSQL | small burstable class, Single-AZ; `db.t3.micro` candidate subject to console availability | Sufficient for the deterministic lab dataset; avoids Multi-AZ cost during migration proof |
| DMS | smallest suitable replication capacity / Serverless option to be selected at execution | Full Load + CDC only for the migration window |
| MGN | one source server | Rehost the Ubuntu/Flask runtime |
| S3 | one migration bucket/prefix structure | Operational files and integrity evidence |
| AWS Backup | post-cutover only where useful | Centralized target protection; not a replacement for the existing source `pg_dump`/config backup |

Final purchasable sizes and prices are checked immediately before creation because service availability and pricing can change.

## Connectivity finding

The source PostgreSQL listener is currently loopback-only (`127.0.0.1:5432`) inside the VMware NAT network (`192.168.14.128/24`). A DMS replication resource in AWS cannot directly address that private VMware address without an explicit connectivity path.

The source VM has verified outbound HTTPS reachability to AWS in `us-east-1`. A request to the MGN regional S3 endpoint reached AWS and returned HTTP 403, which is expected for an unauthenticated bucket request and proves network reachability rather than authorization.

The exact temporary DMS source-connectivity mechanism remains an execution prerequisite. Publicly exposing PostgreSQL is rejected. A secure temporary tunnel or private connectivity design will be selected before DMS endpoint creation; Site-to-Site/Client VPN is not being created during preparation solely for the lab.

## DMS / CDC readiness

Verified source checks:

```text
PostgreSQL version          16.14
wal_level                   replica   <-- expected pre-migration finding
max_replication_slots       10
max_wal_senders             10
config file                 /etc/postgresql/16/main/postgresql.conf
```

`wal_level=replica` is intentionally left unchanged during preparation. During AWS execution, DMS Premigration Assessment should be used first so the readiness gap is recorded by the AWS-native assessment. The source can then be changed to logical replication configuration, reassessed, and only then used for Full Load + CDC.

A safety copy of the PostgreSQL configuration exists at:

```text
/home/madaradmin/madar-backups/postgresql-16-main-before-dms
```

The earlier custom-format database dump remains the independent pre-migration data recovery point.

## Cost guardrail

The account currently uses the AWS Free Plan/credit model. Phase 03 will still treat credits as real money.

Cost controls:

- create paid migration resources only during the execution session,
- target a roughly three-hour migration sprint where practical,
- no NAT Gateway,
- no ALB,
- no Multi-AZ RDS for this lab,
- stop/delete DMS as soon as CDC evidence and cutover are complete,
- finalize/clean MGN resources after acceptance,
- terminate temporary EC2 and delete unneeded EBS/RDS resources,
- inspect Billing/Cost Explorer and residual resources at closeout.

## AWS-native automation preference

Before replacing a task with long manual command sequences, first evaluate an AWS-native assessment, agent or managed workflow. Use it when it meaningfully reduces toil and is affordable for the lab. Manual commands remain appropriate for source changes that AWS cannot safely perform automatically.

Examples in this phase:

- AWS DMS Premigration Assessment for database migration readiness,
- AWS MGN agent/workflow for server rehosting,
- AWS Backup after cutover where target protection adds value,
- manual PostgreSQL configuration only for findings that require a source-side change.
