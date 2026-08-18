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

## D — Synthetic data & source proof
- [x] Deterministic dataset: 10 customers / 50 shipments / 150 events.
- [x] Operational shipment export and status report generated.
- [x] Application read path demonstrated.
- [x] Application write path demonstrated transactionally via PATCH endpoint.
- [x] Background job demonstrated via controlled two-minute cron proof.
- [x] DB row counts independently verified.
- [ ] Capture representative database aggregates for migration reconciliation.
- [x] SHA-256 source-file manifest generated and verified.
- [x] Source file count/size recorded.
- [x] Deterministic baseline restored after write-path proof.
- [x] Source evidence captured locally.

## E — Discovery
- [ ] Inventory compute/runtime.
- [ ] Inventory ports/processes/services.
- [ ] Inventory application configuration.
- [ ] Inventory database dependencies.
- [ ] Inventory filesystem dependencies.
- [ ] Inventory scheduled jobs.
- [ ] Inventory identities/credentials without exposing secrets.
- [ ] Inventory DNS/network dependencies.
- [ ] Inventory external integrations.
- [ ] Draw dependency map.

## F — Assessment & decision
- [ ] Classify component criticality/statefulness.
- [ ] Evaluate migration disposition per component.
- [ ] Compare target options and migration services.
- [ ] Record rejected alternatives.
- [ ] Approve target architecture.
- [ ] Create ADR for migration strategy.
- [ ] Define RTO/RPO assumptions.
- [ ] Define downtime/cutover window and rollback triggers.

## G — AWS readiness
- [ ] Estimate paid components before apply.
- [ ] Check service quotas.
- [ ] Prepare/review Terraform (`fmt`, `validate`, `plan`).
- [ ] Review IAM/network exposure.
- [x] Confirm no application secret committed.

## H — Migration execution
- [ ] Capture final cutover source baseline.
- [ ] Create target infrastructure.
- [ ] Migrate application/runtime as selected.
- [ ] Migrate database/data as selected.
- [ ] Migrate operational files as selected.
- [ ] Reconfigure endpoints/paths.
- [ ] Execute smoke test and record timing.

## I — Validation
- [ ] Database row-count reconciliation.
- [ ] Aggregate/value reconciliation.
- [ ] Representative-record validation.
- [ ] File-count validation.
- [ ] SHA-256 comparison.
- [ ] Application read/write tests on target.
- [ ] Background-job test on target.
- [ ] Restart/recovery, logging/monitoring and security checks.

## J — Cutover & rollback
- [ ] Execute cutover sequence and acceptance criteria.
- [ ] Perform controlled rollback exercise where practical.
- [ ] Validate source/rollback path.
- [ ] Document continue/abort decision point.

## K — Failure exercise
- [ ] Select credible failure after architecture is known.
- [ ] Label CONTROLLED EXERCISE.
- [ ] Capture detection, diagnosis, recovery and corrective improvement.

## L — Closeout
- [ ] Capture final architecture/evidence.
- [ ] Drift/plan check as appropriate.
- [ ] Destroy paid temporary infrastructure and verify residual resources.
- [ ] Review cost.
- [ ] Update README outcome/risk register/master transformation repository.
- [ ] Record Phase 04 trigger.
- [ ] Final Git status clean and remote synchronized.
