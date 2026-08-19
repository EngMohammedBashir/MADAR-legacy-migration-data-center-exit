# Migration Strategy

## Decision summary

The representative legacy VM contains several logical components with different state and operational characteristics. The migration therefore uses a staged component-level strategy rather than pretending the entire VM should remain unchanged forever.

The original Stage 1 rehost mechanism was AWS Transform MGN. MGN replication succeeded, but test conversion was blocked by a Free Plan restriction on a service-managed `m5.large` conversion server that cannot be overridden. The accepted rehost mechanism is now **EC2 VM Import/Export**.

## Current staged strategy

```text
Stage 1 — Rehost / data-center exit

VMware MADAR-LEGACY-01
Ubuntu + Flask + PostgreSQL + files
              |
              | clean VMDK export -> S3 -> EC2 ImportImage
              v
Amazon Machine Image (AMI)
              |
              v
EC2 temporary migrated server
Ubuntu + Flask + PostgreSQL + files

Stage 2 — Database replatform

EC2 PostgreSQL
      |
      | AWS DMS Full Load + CDC
      v
Amazon RDS for PostgreSQL

Stage 3 — File replatform

EC2 operational CSV/reports
      |
      | controlled validated copy
      v
Amazon S3
```

## Component decisions

| Source component | Disposition | AWS target | Mechanism | Reason |
|---|---|---|---|---|
| Ubuntu + Flask runtime | Rehost first | EC2 | EC2 VM Import/Export | Preserves the actual VMware machine image while avoiding the MGN managed-conversion blocker |
| PostgreSQL 16 | Replatform after EC2 acceptance | RDS PostgreSQL | DMS Full Load + CDC | Separates high-value state from host lifecycle and demonstrates managed-database migration |
| Operational CSV/reports | Replatform | S3 | Validated copy + SHA-256 | Dataset is small; DataSync would be unnecessary overhead for this lab |
| Scheduled report job | Reconfigure | target DB/storage path | Retain behavior then point dependencies to AWS target | Avoids rewriting the workload during the rehost step |
| SSH administration | Modernize where practical | SSM Session Manager | AWS-native management path | Reduces long-term inbound administration exposure |

## Why VM Import/Export is now Stage 1

The objective is still a real rehost: move the existing VMware server image, not install a fresh Ubuntu instance and call it migrated.

```text
VMware disk
   -> clean stream-optimized VMDK
   -> private S3 staging
   -> VM Import/Export
   -> EBS-backed AMI
   -> EC2
```

The `vmimport` IAM service role is the permission boundary that lets `vmie.amazonaws.com` read the staged disk and perform the required image/snapshot operations. The operator's `iam:PassRole` authorization is independently checked before import.

## MGN: evaluated, proven, then rejected for this account plan

MGN was not abandoned because replication failed. It successfully demonstrated agent-based block replication:

- 25/25 GiB replicated,
- initial replication completed,
- healthy / ready-for-testing state,
- snapshot creation completed during test launch.

The failure occurred in a different layer: MGN's managed conversion server. CloudTrail showed `m5.large`; AWS Transform confirmed that this instance type is not customer-configurable. Repeating replication or changing the final target instance type would therefore not address the root cause.

Engineering decision: preserve the evidence, clean the temporary MGN resources, and change the rehost mechanism instead of changing the account plan.

## Why DMS still comes after rehost

The original source PostgreSQL is local to the VMware host (`127.0.0.1:5432`) and the VMware NAT address is not a directly routable AWS source. Once the full server is on EC2, DMS can use the EC2-hosted PostgreSQL source inside the AWS networking design.

Mental model:

```text
VM Import/Export = move the house into AWS
DMS              = move the database out of the house into managed RDS
CDC              = keep database changes synchronized during transition
```

## Alternatives considered

### Upgrade the AWS account and continue MGN

Technically viable but rejected for this lab. The project does not change billing/account risk simply to bypass a managed service constraint.

### Change MGN target to another Free-Plan instance

Rejected as irrelevant to the observed failure. The target was not the resource that failed.

### Fresh Ubuntu EC2 rebuild

Rejected as the primary rehost proof. It would demonstrate rebuild/redeploy, not migration of the existing VMware image.

### Direct DMS from AWS to VMware PostgreSQL

Rejected because the current source is loopback-only behind VMware NAT. A secure connectivity design is possible, but unnecessary if the server first lands in EC2.

### Leave PostgreSQL permanently on EC2

Rejected as the final architecture. It preserves patching, backup and host-coupling responsibilities that the RDS replatform track is intended to remove.

### DataSync for the tiny file estate

Rejected as overengineering for the current data volume. It remains a valid service to evaluate for a large independent file estate.

## Cutover principle

The original VMware VM remains a rollback anchor until the imported EC2 workload is validated. No source is destroyed merely because an AMI exists or an EC2 instance reaches `running`.

Acceptance requires:

- boot/network/management validation,
- PostgreSQL service and data reconciliation,
- Flask read/write validation,
- operational-file validation,
- DMS/RDS acceptance when Stage 2 begins,
- explicit continue/abort decision,
- cleanup only after rollback is no longer required.

## Cost and risk principle

Migration tooling is evaluated end-to-end. A visible target instance being inexpensive/free is not sufficient if a managed workflow launches hidden non-eligible compute. Credits are treated as real money and temporary migration infrastructure is kept narrowly scoped.