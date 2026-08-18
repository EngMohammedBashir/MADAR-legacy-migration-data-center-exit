# Phase 03 Master Checklist

## A — Repository & story

- [x] Phase repository created.
- [x] Explain why legacy estate predates Phase 01.
- [x] Business case documented.
- [x] Source-estate model documented.
- [x] Validation philosophy documented.
- [x] Link implementation repository from master transformation repository.

## B — Local host preflight

- [x] Hardware virtualization enabled.
- [x] Hyper-V feature state checked.
- [x] Local free storage checked.
- [x] RAM/CPU constraints considered.
- [x] Install/select hypervisor. — VMware Workstation Pro 26H1.
- [x] Download/select guest OS. — Ubuntu Server 24.04.4 LTS.
- [x] Record hypervisor and guest versions.

## C — Representative legacy VM

- [x] Create VM. — `MADAR-LEGACY-01`.
- [x] Conservative CPU allocation. — 2 vCPU.
- [x] Conservative RAM allocation. — 2560 MB.
- [x] Dynamically allocated disk. — 25 GB virtual disk.
- [x] Configure networking. — VMware NAT; guest interface `ens33`.
- [x] Patch/base-configure guest. — OS patched, rebooted, post-reboot validation passed.
- [x] Install workload dependencies. — Python 3.12.3, pip 24.0, PostgreSQL 16.14 + contrib, isolated Python venv.
- [x] Install shipment application. — Flask dashboard/API backed by real PostgreSQL data.
- [x] Install/configure database. — `madar_legacy`, `madar_app`, customers/shipments/shipment_events schema.
- [ ] Create operational-file area.
- [ ] Configure scheduled/background job.
- [ ] Create pre-migration snapshot/backup.

### Source-lab evidence captured locally

- `madar-legacy-vm-system-baseline.png`
- `madar-legacy-vm-network-ssh.png`
- `madar-lvm-storage-expanded.png`
- `madar-base-os-patched.png`
- `madar-post-reboot-validation.png`
- `madar-runtime-postgresql-installed.png`
- `madar-postgresql-database-role-created.png`
- `madar-postgresql-schema-created.png`
- `madar-python-venv-psycopg2-ready.png`
- `madar-deterministic-dataset-baseline.png`
- `madar-application-dashboard.png`

## D — Synthetic data & source proof

- [x] Generate deterministic fictional customers/shipments. — 10 customers / 50 shipments / 150 shipment events. Repository seed now also fixes timestamps and event progression; local VM must rerun the corrected version before final baseline.
- [ ] Generate operational files.
- [x] Demonstrate application read path. — Dashboard/API reads PostgreSQL customers, shipments, events and summary counts.
- [ ] Demonstrate application write path. — Direct SQL writes were exercised during setup, but an application-level write path is still required.
- [ ] Demonstrate background job.
- [x] Capture DB row counts. — PostgreSQL independently confirmed `10 / 50 / 150`.
- [ ] Capture representative aggregates.
- [ ] Generate SHA-256 file manifest.
- [ ] Record file count/size.
- [x] Capture source evidence. — Focused screenshots captured locally; binary upload still pending review.

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
- [x] Confirm no secrets committed in current application implementation. — DB password is supplied through `MADAR_DB_PASSWORD`; `.env`, keys and venvs remain ignored.

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
