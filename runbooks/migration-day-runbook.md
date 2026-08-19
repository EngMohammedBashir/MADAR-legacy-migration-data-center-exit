# Phase 03 — Migration Day Runbook

## Purpose

Ordered execution guide for the actual Phase 03 path, including the failed MGN branch, the successful VM Import/Export rehost, and the completed DMS Full Load + CDC database replatform.

## Mental model

```text
1. Protect source and baseline data
2. Prepare VMware guest for EC2
3. Export clean VMDK
4. Stage in private S3
5. VM Import/Export -> AMI
6. Launch/validate EC2
7. Prepare PostgreSQL logical replication
8. Provision private RDS + DMS
9. Test endpoints
10. Full Load + CDC
11. Reconcile + controlled CDC proof
12. Cut over / rollback / files / cleanup
```

## A — Source safety gate

Before migration:

- source VM healthy,
- deterministic DB baseline `10 / 50 / 150`,
- logical PostgreSQL backup readable,
- operational-file backup/checksums retained,
- ENA/NVMe/GRUB/LVM state verified,
- `eth0` + DHCP reboot-tested,
- SSH and PostgreSQL enabled,
- VMware source preserved as rollback anchor.

## B — Historical MGN branch

```text
Replication        25/25 GiB / Healthy / Ready for testing
Test snapshot      succeeded
Conversion         failed
Failing resource   service-managed MGN Conversion Server
Requested type     m5.large
Root cause         confirmed through CloudTrail + AWS Transform
```

Do not retry this branch by changing the target instance type; the target and conversion node are separate resources.

## C — Clean VMware export

1. shut down source cleanly,
2. detach installation ISO/CD/DVD,
3. export OVF,
4. inspect file list,
5. confirm no `.iso`,
6. verify `streamOptimized` VMDK,
7. preserve original VM.

Final artifact:

```text
MADAR-LEGACY-01.ovf
MADAR-LEGACY-01.mf
MADAR-LEGACY-01-disk1.vmdk
```

## D — S3 + vmimport preparation

Identity:

```bash
aws sts get-caller-identity
```

Create private S3 staging and Block Public Access.

Create `vmimport` trusted by `vmie.amazonaws.com`, attach the required S3/EC2 import permissions, then verify operator delegation:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::197821101770:user/mohammed-admin \
  --action-names iam:PassRole \
  --resource-arns arn:aws:iam::197821101770:role/vmimport \
  --query 'EvaluationResults[0].EvalDecision' \
  --output text
```

Required result: `allowed`.

## E — Upload VMDK

From Windows PowerShell:

```powershell
aws s3 cp "C:\Users\SCAR\Documents\Virtual Machines\New folder\MADAR-LEGACY-01-disk1.vmdk" `
  "s3://madar-vm-import-197821101770/MADAR-LEGACY-01-disk1.vmdk" `
  --region us-east-1
```

Validate S3 object metadata/size before importing.

## F — ImportImage

```bash
aws ec2 import-image \
  --region us-east-1 \
  --description "MADAR legacy VMware Ubuntu rehost" \
  --license-type BYOL \
  --role-name vmimport \
  --disk-containers '<VMDK S3 container JSON>'
```

Monitor:

```bash
aws ec2 describe-import-image-tasks \
  --region us-east-1 \
  --import-task-ids import-ami-48f44651b4c75774t
```

Final result:

```text
completed
AMI       ami-0cbd2e9ec0d6f9168
Snapshot  snap-0920a020c47fb6447
```

## G — Launch and accept imported EC2

Launch the imported AMI using the chosen lab type (`t3.small`) and restricted SSH ingress.

Acceptance order:

```text
EC2 checks
 -> Linux boot
 -> eth0/DHCP
 -> NVMe/LVM/filesystems
 -> SSH
 -> systemctl --failed
 -> PostgreSQL
 -> madar_legacy schema/data
 -> Flask health/summary
```

Observed acceptance:

```text
DB counts       10 / 50 / 150
Failed units    0
PostgreSQL      active/enabled
Flask health    status=ok / database=connected
```

## H — Prepare source PostgreSQL for CDC

Check:

```bash
sudo -u postgres psql -Atc "SHOW wal_level; SHOW max_replication_slots; SHOW max_wal_senders;"
```

Set `wal_level=logical`, restart PostgreSQL, and confirm:

```text
logical
10
10
```

Configure PostgreSQL to listen on VPC-reachable interfaces and add authenticated VPC access to `pg_hba.conf`.

Create/test a dedicated DMS database principal. Do not commit its password.

## I — Build DMS/RDS network controls

Use dedicated groups:

```text
Source EC2 SG  sg-0589383abcc3ebbbc
DMS SG         sg-085569e2731850c8a
RDS SG         sg-093756a8cabaad407
```

Allow:

```text
DMS SG -> source TCP/5432
DMS SG -> RDS TCP/5432
EC2 SG -> RDS TCP/5432 for validation/cutover
```

Never use `0.0.0.0/0 -> 5432` for this migration.

## J — Provision private RDS

Create DB subnet group across two AZs, then create:

```text
Identifier  madar-postgres-target
Engine      PostgreSQL 16.14
Class       db.t3.micro
Storage     20 GiB gp3
Public      false
```

Wait for `available` before endpoint testing.

## K — Provision DMS control plane

If DMS returns:

```text
dms-vpc-role is not configured properly
```

fix IAM rather than changing network topology:

```text
Trust   dms.amazonaws.com
Role    dms-vpc-role
Policy  AmazonDMSVPCManagementRole
```

Then create the DMS subnet group and private replication instance:

```text
Identifier  madar-dms-repl
Class       dms.t3.small
Engine      3.6.1
Status      available
Private IP  172.31.13.46
```

## L — Source endpoint

Create PostgreSQL source endpoint for `172.31.3.142:5432 / madar_legacy` using the dedicated DMS login.

Test:

```bash
aws dms test-connection \
  --region us-east-1 \
  --replication-instance-arn "$REPL_ARN" \
  --endpoint-arn "$SOURCE_ENDPOINT_ARN"
```

Required: `successful`.

## M — Target endpoint and troubleshooting

Create PostgreSQL target endpoint for private RDS.

If error says `no encryption`, set:

```bash
aws dms modify-endpoint \
  --region us-east-1 \
  --endpoint-arn "$TARGET_ENDPOINT_ARN" \
  --ssl-mode require
```

If next error says `password authentication failed`, synchronize the target endpoint and RDS credential; do **not** weaken the SG.

Required final target test: `successful`.

## N — Create and run Full Load + CDC

Mapping: include `public.%`.

```bash
TASK_ARN=$(aws dms create-replication-task \
  --region us-east-1 \
  --replication-task-identifier madar-full-load-cdc \
  --source-endpoint-arn "$SOURCE_ENDPOINT_ARN" \
  --target-endpoint-arn "$TARGET_ENDPOINT_ARN" \
  --replication-instance-arn "$REPL_ARN" \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json \
  --query 'ReplicationTask.ReplicationTaskArn' \
  --output text)
```

Start when ready:

```bash
aws dms start-replication-task \
  --region us-east-1 \
  --replication-task-arn "$TASK_ARN" \
  --start-replication-task-type start-replication
```

Monitor:

```bash
aws dms describe-replication-tasks ...
aws dms describe-table-statistics ...
```

Accepted Full Load:

```text
Progress        100%
Tables loaded   3
Tables errored  0
customers       10
shipments       50
shipment_events 150
```

## O — Independent RDS reconciliation

Query RDS directly from EC2. Required initial target state:

```text
10 / 50 / 150
```

Do not rely only on DMS console/task statistics.

## P — Controlled CDC proof

Insert a uniquely identifiable row on the source after Full Load:

```sql
INSERT INTO public.customers (company_name, region)
VALUES ('MADAR CDC TEST CUSTOMER', 'Riyadh');
```

Then query RDS without rerunning Full Load.

Accepted result:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

Final RDS counts:

```text
customers         11
shipments         50
shipment_events   150
```

This proves CDC is active.

## Q — Cutover decision

Database migration proof is complete, but application cutover is separate.

Before a real cutover:

1. confirm CDC lag/catch-up,
2. freeze writes for a short final window,
3. final reconcile,
4. securely point Flask DB configuration to RDS,
5. validate `/api/health`, `/api/summary` and a controlled write,
6. explicitly accept/abort,
7. retain rollback source until acceptance.

## R — File replatform

Move approved operational files/reports to S3 and validate object count plus SHA-256/content.

## S — Cleanup

After final evidence/cutover decision:

- stop/delete DMS task and replication instance,
- delete temporary endpoint/network resources if no longer needed,
- remove VM-import VMDK/bucket after recovery decision,
- clean temporary IAM roles/policies if appropriate,
- terminate temporary EC2 if no longer needed,
- delete lab RDS if fully tearing down,
- intentionally decide whether to retain AMI/snapshot,
- inventory all residual resources,
- record cost/credit delta.

## Final rule

Do not call an infrastructure status a migration success. Success requires workload acceptance, independent data reconciliation, CDC proof, an understood rollback path and intentional cleanup.