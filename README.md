# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has an aging shipment-management estate that must be understood, protected and migrated before data-center exit. This phase treats migration as an **engineering engagement**, not an EC2 deployment exercise.

> The VMware environment is a representative lab of MADAR's pre-existing legacy estate. It exists so migration decisions, failure modes and validation can be measured safely.

## Current status

**Discovery and source-readiness are complete. AWS MGN block-level replication succeeded, but test launch was blocked by an AWS Free Plan restriction on the service-managed conversion server. The rehost path has therefore pivoted to EC2 VM Import/Export, with source pre-flight now complete.**

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS / kernel 6.8 / x86_64
├── BIOS + GRUB2
├── 2 vCPU / ~2.4 GiB RAM
├── 25 GiB disk: ext4 + LVM
├── PostgreSQL 16.14
├── Flask 3.1.3 / HTTP 8080
├── 10 customers / 50 shipments / 150 events
├── Operational CSV exports + SHA-256 manifest
└── Verified final PostgreSQL custom-format backup
```

## Migration decision

Discovery proved that the legacy VM contains multiple logical components with different state and operational characteristics. The current lab strategy is:

```text
Representative source                           AWS target

Ubuntu + Flask -------- VM Import/Export ------> EC2
PostgreSQL 16 --------- AWS DMS Full+CDC ------> RDS PostgreSQL
Operational files ----- validated transfer ----> S3
Scheduled job ---------- reconfigure ----------> target DB/storage path
Target protection ------ AWS Backup -----------> where useful after cutover
```

MGN was evaluated first and successfully proved agent-based block replication, but its test/cutover conversion stage requires a service-managed `m5.large` conversion server. The current AWS Free Plan blocks that non-eligible instance type, and the conversion-server type is not customer-configurable. The lab therefore preserves the MGN troubleshooting evidence and uses VM Import/Export for the rehost proof instead of upgrading the account.

## MGN investigation — what was proven

```text
VMware source
   |
   | AWS Replication Agent
   v
AWS Transform MGN
├── 25 / 25 GiB replicated ✅
├── Initial replication finished ✅
├── Replication status Healthy ✅
├── Snapshot creation succeeded ✅
└── Test launch conversion failed ⚠️
       |
       +--> CloudTrail: ec2:RunInstances
            Conversion server: m5.large
            Role: AWSApplicationMigrationConversionServerRole
            Error: instance type not eligible for Free Plan
```

The configured target remained `t3.small`; it was never reached because failure occurred earlier in the managed conversion stage. AWS Transform confirmed there is no supported setting/API/template override for the conversion-server instance type.

The MGN experiment was then cleaned up: the source was removed from MGN, the replication instance was terminated, and residual MGN storage/snapshot resources were removed.

## Revised rehost path

```text
VMware MADAR-LEGACY-01
      |
      | clean export
      v
OVA / supported VM image
      |
      v
Amazon S3
      |
      | EC2 VM Import/Export (ImportImage)
      v
AMI
      |
      v
Free-Plan-eligible x86 EC2 test target
```

This path avoids the MGN-managed conversion-server dependency while preserving a real full-machine rehost workflow.

## VM Import/Export source readiness

Before export, the source VM was checked and prepared specifically for EC2 compatibility:

- Ubuntu `24.04.4 LTS`, kernel `6.8.0-138-generic`, `x86_64`,
- BIOS + GRUB2 boot path,
- ENA driver available in kernel and initramfs,
- NVMe driver available in kernel and initramfs,
- Xen block-front driver built into the kernel,
- VMware predictable NIC name changed from `ens33` to `eth0`,
- GRUB includes `net.ifnames=0`,
- Netplan uses DHCP on `eth0`,
- post-change reboot validated DHCP, default route, Internet and DNS,
- PostgreSQL automatically returned to `active`,
- `madar_legacy` remained present,
- filesystem verification reported no errors,
- no failed systemd services.

A final custom-format PostgreSQL dump was also validated with `pg_restore -l` before export. Binary backups remain outside Git.

## Approved lab target direction

- Region: `us-east-1`.
- EC2 target candidate: Free-Plan-eligible x86 instance, with `t3.small` preferred when allowed by the import result and account plan.
- RDS PostgreSQL: small burstable Single-AZ target; final class confirmed at execution.
- DMS: minimum suitable capacity using Full Load + CDC.
- S3 for the VM import artifact and later operational-file migration.
- No NAT Gateway, ALB or Multi-AZ RDS for the short-lived migration proof.

The final EC2 network placement is confirmed immediately before launch rather than hard-coding an architecture that may conflict with Free Plan constraints.

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
- AWS MGN successfully completed block-level replication and exposed a real account-plan constraint during test conversion.
- CloudTrail root-cause analysis distinguished the service-managed conversion server from the configured target instance.
- Source OS/network/storage drivers required for the VM Import/Export fallback have been pre-validated.

## DMS readiness approach

The known `wal_level=replica` condition remains intentionally unchanged before DMS execution. After the EC2 rehost target is accepted, the project will run **AWS DMS Premigration Assessment**, capture the AWS-native readiness finding, remediate only the required source settings, then reassess before starting **Full Load + CDC**.

The key database-migration proof will be a controlled source shipment update observed on the target RDS database through CDC, including its matching shipment event.

## Security discipline

- normal DB workload identity is `madar_app`, not a PostgreSQL superuser,
- secrets are not committed,
- unattended `psql` uses a protected user `.pgpass`,
- `.venv`, `.env`, keys, credentials, VM images and backup artifacts remain outside Git,
- PostgreSQL is not exposed to `0.0.0.0/0`,
- RDS remains private and accepts only required application/DMS paths,
- target administration prefers Systems Manager Session Manager where practical,
- evidence is reviewed before public upload.

## Cost discipline

The AWS account remains on **Free Plan** and no account upgrade is authorized for this lab. A migration path is not accepted merely because the visible target instance is Free-Plan eligible; service-managed infrastructure is also checked before execution.

Guardrails:

- AWS credits are treated as real money,
- hidden/service-managed compute dependencies are checked before long-running transfers,
- temporary resources are removed immediately after experiments,
- final cost/credit delta is recorded,
- no Paid Plan upgrade is performed solely to make the lab succeed.

## Engineering lifecycle

`Discovery → Inventory → Dependency Mapping → Assessment → Migration Strategy → Target Design → Readiness → Migration → Validation → Cutover → Rollback Validation → Optimization → Cleanup`

### Current gate

We are at **VM Import/Export execution readiness**. Source compatibility and database safety checks are complete. Next: clean VM shutdown, VMware export, local artifact validation, then AWS-side VM Import/Export prerequisite verification before upload/import.

## Repository map

- `CURRENT-STATE.md` — exact current project state and next actions.
- `legacy-lab/app/` — source application, schema, deterministic seed and UI.
- `legacy-lab/scripts/` — source scheduled-job implementation.
- `runbooks/source-lab-operations.md` — source operator reference.
- `runbooks/migration-day-runbook.md` — ordered AWS execution, cutover, rollback and cleanup guide.
- `checklists/phase03-master-checklist.md` — implementation/evidence progress.
- `evidence/README.md` — evidence index and capture policy.
- `docs/03-discovery-assessment.md` — verified source inventory/dependencies.
- `docs/04-migration-strategy.md` — component-level migration strategy.
- `docs/05-target-architecture.md` — lab target, sizing and cost guardrails.
- `docs/06-validation-plan.md` — reconciliation, CDC proof and acceptance criteria.
- `decisions/` — architecture decision records, including the MGN-to-VM-Import pivot.
- `terraform/` — AWS IaC when/where used after readiness approval.

## Success criteria

Success is not "AWS resources exist." The project must prove source understanding, controlled migration, root-cause analysis when a managed path is blocked, database/file reconciliation, application read/write behavior, recoverability, cutover acceptance, rollback logic, security/observability checks, cost discipline and cleanup.

## Integrity rule

MADAR is fictional. Tests, code, failures, outputs, decisions and evidence are technically authentic. Controlled exercises are labeled as such and are never represented as real production incidents.
