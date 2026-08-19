# Interview Guide — MADAR Legacy Migration & Data Center Exit

## 30-second recruiter version

> I built a hands-on migration lab that moved a legacy Ubuntu/PostgreSQL workload from VMware toward AWS. I started with AWS MGN and successfully completed block replication, but the test launch failed because MGN's service-managed conversion server required an `m5.large`, which the account's Free Plan blocked. I traced that with CloudTrail, confirmed the limitation with AWS Transform, cleaned the failed path, and pivoted to EC2 VM Import/Export. I then prepared the Linux guest for EC2 boot/network/storage compatibility, exported a clean stream-optimized VMDK, staged it privately in S3 with a dedicated `vmimport` IAM role, and began the import path to AMI/EC2. The next phase replatforms PostgreSQL to RDS using DMS Full Load + CDC.

## 90-second technical version

> The source is a VMware VM running Ubuntu 24.04, Flask and PostgreSQL 16. I first discovered the workload rather than designing AWS resources blindly: compute, LVM/ext4 storage, ports, services, cron, files, database state and dependencies. I created deterministic data and independent database/file recovery artifacts.
>
> For Stage 1 I evaluated AWS MGN. The agent replicated all 25 GiB and reached Healthy/Ready for testing. Test launch failed during conversion. The target launch template was `t3.small`, so I used CloudTrail to inspect the actual `RunInstances` request and found that MGN itself was launching an `m5.large` conversion server under `AWSApplicationMigrationConversionServerRole`. AWS Transform confirmed that conversion server is service-managed and cannot be resized. Because the lab account is intentionally Free Plan, I did not upgrade or retry the wrong layer.
>
> I pivoted to EC2 VM Import/Export. Before export I verified GRUB/BIOS, GPT/LVM, ENA/NVMe drivers and initramfs, changed the VMware-specific `ens33` interface dependency to `eth0` with DHCP, reboot-tested networking, enabled SSH/PostgreSQL at boot, and created a final logical PostgreSQL dump. I exported a clean stream-optimized VMDK, created a private S3 staging bucket, a least-privilege `vmimport` service role trusted by `vmie.amazonaws.com`, verified `iam:PassRole`, and uploaded the VMDK. The import task should produce an AMI, which is then validated on EC2 before DMS moves PostgreSQL into RDS.

## Architecture mental map

```text
VMware
  |
  | clean VMDK export
  v
S3 staging
  |
  | VM Import/Export + vmimport IAM role
  v
AMI
  |
  v
EC2 intermediate landing
  |
  +--> DMS Full Load + CDC --> RDS PostgreSQL
  |
  +--> validated files ------> S3
```

## The most important story: the MGN failure

Do not hide it. Explain it as layered troubleshooting.

```text
Symptom
MGN test launch failed

Initial assumption to challenge
"Maybe t3.small is wrong"

Evidence
CloudTrail RunInstances

Root cause
service-managed MGN Conversion Server requested m5.large

Why target setting did not help
Target EC2 and conversion server are different resources

Decision
Do not upgrade account for lab; pivot rehost mechanism

Result
MGN evidence preserved, resources cleaned, VM Import/Export path started
```

A strong interview sentence:

> The important part was realizing that the target instance type I controlled was not the instance type that failed. CloudTrail let me identify the actual managed conversion server and avoid repeatedly changing the wrong configuration.

## Likely questions and strong answers

### 1. Why did you choose rehost first instead of refactoring the application?

Rehost reduces simultaneous change during data-center exit. It gives a known intermediate state in AWS. Database modernization can then happen separately through RDS/DMS, so a failure can be attributed to one migration layer rather than an application rewrite plus infrastructure migration at the same time.

### 2. Why not leave PostgreSQL permanently on the imported EC2 instance?

That would preserve host-level patching, backup, failure-domain and database administration responsibilities. EC2 PostgreSQL is only the intermediate source; RDS is the final database direction.

### 3. Why did MGN replication succeed but test launch fail?

They are different phases with different infrastructure. Replication used MGN staging resources successfully. Test launch introduced a service-managed conversion server. CloudTrail showed that server requested `m5.large`, which the Free Plan rejected.

### 4. Why couldn't you just set the conversion server to `t3.small`?

MGN exposes the replication-server configuration and the final target launch template, but not the conversion-server instance type. AWS Transform confirmed it is service-managed and not customer-configurable.

### 5. Why VM Import/Export instead of rebuilding Ubuntu manually?

The migration objective is to prove movement of the existing VMware machine image. A fresh EC2 build would be a rebuild/redeploy project rather than a full-machine rehost.

### 6. What is the role of S3 in VM Import/Export?

S3 is the staging warehouse. The exported VMDK is uploaded there; VM Import/Export reads that object and converts it into AWS image/snapshot resources.

### 7. What is the `vmimport` IAM role?

It is a service role that `vmie.amazonaws.com` assumes. It gives VM Import/Export narrowly scoped access to read the S3 image and perform the required EC2 snapshot/image operations. The role is the service's permission badge, not the migration service itself.

### 8. What is `iam:PassRole` and why did you check it?

The operator may create a role but still be forbidden from telling an AWS service to use it. `iam:PassRole` controls that handoff. I simulated the operator's policy before the expensive/slow import step and got `allowed`.

### 9. Why did you use Windows PowerShell for the upload but CloudShell for IAM/S3 setup?

The VMDK exists on the local Windows filesystem. CloudShell runs inside AWS and cannot see `C:\Users\...`. Local AWS CLI can read the file and upload it to S3; once it is in S3, CloudShell can manage AWS-side resources and the import task.

### 10. Why did you change `ens33` to `eth0`?

The guest configuration was tied to a VMware-specific predictable NIC name. I wanted the imported guest to rely on a simpler DHCP interface configuration rather than a name coupled to the original virtual hardware. I changed GRUB/Netplan together and reboot-tested before export.

### 11. Why check ENA and NVMe?

A workload can be application-healthy yet fail after hypervisor migration because the guest cannot access EC2 networking or storage. ENA is relevant to EC2 network adapters and NVMe to Nitro-era storage presentation. I also checked initramfs so those drivers are available during early boot.

### 12. Why create a PostgreSQL dump if the whole disk is migrating?

The disk migration carries PostgreSQL files, but the logical dump is an independent recovery path. If the VM boots but the database has an application-level integrity problem, I have a PostgreSQL-native recovery artifact instead of relying only on the machine image.

### 13. How do you know the database migration is correct?

I use a deterministic baseline and reconcile row counts, representative records and application behavior. Later, DMS CDC is proven by performing a controlled shipment update plus event insert on the source and verifying the same change appears on RDS.

### 14. Why didn't you make the S3 import bucket public?

There is no need. The service role can read a private bucket. VM images can contain the whole operating system and application data, so public access would be an unnecessary security risk.

### 15. Why not use Terraform for every step?

Terraform is used where desired-state infrastructure benefits from reproducibility. VM Import/Export is an asynchronous conversion workflow driven by an external multi-GB artifact. CLI is clearer for the import task; Terraform can manage the stable target network/compute/database infrastructure after the AMI exists.

### 16. What would make you roll back?

Unexplained database differences, failed critical application paths, unsafe network exposure, inability to manage the host, boot/filesystem issues, or unacceptable DMS replication state. The VMware source remains the rollback anchor until explicit target acceptance.

### 17. What did you learn that an SAA exam would not teach deeply?

The certification teaches service selection and architecture principles. The lab forced me to work through guest OS boot/network/storage compatibility, IAM service-role boundaries, CloudTrail root-cause analysis, asynchronous migration tasks, local-vs-CloudShell execution context and real cleanup/cost constraints.

## Commands worth recognizing — not memorizing

```text
aws sts get-caller-identity
  -> who am I in AWS?

aws s3 cp
  -> move the local VMDK into S3

aws iam create-role / put-role-policy
  -> create the service permission boundary

aws iam simulate-principal-policy
  -> check authorization before execution

aws ec2 import-image
  -> start VMDK-to-AMI conversion

aws ec2 describe-import-image-tasks
  -> monitor asynchronous conversion

modinfo / lsinitramfs
  -> inspect guest driver readiness

lsblk / pvs / vgs / lvs
  -> understand the source disk/LVM layout

systemctl
  -> verify boot-time service state

pg_dump / pg_restore -l
  -> create and validate an independent DB recovery point
```

## What not to say

Avoid weak descriptions such as:

> I used AWS CLI to migrate a VM.

or:

> I copied a server to EC2.

Those hide the engineering work.

Prefer:

> I treated the migration as a sequence of independently validated layers: source discovery, recovery baseline, machine-image compatibility, secure staging, IAM service delegation, asynchronous image conversion, target validation, then database replatforming.

## HR-friendly project value

This project demonstrates more than knowledge of AWS service names. It shows:

- ownership of an ambiguous technical problem,
- evidence-based troubleshooting,
- willingness to change a design when constraints invalidate it,
- cost/risk awareness,
- security discipline,
- documentation of decisions and failures,
- ability to explain technical depth at both executive and engineering levels.

## Final one-line CV bullet candidate

> Engineered a VMware-to-AWS legacy migration lab for Ubuntu/PostgreSQL, troubleshooting an MGN managed-conversion blocker via CloudTrail and pivoting to secure S3/VM Import/Export rehosting with IAM service roles, EC2 compatibility validation, rollback controls, and a staged DMS-to-RDS modernization plan.
