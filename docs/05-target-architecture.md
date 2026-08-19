# Target Architecture

**Status: REHOST STAGING ACTIVE — AMI NOT YET CREATED**

## Design intent

Phase 03 demonstrates controlled data-center exit with a short-lived intermediate EC2 landing point followed by database/file replatforming. The lab is intentionally smaller than a production architecture, but security boundaries, rollback and evidence requirements remain explicit.

## Target flow

```text
VMware MADAR-LEGACY-01
        |
        | stream-optimized VMDK
        v
Private S3 import bucket
        |
        | EC2 VM Import/Export / ImportImage
        | IAM service role: vmimport
        v
AMI
        |
        v
Temporary EC2 landing instance
├── Ubuntu + Flask
├── PostgreSQL (temporary intermediate source)
└── operational files
        |
        +---- DMS Full Load + CDC ----> private RDS PostgreSQL
        |
        +---- validated copy ---------> Amazon S3
```

## Current import staging resources

```text
Region       us-east-1
S3 bucket    madar-vm-import-197821101770
Access       Block Public Access enabled
IAM role     vmimport
Trust        vmie.amazonaws.com / ExternalId vmimport
Operator     mohammed-admin
PassRole     policy simulation = allowed
Artifact     MADAR-LEGACY-01-disk1.vmdk (~3.4 GiB compressed export)
Capacity     25 GiB virtual disk
Format       streamOptimized VMDK
```

The S3 bucket is a migration staging area, not the final application data architecture.

## EC2 landing design

The final instance type is selected only after `ImportImage` completes and the resulting AMI is known to be launchable under the current account plan. The preferred lab direction remains an eligible x86 burstable instance around the source's 2-vCPU / ~2.4-GiB footprint; `t3.small` is a candidate, not a promise.

The landing instance is temporary. Its first job is to prove that the existing VMware machine image can boot and operate correctly on EC2. PostgreSQL then becomes the DMS source for the RDS replatform step.

## Network direction

The previously approved migration VPC direction remains:

```text
VPC 10.30.0.0/16
|
+-- application/landing subnet
|   +-- imported EC2
|
+-- private DB subnet A 10.30.11.0/24
+-- private DB subnet B 10.30.12.0/24
    +-- RDS DB subnet group
```

For a short-lived lab, the exact EC2 subnet/public-access mechanism is finalized at launch time after account-plan and management-access checks. A public application subnet may be used temporarily for proof, but it is explicitly not the recommended production end state.

## Security boundaries

- import S3 bucket remains private,
- VM Import/Export uses the `vmimport` service role instead of static credentials,
- operator must be authorized to `iam:PassRole` to that role,
- SSH, if required for the initial imported-instance validation, is restricted to the operator source and not `0.0.0.0/0`,
- Flask TCP 8080 is exposed only for controlled validation,
- PostgreSQL TCP 5432 is not opened to the Internet,
- RDS remains private and accepts only approved application/DMS paths,
- Session Manager is preferred for steady-state administration where practical,
- VM images, database dumps and credentials are excluded from Git.

## Source-to-target compatibility controls

Before export, the guest was prepared for the change in virtual hardware:

| Area | Verified state |
|---|---|
| OS/arch | Ubuntu 24.04.4 / x86_64 |
| Boot | BIOS + GRUB2 on GPT disk |
| Root | LVM + ext4 |
| Network driver | ENA present in kernel/initramfs |
| Storage driver | NVMe present in kernel/initramfs |
| Legacy block support | xen_blkfront available |
| Interface naming | `eth0`, via `net.ifnames=0` |
| Addressing | DHCP |
| SSH | enabled + active |
| PostgreSQL | enabled + active |
| Failed services | 0 |

## Database target

After EC2 acceptance:

- RDS PostgreSQL uses a small burstable Single-AZ lab class selected at execution,
- DMS uses minimum suitable capacity for Full Load + CDC,
- DMS Premigration Assessment is run before CDC source changes,
- `wal_level=replica` is intentionally preserved until that assessment records the readiness gap,
- final application configuration points Flask to the RDS endpoint only after data/CDC validation.

## Cost guardrails

- no account-plan upgrade solely to make the lab pass,
- no NAT Gateway or ALB unless a demonstrated requirement appears,
- no Multi-AZ RDS for the short-lived proof,
- create RDS/DMS only after the imported AMI/EC2 path succeeds,
- remove VM-import staging objects and temporary images/snapshots when no longer required,
- terminate temporary EC2 and DMS resources after acceptance/evidence,
- record residual resources and actual cost/credit delta at closeout.

## Production direction vs lab direction

The lab accepts temporary simplifications to prove migration. A production-oriented target would normally add stronger ingress controls, private application compute, managed load balancing/HA as justified, central logging/monitoring, formal backup policy and tighter enterprise identity integration.