# Phase 03 Master Checklist

## A — Repository & story
- [x] Phase repository created.
- [x] Business case, source estate and validation philosophy documented.
- [x] Source workload built and baselined.
- [x] MGN attempt/root cause documented truthfully.
- [x] ADR records pivot to VM Import/Export.
- [x] Interview/reviewer narrative documented.

## B — Representative source VM
- [x] VMware Workstation Pro selected.
- [x] `MADAR-LEGACY-01` created.
- [x] Ubuntu Server 24.04.4 LTS.
- [x] 2 vCPU / ~2.4 GiB RAM / 25 GiB dynamic disk.
- [x] Flask + PostgreSQL workload operational.
- [x] deterministic data 10 customers / 50 shipments / 150 events.
- [x] operational files + scheduled report job demonstrated.
- [x] application read/write path demonstrated.
- [x] source DB/file/config backups created and verified.

## C — Discovery & assessment
- [x] compute/runtime inventory.
- [x] disk/LVM/filesystem inventory.
- [x] process/service/listener inventory.
- [x] application/database/file/job dependencies.
- [x] network/DNS dependency assessment.
- [x] component-level migration disposition.
- [x] cutover/rollback principle.
- [ ] final RTO/RPO narrative at closeout.

## D — MGN experiment
- [x] MGN initialized and agent installed.
- [x] source appeared in MGN.
- [x] 25/25 GiB initial replication completed.
- [x] replication status reached Healthy / Ready for testing.
- [x] test launch attempted.
- [x] snapshot step succeeded.
- [x] conversion failure captured.
- [x] CloudTrail `RunInstances` identified `m5.large` conversion server.
- [x] distinguished replication server / target / conversion server.
- [x] AWS Transform confirmation captured: conversion type not configurable.
- [x] decision made not to upgrade Free Plan for lab.
- [x] MGN source deleted.
- [x] replication EC2 terminated.
- [x] residual EBS/snapshot resources cleaned.

## E — VM Import/Export guest preparation
- [x] Ubuntu/kernel/architecture verified.
- [x] BIOS + GRUB2 verified.
- [x] GPT + LVM/ext4 layout verified.
- [x] ENA driver verified in kernel/initramfs.
- [x] NVMe driver verified in kernel/initramfs.
- [x] Xen block support verified.
- [x] GRUB backup created before NIC-name change.
- [x] Netplan backup created.
- [x] `net.ifnames=0` configured.
- [x] Netplan changed `ens33` -> `eth0` with DHCP.
- [x] `update-grub` / `netplan generate` completed.
- [x] reboot validated `eth0`, DHCP, route, Internet and DNS.
- [x] SSH enabled + active.
- [x] PostgreSQL enabled + active.
- [x] `madar_legacy` present after reboot.
- [x] GRUB installed/rechecked on `/dev/sda`.
- [x] kernel/initramfs boot files verified.
- [x] zero failed systemd services.
- [x] final PostgreSQL dump created and readable with `pg_restore -l`.

## F — Clean VMware export
- [x] source shut down cleanly.
- [x] first export inspected.
- [x] installer ISO detected in first OVF export.
- [x] VMware CD/DVD device removed.
- [x] clean second export created.
- [x] final export contains OVF + MF + VMDK only.
- [x] VMDK declared `streamOptimized`.
- [x] VMDK size recorded (~3.4 GiB physical, 25 GiB virtual capacity).

## G — AWS VM Import staging
- [x] AWS CLI identity verified as `mohammed-admin`.
- [x] region fixed to `us-east-1` for the workflow.
- [x] private S3 bucket `madar-vm-import-197821101770` created.
- [x] Block Public Access configured.
- [x] IAM role `vmimport` created.
- [x] trust principal `vmie.amazonaws.com` configured.
- [x] ExternalId `vmimport` configured.
- [x] S3/EC2 import permissions attached to role.
- [x] `iam:PassRole` policy simulation returned `allowed`.
- [x] local Windows upload command started.
- [ ] VMDK upload completed.
- [ ] S3 object size verified.

## H — ImportImage / AMI
- [ ] create import container description.
- [ ] start `aws ec2 import-image` with `vmimport` role.
- [ ] record ImportTaskId.
- [ ] monitor `describe-import-image-tasks`.
- [ ] preserve any failure status message if import fails.
- [ ] import task reaches `completed`.
- [ ] resulting AMI ID recorded.
- [ ] resulting snapshot ID(s) recorded.

## I — Imported EC2 acceptance
- [ ] choose account-eligible x86 instance type.
- [ ] configure least-privilege security group.
- [ ] launch imported AMI.
- [ ] EC2 system/instance checks pass.
- [ ] Linux boot verified.
- [ ] LVM/filesystems verified.
- [ ] `eth0`/DHCP/default route/DNS verified.
- [ ] SSH/management path verified.
- [ ] `systemctl --failed` reviewed.
- [ ] PostgreSQL enabled/active.
- [ ] `madar_legacy` database exists.
- [ ] DB row-count/record reconciliation.
- [ ] Flask health/read/write validation.
- [ ] operational-file/job validation.

## J — Database replatform to RDS
- [ ] create private RDS PostgreSQL target.
- [ ] create minimum suitable DMS capacity.
- [ ] DMS source endpoint points to EC2 PostgreSQL.
- [ ] target endpoint points to RDS.
- [ ] run DMS Premigration Assessment.
- [ ] capture CDC readiness finding.
- [ ] remediate required PostgreSQL logical-replication settings.
- [ ] reassess.
- [ ] run Full Load + CDC.
- [ ] reconcile RDS data.
- [ ] controlled shipment + matching event reaches RDS via CDC.

## K — File replatform
- [ ] transfer approved operational files to S3.
- [ ] object count reconciliation.
- [ ] SHA-256/content verification.
- [ ] scheduled report target disposition validated.

## L — Cutover / rollback
- [ ] final source/intermediate baseline captured.
- [ ] writes frozen for cutover window.
- [ ] CDC caught up.
- [ ] Flask reconfigured to RDS securely.
- [ ] acceptance criteria executed.
- [ ] explicit continue/abort decision documented.
- [ ] rollback path validated until acceptance.

## M — Evidence
- [x] source baseline/recoverability evidence.
- [x] MGN replication evidence.
- [x] MGN conversion failure + CloudTrail root cause.
- [x] MGN cleanup evidence.
- [x] VM compatibility preflight results recorded.
- [x] clean export/file list and streamOptimized evidence recorded.
- [x] S3 bucket + vmimport IAM preparation recorded.
- [x] PassRole `allowed` result recorded.
- [ ] completed VMDK upload evidence.
- [ ] ImportImage progress/completion evidence.
- [ ] AMI evidence.
- [ ] imported EC2 validation evidence.
- [ ] DMS/RDS CDC evidence.
- [ ] file-integrity evidence.
- [ ] final cutover evidence.
- [ ] cleanup/cost evidence.

## N — Cleanup / closeout
- [ ] remove VM import VMDK after no longer needed.
- [ ] clean temporary VM-import IAM/bucket resources if not retained.
- [ ] terminate temporary EC2 after final purpose.
- [ ] stop/delete DMS resources after proof.
- [ ] delete lab RDS if fully tearing down.
- [ ] clean unneeded AMI/EBS snapshots intentionally.
- [ ] verify residual resources across service consoles.
- [ ] review actual cost/credit delta.
- [ ] finalize RTO/RPO and lessons learned.
- [ ] update master transformation repository / next-phase trigger.