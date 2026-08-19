# Phase 03 — Current State

**Status: VM IMPORT/EXPORT EXECUTION — VMDK UPLOAD IN PROGRESS**  
**AWS account plan: Free Plan; no upgrade authorized**

## Source system

```text
MADAR-LEGACY-01
├── Ubuntu Server 24.04.4 LTS
├── kernel 6.8.0-138-generic / x86_64
├── 2 vCPU / ~2.4 GiB RAM
├── BIOS + GRUB2
├── GPT 25 GiB disk
│   ├── 1 MiB BIOS boot
│   ├── 2 GiB ext4 /boot
│   └── ~23 GiB LVM PV -> ubuntu-vg/ubuntu-lv -> ext4 /
├── PostgreSQL 16.14
├── Flask 3.1.3 / TCP 8080
└── deterministic DB baseline 10 / 50 / 150
```

## Completed MGN experiment

AWS Transform MGN successfully copied the source blocks (`25 / 25 GiB`, Healthy, Ready for testing). Test launch then failed before the target EC2 instance because MGN attempted to launch its service-managed conversion server as `m5.large`. CloudTrail recorded `Client.InvalidParameterCombination` because that instance type is not allowed by the account's Free Plan.

AWS Transform confirmed that the conversion-server type is not customer-configurable. The project therefore did not upgrade the account or repeat replication. MGN source, replication EC2, EBS and residual base snapshot resources were cleaned.

## VM Import/Export source preparation — complete

The guest was prepared to reduce VMware-specific boot/network risk before image import:

- ENA driver verified in kernel and initramfs,
- NVMe driver verified in kernel and initramfs,
- Xen block-front support verified,
- `ens33` replaced by stable `eth0` naming using GRUB `net.ifnames=0`,
- Netplan configured for DHCP on `eth0`,
- reboot passed with `192.168.14.128/24`, default route, Internet and DNS,
- SSH explicitly enabled at boot and active,
- PostgreSQL enabled/active after reboot,
- `madar_legacy` verified present,
- GRUB installed/rechecked on `/dev/sda`,
- kernel and initramfs boot artifacts verified,
- `systemctl --failed` returned zero failed services,
- filesystem verification returned zero errors.

## Independent database recovery point

Final logical backup:

```text
/home/madaradmin/madar_legacy_final.dump
Format             PostgreSQL CUSTOM
Size               ~11 KiB compressed lab data
Database           madar_legacy
PostgreSQL         16.14
TOC entries        27
Representative     customers / shipments / shipment_events
Validation         pg_restore -l succeeded
```

The dump is intentionally not committed to Git.

## Clean VMware export — complete

The first OVF export included the Ubuntu installer ISO because a virtual CD/DVD device was still attached. That artifact was rejected as the final migration image. The CD/DVD device was removed and a second clean export was created.

```text
MADAR-LEGACY-01.ovf          13,475 bytes
MADAR-LEGACY-01.mf              195 bytes
MADAR-LEGACY-01-disk1.vmdk  3,629,074,432 bytes (~3.4 GiB)
ISO                          absent
VMDK OVF declaration         streamOptimized
Virtual capacity             25 GiB
```

Local path used for the clean export:

```text
C:\Users\SCAR\Documents\Virtual Machines\New folder\
```

## AWS VM Import/Export staging — active

Region:

```text
us-east-1
```

Private staging bucket created:

```text
madar-vm-import-197821101770
```

Public access is blocked.

IAM service role created:

```text
Role                 vmimport
Trusted service      vmie.amazonaws.com
External ID          vmimport
S3 scope             import bucket + objects
EC2 scope            snapshot/image describe/register/copy operations needed by import
```

Operator authorization was tested with IAM policy simulation:

```text
Principal   arn:aws:iam::197821101770:user/mohammed-admin
Action      iam:PassRole
Resource    arn:aws:iam::197821101770:role/vmimport
Decision    allowed
```

## Current operation

The clean VMDK upload has been started from local Windows PowerShell because AWS CloudShell cannot access `C:\Users\...` on the workstation:

```powershell
aws s3 cp "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

Observed upload progress at the time of this repository update:

```text
62.0 MiB / 3.4 GiB
```

**The repository does not claim the upload is complete yet.**

## Next gate

```text
1. Wait for VMDK upload completion
2. Verify object exists and size in S3
3. Run EC2 ImportImage using the vmimport role
4. Record ImportTaskId
5. Monitor import task until completed or root-cause any failure
6. Record resulting AMI ID
7. Select an account-eligible x86 EC2 target
8. Launch with controlled network/security settings
9. Validate boot / eth0-DHCP / SSH / filesystems
10. Validate PostgreSQL service + madar_legacy database
11. Reconcile tables/data and Flask functionality
12. Continue database replatform track: DMS -> RDS
13. Continue operational-file replatform track: validated copy -> S3
14. Capture cost/security/cleanup evidence
```

## Current stop rule

Do not launch EC2 or create RDS/DMS resources until the `ImportImage` task produces a valid AMI. Do not report VM import success until the asynchronous import task actually completes.