# Phase 03 Master Checklist

## A — Repository & story
- [x] Phase repository created.
- [x] Legacy estate positioned before the AWS transformation.
- [x] Business case, source estate and validation philosophy documented.
- [x] Master transformation repository linkage established.

## B — Local host preflight
- [x] Virtualization/Hyper-V/storage/RAM/CPU constraints checked.
- [x] VMware Workstation Pro 26H1 selected.
- [x] Ubuntu Server 24.04.4 LTS selected and versions recorded.

## C — Representative legacy VM
- [x] `MADAR-LEGACY-01` created.
- [x] 2 vCPU / 2560 MB RAM / 25 GB dynamic disk.
- [x] VMware NAT and SSH administration verified.
- [x] LVM root capacity corrected and OS patched/rebooted.
- [x] Python/PostgreSQL dependencies installed using isolated `.venv`.
- [x] Flask shipment application installed.
- [x] `madar_legacy` / `madar_app` database implementation verified.
- [x] Operational-file area created.
- [x] Scheduled/background job configured and demonstrated.
- [x] Pre-migration database and operational-file backups created and verified.
- [x] PostgreSQL configuration backup created before DMS/CDC changes.

## D — Synthetic data & source proof
- [x] Deterministic dataset: 10 customers / 50 shipments / 150 events.
- [x] Operational shipment export and status report generated.
- [x] Application read path demonstrated.
- [x] Application write path demonstrated transactionally via PATCH endpoint.
- [x] Background job demonstrated via controlled two-minute cron proof.
- [x] DB row counts independently verified.
- [ ] Capture final representative database aggregates immediately before cutover.
- [x] SHA-256 source-file manifest generated and verified.
- [x] Source file count/size recorded.
- [x] Deterministic baseline restored after write-path proof.
- [x] Source evidence captured locally.

## E — Discovery
- [x] Inventory compute/runtime.
- [x] Inventory ports/processes/services.
- [x] Inventory application configuration at the required migration level.
- [x] Inventory database dependencies.
- [x] Inventory filesystem dependencies.
- [x] Inventory scheduled jobs.
- [x] Inventory identities/credentials without exposing secrets.
- [x] Inventory DNS/network dependencies for the representative lab.
- [x] Record external-integration assumptions (none required by the representative workload beyond AWS migration connectivity).
- [x] Draw dependency map.

## F — Assessment & decision
- [x] Classify component criticality/statefulness.
- [x] Evaluate migration disposition per component.
- [x] Compare target options and migration services.
- [x] Record rejected alternatives.
- [x] Approve target architecture for lab execution.
- [x] Document migration strategy and rationale.
- [ ] Define final RTO/RPO assumptions for closeout narrative.
- [x] Define cutover principle and rollback triggers.

## G — AWS readiness
- [x] Define cost guardrails before execution.
- [ ] Check execution-time service quotas.
- [x] Define VPC/subnet/security-group target plan.
- [x] Confirm no NAT Gateway/ALB/Multi-AZ RDS required for the lab proof.
- [x] Confirm no application secret committed.
- [x] Verify source outbound HTTPS reachability to AWS `us-east-1`.
- [x] Check PostgreSQL CDC baseline (`wal_level`, slots, WAL senders).
- [x] Preserve PostgreSQL config before CDC remediation.
- [x] Plan AWS DMS Premigration Assessment before manual CDC changes.
- [ ] Finalize secure DMS-to-source PostgreSQL connectivity mechanism.
- [ ] Prepare/review Terraform if IaC is used for the target (`fmt`, `validate`, `plan`).
- [ ] Review execution-time IAM/network exposure.

## H — Migration execution
- [ ] Start paid-resource migration window and record starting cost/credits.
- [ ] Capture final cutover source baseline.
- [ ] Create target VPC/network/security foundation.
- [ ] Create S3 migration target.
- [ ] Create RDS PostgreSQL target.
- [ ] Initialize MGN and install/activate replication agent.
- [ ] Verify MGN source replication health.
- [ ] Create DMS replication capacity/endpoints only when connectivity is ready.
- [ ] Run DMS Premigration Assessment and capture finding.
- [ ] Remediate required PostgreSQL CDC findings and reassess.
- [ ] Run DMS Full Load + CDC.
- [ ] Prove a controlled source change arrives in RDS through CDC.
- [ ] Transfer operational files to S3.
- [ ] Launch MGN test target and reconfigure application DB endpoint.
- [ ] Execute smoke tests and record timing.

## I — Validation
- [ ] Database row-count reconciliation.
- [ ] Aggregate/value reconciliation.
- [ ] Representative-record validation.
- [ ] CDC shipment + event proof.
- [ ] File-count/object-count validation.
- [ ] SHA-256 comparison.
- [ ] Application read/write tests on target.
- [ ] Background-job test on target/replatformed path.
- [ ] Restart/recovery, logging/monitoring and security checks.

## J — Cutover & rollback
- [ ] Freeze source writes for final cutover window.
- [ ] Confirm DMS CDC caught up.
- [ ] Execute cutover sequence and acceptance criteria.
- [ ] Perform controlled rollback exercise where practical.
- [ ] Validate source/rollback path.
- [ ] Document continue/abort decision point.

## K — Post-cutover protection / failure exercise
- [ ] Evaluate/enable AWS Backup for target resources where useful.
- [ ] Confirm recovery point if AWS Backup is enabled.
- [ ] Select credible controlled failure after target exists.
- [ ] Label failure as CONTROLLED EXERCISE.
- [ ] Capture detection, diagnosis, recovery and corrective improvement.

## L — Evidence gates
- [ ] MGN source healthy/ready screenshot.
- [ ] MGN replication screenshot.
- [ ] DMS Premigration Assessment finding screenshot.
- [ ] DMS reassessment screenshot.
- [ ] DMS Full Load completion screenshot.
- [ ] DMS CDC running screenshot.
- [ ] Source write + target RDS CDC proof screenshots.
- [ ] S3 objects + SHA-256 validation screenshots.
- [ ] MGN test/target application screenshots.
- [ ] Final cutover screenshot.
- [ ] AWS Backup recovery point screenshot if enabled.
- [ ] Cleanup/cost evidence screenshot.

## M — Closeout
- [ ] Stop/delete DMS resources immediately after required proof.
- [ ] Finalize/clean MGN migration resources.
- [ ] Terminate temporary EC2 and delete unneeded EBS.
- [ ] Delete lab RDS after final evidence if no longer needed.
- [ ] Remove temporary public IPv4/network resources.
- [ ] Clean temporary S3/VPC resources where appropriate.
- [ ] Verify residual resources across service consoles.
- [ ] Review actual cost/credit delta.
- [ ] Update README outcome/risk register/master transformation repository.
- [ ] Record Phase 04 trigger.
- [ ] Final Git status clean and remote synchronized.
