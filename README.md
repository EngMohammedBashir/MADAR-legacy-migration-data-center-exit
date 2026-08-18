# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has an aging shipment-management estate that must be understood, protected and migrated before data-center exit. This phase treats migration as an **engineering engagement**, not an EC2 deployment exercise.

> The VMware environment is a representative lab of MADAR's pre-existing legacy estate. It exists so migration decisions, failure modes and validation can be measured safely.

## Current status

**Discovery, dependency assessment, component-level migration strategy and lab target architecture are complete. Pre-migration readiness is in progress. The paid AWS migration-resource window has not started.**

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── 2 vCPU / ~2.4 GiB RAM
├── PostgreSQL 16.14
├── Flask 3.1.3 / HTTP 8080
├── 10 customers / 50 shipments / 150 events
├── Operational CSV exports + SHA-256 manifest
├── Scheduled operations report via cron
└── Verified pre-migration DB + file/config backups
```

## Migration decision

Discovery proved that the legacy VM contains multiple logical components with different state and operational characteristics. The approved lab strategy is therefore component-level:

```text
Representative source                         AWS target

Ubuntu + Flask -------- AWS MGN ------------> EC2
PostgreSQL 16 --------- AWS DMS Full+CDC ---> RDS PostgreSQL
Operational files ----- validated transfer --> S3
Scheduled job ---------- reconfigure --------> target DB/storage path
Target protection ------ AWS Backup ---------> where useful after cutover
```

MGN and DMS intentionally coexist: MGN rehosts the machine/runtime while DMS replatforms and synchronizes the database into managed RDS.

## Approved lab target

- Region: `us-east-1`.
- VPC: `10.30.0.0/16`.
- Public application subnet: `10.30.1.0/24`.
- Private DB subnets: `10.30.11.0/24` and `10.30.12.0/24`.
- EC2 target candidate: `t3.small`.
- RDS PostgreSQL: small burstable Single-AZ target; final class confirmed at execution.
- DMS: minimum suitable capacity using Full Load + CDC.
- S3 for operational files and integrity validation.
- No NAT Gateway, ALB or Multi-AZ RDS for the short-lived migration proof.

The temporary public EC2 placement is a lab simplification. A production-oriented target would normally place application compute behind controlled ingress rather than expose the instance directly.

## What has been proven

- PostgreSQL-backed application read path works.
- Transactional application write path works: shipment update + event insert commit together.
- The controlled write proof was removed by deterministic reseeding; the migration baseline returned to `10 / 50 / 150`.
- Operational source files are generated from workload data and protected by SHA-256 baseline verification.
- A scheduled Linux job queries PostgreSQL and generates timestamped operations reports without an interactive session.
- Source timezone is explicitly `Asia/Riyadh` and NTP is active.
- PostgreSQL custom-format backup is readable with `pg_restore --list`.
- Operational-file archive is inspectable and checksum-verifiable.
- Discovery verified runtime, storage, processes, listeners, services, network and workload dependencies.
- Source outbound HTTPS reachability to AWS `us-east-1` has been verified for MGN readiness.
- PostgreSQL CDC baseline has been inspected: `wal_level=replica`, `max_replication_slots=10`, `max_wal_senders=10`.
- PostgreSQL configuration was backed up before DMS/CDC remediation.

## DMS readiness approach

The known `wal_level=replica` condition is intentionally left unchanged before AWS execution. The project will first run **AWS DMS Premigration Assessment**, capture the AWS-native readiness finding, remediate only the required source settings, then reassess before starting **Full Load + CDC**.

The key migration proof will be a controlled source shipment update that is observed on the target RDS database through CDC, including its matching shipment event.

## Source workload model

```text
Windows operations host
        |
        | HTTP / SSH
        v
MADAR-LEGACY-01 (VMware)
        |
   +----+-----------+----------------+
   |                |                |
Flask API       PostgreSQL      Operational files
   |                ^                ^
   | PATCH/GET      |                |
   +----------------+        scheduled report
                                  ^
                                  |
                                cron
```

The compact lab deliberately co-locates logical roles on one VM because of local hardware constraints. Migration decisions are made per logical component rather than pretending the lab topology is a production topology.

## Security discipline

- normal DB workload identity is `madar_app`, not a PostgreSQL superuser,
- secrets are not committed,
- unattended `psql` uses a protected user `.pgpass` rather than a password embedded in cron,
- `.venv`, `.env`, keys, credentials and backup artifacts remain outside Git,
- PostgreSQL will not be opened to `0.0.0.0/0` merely to make DMS connectivity work,
- RDS remains private and accepts only required application/DMS paths,
- target administration prefers Systems Manager Session Manager where practical,
- binary evidence is reviewed before public upload.

## Cost discipline

The paid AWS migration window has not started. The execution plan creates paid resources only when required, targets a short migration sprint, and removes temporary resources immediately after evidence and acceptance.

The lab intentionally excludes NAT Gateway, ALB and Multi-AZ RDS because they do not contribute to the migration hypothesis being tested. AWS credits are treated as real money and the final cost/credit delta will be recorded.

## AWS-native automation preference

Before introducing long manual command sequences, the project evaluates AWS-native assessments, agents and managed workflows. They are preferred when they materially reduce toil and are affordable. Examples include DMS Premigration Assessment, MGN replication workflow and post-cutover AWS Backup. Manual source commands are retained only where an AWS service cannot safely perform the required source-side change.

## Engineering lifecycle

`Discovery → Inventory → Dependency Mapping → Assessment → Migration Strategy → Target Design → Readiness → Migration → Validation → Cutover → Rollback Validation → Optimization → Cleanup`

### Current gate

We are at **Readiness**. Discovery and target selection are complete. The remaining pre-execution gate is secure DMS-to-source connectivity plus execution-time quota/cost checks. No paid migration resources should be created until the migration session explicitly starts.

## Repository map

- `CURRENT-STATE.md` — exact current project state and next actions.
- `legacy-lab/app/` — source application, schema, deterministic seed and UI.
- `legacy-lab/scripts/` — source scheduled-job implementation.
- `runbooks/source-lab-operations.md` — source operator reference.
- `runbooks/migration-day-runbook.md` — ordered AWS execution, cutover, rollback and cleanup guide.
- `checklists/phase03-master-checklist.md` — implementation/evidence progress.
- `evidence/README.md` — evidence index and capture policy.
- `docs/03-discovery-assessment.md` — verified source inventory/dependencies.
- `docs/04-migration-strategy.md` — approved component-level migration strategy.
- `docs/05-target-architecture.md` — approved lab target, network, sizing, readiness and cost guardrails.
- `docs/06-validation-plan.md` — reconciliation, CDC proof and acceptance criteria.
- `decisions/` — ADRs.
- `terraform/` — AWS IaC when/where used after readiness approval.

## Success criteria

Success is not "AWS resources exist." The project must prove source understanding, controlled migration, database/file reconciliation, CDC behavior, application read/write behavior, scheduled processing, recoverability, cutover acceptance, rollback logic, security/observability checks, cost discipline and cleanup.

## Integrity rule

MADAR is fictional. Tests, code, failures, outputs, decisions and evidence are technically authentic. Controlled exercises are labeled as such and are never represented as real production incidents.
