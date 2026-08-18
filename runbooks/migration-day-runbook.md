# Phase 03 — Migration Day Runbook

## Purpose

This is the ordered execution guide for the short-lived AWS migration window. Preparation is completed before paid resources are created so the migration session is spent executing and validating rather than researching.

## Cost clock rule

Do not create paid migration resources until the operator explicitly starts the migration session. Check Billing/credits first. Record the start time. Create each paid component only when needed and remove it as soon as its evidence/validation purpose is complete.

## Phase A — Pre-execution gate

Confirm before AWS creation:

- source VM is running and application is healthy,
- deterministic source baseline is known,
- pre-migration PostgreSQL dump exists,
- PostgreSQL configuration backup exists,
- operational-file SHA-256 baseline exists,
- source outbound HTTPS to AWS works,
- target architecture is approved,
- no credentials/secrets are committed,
- rollback source remains intact.

## Phase B — AWS foundation

1. Check current credits/cost and record migration-window start time.
2. Confirm `us-east-1` and required service quotas.
3. Create VPC `10.30.0.0/16`.
4. Create public application subnet `10.30.1.0/24`.
5. Create private DB subnets `10.30.11.0/24` and `10.30.12.0/24` in separate AZs.
6. Attach Internet Gateway and configure only the required public route.
7. Create narrowly scoped EC2 and RDS security groups.
8. Create the S3 migration bucket/prefix structure.
9. Create Single-AZ RDS PostgreSQL using the smallest approved lab class available at execution.

No NAT Gateway or ALB is required for the migration proof.

## Phase C — MGN rehost path

1. Initialize AWS Application Migration Service in `us-east-1`.
2. Obtain/install the AWS Replication Agent on `MADAR-LEGACY-01` using the AWS-provided workflow.
3. Confirm the source server appears in MGN.
4. Wait for initial replication to reach a healthy/ready state.
5. Capture evidence when instructed.
6. Launch an MGN test instance only when ready to validate.
7. Do not perform final cutover until database/file paths and acceptance criteria are ready.

## Phase D — DMS readiness before migration

1. Create the selected minimum DMS replication capacity only when RDS and source connectivity are ready.
2. Create source PostgreSQL and target RDS endpoints.
3. Establish the approved secure temporary source-connectivity path. Do not expose PostgreSQL to `0.0.0.0/0`.
4. Run AWS DMS Premigration Assessment before changing the known source readiness gap.
5. Capture the AWS-native assessment finding.
6. Remediate only the findings required for the lab. The known candidate is PostgreSQL logical replication (`wal_level`).
7. Restart/reload PostgreSQL only as required by the chosen setting and verify the source application still works.
8. Re-run the assessment and capture the successful/acceptable result.

## Phase E — Database migration

1. Create a DMS task using **Full Load + CDC**.
2. Start the task.
3. Wait for Full Load completion and verify table statistics.
4. Keep CDC running.
5. Reconcile the deterministic baseline on RDS.
6. Execute the controlled CDC proof: change a representative shipment through the source Flask API.
7. Verify the shipment status and matching event appear on RDS through CDC.
8. Record replication state/latency evidence.

## Phase F — Operational files to S3

1. Transfer approved `exports/` and `reports/` artifacts to S3 using the selected AWS-supported transfer method.
2. Preserve the source manifest separately for validation.
3. Verify expected object count/prefixes.
4. Retrieve/compare immutable baseline artifacts and validate SHA-256.
5. Capture S3 and integrity evidence.

## Phase G — Target application validation

1. Launch/use the MGN test EC2 instance.
2. Reconfigure the application database endpoint from localhost to RDS using a secure configuration method.
3. Start the application.
4. Test health, summary, representative reads and a controlled write.
5. Verify target DB persistence.
6. Validate the scheduled/background reporting path or record the explicitly approved replatform step.
7. Review network exposure and management access.

## Phase H — Cutover

1. Capture final source baseline.
2. Freeze/stop new source writes for the short cutover window.
3. Wait until DMS CDC is caught up.
4. Reconcile final database state.
5. Confirm operational files are current.
6. Promote/finalize the MGN cutover target as required by the chosen workflow.
7. Direct operations to the target application.
8. Run the full acceptance checklist.
9. Keep the source intact until acceptance is explicitly declared.

## Phase I — Rollback trigger

Rollback if there is an unexplained integrity mismatch, failed critical application write/read path, unacceptable replication gap, missing operational state, or a security/network issue that cannot be safely corrected inside the cutover window.

Rollback means returning operations to the preserved source, not attempting risky live repairs while the source has already been destroyed.

## Phase J — Post-cutover protection

After acceptance, evaluate/enable AWS Backup for the target resources where it adds useful recovery protection. This is post-cutover target protection; it does not replace the independent source `pg_dump` and PostgreSQL configuration backup created before migration.

## Phase K — Cleanup

Immediately after required evidence and acceptance:

1. stop/delete DMS task and replication capacity,
2. remove temporary DMS connectivity resources,
3. finalize/clean MGN migration resources according to the service workflow,
4. terminate temporary/test EC2 instances that are no longer needed,
5. delete unneeded EBS volumes/snapshots,
6. delete RDS after final evidence if the lab is being fully torn down; skip final snapshot unless explicitly required,
7. remove unused public IPv4 resources,
8. empty/delete temporary S3 data if not retained as approved evidence,
9. delete temporary security groups/routes/subnets/VPC when dependencies are gone,
10. inspect Billing/Cost Explorer and service consoles for residual resources,
11. record end time and actual credit/cost delta.

## Evidence reminder

The assistant/operator workflow should explicitly call out `SCREENSHOT NOW` at evidence gates. Do not capture credentials, secrets, private keys or unrelated desktop information.
