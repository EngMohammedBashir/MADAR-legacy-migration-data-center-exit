# Phase 03 — Migration Day Runbook

## Purpose

Ordered guide for a short-lived AWS migration window. Preparation is completed before paid resources are created.

## Mental model

```text
1. MGN   : VMware server -> EC2
2. DMS   : EC2 PostgreSQL -> RDS (Full Load + CDC)
3. S3    : small operational files -> S3
4. Validate
5. Cut over
6. Protect target
7. Clean up
```

## Cost clock rule

Do not create paid migration resources until the operator explicitly starts the migration session. Check Billing/credits first, record the start time, create each paid component only when needed, and remove temporary resources as soon as their evidence purpose is complete.

## Phase A — Pre-execution gate

Confirm:

- source VM/application healthy,
- deterministic source baseline known,
- PostgreSQL dump exists,
- PostgreSQL configuration backup exists,
- operational-file SHA-256 baseline exists,
- source outbound HTTPS to AWS works,
- staged target architecture approved,
- no credentials/secrets committed,
- original VMware source remains the rollback anchor.

## Phase B — Minimal AWS foundation

1. Check current credits/cost and record start time.
2. Confirm `us-east-1` and required quotas.
3. Create VPC `10.30.0.0/16`.
4. Create application subnet `10.30.1.0/24`.
5. Create private DB subnets `10.30.11.0/24` and `10.30.12.0/24` in separate AZs.
6. Configure only required routing/Internet Gateway for the lab landing path.
7. Create narrowly scoped security groups.
8. Do not create NAT Gateway or ALB for this migration proof.

## Phase C — Stage 1: MGN rehost

1. Initialize AWS Application Migration Service in `us-east-1`.
2. Use the AWS-provided MGN workflow to install/activate the replication agent on `MADAR-LEGACY-01`.
3. Confirm the source server appears in MGN.
4. Wait for replication to reach healthy/ready state.
5. **SCREENSHOT NOW:** MGN source health/replication evidence.
6. Launch an MGN test instance.
7. Verify Ubuntu, Flask, PostgreSQL and required local files exist on the EC2 test target.
8. Verify the application works against its still-local PostgreSQL database on EC2.
9. Keep the original VMware source intact.

At this point the workload has exited the local data center into an intermediate AWS EC2 state.

## Phase D — Stage 2 foundation: RDS + DMS

Only after the EC2 source is healthy:

1. Create Single-AZ RDS PostgreSQL using the smallest approved lab class available at execution.
2. Confirm RDS is private.
3. Allow PostgreSQL traffic only across the required EC2/DMS/RDS security-group paths.
4. Create the selected minimum DMS replication capacity.
5. Define the source endpoint as PostgreSQL on the migrated EC2 server.
6. Define the target endpoint as RDS PostgreSQL.
7. Test endpoint connectivity.

This staged design avoids direct DMS connectivity to the private VMware `192.168.14.128` source.

## Phase E — DMS Premigration Assessment / CDC readiness

1. Run AWS DMS Premigration Assessment before changing the known PostgreSQL CDC gap.
2. **SCREENSHOT NOW:** assessment finding, including `wal_level` if reported.
3. Remediate only required source-side findings on the EC2 PostgreSQL source.
4. For logical replication, apply the required PostgreSQL setting(s) and restart/reload only as required.
5. Verify the EC2-hosted legacy application still works after the database configuration change.
6. Re-run DMS Premigration Assessment.
7. **SCREENSHOT NOW:** acceptable/pass reassessment.

## Phase F — DMS Full Load + CDC

1. Create DMS task using **Full Load + CDC**.
2. Start task.
3. Wait for Full Load completion and inspect table statistics.
4. **SCREENSHOT NOW:** Full Load completion.
5. Keep CDC running.
6. **SCREENSHOT NOW:** CDC running/healthy.
7. Reconcile the deterministic database baseline on RDS.
8. Through the source Flask application on EC2, perform the controlled shipment status update.
9. Verify the same shipment status and matching event appear on RDS through CDC.
10. **SCREENSHOT NOW:** source write and matching target RDS change.

## Phase G — Stage 3: small operational files to S3

1. Create the S3 migration bucket/prefix only when ready to transfer.
2. Transfer approved `exports/` and `reports/` artifacts using the simplest approved AWS-supported method.
3. Preserve/use the source SHA-256 manifest for integrity validation.
4. Verify object count/prefixes.
5. Compare immutable baseline artifacts/checksums.
6. **SCREENSHOT NOW:** S3 objects and successful integrity validation.

AWS DataSync is deliberately not used for this tiny representative file set. It would be evaluated for a large independent file estate.

## Phase H — Application reconfiguration and validation

1. Change the EC2 Flask application DB endpoint from local PostgreSQL to RDS using secure configuration.
2. Start/restart the application as required.
3. Test `/api/health`, `/api/summary`, representative reads and controlled write.
4. Verify target DB persistence.
5. Reconfigure/validate scheduled report path for target DB/storage.
6. Review network exposure and management access.
7. **SCREENSHOT NOW:** application functioning against the AWS target architecture.

## Phase I — Final cutover

1. Capture final source/intermediate baseline.
2. Freeze new writes for the short cutover window.
3. Wait until DMS CDC is caught up.
4. Reconcile final database state.
5. Confirm operational files are current.
6. Complete the MGN cutover/finalization workflow as appropriate.
7. Direct operations to the EC2 + RDS target.
8. Run full acceptance checklist.
9. Keep rollback source until acceptance is explicit.
10. **SCREENSHOT NOW:** accepted final target state.

## Phase J — Rollback

Rollback if there is an unexplained integrity mismatch, failed critical read/write path, unacceptable replication gap, missing operational state, or an unsafe network/security issue that cannot be corrected inside the window.

Rollback means returning operations to the preserved known-good source/intermediate state rather than destroying the source and attempting risky emergency repairs.

## Phase K — Post-cutover protection

After acceptance, evaluate/enable AWS Backup for target resources where useful. AWS Backup is post-cutover protection; it does not replace the independent pre-migration `pg_dump` and PostgreSQL configuration backup.

If enabled, **SCREENSHOT NOW:** target recovery point/backup evidence.

## Phase L — Cleanup

1. Stop/delete DMS task and replication capacity.
2. Finalize/clean MGN migration resources according to the service workflow.
3. Remove the temporary EC2-local PostgreSQL dependency after the application is confirmed on RDS; do not delete anything needed for rollback before acceptance.
4. Terminate temporary/test EC2 instances no longer needed.
5. Delete unneeded EBS volumes/snapshots.
6. Delete RDS after final evidence if the lab is being fully torn down; avoid an unnecessary final snapshot unless intentionally retained.
7. Remove unused public IPv4 resources.
8. Empty/delete temporary S3 data if not retained as approved evidence.
9. Delete temporary security groups/routes/subnets/VPC after dependencies are gone.
10. Inspect Billing/Cost Explorer and service consoles for residual resources.
11. Record end time and actual credit/cost delta.
12. **SCREENSHOT NOW:** cleanup/cost evidence.

## Final rule

Never declare migration success because an AWS resource says `Available`. Success requires data reconciliation, CDC proof, file integrity, application functionality, operational validation and an understood rollback path.
