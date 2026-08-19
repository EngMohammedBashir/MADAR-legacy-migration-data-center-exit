# Phase 03 — Migration Day Runbook

## Purpose

Ordered execution guide for the actual Phase 03 path. It records both the abandoned MGN path and the active VM Import/Export path so the repository tells the truth about what happened.

## Mental model

```text
1. Prepare/export VMware VM
2. Upload clean VMDK to private S3
3. VM Import/Export -> AMI
4. Launch/validate EC2
5. DMS -> RDS
6. Files -> S3
7. Cut over / validate / roll back if required
8. Clean up
```

## Phase A — Source safety gate

Confirm before migration image work:

- source VM healthy,
- deterministic DB baseline known,
- final PostgreSQL dump readable with `pg_restore -l`,
- operational-file backup/checksums retained,
- ENA/NVMe drivers present,
- GRUB/BIOS boot path verified,
- `eth0` + DHCP configuration proven after reboot,
- SSH and PostgreSQL enabled at boot,
- zero unexplained failed services,
- VMware source remains available as rollback anchor.

## Phase B — Historical MGN result

MGN was attempted first and must not be repeated under the current account plan:

```text
Replication        25/25 GiB / Healthy / Ready for testing
Test snapshot      succeeded
Conversion         failed
Failing resource   MGN service-managed Conversion Server
Requested type     m5.large
Account result     Free Plan rejected the instance type
Root cause         confirmed via CloudTrail + AWS Transform
```

Do not attempt to solve this by changing the target launch-template type. The target was not the failing compute resource.

MGN temporary resources were cleaned after the decision to pivot.

## Phase C — Clean VMware export

1. Shut down `MADAR-LEGACY-01` cleanly.
2. Ensure the Ubuntu installation ISO/CD-ROM is detached.
3. Export from VMware Workstation using **File -> Export to OVF**.
4. Inspect resulting files.
5. Confirm no `.iso` is included in the final artifact.
6. Inspect the OVF and verify the disk format is `streamOptimized`.
7. Keep the original VMware VM untouched as rollback source.

Verified clean artifact for this lab:

```text
MADAR-LEGACY-01.ovf
MADAR-LEGACY-01.mf
MADAR-LEGACY-01-disk1.vmdk
```

## Phase D — AWS import staging

### 1. Identity

```bash
aws sts get-caller-identity
```

Purpose: prove which IAM principal is operating the migration.

### 2. S3 staging bucket

Create a private bucket in `us-east-1`. For this execution:

```text
madar-vm-import-197821101770
```

Enable Block Public Access. This bucket is a temporary migration landing area, not a public distribution path.

### 3. vmimport service role

Create role `vmimport` trusted by:

```text
vmie.amazonaws.com
```

with ExternalId:

```text
vmimport
```

Grant only the S3 read and EC2 image/snapshot permissions needed for VM Import/Export.

### 4. PassRole authorization

Before a multi-GB upload/import, verify that the operator is allowed to pass the role:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::197821101770:user/mohammed-admin \
  --action-names iam:PassRole \
  --resource-arns arn:aws:iam::197821101770:role/vmimport \
  --query 'EvaluationResults[0].EvalDecision' \
  --output text
```

Expected:

```text
allowed
```

## Phase E — Upload VMDK

Run from **Windows PowerShell**, not CloudShell, because the exported VMDK is on the local `C:` drive:

```powershell
aws s3 cp "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

After completion:

```powershell
aws s3 ls s3://madar-vm-import-197821101770/ --region us-east-1
```

Validation: object exists and size is consistent with the local export.

## Phase F — Start ImportImage

Only after S3 verification, create a container description that references the S3 VMDK and run `aws ec2 import-image` using service role `vmimport`.

Record immediately:

- ImportTaskId,
- initial status,
- description,
- role used,
- source bucket/key.

Then monitor with `describe-import-image-tasks` until completion.

Do not move on while status is merely `active`. Capture the exact status message if the task fails.

Expected successful output:

```text
ImportImage task -> completed -> AMI ID + snapshot
```

## Phase G — Launch imported EC2

After AMI completion:

1. verify AMI state,
2. select an x86 instance type allowed by the account plan,
3. attach only required security-group ingress,
4. launch in the approved lab subnet,
5. wait for EC2 status checks,
6. obtain management access,
7. do not expose PostgreSQL publicly.

## Phase H — EC2 acceptance

Validate in this order:

```text
boot
-> filesystem/LVM
-> eth0/DHCP/default route/DNS
-> SSH or selected management path
-> systemctl --failed
-> PostgreSQL enabled/active
-> madar_legacy exists
-> table/row reconciliation
-> Flask health/read/write
-> operational files/job behavior
```

If boot or data integrity fails, stop and preserve the imported image/task evidence. Do not compensate by silently rebuilding the target.

## Phase I — Database replatform

Only after EC2 acceptance:

1. create private RDS PostgreSQL,
2. create minimum suitable DMS capacity,
3. define EC2 PostgreSQL source and RDS target endpoints,
4. run DMS Premigration Assessment,
5. capture `wal_level`/CDC finding,
6. remediate required settings on EC2 source,
7. reassess,
8. run Full Load + CDC,
9. reconcile database,
10. perform controlled shipment/event write and verify it reaches RDS.

## Phase J — File replatform

Transfer approved operational exports/reports to S3 and validate object count plus SHA-256/content. DataSync remains unnecessary for this tiny representative data set.

## Phase K — Cutover

- freeze writes for the short final window,
- ensure CDC is caught up,
- reconcile final database state,
- point Flask to RDS securely,
- validate read/write paths,
- validate scheduled processing,
- explicitly accept or abort,
- retain rollback anchor until acceptance.

## Phase L — Rollback

Rollback triggers include unexplained data differences, critical boot/application failure, unsafe network exposure, unacceptable replication lag or missing operational state.

Rollback means returning operations to the preserved known-good source/intermediate state, not improvising destructive repairs under time pressure.

## Phase M — Cleanup

After acceptance/evidence:

- stop/delete DMS resources,
- terminate temporary EC2 targets no longer required,
- remove unneeded EBS snapshots/AMI artifacts after deciding what evidence/recovery point to retain,
- delete the VM-import VMDK object and staging bucket when no longer required,
- delete temporary IAM role/policies if not retained for repeatability,
- delete lab RDS if the phase is fully torn down,
- remove temporary SG/routes/network resources,
- check all service consoles for residual resources,
- record actual cost/credit delta.

## Final rule

A successful import task is not a successful migration. A successful migration requires accepted business data and workload behavior on the target plus an understood rollback and cleanup state.