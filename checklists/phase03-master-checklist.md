# Phase 03 Master Checklist

## A — Repository & story

- [x] Phase repository created.
- [x] Explain why legacy estate predates Phase 01.
- [x] Business case documented.
- [x] Source-estate model documented.
- [x] Validation philosophy documented.
- [ ] Link implementation repository from master transformation repository.

## B — Local host preflight

- [x] Hardware virtualization enabled.
- [x] Hyper-V feature state checked.
- [x] Local free storage checked.
- [x] RAM/CPU constraints considered.
- [ ] Install/select hypervisor.
- [ ] Download/select guest OS.
- [ ] Record hypervisor and guest versions.

## C — Representative legacy VM

- [ ] Create VM.
- [ ] Conservative CPU allocation.
- [ ] Conservative RAM allocation.
- [ ] Dynamically allocated disk.
- [ ] Configure networking.
- [ ] Patch/base-configure guest.
- [ ] Install workload dependencies.
- [ ] Install shipment application.
- [ ] Install/configure database.
- [ ] Create operational-file area.
- [ ] Configure scheduled/background job.
- [ ] Create pre-migration snapshot/backup.

## D — Synthetic data & source proof

- [ ] Generate deterministic fictional customers/shipments.
- [ ] Generate operational files.
- [ ] Demonstrate application read path.
- [ ] Demonstrate application write path.
- [ ] Demonstrate background job.
- [ ] Capture DB row counts.
- [ ] Capture representative aggregates.
- [ ] Generate SHA-256 file manifest.
- [ ] Record file count/size.
- [ ] Capture source evidence.

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
- [ ] Compare target options.
- [ ] Record rejected alternatives.
- [ ] Approve target architecture.
- [ ] Create ADR for migration strategy.
- [ ] Define RTO/RPO assumptions for the lab scenario.
- [ ] Define downtime/cutover window.
- [ ] Define rollback triggers.

## G — AWS readiness

- [ ] Estimate paid components before apply.
- [ ] Check relevant service quotas.
- [ ] Prepare Terraform.
- [ ] `terraform fmt`.
- [ ] `terraform validate`.
- [ ] Review `terraform plan`.
- [ ] Review IAM/network exposure.
- [ ] Confirm no secrets committed.

## H — Migration execution

- [ ] Capture final source baseline.
- [ ] Create target infrastructure.
- [ ] Migrate application/runtime as selected.
- [ ] Migrate database/data as selected.
- [ ] Migrate operational files as selected.
- [ ] Reconfigure endpoints/paths.
- [ ] Execute smoke test.
- [ ] Record migration timing.

## I — Validation

- [ ] Database row-count reconciliation.
- [ ] Aggregate/value reconciliation.
- [ ] Representative-record validation.
- [ ] File-count validation.
- [ ] SHA-256 comparison.
- [ ] Application read test.
- [ ] Application write test.
- [ ] Background-job test.
- [ ] Restart/recovery behavior.
- [ ] Logging/monitoring check.
- [ ] Security exposure check.

## J — Cutover & rollback

- [ ] Execute documented cutover sequence.
- [ ] Validate cutover acceptance criteria.
- [ ] Perform controlled rollback exercise where practical.
- [ ] Validate source/rollback path.
- [ ] Document decision point: continue vs abort.

## K — Failure exercise

- [ ] Select one credible migration failure only after architecture is known.
- [ ] Label it CONTROLLED EXERCISE.
- [ ] Capture detection.
- [ ] Diagnose cause.
- [ ] Recover.
- [ ] Record corrective improvement.

## L — Closeout

- [ ] Capture final architecture/evidence.
- [ ] `terraform plan` / drift check as appropriate.
- [ ] Destroy paid temporary infrastructure.
- [ ] Handle stateful deletion prerequisites safely.
- [ ] Verify residual EC2/network/database/storage/log/monitoring resources.
- [ ] Review billing/cost without requiring billing screenshot.
- [ ] Update README outcome.
- [ ] Update risk register.
- [ ] Update master transformation repository.
- [ ] Record Phase 04 trigger.
- [ ] Final Git status clean and remote synchronized.
