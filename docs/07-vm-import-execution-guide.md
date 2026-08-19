# VM Import/Export Execution Guide

## Purpose

This document explains the completed VMware-to-EC2 rehost path command by command: **what ran where, why it mattered, what failed, and what proved success**.

## Mental model

```text
VMware VM
  -> source compatibility preparation
  -> clean streamOptimized VMDK
  -> local Windows AWS CLI upload
  -> private S3
  -> EC2 VM Import/Export
  -> EBS snapshot + AMI
  -> EC2
  -> OS / DB / app validation
```

Execution environments:

```text
Ubuntu VM       source preparation and workload validation
Windows         VMware export + local VMDK upload
AWS CloudShell  AWS IAM/S3/VM Import commands
```

Do not mix them: CloudShell cannot see `C:\Users\...`, while local PowerShell can.

## 1. Source OS, boot and disk discovery

```bash
cat /etc/os-release
uname -r
uname -m
lsblk -o NAME,SIZE,FSTYPE,TYPE,MOUNTPOINTS
sudo fdisk -l /dev/sda
sudo pvs
sudo vgs
sudo lvs
```

Observed:

```text
Ubuntu 24.04.4 LTS
kernel 6.8.0-138-generic
x86_64
BIOS + GRUB2
25 GiB GPT disk
2 GiB ext4 /boot
~23 GiB LVM -> ext4 /
```

Purpose: know exactly what must boot and mount after the hypervisor changes.

## 2. AWS virtual-hardware readiness

```bash
modinfo ena | head
modinfo nvme | head
modinfo xen_blkfront | head
lsinitramfs /boot/initrd.img-$(uname -r) | \
  grep -E '/(ena|nvme|xen_blkfront)\.ko' | head
```

Observed: ENA and NVMe support present; Xen block-front available/built in.

Mental model:

```text
ENA   -> can the migrated guest use EC2 networking?
NVMe  -> can it see Nitro-era EBS presentation?
initramfs -> are required drivers available early enough to boot?
```

## 3. Bootloader readiness

```bash
grub-install --version
sudo grub-install --recheck /dev/sda
sudo update-grub
```

Observed:

```text
Installing for i386-pc platform.
Installation finished. No error reported.
```

`i386-pc` is GRUB's BIOS target; the OS remains x86_64.

## 4. Network portability: `ens33` -> `eth0`

Back up configuration:

```bash
sudo cp /etc/default/grub /etc/default/grub.pre-aws
sudo cp -a /etc/netplan /etc/netplan.pre-aws
```

Set:

```text
GRUB_CMDLINE_LINUX="net.ifnames=0"
```

Netplan:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
```

Generate and reboot:

```bash
sudo update-grub
sudo netplan generate
sudo reboot
```

Validate after reboot:

```bash
ip -br addr
ip route
ping -c 3 8.8.8.8
getent hosts aws.amazon.com
```

Observed on VMware after preparation:

```text
eth0 192.168.14.128/24
default via 192.168.14.2
Internet/DNS passed
```

Purpose: remove a VMware-specific NIC-name dependency and use DHCP so the guest can receive a new identity in AWS.

## 5. Service and recovery safety

SSH:

```bash
sudo systemctl enable ssh
systemctl is-enabled ssh
systemctl is-active ssh
```

PostgreSQL:

```bash
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -Atc "SELECT datname FROM pg_database;"
systemctl --failed --no-pager
```

Final logical DB recovery point:

```bash
sudo -u postgres pg_dump -Fc madar_legacy -f /tmp/madar_legacy_final.dump
sudo mv /tmp/madar_legacy_final.dump /home/madaradmin/madar_legacy_final.dump
sudo chown madaradmin:madaradmin /home/madaradmin/madar_legacy_final.dump
pg_restore -l /home/madaradmin/madar_legacy_final.dump | head -20
```

Observed:

```text
PostgreSQL 16.14
madar_legacy present
0 failed systemd units
CUSTOM dump / 27 TOC entries / expected tables
```

The logical dump is an independent recovery layer; it is not the primary disk-migration mechanism.

## 6. VMware export hygiene

The first OVF export included the Ubuntu installer ISO because the virtual CD/DVD remained attached. That export was rejected.

After removing the CD/DVD device, the VM was exported again:

```text
MADAR-LEGACY-01.ovf
MADAR-LEGACY-01.mf
MADAR-LEGACY-01-disk1.vmdk
```

PowerShell inspection:

```powershell
Get-ChildItem "C:\Users\SCAR\Documents\Virtual Machines\New folder" |
  Select-Object Name,Length

Select-String -Path "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01.ovf" `
  -Pattern "vmdk|iso|DiskSection|ResourceType|HostResource"
```

Critical result:

```text
VMDK format       streamOptimized
VMDK bytes        3,629,074,432
Virtual capacity  25 GiB
ISO               absent
```

## 7. AWS CLI identity

From local PowerShell:

```powershell
aws login
aws sts get-caller-identity
```

Observed principal: `mohammed-admin` in the lab account.

Purpose: always prove account/principal context before provisioning.

## 8. Private S3 staging

CloudShell:

```bash
REGION="us-east-1"
BUCKET="madar-vm-import-197821101770"

aws s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION"

aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
```

The VM image is a migration artifact, so the S3 landing zone stays private.

## 9. IAM service role `vmimport`

VM Import/Export needs a role it can assume.

Trust concept:

```json
{
  "Principal": {"Service": "vmie.amazonaws.com"},
  "Action": "sts:AssumeRole",
  "Condition": {"StringEquals": {"sts:Externalid": "vmimport"}}
}
```

Role:

```bash
aws iam create-role \
  --role-name vmimport \
  --assume-role-policy-document file://trust-policy.json
```

The inline policy grants S3 read access to the import bucket plus required EC2 image/snapshot operations.

Mental model:

```text
VM Import/Export = worker
vmimport role     = worker badge
S3               = warehouse
VMDK              = package
AMI               = converted product
```

## 10. Verify `iam:PassRole`

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

Purpose: prove the operator can pass the service role before spending time on a multi-GB transfer/import.

## 11. Upload VMDK from Windows

Run from **Windows PowerShell**, because the VMDK lives on the workstation:

```powershell
aws s3 cp "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

Verify object metadata:

```powershell
aws s3api head-object `
  --bucket madar-vm-import-197821101770 `
  --key "MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

Observed:

```text
ContentLength         3629074432
ServerSideEncryption  AES256
```

The S3 object size matched the local clean VMDK exactly.

## 12. Start EC2 VM Import/Export

CloudShell:

```bash
aws ec2 import-image \
  --region us-east-1 \
  --description "MADAR legacy VMware Ubuntu rehost" \
  --license-type BYOL \
  --role-name vmimport \
  --disk-containers '[
    {
      "Description": "MADAR-LEGACY-01 VMware disk",
      "Format": "VMDK",
      "UserBucket": {
        "S3Bucket": "madar-vm-import-197821101770",
        "S3Key": "MADAR-LEGACY-01-disk1.vmdk"
      }
    }
  ]'
```

Returned:

```text
ImportTaskId import-ami-48f44651b4c75774t
Status       active
```

Monitor:

```bash
aws ec2 describe-import-image-tasks \
  --region us-east-1 \
  --import-task-ids import-ami-48f44651b4c75774t \
  --query 'ImportImageTasks[0].{Task:ImportTaskId,Status:Status,Progress:Progress,Message:StatusMessage,AMI:ImageId,Snapshot:SnapshotDetails[0].SnapshotId}' \
  --output table
```

Observed progress included:

```text
converting  9%
updating    43%
booting     62%
completed   -> AMI + snapshot
```

Final:

```text
Status    completed
AMI       ami-0cbd2e9ec0d6f9168
Snapshot  snap-0920a020c47fb6447
```

## 13. Validate the imported AMI

```bash
aws ec2 describe-images \
  --region us-east-1 \
  --image-ids ami-0cbd2e9ec0d6f9168 \
  --query 'Images[0].{AMI:ImageId,State:State,Architecture:Architecture,RootDevice:RootDeviceName,Virtualization:VirtualizationType,ENA:EnaSupport,BlockDevices:BlockDeviceMappings}' \
  --output json
```

Observed:

```text
State          available
Architecture   x86_64
Virtualization hvm
ENA            true
Root volume    25 GiB
```

## 14. Launch EC2

The account-eligible x86 list was inspected and `t3.small` selected for the lab.

Launch choices:

```text
Name       MADAR-LEGACY-EC2
AMI        ami-0cbd2e9ec0d6f9168
Type       t3.small
Storage    25 GiB gp3
Public IP  enabled for temporary SSH validation
SSH        My IP only
```

Result:

```text
Instance   i-051336c5f304a5319
Private IP 172.31.3.142
Status     running / checks passed
```

## 15. Post-migration OS/workload validation

From SSH:

```bash
hostname
uname -a
ip -br addr
ip route
lsblk -f
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -Atc "SELECT datname FROM pg_database WHERE datname='madar_legacy';"
systemctl --failed --no-pager
```

Important hypervisor-change evidence:

```text
VMware disk name  sda
EC2 disk name     nvme0n1
root LVM          still activated correctly
VMware network    192.168.14.x
EC2 network       172.31.3.142
```

Database reconciliation:

```bash
sudo -u postgres psql -d madar_legacy -c "
SELECT 'customers' AS table_name, COUNT(*) FROM customers
UNION ALL
SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL
SELECT 'shipment_events', COUNT(*) FROM shipment_events;
"
```

Observed:

```text
customers         10
shipments         50
shipment_events   150
```

## 16. Flask validation

The legacy Flask app was not configured as a systemd service, so it did not auto-start after migration. That operational weakness was discovered during validation rather than hidden.

After loading the runtime database credential into the process environment:

```bash
cd ~/madar-legacy-app
source .venv/bin/activate
export MADAR_DB_PASSWORD='<REDACTED>'
python app.py
```

From another session:

```bash
curl -s http://127.0.0.1:8080/api/health
curl -s http://127.0.0.1:8080/api/summary
```

Observed:

```text
health   status=ok / database=connected
summary  customers=10 / shipments=50 / events=150
```

## Stage 1 acceptance

```text
VMDK upload                 PASS
ImportImage                 PASS
AMI                         available
EC2 boot/checks             PASS
network                     PASS
NVMe/LVM/filesystem         PASS
SSH                         PASS
PostgreSQL                  PASS
10 / 50 / 150 reconciliation PASS
Flask health/summary        PASS
```

**VMware -> EC2 rehost: COMPLETE.**

Continue with `docs/09-dms-rds-execution-guide.md` for the database replatform.

## What to remember for interviews

```text
Can it boot?         -> GRUB / disk / initramfs
Can it see AWS NIC?  -> ENA / eth0 / DHCP
Can it see storage?  -> NVMe / LVM
Can I administer it? -> SSH + SG
Is data safe?        -> pg_dump + reconciliation
Can AWS read image?  -> S3 + vmimport role
Can operator pass it?-> iam:PassRole
Did import finish?   -> ImportTaskId / AMI / snapshot
Did migration work?  -> OS + DB + app validation
```

The commands matter for reproducibility; the interview value comes from understanding why each gate existed.