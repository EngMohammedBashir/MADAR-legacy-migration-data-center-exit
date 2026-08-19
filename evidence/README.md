# Phase 03 Evidence Index

Evidence exists to prove engineering claims. Screenshots are not collected as decoration, and a planned checkpoint is never described as completed before it is actually observed.

## Security rule

Before publishing evidence:

- never expose passwords, private keys, session tokens or shell history containing secrets,
- crop unrelated desktop content,
- preserve errors when they explain an engineering decision,
- keep VM images/database dumps outside Git,
- prefer a focused screenshot that proves one fact clearly.

---

# 1. Source workload evidence

The source-lab screenshots prove that the VMware workload existed and had deterministic state before migration.

Important files:

```text
madar-legacy-vm-system-baseline.png
madar-legacy-vm-network-ssh.png
madar-lvm-storage-expanded.png
madar-base-os-patched.png
madar-runtime-postgresql-installed.png
madar-postgresql-database-role-created.png
madar-postgresql-schema-created.png
madar-deterministic-dataset-baseline.png
madar-application-dashboard.png
madar-application-write-path-verified.png
madar-cron-background-job-verified.png
madar-source-files-sha256-baselin.png
madar-pre-migration-db-backup-verified-v2.png
madar-pre-migration-files-backup-verified.png
madar-final-pre-migration-snapshot.png
```

### Representative application baseline

![MADAR application dashboard](madar-application-dashboard.png)

### Deterministic migration baseline

![Deterministic dataset](madar-deterministic-dataset-baseline.png)

### Pre-migration database recovery point

![Pre-migration DB backup](madar-pre-migration-db-backup-verified-v2.png)

---

# 2. AWS MGN experiment evidence

The MGN screenshots are retained because they prove the first strategy was actually tested rather than invented after the fact.

```text
mgn-source-server-discovery-details.png
mgn-initial-replication-initiating.png
mgn-initial-sync-100-percent-finalizing-snapshot.png
mgn-ready-for-testing-healthy-replication.png
mgn-launch-template-t3-small-created.png
mgn-launch-template-t3-small-default.png
```

The key visual checkpoint is:

![MGN Healthy / Ready for testing](mgn-ready-for-testing-healthy-replication.png)

These images support the documented MGN story: source discovery and block replication succeeded, while test conversion later failed in a different service-managed compute layer. CloudTrail/root-cause text is documented in the ADR and interview guide.

---

# 3. VM Import/Export evidence

The final rehost path was EC2 VM Import/Export.

Important files:

```text
vmdk-in-s3.png
vmimport-role-permissions.png
vm-import-converting.png
vm-import-updating-43-percent.png
vm-import-booting-62-percent.png
vm-import-completed-ami-created.png
imported-ami-available.png
ec2-imported-vm-running.png
ec2-status-checks-passed.png
ssh-success-migrated-ubuntu.png
post-migration-workload-validation.png
rehost-database-validation-pas.png
flask-running-on-migrated-ec2.png
migrated-application-api-validation-pass.png
```

### VMDK staged in private S3

![VMDK in S3](vmdk-in-s3.png)

### Import task progress

![VM Import converting](vm-import-converting.png)

![VM Import booting](vm-import-booting-62-percent.png)

### Import completed and AMI created

![VM Import complete](vm-import-completed-ami-created.png)

### Imported AMI available

![AMI available](imported-ami-available.png)

### Imported EC2 instance healthy

![EC2 status checks](ec2-status-checks-passed.png)

### Workload validation after hypervisor migration

![Post-migration workload validation](post-migration-workload-validation.png)

### Flask/API validation

![Migrated API validation](migrated-application-api-validation-pass.png)

This group proves more than `EC2 running`: it captures Linux boot, VPC DHCP, NVMe/LVM survival, PostgreSQL 16.14, deterministic data reconciliation and Flask application health.

---

# 4. PostgreSQL CDC preparation

File:

```text
postgresql-cdc-ready.png
```

Observed state:

```text
wal_level              logical
max_replication_slots  10
max_wal_senders        10
```

![PostgreSQL CDC ready](postgresql-cdc-ready.png)

---

# 5. RDS / DMS evidence

The actual screenshot filenames currently stored in this directory are intentionally used below; README links should point to these exact paths.

## RDS target available

```text
ds-postgresql-target-available.png
```

> The filename was uploaded as `ds-postgresql-target-available.png`; the evidence itself represents the RDS PostgreSQL target.

![RDS PostgreSQL target available](ds-postgresql-target-available.png)

## DMS replication instance available

```text
dms-replication-instance-available.png
```

Captured facts:

```text
Class       dms.t3.small
Private IP  172.31.13.46
Status      available
```

![DMS replication instance](dms-replication-instance-available.png)

## Source endpoint test successful

```text
source-endpoint-connection-success.png
```

![Source endpoint success](source-endpoint-connection-success.png)

## Target endpoint test successful

```text
target-endpoint-connection-success.png
```

![Target endpoint success](target-endpoint-connection-success.png)

The successful target screenshot follows two useful troubleshooting states documented in `docs/09-dms-rds-execution-guide.md`: first RDS rejected an unencrypted connection, then it rejected a credential mismatch. The final endpoint used SSL and a synchronized credential.

## Full Load completed

```text
dms-full-load-completed.png
```

Expected/observed task facts:

```text
FullLoadProgress  100
TablesLoaded      3
TablesErrored     0
customers         10 rows
shipments         50 rows
shipment_events   150 rows
```

![DMS Full Load](dms-full-load-completed.png)

## CDC controlled-change proof

```text
cdc-replication-proof.png
```

The controlled change was a new source customer after Full Load:

```text
customer_id   11
company_name  MADAR CDC TEST CUSTOMER
region        Riyadh
```

The same record appeared on RDS without rerunning Full Load.

![CDC replication proof](cdc-replication-proof.png)

## Final RDS reconciliation

```text
final-data-reconciliation.png
```

Final target counts:

```text
customers        11
shipments        50
shipment_events  150
```

![Final data reconciliation](final-data-reconciliation.png)

---

# 6. Curated reviewer path

A reviewer does not need to open every screenshot. The shortest evidence story is:

```text
1. madar-application-dashboard.png
   -> legacy business workload exists

2. madar-deterministic-dataset-baseline.png
   -> known pre-migration data baseline

3. mgn-ready-for-testing-healthy-replication.png
   -> first MGN strategy genuinely progressed

4. vmdk-in-s3.png
   -> clean fallback artifact staged in AWS

5. vm-import-completed-ami-created.png
   -> VM Import/Export completed

6. ec2-status-checks-passed.png
   -> imported machine passed EC2 infrastructure checks

7. migrated-application-api-validation-pass.png
   -> workload itself passed after rehost

8. postgresql-cdc-ready.png
   -> source prepared for logical CDC

9. ds-postgresql-target-available.png
   -> private RDS target exists

10. dms-replication-instance-available.png
    -> migration compute ready

11. source-endpoint-connection-success.png
12. target-endpoint-connection-success.png
    -> both sides reachable by DMS

13. dms-full-load-completed.png
    -> initial 10/50/150 load completed with zero table errors

14. cdc-replication-proof.png
    -> new source change replicated automatically

15. final-data-reconciliation.png
    -> final RDS state reconciled
```

The top-level `README.md` embeds this curated path directly so the project can be understood visually without browsing the evidence folder first.

---

# 7. Evidence not yet complete

The two major compute/database migration stages are complete. Remaining evidence belongs to later closeout work:

```text
operational files -> S3 integrity validation
application cutover to RDS
final rollback/accept decision
cleanup / residual resource review
actual cost or AWS-credit delta
final RTO/RPO closeout
```
