# VM Import/Export Execution Guide

## Purpose

This document explains the active VMware-to-EC2 rehost path command by command. It is written for a reviewer who wants to understand not only **what** was typed, but **why each command exists, what system it runs on, and what evidence proves success**.

## Mental model

```text
Local VMware VM
    |
    | export
    v
stream-optimized VMDK
    |
    | local Windows AWS CLI
    v
private Amazon S3 bucket
    |
    | EC2 VM Import/Export
    | assumes role: vmimport
    v
EBS-backed AMI
    |
    | launch
    v
EC2
```

There are three execution environments in this workflow:

```text
Ubuntu VM       source preparation and workload validation
Windows         VMware export + local VMDK upload
AWS CloudShell  AWS-side IAM/S3/import commands
```

Confusing these environments is a common source of errors. CloudShell cannot see `C:\Users\...`; local PowerShell can.

---

## 1. Source operating-system compatibility checks

### OS / kernel / architecture

```bash
cat /etc/os-release
uname -r
uname -m
```

Purpose: confirm the guest OS, kernel and CPU architecture before selecting an AWS import/launch path.

Observed:

```text
Ubuntu 24.04.4 LTS
6.8.0-138-generic
x86_64
```

### Boot and disk topology

```bash
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINTS
sudo fdisk -l /dev/sda
sudo pvs
sudo vgs
sudo lvs
```

Purpose: understand whether the root filesystem is simple, LVM-backed, RAIDed, encrypted, etc. A migration engineer needs to know what must activate during early boot.

Observed:

```text
25 GiB GPT disk
1 MiB BIOS boot partition
2 GiB ext4 /boot
~23 GiB LVM physical volume
ubuntu-vg -> ubuntu-lv -> ext4 /
```

### Bootloader

```bash
grub-install --version
sudo grub-install --recheck /dev/sda
sudo update-grub
```

Purpose: verify/install the BIOS GRUB bootloader and regenerate boot configuration before exporting the machine image.

Observed result:

```text
Installing for i386-pc platform.
Installation finished. No error reported.
```

`i386-pc` here refers to GRUB's BIOS platform target; the operating system itself remains x86_64.

---

## 2. AWS virtual-hardware driver readiness

### ENA network driver

```bash
modinfo ena | head
```

Purpose: verify support for the Elastic Network Adapter used by many EC2 instance families.

### NVMe storage driver

```bash
modinfo nvme | head
```

Purpose: verify the guest can access Nitro-era storage presented through NVMe.

### Early-boot initramfs

```bash
lsinitramfs /boot/initrd.img-$(uname -r) | \
  grep -E '/(ena|nvme|xen_blkfront)\.ko' | head
```

Purpose: a driver existing somewhere under `/lib/modules` is weaker evidence than it being available during early boot. The initramfs is involved before the full root filesystem is available.

Observed:

```text
ENA present
NVMe present
xen_blkfront available/built in
```

---

## 3. Network portability: `ens33` -> `eth0`

The VMware guest originally used:

```text
ens33
```

with Netplan tied to that exact interface name. To reduce dependence on VMware-specific predictable naming, the guest was changed to traditional `eth0` naming.

### Backups before change

```bash
sudo cp /etc/default/grub /etc/default/grub.pre-aws
sudo cp -a /etc/netplan /etc/netplan.pre-aws
```

Purpose: create an immediate rollback point for the two configuration areas being changed.

### Disable predictable interface names

`/etc/default/grub`:

```text
GRUB_CMDLINE_LINUX="net.ifnames=0"
```

Then:

```bash
sudo update-grub
```

### Netplan DHCP configuration

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
```

Then:

```bash
sudo netplan generate
```

`netplan apply` was deliberately not run while the live interface was still named `ens33`; the configuration and kernel naming change were activated together by reboot.

### Reboot validation

```bash
ip -br addr
ip route
ping -c 3 8.8.8.8
getent hosts aws.amazon.com
```

Observed after reboot:

```text
eth0 UP 192.168.14.128/24
default via 192.168.14.2
Internet reachable
DNS resolution working
```

Engineering meaning: the guest survived the interface-name change and can dynamically obtain network configuration rather than depending on the VMware identity.

---

## 4. Service and data safety checks

### SSH

```bash
sudo systemctl enable ssh
systemctl is-enabled ssh
systemctl is-active ssh
```

Expected/observed:

```text
enabled
active
```

Purpose: `active` proves SSH works now; `enabled` proves it is scheduled to start on the next boot.

### PostgreSQL

```bash
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -Atc "SELECT datname FROM pg_database;"
```

Purpose: ensure the stateful service survives the preparation reboot and the expected database still exists.

### Failed services

```bash
systemctl --failed --no-pager
```

Observed: zero failed units.

### Final logical database backup

```bash
sudo -u postgres pg_dump -Fc madar_legacy -f /tmp/madar_legacy_final.dump
sudo mv /tmp/madar_legacy_final.dump /home/madaradmin/madar_legacy_final.dump
sudo chown madaradmin:madaradmin /home/madaradmin/madar_legacy_final.dump
pg_restore -l /home/madaradmin/madar_legacy_final.dump | head -20
```

Purpose: VM Import/Export carries the disk-level database files, but a logical PostgreSQL dump gives an independent application-level recovery path.

Observed:

```text
Format: CUSTOM
Database: madar_legacy
TOC entries: 27
customers / shipments / shipment_events present
```

---

## 5. VMware export hygiene

The VM was powered off cleanly before export.

VMware Workstation path:

```text
File -> Export to OVF
```

### First export finding

The first export contained:

```text
MADAR-LEGACY-01-file1.iso
```

because the Ubuntu installation ISO was still attached to the VM's virtual CD/DVD device.

The first artifact was not used. The CD/DVD device was removed in VMware settings and the export was repeated.

### Final clean export

```text
MADAR-LEGACY-01.ovf
MADAR-LEGACY-01.mf
MADAR-LEGACY-01-disk1.vmdk
```

No ISO.

PowerShell inspection:

```powershell
Get-ChildItem "C:\Users\SCAR\Documents\Virtual Machines\New folder" |
  Select-Object Name,Length
```

OVF inspection:

```powershell
Select-String -Path "...\MADAR-LEGACY-01.ovf" `
  -Pattern "vmdk|iso|DiskSection|ResourceType|HostResource"
```

Important result:

```text
ovf:format="...#streamOptimized"
```

---

## 6. AWS CLI identity

Local PowerShell authentication:

```powershell
aws login
aws sts get-caller-identity
```

Observed principal:

```text
arn:aws:iam::197821101770:user/mohammed-admin
```

Purpose: a CLI command is only as trustworthy as the identity executing it. `sts get-caller-identity` is the fastest proof of account/principal context.

---

## 7. Private S3 import staging

In AWS CloudShell:

```bash
REGION="us-east-1"
BUCKET="madar-vm-import-197821101770"

aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION"
```

For `us-east-1`, `get-bucket-location` returning `null` is expected behavior.

Block public access:

```bash
aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
```

Purpose: the VM disk is a migration artifact, not public content.

---

## 8. IAM service role: `vmimport`

VM Import/Export needs an IAM role it can assume to read the S3 artifact and perform image/snapshot operations.

Trust policy concept:

```json
{
  "Principal": {"Service": "vmie.amazonaws.com"},
  "Action": "sts:AssumeRole",
  "Condition": {"StringEquals": {"sts:Externalid": "vmimport"}}
}
```

Role creation:

```bash
aws iam create-role \
  --role-name vmimport \
  --assume-role-policy-document file://trust-policy.json
```

The inline role policy grants S3 read access to the import bucket and the EC2 image/snapshot actions required by the import workflow.

Mental model:

```text
VM Import/Export = worker
vmimport role     = worker's badge
S3 bucket        = warehouse
VMDK             = package
AMI              = converted product
```

---

## 9. `iam:PassRole` verification

Creating a service role is not enough. The operator must be allowed to tell AWS to use/pass that role.

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::197821101770:user/mohammed-admin \
  --action-names iam:PassRole \
  --resource-arns arn:aws:iam::197821101770:role/vmimport \
  --query 'EvaluationResults[0].EvalDecision' \
  --output text
```

Observed:

```text
allowed
```

Purpose: discover authorization failure **before** spending time uploading/importing a multi-GB image.

---

## 10. Upload VMDK from Windows

This command must run on the Windows workstation because the file lives on the local disk:

```powershell
aws s3 cp "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

`aws s3 cp` means:

```text
source = local Windows file
transport = authenticated HTTPS through AWS CLI
API destination = Amazon S3
object = same VMDK inside the private bucket
```

At this document update, upload had started and was observed at `62.0 MiB / 3.4 GiB`. Completion must be verified before continuing.

Verification after completion:

```powershell
aws s3 ls s3://madar-vm-import-197821101770/ --region us-east-1
```

---

## 11. Next: `ImportImage`

After object verification, create a disk-container description that points to the S3 VMDK and run:

```text
aws ec2 import-image
```

The task is asynchronous. Immediately record the returned `ImportTaskId`, then monitor with:

```text
aws ec2 describe-import-image-tasks
```

Expected lifecycle:

```text
active / converting
      -> progress changes
      -> completed
      -> AMI ID + snapshot
```

A failure status message is evidence and must be preserved; do not hide it by repeatedly restarting tasks.

---

## 12. After AMI creation

Only after import completion:

```text
AMI
 -> choose eligible x86 EC2 instance type
 -> least-privilege security group
 -> launch
 -> EC2 status checks
 -> Linux boot
 -> network
 -> management access
 -> PostgreSQL/data reconciliation
 -> Flask validation
```

The original VMware source remains the rollback anchor until the imported workload is explicitly accepted.

## What to remember for interviews

Do not memorize every command. Remember the engineering questions:

```text
Can it boot?         -> GRUB / disk / initramfs
Can it see AWS NIC?  -> ENA / eth0 / DHCP
Can it see storage?  -> NVMe / LVM
Can I administer it? -> SSH / IAM/network controls
Is data safe?        -> pg_dump + reconciliation
Can AWS read image?  -> S3 + vmimport role
Can I pass the role? -> iam:PassRole
Did import finish?   -> ImportTaskId / status / AMI
```

That mental model is more valuable than memorizing syntax.