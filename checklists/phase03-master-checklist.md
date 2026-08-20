# Phase 03 Master Checklist — FINAL

**Status: COMPLETE**  
**Closed: 2026-08-20**

## A — Repository & story
- [x] Phase repository created and scoped.
- [x] Business case, source estate, migration strategy and validation philosophy documented.
- [x] Source workload built and baselined.
- [x] MGN attempt and root cause documented truthfully.
- [x] ADR records pivot to VM Import/Export.
- [x] VM Import/Export execution documented.
- [x] DMS/RDS execution and troubleshooting documented.
- [x] Final cutover, file migration and cleanup documented.
- [x] Reviewer/interview narrative updated for final outcome.

## B — Representative source VM
- [x] VMware source created with Ubuntu 24.04.4 LTS.
- [x] 2 vCPU / ~2.4 GiB RAM / 25 GiB disk.
- [x] Flask + PostgreSQL workload operational.
- [x] deterministic baseline created.
- [x] operational files and scheduled report job demonstrated.
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
- [x] recovery/closeout narrative documented.

## D — MGN experiment
- [x] MGN initialized and source discovered.
- [x] 25/25 GiB replication completed.
- [x] Healthy / Ready for testing reached.
- [x] test launch attempted.
- [x] conversion failure captured.
- [x] CloudTrail identified service-managed `m5.large` conversion server.
- [x] AWS Transform confirmation captured.
- [x] decision made not to upgrade account solely for lab.
- [x] MGN resources cleaned.

## E — VM Import/Export
- [x] BIOS/GRUB/LVM/ext4 compatibility verified.
- [x] ENA/NVMe/Xen support verified.
- [x] VMware NIC dependency removed and `eth0` DHCP reboot-tested.
- [x] SSH/PostgreSQL enabled and healthy.
- [x] clean export produced with no installer ISO.
- [x] streamOptimized VMDK verified.
- [x] private S3 staging and `vmimport` role configured.
- [x] `iam:PassRole` verified.
- [x] VMDK uploaded and ImportImage monitored.
- [x] import completed.
- [x] AMI `ami-0cbd2e9ec0d6f9168` created.
- [x] snapshot `snap-0920a020c47fb6447` created.

## F — Imported EC2 acceptance
- [x] imported AMI launched on `t3.small`.
- [x] EC2 system/instance checks passed.
- [x] Linux boot verified.
- [x] LVM/filesystems survived NVMe presentation.
- [x] `eth0`/DHCP/default route verified.
- [x] SSH path verified.
- [x] zero failed systemd units at acceptance.
- [x] PostgreSQL/schema/data verified.
- [x] Flask health/summary passed.

## G — Database replatform
- [x] PostgreSQL logical replication configured.
- [x] dedicated DMS source login created/tested.
- [x] private SG-to-SG migration paths configured.
- [x] private RDS PostgreSQL 16.14 target created.
- [x] DMS IAM prerequisite failure root-caused and fixed.
- [x] private DMS replication instance created.
- [x] source endpoint test successful.
- [x] target TLS requirement diagnosed and fixed.
- [x] target credential mismatch diagnosed and fixed.
- [x] target endpoint test successful.
- [x] Full Load + CDC reached 100% / 3 tables / 0 errors.
- [x] initial RDS reconciliation `10 / 50 / 150`.
- [x] controlled CDC insert replicated without rerunning Full Load.
- [x] final RDS reconciliation `11 / 50 / 150`.

## H — File replatform
- [x] approved operational files synchronized to S3.
- [x] source file count = 14.
- [x] S3 object count = 14.
- [x] S3 data downloaded independently for verification.
- [x] SHA-256 comparison passed for every file.
- [x] final operational bucket retained: `madar-operational-files-197821101770`.

## I — Application cutover
- [x] application DB configuration changed to environment-driven host/name/user/password/SSL settings.
- [x] application pointed to RDS using SSL.
- [x] Flask `/api/health` passed against RDS.
- [x] Flask `/api/summary` returned `11 / 50 / 150` business state.
- [x] dashboard relabeled to reflect AWS migrated estate.
- [x] local PostgreSQL stopped.
- [x] local PostgreSQL confirmed inactive.
- [x] Flask health still passed after local DB shutdown.
- [x] Flask summary still passed after local DB shutdown.
- [x] explicit cutover decision: ACCEPT / CONTINUE.

## J — Evidence
- [x] source baseline/recoverability evidence.
- [x] MGN replication/failure evidence.
- [x] VM Import/Export evidence.
- [x] EC2 acceptance evidence.
- [x] RDS/DMS endpoint, Full Load and CDC evidence.
- [x] final data reconciliation evidence.
- [x] pre-cutover dashboard evidence.
- [x] post-cutover AWS dashboard evidence.
- [x] local-PostgreSQL-disabled RDS dependency proof.
- [x] file count/hash integrity evidence.
- [x] final AWS cleanup audit evidence.
- [x] curated final screenshot index added under `evidence/screenshots/`.

## K — Cleanup / closeout
- [x] DMS task deleted.
- [x] DMS endpoints deleted.
- [x] DMS replication instance deleted.
- [x] DMS subnet group deleted.
- [x] RDS deleted after final acceptance evidence.
- [x] RDS subnet group deleted.
- [x] temporary migration Security Groups deleted.
- [x] temporary EC2 terminated.
- [x] orphaned 25 GiB EC2 volume deleted.
- [x] VM-import staging VMDK deleted.
- [x] VM-import staging bucket deleted.
- [x] temporary EC2 S3 instance profile/role/policy deleted.
- [x] final audit confirmed no active EC2/RDS/DMS/NAT/EIP/ALB resources from the lab.
- [x] imported AMI intentionally retained.
- [x] AMI backing snapshot intentionally retained.
- [x] operational S3 bucket intentionally retained.
- [x] Phase 03 closeout state documented.

## Final acceptance

```text
VM rehost                 PASS
Database Full Load        PASS
Database CDC              PASS
File migration            PASS
SHA-256 integrity         PASS
Application RDS cutover   PASS
Local DB dependency test  PASS
Cleanup                   PASS
```

**PHASE 03 COMPLETE.**