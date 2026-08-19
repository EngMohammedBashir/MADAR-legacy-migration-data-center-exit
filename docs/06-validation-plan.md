# Migration Validation Plan

## Principle

A migration is not trusted because an AMI exists or an EC2 instance reaches `running`. Validation compares the target against the recorded source baseline and proves boot, network, application and data integrity.

## Source baseline

```text
Customers        10
Shipments        50
Shipment events  150
Database         madar_legacy
PostgreSQL       16.14
Representative tables
├── public.customers
├── public.shipments
└── public.shipment_events
```

An independent PostgreSQL custom-format dump exists and was validated with `pg_restore -l`.

## Gate 1 — VM import artifact

Before `ImportImage`:

- clean export contains no attached installer ISO,
- VMDK is `streamOptimized`,
- S3 object name/size matches the local export,
- S3 bucket is private,
- `vmimport` role exists and trusts `vmie.amazonaws.com`,
- role has required S3/image permissions,
- operator `iam:PassRole` decision is `allowed`.

Pass condition: the artifact and permissions are known before asynchronous import begins.

## Gate 2 — ImportImage task

Record:

- `ImportTaskId`,
- status transitions,
- progress percentage,
- status message if any,
- resulting AMI ID,
- related snapshot ID(s).

Do not call the import successful until task status is `completed` and an AMI is returned. If it fails, preserve the exact status message and troubleshoot the failing layer rather than repeatedly restarting the task.

## Gate 3 — EC2 boot acceptance

After launching the imported AMI:

```text
Instance running
      ↓
EC2 system/instance checks pass
      ↓
Linux boots
      ↓
network interface obtains DHCP
      ↓
default route/DNS work
      ↓
management access works
```

Validate:

- boot completes without emergency mode,
- expected root and `/boot` filesystems mount,
- LVM volume group/logical volume activate,
- network interface is usable,
- DHCP address/default route exist,
- SSH or selected management path works,
- no unexpected failed systemd services.

## Gate 4 — OS and service reconciliation

Confirm target identity/runtime:

- Ubuntu release and kernel,
- expected hostname/host configuration disposition,
- PostgreSQL 16.14 starts automatically,
- Flask/application files exist,
- expected operational data directories exist,
- scheduled-job configuration has an explicit target disposition.

## Gate 5 — Database reconciliation

On the imported EC2 source, verify:

- `madar_legacy` exists,
- expected schema/tables exist,
- baseline row counts match,
- representative records match,
- representative aggregate values match,
- no unexplained duplicate/missing records exist.

The independent dump is a recovery layer, not evidence that the disk-level migration itself succeeded.

## Gate 6 — Application validation

- application process starts,
- `/api/health` passes,
- `/api/summary` returns expected values,
- representative reads succeed,
- controlled shipment write succeeds,
- shipment event insertion remains transactional,
- expected logs are generated.

## Gate 7 — DMS/RDS database replatform

Only after imported EC2 acceptance:

1. create private RDS target,
2. run DMS Premigration Assessment,
3. record known CDC readiness findings,
4. remediate only required source settings,
5. reassess,
6. run Full Load + CDC,
7. reconcile target data,
8. prove a new source shipment/event change arrives on RDS.

CDC proof:

```text
EC2 PostgreSQL
shipment 3 = IN_TRANSIT
      |
      | controlled application write
      v
shipment 3 = DELIVERED + matching event
      |
      | DMS CDC
      v
RDS PostgreSQL
same shipment/event state
```

## Gate 8 — File validation

- source file count recorded,
- target object count matches expected scope,
- SHA-256 validation passes for immutable baseline files,
- representative files can be retrieved/read,
- naming/prefix structure is correct.

## Operational/security validation

- no unintended PostgreSQL Internet exposure,
- import S3 bucket remains private,
- temporary SSH/app ingress is narrow,
- restart/reboot behavior is tested where practical,
- monitoring/logging visibility is checked,
- rollback anchor remains available until acceptance,
- temporary migration resources are inventoried for cleanup.

## Evidence gates

Capture evidence for:

1. source baseline and independent backup validation,
2. MGN replication success,
3. MGN test-conversion failure and CloudTrail root cause,
4. MGN cleanup,
5. EC2 compatibility preparation (`eth0`, DHCP, drivers, GRUB, services),
6. clean VMware export and `streamOptimized` declaration,
7. private S3 staging bucket,
8. `vmimport` IAM role and PassRole authorization,
9. completed S3 VMDK upload,
10. ImportImage task/progress/completion,
11. resulting AMI,
12. imported EC2 boot/system checks,
13. PostgreSQL/data reconciliation,
14. application functional test,
15. DMS assessment/reassessment,
16. Full Load + CDC proof,
17. file integrity proof,
18. final cutover/rollback decision,
19. cleanup/cost evidence.

## Pass/fail rule

Unexplained differences are failures until reconciled or explicitly accepted with justification. The project never converts a warning into a success claim simply to make the portfolio look cleaner.