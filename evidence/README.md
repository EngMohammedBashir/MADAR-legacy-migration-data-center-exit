# Phase 03 Evidence Index

Evidence exists to prove engineering claims. Screenshots are not collected as decoration, and planned evidence is not described as completed evidence.

## Source baseline evidence

Existing local evidence proves:

- representative VMware source exists,
- Ubuntu runtime and storage baseline,
- SSH/network administration,
- PostgreSQL and application runtime,
- deterministic `10 / 50 / 150` dataset,
- Flask dashboard/read path,
- transactional application write path,
- scheduled Linux job behavior,
- source file SHA-256 baseline,
- restored deterministic migration baseline,
- PostgreSQL custom-format backup readability,
- operational-file backup integrity.

Representative filenames retained locally include:

```text
madar-legacy-vm-system-baseline.png
madar-legacy-vm-network-ssh.png
madar-lvm-storage-expanded.png
madar-base-os-patched.png
madar-runtime-postgresql-installed.png
madar-deterministic-dataset-baseline.png
madar-application-dashboard.png
madar-source-files-sha256-baseline.png
madar-cron-background-job-verified.png
madar-application-write-path-verified.png
madar-source-baseline-restored.png
madar-pre-migration-db-backup-verified-v2.png
madar-pre-migration-files-backup-verified.png
```

## MGN experiment evidence

Evidence to retain/publish after review:

```text
MGN source server -> 25/25 GiB replicated
MGN status -> Healthy / Ready for testing
MGN launch history -> snapshot success / conversion failure
CloudTrail RunInstances -> m5.large Conversion Server
AWS Transform response -> conversion-server type not configurable
EC2 -> replication server terminated
MGN -> zero active source servers after cleanup
EBS/Snapshot -> residual resources cleaned
```

This evidence supports the ADR that the visible `t3.small` target was not the failing resource.

## VM Import/Export source-preparation evidence

Command output already observed and should be represented with focused, sanitized captures where useful:

```text
OS/Kernel/Arch           Ubuntu 24.04.4 / 6.8.0-138 / x86_64
Boot                     BIOS / GRUB2
Disk                     GPT 25 GiB / ext4 + LVM
ENA                      kernel + initramfs
NVMe                     kernel + initramfs
xen_blkfront             built in
NIC after reboot         eth0 / DHCP / 192.168.14.128
Default route            192.168.14.2
Internet/DNS             pass
SSH                      enabled + active
PostgreSQL               enabled + active
DB                       madar_legacy present
Failed services          0
Final DB dump            CUSTOM / pg_restore -l readable
```

## VMware export evidence

The first OVF export contained an attached Ubuntu ISO and was intentionally rejected as the final migration artifact. After removing the virtual CD/DVD device, a clean export produced:

```text
MADAR-LEGACY-01.ovf          13,475 bytes
MADAR-LEGACY-01.mf              195 bytes
MADAR-LEGACY-01-disk1.vmdk  3,629,074,432 bytes
ISO                          absent
OVF VMDK format              streamOptimized
```

This is useful evidence of inspection rather than blindly uploading the first artifact.

## AWS import-staging evidence

Current proven AWS-side preparation:

```text
AWS identity            mohammed-admin
Region                  us-east-1
S3 bucket               madar-vm-import-197821101770
S3 public access        blocked
IAM role                vmimport
Trusted service         vmie.amazonaws.com
ExternalId              vmimport
PassRole simulation     allowed
VMDK upload             started; completion not yet claimed
```

## Evidence still required

### VM Import/Export
- completed S3 object + size,
- ImportTaskId,
- import status/progress,
- final `completed` status,
- AMI ID and snapshot ID(s),
- any import failure message if encountered.

### Imported EC2
- instance/system checks,
- boot and filesystem/LVM state,
- target NIC/DHCP/routing,
- SSH/management access,
- PostgreSQL active,
- DB/schema/row-count reconciliation,
- Flask functional validation,
- operational-file/job validation.

### DMS/RDS
- premigration assessment finding,
- reassessment after CDC remediation,
- Full Load completion,
- CDC running,
- controlled shipment/event replication proof,
- final RDS reconciliation.

### File/cutover/closeout
- S3 file-integrity validation,
- final cutover decision,
- rollback proof where practical,
- cleanup/residual-resource review,
- actual cost/credit delta.

## Quality and security rules

- never publish credentials, tokens, `.pgpass`, `.env`, private keys or raw session credentials,
- VM images and database backups remain outside Git,
- review screenshots for account-sensitive identifiers and unrelated desktop content,
- crop evidence to the engineering fact being demonstrated,
- preserve failures and status messages when they explain a decision,
- never mark a planned gate as passed merely because a command was started.