# Phase 03 — Migration & Closeout Runbook

## Status

**Executed successfully and closed on 2026-08-20.**

This runbook records the actual Phase 03 path, including the MGN branch that was root-caused and abandoned, the successful VM Import/Export rehost, DMS Full Load + CDC, operational-file migration to S3, application cutover to RDS, dependency proof, and final cleanup.

## End-to-end mental model

```text
1. Protect and baseline source
2. Test MGN -> diagnose managed conversion blocker
3. Prepare VMware guest
4. Export clean VMDK
5. Private S3 -> VM Import/Export -> AMI
6. Launch and validate EC2
7. Prepare PostgreSQL logical replication
8. Private RDS + DMS
9. Full Load + CDC
10. Reconcile target data
11. Sync operational files to S3 + verify hashes
12. Point Flask to RDS
13. Stop local PostgreSQL and re-test app
14. Accept cutover
15. Delete temporary migration infrastructure
16. Retain only intentional recovery/data assets
```

## A — Source safety gate

Before migration the source VM was healthy, the deterministic database baseline was captured, PostgreSQL backup was readable, operational files/checksums were retained, guest boot/network/storage compatibility was checked, and the VMware source remained the rollback anchor.

## B — MGN branch

```text
Replication        25/25 GiB / Healthy / Ready for testing
Test snapshot      succeeded
Conversion         failed
Failing resource   service-managed MGN Conversion Server
Requested type     m5.large
Root cause         CloudTrail + AWS Transform confirmation
Decision           pivot; do not upgrade account solely for lab
```

## C — Successful VM Import/Export branch

The guest was prepared for ENA/NVMe, `eth0` DHCP, GRUB and LVM/ext4 compatibility. The installer ISO was removed before the final export.

```text
VMware -> streamOptimized VMDK -> private S3 -> ImportImage
       -> AMI ami-0cbd2e9ec0d6f9168
       -> snapshot snap-0920a020c47fb6447
       -> temporary t3.small EC2
```

Acceptance required EC2 checks, Linux boot, network, storage/LVM, SSH, PostgreSQL, deterministic data and Flask APIs.

## D — PostgreSQL to RDS

Source PostgreSQL was configured with `wal_level=logical`. Private Security Group paths were used instead of Internet-wide PostgreSQL ingress.

DMS troubleshooting sequence:

```text
DMS IAM prerequisite failure
 -> fix dms-vpc-role

Target endpoint no-encryption rejection
 -> require SSL

Target endpoint password rejection
 -> synchronize credentials

Final endpoint tests
 -> source successful
 -> target successful
```

Full Load result:

```text
customers         10
shipments         50
shipment_events   150
Tables loaded     3
Tables errored    0
```

CDC proof inserted customer #11 on the source and observed the same record on RDS without rerunning Full Load.

Final RDS state:

```text
customers         11
shipments         50
shipment_events   150
```

## E — Operational files to S3

Executed:

```bash
aws s3 sync \
  /home/madaradmin/madar-legacy-data/ \
  s3://madar-operational-files-197821101770/operational-data/
```

Count verification:

```text
source files  14
S3 objects    14
```

The S3 objects were then downloaded into an independent temporary directory and SHA-256 hashes were compared against the source.

Observed result:

```text
ALL FILE HASHES MATCH
```

This is stronger than trusting the `sync` exit status alone: it proves the retrieved S3 content matched the source bytes.

## F — Application database cutover

The Flask application originally used hard-coded local database settings. The configuration was changed to accept environment-driven database values:

```text
MADAR_DB_HOST
MADAR_DB_NAME
MADAR_DB_USER
MADAR_DB_PASSWORD
MADAR_DB_SSLMODE
```

The runtime was pointed to private RDS with SSL required and restarted.

Acceptance:

```text
/api/health   database=connected / environment=aws / status=ok
/api/summary  customers=11 / shipments=50 / events=150
```

## G — Dependency-removal proof

After the application was healthy against RDS, local PostgreSQL was deliberately stopped:

```bash
sudo systemctl stop postgresql
sudo systemctl is-active postgresql
```

Observed:

```text
inactive
```

The application was tested again:

```text
/api/health   PASS
/api/summary  PASS
```

This was the final technical proof that the application was no longer dependent on the local PostgreSQL service.

**Cutover decision: ACCEPT / CONTINUE.**

## H — Cleanup sequence

After all evidence was captured:

1. delete DMS replication task,
2. delete DMS endpoints,
3. delete DMS replication instance,
4. delete DMS subnet group,
5. delete RDS after final cutover proof,
6. delete RDS subnet group,
7. terminate temporary imported EC2,
8. delete orphaned EBS volume,
9. delete migration Security Groups after dependencies cleared,
10. delete VM-import VMDK and staging bucket,
11. delete temporary EC2 S3 instance profile/role/policy,
12. run a broad AWS resource audit.

Final audit showed no active lab EC2, RDS, DMS, standalone EBS, NAT Gateway, Elastic IP or load balancer.

## I — Assets intentionally retained

```text
AMI       ami-0cbd2e9ec0d6f9168
Snapshot  snap-0920a020c47fb6447
S3 bucket madar-operational-files-197821101770
```

The AMI/snapshot preserve a reusable machine recovery artifact. The operational S3 bucket preserves the migrated file dataset. These are intentional storage assets, not forgotten running infrastructure.

## J — Final acceptance rule

```text
EC2 running          != migration success
RDS available        != database migration success
DMS running          != CDC proof
S3 upload completed  != file-integrity proof

Success = workload behavior
        + independent reconciliation
        + controlled CDC change
        + round-trip file hash verification
        + application cutover proof
        + local dependency removal
        + intentional cleanup
```

Final result: **PHASE 03 COMPLETE.**