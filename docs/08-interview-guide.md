# Interview Guide — MADAR Legacy Migration & Data Center Exit

## 30-second recruiter version

> I built an end-to-end legacy migration lab that moved an Ubuntu/PostgreSQL workload from VMware to AWS. I first tested AWS MGN and completed block replication, but the managed conversion stage failed because it required an `m5.large` that the lab account plan rejected. I traced the exact failure through CloudTrail, confirmed the managed-service limitation, and pivoted to EC2 VM Import/Export. I successfully converted the VMware VMDK into an AMI, launched and validated the workload on EC2, then replatformed PostgreSQL to private Amazon RDS using AWS DMS Full Load + CDC. The initial `10/50/150` dataset reconciled exactly, and I proved CDC by inserting a new source record and watching it appear automatically in RDS.

## 90-second technical version

> The source was a VMware VM running Ubuntu 24.04.4, Flask and PostgreSQL 16.14. Before migration I inventoried compute, BIOS/GRUB, GPT/LVM storage, network dependencies, services, database state, cron jobs and recovery artifacts. I also created an independent PostgreSQL logical backup.
>
> My first rehost path was AWS MGN. Its agent replicated all 25 GiB and reached Healthy/Ready for testing, but test launch failed in a separate managed conversion phase. CloudTrail showed that MGN was launching an `m5.large` conversion server under the service role, while the customer-controlled target remained `t3.small`. I confirmed the conversion node could not be resized, so I stopped changing the wrong layer and pivoted to VM Import/Export.
>
> I prepared the guest for EC2 by validating ENA/NVMe support, GRUB, LVM and initramfs, replaced the VMware-specific `ens33` dependency with `eth0` plus DHCP, exported a clean stream-optimized VMDK, uploaded it to private S3, created the `vmimport` IAM service role, verified `iam:PassRole`, and imported the disk. The task completed with an AMI and snapshot. The EC2 instance passed boot, networking, NVMe/LVM, SSH, PostgreSQL, database-count and Flask API validation.
>
> For the database replatform I enabled PostgreSQL logical WAL, built SG-to-SG TCP/5432 paths, created private RDS PostgreSQL 16.14, repaired the required `dms-vpc-role`, provisioned a private DMS replication instance, tested source and target endpoints, and troubleshot target TLS and authentication separately. The `full-load-and-cdc` task loaded all three tables with zero errors. I then inserted `MADAR CDC TEST CUSTOMER` on the EC2 source and verified the same row appeared on RDS without rerunning Full Load. Final RDS counts were `11 / 50 / 150`.

## Architecture mental map

```text
VMware
  |
  | clean VMDK
  v
private S3
  |
  | VM Import/Export
  v
AMI -> EC2
       |
       | PostgreSQL logical WAL
       v
      DMS
       |
       | Full Load + CDC
       v
private RDS PostgreSQL
```

## Three troubleshooting stories worth telling

### 1. MGN conversion-server blocker

```text
Symptom       MGN test launch failed
Evidence      CloudTrail RunInstances
Root cause    managed conversion server requested m5.large
Wrong fix     repeatedly changing target t3.small
Decision      pivot to VM Import/Export
```

Strong sentence:

> I separated the customer-controlled target from the service-managed conversion node and used CloudTrail to prove which resource actually failed.

### 2. DMS IAM prerequisite

```text
Symptom       CreateReplicationSubnetGroup AccessDeniedFault
Message       dms-vpc-role not configured properly
Root cause    DMS control-plane IAM prerequisite
Fix           trust dms.amazonaws.com + AmazonDMSVPCManagementRole
Result        same subnet-group operation succeeded
```

Strong sentence:

> I treated it as an IAM control-plane failure, not a routing problem, so I did not start changing subnets or opening security groups.

### 3. DMS target connection: TLS then password

```text
Failure 1  no encryption
Meaning    DMS reached PostgreSQL; network path worked
Fix        ssl-mode=require

Failure 2  password authentication failed
Meaning    network + TLS now worked; credentials were wrong
Fix        synchronize endpoint/RDS credentials

Final      successful
```

Strong sentence:

> Each error narrowed the failing layer. I did not respond to an authentication problem by weakening network controls.

## Likely questions and strong answers

### Why rehost before database modernization?

It reduces simultaneous change. First I proved the same machine could run on EC2. Then I changed the database operating model separately. That makes failures attributable to a specific layer and keeps rollback clearer.

### Why VM Import/Export instead of rebuilding Ubuntu?

The rehost objective was to move the existing VMware machine image. A clean EC2 rebuild would demonstrate redeployment, not machine-image migration.

### Why S3?

S3 is the private staging warehouse for the exported VMDK. VM Import/Export reads the object and produces AWS image/snapshot resources.

### What is `vmimport`?

A service role trusted by `vmie.amazonaws.com`. It is the permission badge that allows the import service to read the S3 artifact and perform required EC2 image/snapshot actions.

### Why check `iam:PassRole`?

Because creating a role does not automatically mean the operator is authorized to delegate it to an AWS service. I validated the handoff before executing the long import workflow.

### Why ENA and NVMe?

An application can be healthy while the migrated guest fails to access AWS virtual networking or storage. I verified both the installed modules and early-boot availability before exporting.

### Why change `ens33`?

The network configuration was coupled to VMware virtual hardware. I switched to `eth0` with DHCP and reboot-tested it before export so the guest could accept a new VPC identity.

### Why take `pg_dump` if the whole disk moves?

The disk image is the primary rehost mechanism. The PostgreSQL logical dump is an independent application-level recovery path if the machine boots but database-level recovery is needed.

### What does `wal_level=logical` do for DMS?

It exposes logical row-change information through PostgreSQL WAL so DMS can continue replicating INSERT/UPDATE/DELETE activity after the initial load.

### Full Load vs CDC?

```text
Full Load = copy the existing database state
CDC       = propagate changes that occur after/while the migration is running
```

In this lab Full Load copied `10 / 50 / 150`; CDC then propagated a new customer, changing the target to `11 / 50 / 150`.

### How did you prove CDC rather than assume it?

I inserted a uniquely named customer on the EC2 source after Full Load. Without restarting the task, I queried RDS and found the same row with the target count incremented to 11.

### Why is RDS private?

A database does not need Internet exposure for this design. DMS and EC2 reach it through VPC networking and SG-to-SG rules on TCP/5432.

### What would be different in production?

The lab intentionally uses small/single-AZ resources and temporary operational choices. Production would require HA sizing, backups/retention, secret management, monitoring, defined maintenance/patch policy, formal cutover windows, measured replication lag, stronger application runtime management and tested DR/RTO/RPO controls.

### Why not Terraform every migration action?

Terraform is ideal for stable desired-state infrastructure. An import task and a one-time DMS migration are asynchronous operational workflows around external artifacts/data streams. I used CLI where it made the execution state explicit, while the repository documents how stable target infrastructure can later be codified.

## Commands worth recognizing — not memorizing

```text
aws sts get-caller-identity
  -> verify operator identity

aws s3 cp / s3api head-object
  -> stage and verify the VMDK

aws iam simulate-principal-policy
  -> verify PassRole authorization

aws ec2 import-image
aws ec2 describe-import-image-tasks
  -> create/monitor VMDK -> AMI conversion

modinfo / lsinitramfs / lsblk / pvs / vgs / lvs
  -> prove guest driver/boot/storage readiness

SHOW wal_level / max_replication_slots / max_wal_senders
  -> prove PostgreSQL CDC readiness

aws dms test-connection
aws dms describe-connections
  -> validate source/target paths

aws dms create-replication-task
aws dms start-replication-task
aws dms describe-table-statistics
  -> execute and validate Full Load + CDC

psql COUNT(*) + controlled INSERT
  -> independently reconcile target and prove CDC
```

## What not to say

Weak:

> I moved a VM to EC2 and used DMS.

Better:

> I migrated the workload as independently validated layers: source recovery, guest compatibility, secure image staging, IAM delegation, image conversion, EC2 workload acceptance, PostgreSQL logical-replication readiness, private DMS/RDS networking, Full Load reconciliation and a controlled CDC proof.

## HR-friendly project value

This project demonstrates:

- ownership of an ambiguous migration problem,
- evidence-based troubleshooting rather than random retries,
- Linux/VMware depth beyond clicking AWS services,
- security and least-exposure thinking,
- cost/account-constraint awareness,
- data-integrity validation,
- willingness to preserve and explain failures,
- ability to communicate one project at recruiter, architect and operator depth.

## CV bullet candidates

Concise:

> Migrated a legacy Ubuntu/PostgreSQL workload from VMware to AWS, pivoting from an MGN managed-conversion blocker to EC2 VM Import/Export, validating the rehost end-to-end, and replatforming PostgreSQL to private Amazon RDS using AWS DMS Full Load + CDC with zero table-load errors and controlled change-replication proof.

More technical:

> Engineered a VMware-to-AWS migration for Ubuntu 24.04/PostgreSQL 16.14: diagnosed an AWS MGN conversion-server blocker via CloudTrail, imported a stream-optimized VMDK through private S3 into EC2, validated ENA/NVMe/LVM/network/application state, then executed DMS Full Load + CDC to private RDS PostgreSQL with SG-to-SG controls, TLS, `3/3` tables loaded, `0` errors, and verified post-load CDC.