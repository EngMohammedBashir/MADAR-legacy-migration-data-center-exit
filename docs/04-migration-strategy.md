# Migration Strategy

## Decision summary

Discovery showed that the representative legacy VM contains several logical workload components with different state and operational characteristics. The project uses a **staged component-level migration strategy** rather than trying to connect AWS DMS directly to PostgreSQL behind the local VMware NAT network.

## Approved staged strategy

```text
Stage 1 — Data-center exit / Rehost

VMware MADAR-LEGACY-01
Ubuntu + Flask + PostgreSQL + files
              |
              | AWS MGN
              v
AWS EC2 temporary migrated server
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

This sequencing removes the need for AWS DMS to reach the private VMware address `192.168.14.128` directly. MGN first brings the representative server into AWS. DMS then works from the temporary PostgreSQL source on EC2 to the managed RDS target inside the AWS network design.

## Component decisions

| Source component | Disposition | AWS target | Migration mechanism / approach | Reason |
|---|---|---|---|---|
| Ubuntu + Flask application | Rehost | Amazon EC2 | AWS Application Migration Service (MGN) | Preserves the legacy runtime with minimal application change and establishes the first AWS landing point |
| PostgreSQL 16 | Replatform after rehost | Amazon RDS for PostgreSQL | AWS DMS Full Load + CDC from migrated EC2 PostgreSQL | Moves state to a managed database after the server is reachable inside AWS |
| Small operational CSV/files | Replatform | Amazon S3 | Controlled copy with checksum validation | Dataset is tiny; a dedicated transfer service would add unnecessary complexity |
| Scheduled report job | Modest replatform | Initially retained with migrated application, then pointed at target DB/storage | Reconfigure DB endpoint/output destination | Preserves behavior while dependencies move |
| SSH administration | Modernize operations | AWS Systems Manager Session Manager where practical | AWS-native management path | Reduces reliance on inbound SSH |

## Why MGN comes before DMS

The source PostgreSQL currently listens on loopback inside a VMware NAT network. Direct AWS DMS access would require an additional secure connectivity design such as private connectivity or a temporary tunnel. For this representative lab, that infrastructure would add cost and troubleshooting without strengthening the migration hypothesis.

MGN solves the first problem: move the server/runtime into AWS using source-initiated replication. Once PostgreSQL is on EC2, DMS can solve the second problem: replatform the database into RDS and keep changes synchronized with CDC.

```text
MGN = move the house into AWS
DMS = move the database out of that house into managed RDS
CDC = keep new database changes synchronized during transition
```

## Why MGN and DMS both remain necessary

MGN does not turn PostgreSQL into RDS. It rehosts the source machine. DMS does not migrate the Flask/Ubuntu server. It migrates and synchronizes database data. The staged design deliberately uses each service for the problem it is designed to solve.

## File-transfer decision and DataSync alternative

The representative MADAR file estate is only a small collection of CSV exports/reports. AWS DataSync was evaluated but rejected for this lab because deploying a dedicated transfer workflow for a few small files would be overengineering.

For a real independent file estate measured in large GB/TB/PB ranges, AWS DataSync would be a strong candidate for online transfer to S3/EFS/FSx. Very large offline-transfer requirements would trigger a separate evaluation of the currently available AWS bulk/offline data-transfer options. The project does not claim that MGN is the preferred bulk-file migration service.

## Alternatives rejected

### Direct DMS from AWS to VMware PostgreSQL

Rejected for this lab because the source is behind VMware NAT and PostgreSQL is loopback-only. Secure connectivity could be built, but it is unnecessary once the server is staged into AWS with MGN.

### Rehost the entire VM and leave PostgreSQL permanently on EC2

Rejected as the final target because it preserves database administration, patching, local-disk coupling and the single-host failure domain. EC2 PostgreSQL is only an intermediate migration state.

### AWS DataSync for the tiny representative file set

Rejected as unnecessary infrastructure for the current data volume. It remains the preferred class of AWS-native service to evaluate when the independent file estate is large.

### Refactor Flask immediately

Rejected for this phase. The objective is migration/data-center exit with controlled modernization, not an application rewrite.

### Containers/serverless during migration

Rejected because too many simultaneous architectural changes would make migration failures harder to attribute.

## Cutover principle

The original VMware source remains the rollback anchor through the initial MGN stage. After the EC2 source is validated and DMS Full Load + CDC is active, final cutover reconciles database state, representative records, operational files, application read/write behavior and scheduled processing. The source is not destroyed before acceptance.

## Implementation gate

Before creating paid migration resources:

1. approved staged MGN -> EC2 -> DMS -> RDS sequence,
2. VPC/subnet/security-group plan approved,
3. source outbound AWS connectivity verified,
4. PostgreSQL CDC baseline recorded and configuration backed up,
5. DMS Premigration Assessment planned after EC2 source is available,
6. small-file S3 transfer/checksum plan defined,
7. cost, evidence, rollback and cleanup plans defined.
