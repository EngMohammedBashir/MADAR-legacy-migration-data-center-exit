# ADR-002 — Pivot from AWS Transform MGN to EC2 VM Import/Export under Free Plan constraints

- **Status:** Accepted
- **Date:** 2026-08-19
- **Scope:** Phase 03 rehost track

## Context

The initial rehost design used AWS Transform MGN to migrate the representative VMware server `MADAR-LEGACY-01` to EC2.

MGN agent installation and block-level replication succeeded. The source reached:

- `25 / 25 GiB` replicated,
- initial replication finished,
- healthy replication state,
- ready-for-testing lifecycle state.

The target EC2 launch template was deliberately cost-optimized to `t3.small`, with right-sizing disabled so the selected instance type would be respected.

During **Launch test instance**, snapshot creation succeeded but conversion failed before the target EC2 instance was launched.

CloudTrail isolated the failing API request:

```text
Event                    ec2:RunInstances
Invoked by               mgn.amazonaws.com
IAM instance profile     AWSApplicationMigrationConversionServerRole
Resource tag             AWS Application Migration Service Conversion Server
Requested instance type  m5.large
Error                    Client.InvalidParameterCombination
Reason                   instance type not eligible for Free Tier
```

AWS Transform subsequently confirmed that MGN has three distinct compute roles:

1. replication server — configurable,
2. test/cutover target — configurable,
3. conversion server — service-managed and not customer-configurable.

The `m5.large` conversion server cannot be overridden through a target launch template, launch configuration, public MGN API parameter, quota, or AWS Transform workflow.

The account is intentionally kept on the AWS **Free Plan**. Upgrading to Paid Plan solely to make a lab migration succeed violates the project's cost/risk guardrail.

## Decision

Do **not** retry MGN test launch/cutover and do **not** upgrade the AWS account.

Preserve the MGN execution as valid troubleshooting evidence, clean up its temporary resources, and pivot the rehost proof to **EC2 VM Import/Export**:

```text
VMware VM
   |
   | export OVA / supported image
   v
Amazon S3
   |
   | EC2 ImportImage
   v
AMI
   |
   | launch Free-Plan-eligible x86 target
   v
EC2 test target
```

The database and file replatform tracks remain separate:

- PostgreSQL -> AWS DMS Full Load + CDC -> RDS PostgreSQL,
- operational files -> validated transfer -> Amazon S3.

## Source remediation required for VM Import/Export

Before export, the VMware guest was prepared and validated for AWS compatibility:

- Ubuntu `24.04.4 LTS`, kernel `6.8.0-138-generic`, `x86_64`,
- BIOS + GRUB2,
- ENA driver verified in kernel and initramfs,
- NVMe driver verified in kernel and initramfs,
- Xen block-front driver built into the kernel,
- NIC naming changed from VMware-style `ens33` to `eth0`,
- GRUB updated with `net.ifnames=0`,
- Netplan updated to DHCP on `eth0`,
- reboot validation confirmed networking, Internet, DNS and PostgreSQL health,
- final PostgreSQL custom-format dump created and validated with `pg_restore -l`.

## Consequences

### Positive

- avoids a hard Free Plan blocker outside customer control,
- preserves account-plan safety and avoids exposing a payment method to unexpected non-free resources,
- keeps the migration proof technically authentic,
- turns the MGN failure into a documented root-cause and cost-governance case,
- continues toward a full-machine rehost rather than replacing the VM with a fresh installation.

### Negative

- VM Import/Export requires a powered-off export window,
- the VM image must be uploaded to S3 before import,
- additional local source preparation is required,
- the final EC2 target will not benefit from MGN continuous replication/cutover orchestration.

## Alternatives considered

### Upgrade AWS account to Paid Plan

Rejected. It would allow the managed `m5.large` conversion server to run, but the project explicitly avoids upgrading the account solely to bypass a lab constraint.

### Change MGN target instance type

Rejected as ineffective. The failure happens on the service-managed conversion server before the configured target instance is launched.

### Retry MGN replication

Rejected. Replication had already succeeded and was not the root cause.

### Rebuild a fresh Ubuntu EC2 instance manually

Rejected as the primary rehost proof because it would no longer demonstrate migration of the existing VMware machine image.

## Evidence

The authoritative evidence for this decision is retained outside sensitive/raw credential material and includes:

- MGN replication healthy/ready-for-testing state,
- MGN launch job showing snapshot success and conversion failure,
- CloudTrail `RunInstances` event showing `m5.large`,
- AWS Transform confirmation that the conversion-server instance type is not configurable,
- cleanup proof for the MGN replication instance and storage resources.

## Review trigger

Revisit this ADR only if one of the following changes:

- AWS exposes a supported conversion-server instance-type control,
- the account plan intentionally changes,
- VM Import/Export introduces a new blocker that invalidates the fallback path.
