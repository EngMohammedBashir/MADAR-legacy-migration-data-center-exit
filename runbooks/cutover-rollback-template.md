# Runbook — Migration Cutover & Rollback

**Status:** Template until target architecture is approved

## Preconditions

- approved target architecture,
- migration completed to pre-cutover stage,
- source and target validation baselines available,
- backups/snapshots confirmed,
- rollback owner identified,
- rollback deadline/point-of-no-return understood,
- monitoring available,
- no unresolved critical integrity differences.

## Cutover sequence

1. Announce/start migration window in the scenario record.
2. Stop or freeze source writes if required by the selected strategy.
3. Capture final source counts/checksums/transaction marker.
4. Apply final delta/synchronization.
5. Validate target integrity.
6. Change application endpoint/DNS/configuration as designed.
7. Run smoke tests.
8. Run representative business transaction.
9. Observe logs/metrics.
10. Compare against acceptance criteria.
11. Declare `CONTINUE` or `ROLLBACK` with reason.

## Abort / rollback triggers

Examples to finalize later:

- unexplained data mismatch,
- target application unavailable,
- critical dependency unreachable,
- error rate above agreed threshold,
- migration exceeds safe window,
- final synchronization fails,
- security control is not functioning as designed.

## Rollback outline

1. Stop target writes if required.
2. Preserve target evidence/logs.
3. Restore routing/configuration to source.
4. Re-enable source writes.
5. Validate source application and data.
6. Record any target-originated data requiring reconciliation.
7. Declare rollback outcome.
8. Open incident/decision follow-up if the exercise exposed a design gap.

## Evidence

Capture timestamps, baseline outputs, validation results, routing/config changes, smoke-test results and the continue/rollback decision.
