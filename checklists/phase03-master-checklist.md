# Phase 03 Master Checklist

## A — Repository & story
- [x] Phase repository created.
- [x] Business case, source estate and validation philosophy documented.
- [x] Source workload built and baselined.
- [x] MGN attempt/root cause documented truthfully.
- [x] ADR records pivot to VM Import/Export.
- [x] Interview/reviewer narrative documented.
- [x] DMS/RDS execution guide added with real troubleshooting and validated commands.

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
- [x] VMDK upload completed.
- [x] S3 object size verified at 3,629,074,432 bytes.

## H — ImportImage / AMI
- [x] source S3 disk container defined.
- [x] `aws ec2 import-image` started with `vmimport` role.
- [x] ImportTaskId recorded: `import-ami-48f44651b4c75774t`.
- [x] `describe-import-image-tasks` monitored.
- [x] progress evidence captured through converting/updating/booting.
- [x] import task reached `completed`.
- [x] AMI recorded: `ami-0cbd2e9ec0d6f9168`.
- [x] snapshot recorded: `snap-0920a020c47fb6447`.

## I — Imported EC2 acceptance
- [x] account-eligible x86 instance type selected: `t3.small`.
- [x] least-privilege SSH SG configured using My IP.
- [x] imported AMI launched as `i-051336c5f304a5319`.
- [x] EC2 system/instance checks passed.
- [x] Linux boot verified.
- [x] LVM/filesystems verified on NVMe-presented storage.
- [x] `eth0`/DHCP/default route verified.
- [x] SSH/management path verified.
- [x] `systemctl --failed` reviewed: zero failed units.
- [x] PostgreSQL enabled/active.
- [x] `madar_legacy` exists.
- [x] DB row-count reconciliation passed: 10 / 50 / 150.
- [x] Flask health/summary validation passed.
- [ ] convert legacy Flask manual startup to a managed runtime service if retained long term.

## J — Database replatform to RDS
- [x] PostgreSQL source configured for logical replication (`wal_level=logical`).
- [x] replication slots/senders capacity validated.
- [x] PostgreSQL VPC listener and `pg_hba.conf` configured.
- [x] dedicated DMS source DB login created/tested.
- [x] DMS and RDS Security Groups created.
- [x] SG-to-SG TCP/5432 rules configured; no Internet-wide DB ingress.
- [x] private RDS PostgreSQL 16.14 target created.
- [x] RDS target reached `available`.
- [x] `dms-vpc-role` prerequisite failure captured.
- [x] `dms-vpc-role` trust + `AmazonDMSVPCManagementRole` fixed.
- [x] DMS replication subnet group created across two AZs.
- [x] DMS `dms.t3.small` replication instance reached `available`.
- [x] DMS source endpoint created.
- [x] source endpoint connection test returned `successful`.
- [x] target endpoint created.
- [x] target TLS failure diagnosed and `ssl-mode=require` configured.
- [x] target password failure diagnosed and credentials synchronized.
- [x] target endpoint connection test returned `successful`.
- [x] `full-load-and-cdc` task created and started.
- [x] Full Load reached 100%.
- [x] 3/3 tables loaded; 0 tables errored.
- [x] RDS initial counts reconciled to 10 / 50 / 150.
- [x] controlled source customer insert performed.
- [x] same record reached RDS via CDC without rerunning Full Load.
- [x] final RDS reconciliation passed: 11 / 50 / 150.

## K — File replatform
- [ ] transfer approved operational files to S3.
- [ ] object count reconciliation.
- [ ] SHA-256/content verification.
- [ ] scheduled report target disposition validated.

## L — Cutover / rollback
- [ ] final source/intermediate baseline captured.
- [ ] writes frozen for cutover window if actual cutover is executed.
- [ ] confirm CDC caught up immediately before cutover.
- [ ] Flask reconfigured to RDS securely if actual DB cutover is executed.
- [ ] application health/read/write acceptance executed against RDS.
- [ ] explicit continue/abort decision documented.
- [ ] rollback path retained until acceptance.

## M — Evidence
- [x] source baseline/recoverability evidence.
- [x] MGN replication evidence.
- [x] MGN conversion failure + CloudTrail root cause.
- [x] MGN cleanup evidence.
- [x] VM compatibility preflight results recorded.
- [x] clean export/file list and streamOptimized evidence recorded.
- [x] S3 bucket + vmimport IAM preparation recorded.
- [x] PassRole `allowed` result recorded.
- [x] completed VMDK upload evidence.
- [x] ImportImage progress/completion evidence.
- [x] AMI evidence.
- [x] imported EC2 validation evidence.
- [x] RDS available evidence.
- [x] DMS replication instance available evidence.
- [x] source/target endpoint success evidence.
- [x] Full Load completion evidence.
- [x] CDC proof evidence.
- [x] final RDS reconciliation evidence.
- [ ] actual screenshot binaries copied into final repository evidence subfolders from workstation.
- [ ] file-integrity evidence.
- [ ] final cutover evidence.
- [ ] cleanup/cost evidence.

## N — Cleanup / closeout
- [ ] decide whether DMS must remain running for a final cutover demonstration.
- [ ] stop/delete DMS task/instance after final CDC purpose.
- [ ] remove VM import VMDK after no longer needed.
- [ ] clean temporary VM-import IAM/bucket resources if not retained.
- [ ] terminate temporary EC2 after final purpose.
- [ ] delete lab RDS if fully tearing down.
- [ ] clean unneeded AMI/EBS snapshots intentionally.
- [ ] verify residual resources across service consoles.
- [ ] review actual cost/credit delta.
- [ ] finalize RTO/RPO and lessons learned.
- [ ] update master transformation repository / next-phase trigger.