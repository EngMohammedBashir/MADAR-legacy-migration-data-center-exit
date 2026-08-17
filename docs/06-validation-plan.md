# Migration Validation Plan

## Principle

A migrated workload is not trusted because the application homepage opens.

Validation compares the destination against a recorded source baseline.

## Data validation

### Database

- schema/version expected,
- table row counts match expected cutover state,
- selected aggregate totals match,
- representative records match by ID,
- constraints/indexes expected,
- no unexplained records missing or duplicated.

### Files

- file count matches,
- total expected size is reasonable,
- SHA-256 manifest comparison passes for immutable test files,
- representative files can be retrieved/read,
- expected paths/naming behavior works.

## Functional validation

- application starts,
- health endpoint or smoke test passes,
- representative shipment can be read,
- representative state-changing operation works if safe,
- database writes persist,
- operational file workflow works,
- scheduled/background process completes,
- expected logs are generated.

## Operational validation

- monitoring/log collection visible,
- least-privilege access reviewed,
- backups/recovery point confirmed where in scope,
- expected inbound/outbound network flows work,
- unintended public exposure absent,
- restart/reboot behavior tested,
- rollback trigger and owner understood.

## Cutover reconciliation

Capture a final source baseline immediately before cutover or source freeze, then compare the target after migration.

## Pass/fail rule

Do not call the migration successful while unexplained integrity differences remain. Either reconcile them, explicitly accept them with justification, or roll back.
