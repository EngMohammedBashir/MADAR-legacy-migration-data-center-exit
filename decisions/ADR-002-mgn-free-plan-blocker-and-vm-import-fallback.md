# ADR-002 — Pivot from AWS Transform MGN to EC2 VM Import/Export under Free Plan constraints

- **Status:** Accepted and in execution
- **Date:** 2026-08-19
- **Scope:** Phase 03 rehost track

## Context

The initial design used AWS Transform MGN to rehost `MADAR-LEGACY-01` from VMware to EC2.

MGN replication itself succeeded:

- 25 / 25 GiB replicated,
- initial replication completed,
- replication Healthy,
- lifecycle Ready for testing.

The target launch template was deliberately set to `t3.small` with right-sizing disabled. During test launch, snapshot creation succeeded, then conversion failed before the target instance existed.

CloudTrail isolated the failing request:

```text
Event                    ec2:RunInstances
Invoked by               mgn.amazonaws.com
Profile                  AWSApplicationMigrationConversionServerRole
Purpose                  AWS Application Migration Service Conversion Server
Requested instance type  m5.large
Result                   Client.InvalidParameterCombination
Reason                   instance type not eligible for AWS Free Plan
```

AWS Transform confirmed three distinct compute roles:

```text
Replication server       configurable
Test/cutover target      configurable
Conversion server        service-managed / not customer-configurable
```

Changing the target instance type therefore cannot fix this failure.

## Decision

Do not upgrade the account solely to make this lab pass, do not repeat successful block replication, and do not continue MGN test/cutover under the current Free Plan.

Use **EC2 VM Import/Export** for Stage 1 rehost:

```text
VMware VM
   |
   | clean export
   v
stream-optimized VMDK
   |
   | upload
   v
private S3 bucket
   |
   | VM Import/Export / ImportImage
   | role = vmimport
   v
AMI
   |
   v
account-eligible x86 EC2 target
```

Database/file modernization remains separate:

- PostgreSQL -> DMS Full Load + CDC -> RDS PostgreSQL,
- operational files -> validated copy -> S3.

## Implementation controls completed

### Guest compatibility

- Ubuntu 24.04.4 / kernel 6.8 / x86_64,
- BIOS + GRUB2,
- GPT + LVM/ext4,
- ENA and NVMe in kernel/initramfs,
- Xen block support,
- `ens33` -> `eth0`,
- GRUB `net.ifnames=0`,
- Netplan DHCP on `eth0`,
- reboot/route/Internet/DNS validation,
- SSH enabled at boot,
- PostgreSQL enabled/active,
- final PostgreSQL dump validated.

### VMware artifact hygiene

The first export contained the attached Ubuntu ISO. It was rejected as the migration artifact. The virtual CD/DVD device was removed and a second clean export produced OVF/MF/VMDK only.

The OVF declares the VMDK as `streamOptimized`.

### AWS permission boundary

Created private import bucket:

```text
madar-vm-import-197821101770
```

Created service role:

```text
vmimport
Trust: vmie.amazonaws.com
ExternalId: vmimport
```

Attached narrowly scoped S3 read and EC2 image/snapshot permissions. IAM simulation confirmed the operator may `iam:PassRole` the role:

```text
Decision: allowed
```

The local VMDK upload to S3 has started; completion is intentionally not claimed until the copy finishes and the object is verified.

## Consequences

### Positive

- avoids a hard managed-compute blocker outside customer control,
- preserves the Free Plan/account-risk constraint,
- still demonstrates migration of the existing VMware machine image,
- produces a strong real-world troubleshooting and architecture-decision story,
- makes IAM service-role/PassRole boundaries explicit,
- preserves the original VMware VM as rollback anchor.

### Negative

- requires a powered-off/export window,
- requires a multi-GB upload before conversion,
- lacks MGN continuous replication/cutover orchestration,
- requires explicit guest compatibility preparation and post-import validation,
- import is asynchronous and may expose image-format/boot issues that must be diagnosed separately.

## Alternatives rejected

### Upgrade to Paid Plan

Rejected as a lab-governance decision. It may remove the MGN Free Plan enforcement boundary, but the project does not alter billing risk merely to make a portfolio path look successful.

### Retry MGN with a different target instance

Rejected. The service-managed conversion server, not the target, failed.

### Fresh Ubuntu EC2 rebuild

Rejected as the primary rehost proof because it would demonstrate rebuild/redeploy rather than migration of the existing VM image.

### Direct DMS from VMware

Rejected for this lab because PostgreSQL is loopback-only behind VMware NAT; the EC2 landing point makes the later DMS source much cleaner.

## Evidence

Authoritative evidence includes:

- MGN healthy/ready replication state,
- MGN launch history showing snapshot success then conversion failure,
- CloudTrail `RunInstances` showing `m5.large`,
- AWS Transform explanation of the non-configurable conversion server,
- MGN cleanup state,
- driver/boot/network preflight results,
- clean VMware export file list and OVF `streamOptimized` declaration,
- S3 bucket/IAM role configuration,
- `iam:PassRole` simulation = `allowed`,
- subsequent ImportImage/AMI/EC2 evidence when execution completes.

## Review trigger

Revisit this ADR only if the account plan intentionally changes, AWS exposes a supported MGN conversion-server control, or VM Import/Export proves technically invalid for this source image.