# Migration Validation Plan

## Principle

A migrated workload is not trusted because the application homepage opens. Validation compares the AWS destination against the recorded source baseline and proves both static integrity and live change replication.

## Frozen source baseline

The deterministic pre-migration baseline is:

```text
Customers:        10
Shipments:        50
Shipment events: 150
```

Shipment 3 is restored to `IN_TRANSIT` after the earlier controlled write-path proof.

## Database validation

Before cutover, capture the final source state. After DMS Full Load:

- expected schema/tables exist,
- row counts match the expected source state,
- representative aggregate values match,
- representative records match by ID,
- expected constraints/indexes are present where applicable,
- no unexplained records are missing or duplicated.

### CDC proof

The key live-migration experiment is:

```text
SOURCE PostgreSQL
shipment 3 = IN_TRANSIT
        |
        | Flask PATCH write
        v
shipment 3 = DELIVERED
        |
        | PostgreSQL WAL / DMS CDC
        v
TARGET RDS PostgreSQL
shipment 3 = DELIVERED
```

The test must also verify that the matching shipment event is replicated. This demonstrates that the target is not merely a one-time copy; DMS is capturing source changes while CDC is active.

## File validation

- source file count recorded,
- expected object count checked after transfer,
- SHA-256 manifest comparison passes for immutable baseline files,
- representative files can be retrieved/read,
- object naming/prefix structure is correct,
- no migration is declared successful merely because an upload command returned success.

## Application validation

On the migrated target:

- application starts,
- `/api/health` passes,
- `/api/summary` returns expected values,
- representative customer/shipment reads work,
- a controlled shipment status update works,
- database write persists in RDS after endpoint reconfiguration,
- shipment event insertion remains transactional with the status update,
- expected logs are generated.

## Scheduled/background processing

- scheduled report mechanism is reconfigured for the target database/storage path,
- one controlled execution completes,
- expected report is generated,
- log reports success,
- source cron remains available until target acceptance.

## Operational validation

- required inbound/outbound network flows work,
- RDS has no unintended public exposure,
- management access works through the selected target administration path,
- restart/reboot behavior is tested where practical,
- monitoring/logging visibility is checked,
- post-cutover backup/recovery point is confirmed if AWS Backup is enabled,
- rollback trigger and owner are understood.

## Screenshot / evidence gates

The operator should stop for evidence at these points:

1. source legacy application/baseline,
2. MGN source server ready/healthy,
3. MGN replication status,
4. DMS Premigration Assessment finding before CDC remediation,
5. DMS reassessment after remediation,
6. DMS Full Load completed,
7. DMS CDC running,
8. source shipment change,
9. matching target RDS shipment/event change via CDC,
10. S3 migrated objects,
11. SHA-256 file-integrity validation,
12. MGN test instance,
13. application functional on AWS,
14. final cutover state,
15. AWS Backup recovery point if enabled,
16. cleanup/cost evidence.

Binary screenshots remain local until reviewed for credentials, account-sensitive information and unrelated desktop content.

## Pass/fail rule

Do not call the migration successful while unexplained integrity differences remain. Either reconcile them, explicitly accept them with justification, or roll back.

## Acceptance criteria

Phase 03 passes only when:

- database reconciliation succeeds,
- CDC change proof succeeds,
- operational-file integrity succeeds,
- target application read/write paths succeed,
- scheduled processing succeeds or has an explicitly accepted migration disposition,
- security exposure is reviewed,
- rollback remains viable until acceptance,
- paid temporary resources are cleaned up after evidence capture.
