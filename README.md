# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has a representative legacy shipment-management workload hosted on VMware. This phase demonstrates how a cloud engineer discovers, protects, migrates, validates, troubleshoots and modernizes that workload without pretending that migration is merely "launch an EC2 instance".

> MADAR is fictional. The workload, commands, failures, AWS behavior, troubleshooting and evidence are technically authentic lab work.

## Executive summary

The source is a VMware VM running Ubuntu 24.04, Flask and PostgreSQL. The original server-rehost plan used AWS Transform MGN. Block-level replication completed successfully, but the MGN test launch failed because the service-managed conversion stage attempted to launch an `m5.large`, which the account's AWS Free Plan rejects. CloudTrail isolated the exact `RunInstances` failure and AWS Transform confirmed that the conversion-server type is not customer-configurable.

Rather than upgrading the account simply to force the lab through, the project changed the rehost mechanism to **EC2 VM Import/Export** while preserving the same engineering objective: migrate the existing VMware machine image into AWS.

Current state:

```text
VMware MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS / kernel 6.8.0-138 / x86_64
├── BIOS + GRUB2
├── 2 vCPU / ~2.4 GiB RAM
├── 25 GiB GPT disk: /boot ext4 + LVM/ext4 root
├── Flask 3.1.3 / TCP 8080
├── PostgreSQL 16.14 / madar_legacy
├── deterministic baseline: 10 customers / 50 shipments / 150 events
└── verified PostgreSQL + file/config recovery artifacts

Rehost execution
├── MGN block replication: SUCCESS
├── MGN test conversion: BLOCKED by managed m5.large / Free Plan
├── MGN resources: CLEANED
├── EC2 compatibility preparation: COMPLETE
├── clean VMware OVF/VMDK export: COMPLETE
├── VMDK format: streamOptimized
├── S3 staging bucket: CREATED / private
├── IAM service role `vmimport`: CREATED
├── iam:PassRole simulation: ALLOWED
└── VMDK upload to S3: IN PROGRESS
```

## Architecture and migration strategy

```text
STAGE 1 — REHOST

VMware MADAR-LEGACY-01
        |
        | clean VMware export
        v
stream-optimized VMDK
        |
        | aws s3 cp
        v
private Amazon S3 staging bucket
        |
        | EC2 VM Import/Export / ImportImage
        | assumes IAM role: vmimport
        v
AMI
        |
        | launch accepted x86 target
        v
EC2: Ubuntu + Flask + PostgreSQL + files

STAGE 2 — DATABASE REPLATFORM

EC2 PostgreSQL
        |
        | AWS DMS Full Load + CDC
        v
Amazon RDS for PostgreSQL

STAGE 3 — FILE REPLATFORM

Operational CSV/reports
        |
        | validated transfer + SHA-256 verification
        v
Amazon S3
```

The strategy deliberately separates **machine rehosting** from **database replatforming**. VM Import/Export moves the server image; DMS later moves PostgreSQL into managed RDS. One service is not misrepresented as solving both problems.

## Why the MGN failure matters

The strongest engineering lesson in this phase came from a path that did not complete.

MGN reached `25 / 25 GiB`, `Initial replication finished`, `Healthy`, and `Ready for testing`. The configured target launch template used `t3.small`, but test launch still failed. CloudTrail showed why:

```text
Caller / service        mgn.amazonaws.com
API                     ec2:RunInstances
Purpose                 AWS Application Migration Service Conversion Server
IAM profile             AWSApplicationMigrationConversionServerRole
Requested type          m5.large
Result                  Client.InvalidParameterCombination
Reason                  instance type is not eligible for AWS Free Plan
```

This distinguished three different compute roles:

```text
MGN replication server     configurable
MGN target EC2             configurable
MGN conversion server      service-managed; not customer-configurable
```

The target `t3.small` was therefore never the failing resource. The experiment was stopped, documented and cleaned rather than repeatedly retried.

See `decisions/ADR-002-mgn-free-plan-blocker-and-vm-import-fallback.md`.

## EC2 compatibility work performed before export

Moving a disk image between hypervisors is similar to moving an engine into a different vehicle: the application can be healthy while boot, storage or network assumptions still prevent startup on the new platform.

The source was therefore validated and prepared before export:

- verified Ubuntu `24.04.4`, `x86_64`, BIOS and GRUB2,
- verified GPT layout and LVM/ext4 root filesystem,
- reinstalled/rechecked GRUB on `/dev/sda`,
- verified ENA driver in the kernel and initramfs,
- verified NVMe driver in the kernel and initramfs,
- verified Xen block-front support,
- changed predictable VMware NIC naming from `ens33` to `eth0`,
- set GRUB `net.ifnames=0`,
- configured Netplan DHCP on `eth0`,
- rebooted and revalidated IP, route, Internet and DNS,
- enabled SSH at boot and verified it active,
- verified PostgreSQL enabled/active after reboot,
- verified `madar_legacy` remained available,
- verified no failed systemd services,
- verified filesystem/fstab state,
- created a final PostgreSQL custom-format dump and validated its table-of-contents with `pg_restore -l`.

The final VMware export was repeated after removing the attached installation ISO. The clean artifact contains only the OVF manifest and VM disk; the VMDK advertises `streamOptimized` format.

## AWS-side import preparation

The import staging layer is intentionally narrow and private:

```text
S3 bucket
madar-vm-import-197821101770
├── public access blocked
└── destination for MADAR-LEGACY-01-disk1.vmdk

IAM role
vmimport
├── trusted service: vmie.amazonaws.com
├── external ID: vmimport
├── S3 read permissions for the import bucket
└── EC2 snapshot/image permissions required by VM Import/Export

Operator
mohammed-admin
└── iam:PassRole on vmimport verified by IAM policy simulation
```

The Windows workstation performs the upload because the VMDK exists on the local `C:` drive. AWS CloudShell is used for AWS-side provisioning and inspection because it cannot directly see local Windows paths.

## Important commands — and what they mean

These are implementation examples, not commands to memorize blindly.

```bash
# Identity: prove which AWS principal is executing commands
aws sts get-caller-identity

# S3 staging: create the private landing area for the VM disk
aws s3api create-bucket --bucket <bucket> --region us-east-1

# IAM: create the service role that VM Import/Export can assume
aws iam create-role --role-name vmimport --assume-role-policy-document file://trust-policy.json

# Authorization check: can the operator pass vmimport to the AWS service?
aws iam simulate-principal-policy ... --action-names iam:PassRole ...
```

From Windows PowerShell:

```powershell
# Upload the exported VMware disk from the local workstation to S3
aws s3 cp "C:\...\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

The next execution command after upload verification is `aws ec2 import-image`, which starts the asynchronous VM Import/Export conversion task. The expected output of that process is an AMI; EC2 is launched only after import completion and validation.

Full command-by-command explanation is maintained in `docs/07-vm-import-execution-guide.md`.

## Validation philosophy

A migration is not successful because an AWS resource says `Available`.

The target must prove:

```text
Boot
  -> network / DHCP
  -> SSH / administration
  -> filesystem
  -> PostgreSQL service
  -> madar_legacy database
  -> schema + representative data
  -> Flask health/read/write path
  -> operational files
  -> scheduled processing
  -> security review
  -> rollback viability
```

The database baseline and independent dump make it possible to distinguish "the VM booted" from "the business state migrated correctly."

## Security and cost discipline

- no VM image, database dump, secret, `.env`, `.pgpass` or key is committed to Git,
- S3 VM-import staging is private,
- VM Import/Export uses an IAM service role instead of static service credentials,
- PostgreSQL is not opened to the Internet merely to simplify migration,
- AWS credits are treated as real money,
- the account is not upgraded simply to hide an architectural/service constraint,
- temporary migration resources are removed after their evidence purpose is complete,
- service-managed dependencies are investigated as carefully as resources visible in the launch template.

## What this project demonstrates to a reviewer

This repository is intended to show evidence of practical cloud-engineering behavior:

- source discovery before target design,
- VMware/Linux administration,
- PostgreSQL recoverability and data validation,
- AWS MGN replication and troubleshooting,
- CloudTrail root-cause analysis,
- IAM trust policies, service roles and `PassRole`,
- S3 staging and AWS CLI operation,
- EC2 VM Import/Export concepts,
- architecture decisions under account/cost constraints,
- migration validation, rollback thinking and cleanup discipline.

It intentionally documents the failed MGN test conversion because production engineering is not a sequence of perfect screenshots; it is the ability to identify the failing layer, prove the root cause and change the plan without losing control of risk.

## Repository map

- `CURRENT-STATE.md` — exact execution state and next gate.
- `docs/01-business-case.md` — business reason for the migration.
- `docs/02-source-estate.md` — logical estate and representative lab topology.
- `docs/03-discovery-assessment.md` — verified source dependencies and assessment.
- `docs/04-migration-strategy.md` — staged rehost/replatform strategy.
- `docs/05-target-architecture.md` — target boundaries, security and sizing.
- `docs/06-validation-plan.md` — acceptance and reconciliation criteria.
- `docs/07-vm-import-execution-guide.md` — detailed commands, purpose and expected results.
- `docs/08-interview-guide.md` — recruiter/interview explanation and likely questions.
- `runbooks/migration-day-runbook.md` — ordered execution/rollback/cleanup procedure.
- `runbooks/source-lab-operations.md` — source operational commands.
- `checklists/phase03-master-checklist.md` — implementation and evidence progress.
- `evidence/README.md` — evidence catalog and capture rules.
- `decisions/` — ADRs, including the MGN-to-VM-Import pivot.
- `legacy-lab/` — representative source application and scheduled workload.
- `terraform/` — IaC position and future target infrastructure scope.

## Success criteria

Phase 03 is complete only when the imported EC2 workload is accepted, PostgreSQL is reconciled/replatformed as planned, operational files are validated, the application read/write path works, rollback is understood, cost/security exposure is reviewed and temporary migration resources are cleaned.

## Integrity rule

Tests, outputs, failures, decisions and evidence are reported as they occurred. Planned steps are labeled as planned; incomplete steps are not presented as successful.