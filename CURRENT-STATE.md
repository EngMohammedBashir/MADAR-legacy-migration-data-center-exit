# Phase 03 — Final State

**Status: COMPLETE / ACCEPTED / CLEANED UP**  
**Region: us-east-1**  
**Closeout date: 2026-08-20**

## Executive state

Phase 03 completed the full migration path and its acceptance evidence:

```text
Stage 1  VMware -> EC2 VM rehost                    COMPLETE
Stage 2  EC2 PostgreSQL -> RDS via DMS              COMPLETE
Stage 3  operational files -> Amazon S3             COMPLETE
Cutover  Flask database path -> Amazon RDS           COMPLETE
Proof    local PostgreSQL stopped; app stayed healthy PASS
Cleanup  temporary migration infrastructure          COMPLETE
```

## Final migration chain

```text
VMware MADAR-LEGACY-01
        |
        | VM Import/Export
        v
Imported AMI / temporary EC2 landing workload
        |
        | AWS DMS Full Load + CDC
        v
Amazon RDS PostgreSQL
        |
        | application configuration cutover
        v
Flask application using RDS

Operational files
        |
        | aws s3 sync + count + SHA-256 verification
        v
Amazon S3
```

## Stage 1 — VM rehost acceptance

The VMware guest was prepared for AWS virtual hardware, exported as a clean streamOptimized VMDK, imported to an EBS-backed AMI, and launched on EC2.

Accepted checks included Linux boot, `eth0`/DHCP, NVMe-presented storage, LVM/ext4, SSH, PostgreSQL, deterministic business data, and Flask health/API behavior.

Key retained recovery artifact:

```text
AMI       ami-0cbd2e9ec0d6f9168
Snapshot  snap-0920a020c47fb6447
```

## Stage 2 — Database replatform acceptance

AWS DMS migrated PostgreSQL 16.14 from the imported EC2 workload to private Amazon RDS PostgreSQL 16.14.

```text
Full Load baseline
customers         10
shipments         50
shipment_events   150
Tables errored    0

CDC proof
source customer #11 -> RDS customer #11

Final RDS reconciliation
customers         11
shipments         50
shipment_events   150
```

The source and target endpoint troubleshooting is intentionally retained in the execution documentation: TLS and credential failures were isolated without weakening the network controls.

## Stage 3 — Operational files to S3

The operational dataset was synchronized to:

```text
s3://madar-operational-files-197821101770/operational-data/
```

Validation was independent of the upload command:

```text
Source files       14
S3 objects         14
Downloaded copy    14
SHA-256 comparison ALL FILE HASHES MATCH
```

This proves both object-count reconciliation and content integrity after round-trip download.

## Application cutover — accepted

The Flask database configuration was changed from hard-coded localhost settings to environment-driven configuration supporting the RDS host, database, user, password and SSL mode.

Final runtime values pointed the application to private RDS with SSL required.

Observed application acceptance:

```json
{"database":"connected","environment":"aws","host":"MADAR-LEGACY-EC2","service":"madar-legacy-app","status":"ok"}
```

```json
{"customers":11,"delivered":10,"events":150,"in_transit":10,"shipments":50}
```

The strongest cutover proof was then executed: local PostgreSQL was stopped.

```text
local postgresql.service  inactive
Flask /api/health         database=connected / status=ok
Flask /api/summary        11 customers / 50 shipments / 150 events
```

Therefore the application could not have been serving these database-backed responses from the stopped local PostgreSQL instance. The RDS cutover was accepted.

## Final cleanup

Temporary migration resources were intentionally removed after acceptance:

```text
EC2 instance                     terminated
attached temporary EBS volume    deleted
RDS target                        deleted after cutover evidence
DMS task                          deleted
DMS endpoints                     deleted
DMS replication instance          deleted
DMS subnet group                  deleted
RDS subnet group                  deleted
migration security groups         deleted
VM-import staging VMDK/bucket     deleted
temporary EC2 S3 role/profile     deleted
NAT gateways                      none
Elastic IPs                       none
Load balancers                    none
```

A final account audit showed no active EC2, RDS, DMS, standalone EBS, NAT Gateway, Elastic IP or load-balancer resources from the lab.

## Intentionally retained assets

```text
AMI       ami-0cbd2e9ec0d6f9168
Snapshot  snap-0920a020c47fb6447  (25 GiB recovery backing artifact)
S3        madar-operational-files-197821101770
```

These are retained deliberately as reusable recovery/data artifacts rather than forgotten compute infrastructure. The snapshot and S3 storage can still incur storage charges; no continuously running compute remains from the Phase 03 lab.

## Final evidence

Curated closeout screenshots:

- [`evidence/screenshots/README.md`](evidence/screenshots/README.md)
- [`evidence/before-cutover-on-premises-dashboard.png`](evidence/before-cutover-on-premises-dashboard.png)
- [`evidence/browser-pre-cutover-validation.png`](evidence/browser-pre-cutover-validation.png)
- [`evidence/after-cutover-aws-dashboard.png`](evidence/after-cutover-aws-dashboard.png)
- [`evidence/local-postgres-disabled-rds-cutover-proof.png`](evidence/local-postgres-disabled-rds-cutover-proof.png)
- [`evidence/final-aws-cleanup-audit.png`](evidence/final-aws-cleanup-audit.png)

## Final decision

**CONTINUE / ACCEPT.**

The migration met the technical acceptance criteria: rehosted workload validation, independent database reconciliation, CDC proof, file-integrity proof, application cutover validation, dependency-removal proof, and intentional resource cleanup.

Phase 03 is closed.