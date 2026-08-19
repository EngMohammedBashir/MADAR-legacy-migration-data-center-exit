# Phase 03 — Current State

**Status: REHOST PATH PIVOTED — VM IMPORT/EXPORT PRE-FLIGHT IN PROGRESS**  
**AWS account plan: Free Plan; no upgrade authorized**

## Verified source estate

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── Kernel 6.8.0-138-generic / x86_64
├── 2 vCPU / ~2.4 GiB RAM
├── BIOS + GRUB2
├── 25 GiB disk: /boot ext4 + LVM/ext4 root
├── PostgreSQL 16.14
├── Flask 3.1.3 on port 8080
├── Customers: 10
├── Shipments: 50
├── Shipment events: 150
└── Verified DB/file/config backups
```

## MGN execution result

AWS Transform MGN replication was executed successfully against the VMware source:

```text
VMware source
   |
   | AWS Replication Agent
   v
MGN staging
├── 25 / 25 GiB replicated
├── Initial replication finished
├── Data replication status: Healthy
└── Ready for testing
```

The test launch then failed during the **conversion** stage, before the configured `t3.small` target instance was launched.

CloudTrail isolated the exact failing API call:

```text
Service                  AWS Transform MGN
Event                    ec2:RunInstances
Role                     AWSApplicationMigrationConversionServerRole
Resource                 AWS Application Migration Service Conversion Server
Requested instance type  m5.large
Result                   Client.InvalidParameterCombination
Reason                   instance type not eligible for AWS Free Plan
```

This is distinct from both the configurable MGN replication server and the target EC2 launch template. AWS Transform confirmed that the conversion-server instance type is service-managed and cannot be overridden through a launch template, MGN launch setting, public API parameter, quota, or Transform workflow.

Because upgrading the AWS account from Free Plan is outside this lab's cost/risk guardrails, **MGN test launch/cutover is not being retried**.

## Cleanup completed

The unsuccessful MGN execution was cleaned up deliberately:

- source server disconnected and deleted from MGN,
- MGN replication EC2 instance terminated,
- residual MGN EBS resources removed,
- residual MGN base snapshot removed,
- no MGN source servers remain active.

The CloudTrail and MGN launch-history evidence is retained as the root-cause record.

## Revised rehost path

The rehost track is now:

```text
VMware MADAR-LEGACY-01
      |
      | Export OVA / supported VM image
      v
Amazon S3
      |
      | EC2 VM Import/Export (ImportImage)
      v
AMI
      |
      | launch Free-Plan-eligible x86 EC2 target
      v
EC2 test target
```

This removes the MGN-managed `m5.large` conversion-server dependency that blocked the previous path.

## VM Import/Export pre-flight completed

The source VM has been prepared and validated before export:

- Ubuntu `24.04.4 LTS` / kernel `6.8.0-138-generic` / `x86_64`,
- BIOS boot with GRUB2,
- ENA driver present in kernel and initramfs,
- NVMe driver present in kernel and initramfs,
- `xen_blkfront` built into the kernel,
- predictable VMware NIC name changed from `ens33` to `eth0`,
- GRUB now includes `net.ifnames=0`,
- Netplan uses DHCP on `eth0`,
- reboot validation passed: interface, DHCP, default route, Internet and DNS all healthy,
- PostgreSQL starts successfully after reboot,
- `madar_legacy` database remains present,
- filesystem verification reports `0 parse errors, 0 errors`,
- no failed systemd services,
- root filesystem remains healthy on LVM/ext4.

## Database safety baseline

A final PostgreSQL custom-format dump was created and validated before export:

```text
Database            madar_legacy
PostgreSQL          16.14
Dump format         CUSTOM
Archive TOC entries 27
Representative tables
├── public.customers
├── public.shipments
└── public.shipment_events
```

`pg_restore -l` successfully reads the archive. The dump remains outside Git.

## Component migration strategy

```text
STAGE 1 — REHOST
VMware MADAR-LEGACY-01
      |
      | VM Import/Export
      v
EC2: Ubuntu + Flask + PostgreSQL + files

STAGE 2 — REPLATFORM DATABASE
EC2 PostgreSQL
      |
      | AWS DMS Full Load + CDC
      v
RDS PostgreSQL

STAGE 3 — REPLATFORM FILES
Small operational CSV/reports
      |
      | validated transfer
      v
Amazon S3
```

## Cost posture

The AWS account remains on the **Free Plan**. No account upgrade is authorized for this lab. Any migration step must be checked end-to-end for hidden service-managed compute dependencies before execution.

Guardrails:

1. use only resources permitted by the current account plan,
2. treat credits as real money,
3. verify service-managed infrastructure before long-running transfers,
4. create only resources needed for the current gate,
5. capture evidence immediately,
6. clean temporary resources after each experiment.

## Exact next actions

```text
1. Preserve current VM state; no further MGN work
2. Clean shutdown of MADAR-LEGACY-01
3. Export VMware VM as supported OVA/image
4. Validate exported artifact locally
5. Re-check AWS VM Import/Export account prerequisites and IAM vmimport role
6. Upload image to S3 in us-east-1
7. Run ImportImage and monitor task to AMI availability
8. Launch a Free-Plan-eligible x86 EC2 test instance
9. Validate boot, eth0/DHCP, SSH and filesystem
10. Validate PostgreSQL 16.14 + madar_legacy data
11. Validate Flask read/write behavior and operational files
12. Continue DMS -> RDS and files -> S3 tracks only after EC2 acceptance
13. Capture cost/credit evidence and cleanup temporary resources
```

## Current gate

**STOP before export/upload until the VMware image is produced and the VM Import/Export execution prerequisites are re-checked against the current Free Plan.**
