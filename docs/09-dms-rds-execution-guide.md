# AWS DMS -> Amazon RDS PostgreSQL Execution Guide

## Purpose

This guide documents the **actual Stage 2 execution** used to replatform the migrated PostgreSQL workload from EC2 to Amazon RDS for PostgreSQL. It keeps the important commands, explains what each step accomplishes, and records the observed troubleshooting path instead of presenting an unrealistically perfect migration.

> Secrets are deliberately omitted. Passwords used during the lab must never be committed to Git.

## Mental model

```text
EC2 PostgreSQL 16.14
172.31.3.142:5432
        |
        | Source Endpoint
        v
AWS DMS replication instance
madar-dms-repl / dms.t3.small
        |
        | Full Load + CDC
        v
RDS PostgreSQL 16.14
madar-postgres-target
```

Think of DMS as a logistics company:

```text
Source endpoint  = address of the old warehouse
Replication node = transport truck
Target endpoint  = address of the new warehouse
Full Load        = move existing inventory
CDC              = keep forwarding new inventory changes
```

---

## 1. Prepare PostgreSQL for CDC

DMS CDC for PostgreSQL requires logical change information from WAL.

Check current settings:

```bash
sudo -u postgres psql -Atc "SHOW wal_level; SHOW max_replication_slots; SHOW max_wal_senders;"
```

Initial result:

```text
replica
10
10
```

Back up and enable logical WAL:

```bash
sudo cp /etc/postgresql/16/main/postgresql.conf \
  /etc/postgresql/16/main/postgresql.conf.pre-dms

sudo sed -i "s/^#*wal_level.*/wal_level = logical/" \
  /etc/postgresql/16/main/postgresql.conf

sudo systemctl restart postgresql
```

Validate:

```bash
sudo -u postgres psql -Atc "SHOW wal_level; SHOW max_replication_slots; SHOW max_wal_senders;"
```

Observed:

```text
logical
10
10
```

### Why this matters

`wal_level=logical` lets DMS understand row-level changes instead of seeing WAL only as physical replication data. Replication slots keep required WAL available long enough for a consumer, and WAL senders provide replication connections.

---

## 2. Allow VPC-local PostgreSQL connectivity

The source originally served local application traffic. DMS is a different node in the VPC, so PostgreSQL must listen beyond loopback.

```bash
sudo sed -i "s/^#*listen_addresses.*/listen_addresses = '*'/" \
  /etc/postgresql/16/main/postgresql.conf
```

Permit authenticated VPC traffic in `pg_hba.conf`:

```bash
echo "host    madar_legacy    all    172.31.0.0/16    scram-sha-256" | \
  sudo tee -a /etc/postgresql/16/main/pg_hba.conf

sudo systemctl restart postgresql
sudo ss -lntp | grep 5432
```

Observed listener:

```text
0.0.0.0:5432
[::]:5432
```

Important: `listen_addresses='*'` does **not** mean the database was opened to the Internet. AWS Security Groups still restrict who can reach TCP/5432.

---

## 3. Create a dedicated DMS source login

A dedicated migration principal separates application authentication from migration authentication.

```sql
CREATE USER dms_user WITH LOGIN PASSWORD '<REDACTED>';
ALTER USER dms_user WITH SUPERUSER;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dms_user;
GRANT USAGE ON SCHEMA public TO dms_user;
```

Connectivity was tested against the EC2 private address:

```bash
PGPASSWORD='<REDACTED>' psql \
  -h 172.31.3.142 \
  -U dms_user \
  -d madar_legacy \
  -c "SELECT current_user, current_database();"
```

Observed:

```text
dms_user | madar_legacy
```

---

## 4. Build SG-to-SG migration controls

Identifiers used in this lab:

```text
Source EC2 SG  sg-0589383abcc3ebbbc
DMS SG         sg-085569e2731850c8a
RDS SG         sg-093756a8cabaad407
```

Create the DMS and RDS groups:

```bash
VPC="vpc-015017581b8954e61"
SOURCE_SG="sg-0589383abcc3ebbbc"

DMS_SG=$(aws ec2 create-security-group \
  --region us-east-1 \
  --group-name madar-dms-sg \
  --description "DMS replication traffic for MADAR migration" \
  --vpc-id "$VPC" \
  --query GroupId --output text)

RDS_SG=$(aws ec2 create-security-group \
  --region us-east-1 \
  --group-name madar-rds-sg \
  --description "Private RDS PostgreSQL for MADAR migration" \
  --vpc-id "$VPC" \
  --query GroupId --output text)
```

Permit DMS to the source:

```bash
aws ec2 authorize-security-group-ingress \
  --region us-east-1 \
  --group-id "$SOURCE_SG" \
  --protocol tcp --port 5432 \
  --source-group "$DMS_SG"
```

Permit DMS to the target:

```bash
aws ec2 authorize-security-group-ingress \
  --region us-east-1 \
  --group-id "$RDS_SG" \
  --protocol tcp --port 5432 \
  --source-group "$DMS_SG"
```

Later, EC2-to-RDS access was also added for direct validation and eventual cutover testing:

```bash
aws ec2 authorize-security-group-ingress \
  --region us-east-1 \
  --group-id sg-093756a8cabaad407 \
  --protocol tcp --port 5432 \
  --source-group sg-0589383abcc3ebbbc
```

No `0.0.0.0/0 -> 5432` rule was used.

---

## 5. Create private RDS PostgreSQL

Create a DB subnet group spanning two AZs:

```bash
aws rds create-db-subnet-group \
  --region us-east-1 \
  --db-subnet-group-name madar-rds-subnets \
  --db-subnet-group-description "MADAR RDS migration subnet group" \
  --subnet-ids \
    subnet-04e63af31360b080a \
    subnet-0d70c1cf55218c14f
```

Create the target with the same PostgreSQL release used by the source:

```bash
read -s -p "RDS master password: " RDS_PASSWORD

a ws rds create-db-instance  # illustrative split below
```

Actual command structure:

```bash
aws rds create-db-instance \
  --region us-east-1 \
  --db-instance-identifier madar-postgres-target \
  --engine postgres \
  --engine-version 16.14 \
  --db-instance-class db.t3.micro \
  --allocated-storage 20 \
  --storage-type gp3 \
  --master-username postgres \
  --master-user-password "$RDS_PASSWORD" \
  --db-name madar_legacy \
  --vpc-security-group-ids "$RDS_SG" \
  --db-subnet-group-name madar-rds-subnets \
  --no-publicly-accessible \
  --no-multi-az \
  --backup-retention-period 0 \
  --no-deletion-protection
```

Observed target:

```text
Engine      PostgreSQL 16.14
Class       db.t3.micro
Public      false
Status      available
Endpoint    madar-postgres-target.cgx64cygc3mj.us-east-1.rds.amazonaws.com
```

Single-AZ and disabled backups were lab/cost decisions, not production recommendations.

---

## 6. Resolve the `dms-vpc-role` prerequisite

First attempt to create the DMS replication subnet group failed:

```text
AccessDeniedFault:
dms-vpc-role is not configured properly
```

The correct fix was IAM, not changing subnets.

Trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "dms.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

Create/update the role and attach the AWS-managed policy:

```bash
aws iam create-role \
  --role-name dms-vpc-role \
  --assume-role-policy-document file://dms-trust.json

aws iam attach-role-policy \
  --role-name dms-vpc-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole
```

This gives DMS the service permissions required to work with VPC networking resources.

---

## 7. Create DMS subnet group and replication instance

```bash
aws dms create-replication-subnet-group \
  --region us-east-1 \
  --replication-subnet-group-identifier madar-dms-subnets \
  --replication-subnet-group-description "MADAR DMS migration subnets" \
  --subnet-ids \
    subnet-04e63af31360b080a \
    subnet-0d70c1cf55218c14f
```

Observed status: `Complete` across `us-east-1a` and `us-east-1b`.

Replication instance:

```bash
aws dms create-replication-instance \
  --region us-east-1 \
  --replication-instance-identifier madar-dms-repl \
  --replication-instance-class dms.t3.small \
  --allocated-storage 20 \
  --replication-subnet-group-identifier madar-dms-subnets \
  --vpc-security-group-ids sg-085569e2731850c8a \
  --no-multi-az \
  --no-publicly-accessible \
  --engine-version 3.6.1
```

Observed when ready:

```text
Status      available
Private IP  172.31.13.46
Class       dms.t3.small
```

---

## 8. Create and test source endpoint

```bash
SOURCE_ENDPOINT_ARN=$(aws dms create-endpoint \
  --region us-east-1 \
  --endpoint-identifier madar-postgres-source \
  --endpoint-type source \
  --engine-name postgres \
  --server-name 172.31.3.142 \
  --port 5432 \
  --database-name madar_legacy \
  --username dms_user \
  --password '<REDACTED>' \
  --query 'Endpoint.EndpointArn' \
  --output text)
```

Test:

```bash
aws dms test-connection \
  --region us-east-1 \
  --replication-instance-arn "$REPL_ARN" \
  --endpoint-arn "$SOURCE_ENDPOINT_ARN"
```

Observed:

```text
madar-postgres-source | successful
```

---

## 9. Create and troubleshoot target endpoint

Create target endpoint using the RDS endpoint and master login. Passwords were entered through shell variables rather than committed to source control.

First connection failure:

```text
no pg_hba.conf entry ... no encryption
```

Interpretation: network routing and security groups were already working because the request reached PostgreSQL. The remaining problem was TLS mode.

Fix:

```bash
aws dms modify-endpoint \
  --region us-east-1 \
  --endpoint-arn "$TARGET_ENDPOINT_ARN" \
  --ssl-mode require
```

Second failure:

```text
password authentication failed for user "postgres"
```

Interpretation: TLS/network were now working; credentials were the remaining failing layer.

The RDS master password was reset and the DMS endpoint was updated with the same new password:

```bash
aws rds modify-db-instance \
  --region us-east-1 \
  --db-instance-identifier madar-postgres-target \
  --master-user-password "$NEW_RDS_PASSWORD" \
  --apply-immediately

aws dms modify-endpoint \
  --region us-east-1 \
  --endpoint-arn "$TARGET_ENDPOINT_ARN" \
  --username postgres \
  --password "$NEW_RDS_PASSWORD" \
  --ssl-mode require
```

Final target test:

```text
madar-postgres-target | successful
```

Engineering lesson: each failure narrowed the layer — first TLS, then credentials. Do not respond to an authentication error by opening more network access.

---

## 10. Create Full Load + CDC task

Table mapping includes all tables in `public`:

```json
{
  "rules": [{
    "rule-type": "selection",
    "rule-id": "1",
    "rule-name": "include-public",
    "object-locator": {
      "schema-name": "public",
      "table-name": "%"
    },
    "rule-action": "include"
  }]
}
```

Create task:

```bash
TASK_ARN=$(aws dms create-replication-task \
  --region us-east-1 \
  --replication-task-identifier madar-full-load-cdc \
  --source-endpoint-arn "$SOURCE_ENDPOINT_ARN" \
  --target-endpoint-arn "$TARGET_ENDPOINT_ARN" \
  --replication-instance-arn "$REPL_ARN" \
  --migration-type full-load-and-cdc \
  --table-mappings file://table-mappings.json \
  --query 'ReplicationTask.ReplicationTaskArn' \
  --output text)
```

Start when ready:

```bash
aws dms start-replication-task \
  --region us-east-1 \
  --replication-task-arn "$TASK_ARN" \
  --start-replication-task-type start-replication
```

Monitor:

```bash
aws dms describe-replication-tasks \
  --region us-east-1 \
  --filters Name=replication-task-id,Values=madar-full-load-cdc \
  --query 'ReplicationTasks[0].{Status:Status,FullLoadProgress:ReplicationTaskStats.FullLoadProgressPercent,TablesLoaded:ReplicationTaskStats.TablesLoaded,TablesLoading:ReplicationTaskStats.TablesLoading,TablesErrored:ReplicationTaskStats.TablesErrored}' \
  --output table
```

Observed:

```text
Status            running
FullLoadProgress  100
TablesLoaded      3
TablesErrored     0
```

Per-table statistics:

```bash
aws dms describe-table-statistics \
  --region us-east-1 \
  --replication-task-arn "$TASK_ARN" \
  --query 'TableStatistics[*].{Schema:SchemaName,Table:TableName,State:TableState,FullLoadRows:FullLoadRows,Inserts:Inserts,Updates:Updates,Deletes:Deletes}' \
  --output table
```

Observed Full Load:

```text
customers         Table completed   10 rows
shipments         Table completed   50 rows
shipment_events   Table completed   150 rows
```

---

## 11. Validate RDS independently

From the migrated EC2 host, connect directly to private RDS:

```bash
PGPASSWORD="$RDS_PASSWORD" psql \
  -h "$RDS_ENDPOINT" \
  -U postgres \
  -d madar_legacy \
  -c "
SELECT 'customers' AS table_name, COUNT(*) FROM public.customers
UNION ALL
SELECT 'shipments', COUNT(*) FROM public.shipments
UNION ALL
SELECT 'shipment_events', COUNT(*) FROM public.shipment_events;
"
```

Initial target result:

```text
customers         10
shipments         50
shipment_events   150
```

This proves that DMS statistics and target database state agree.

---

## 12. Prove CDC with a controlled change

Create one unmistakable source-side record:

```bash
sudo -u postgres psql -d madar_legacy -c "
INSERT INTO public.customers (company_name, region)
VALUES ('MADAR CDC TEST CUSTOMER', 'Riyadh')
RETURNING customer_id, company_name, region;
"
```

Observed source:

```text
customer_id  11
company      MADAR CDC TEST CUSTOMER
region       Riyadh
customers    11
```

Without restarting Full Load, query RDS:

```bash
PGPASSWORD="$RDS_PASSWORD" psql \
  -h "$RDS_ENDPOINT" \
  -U postgres \
  -d madar_legacy \
  -c "
SELECT customer_id, company_name, region
FROM public.customers
WHERE company_name = 'MADAR CDC TEST CUSTOMER';

SELECT COUNT(*) AS target_customers
FROM public.customers;
"
```

Observed target:

```text
11 | MADAR CDC TEST CUSTOMER | Riyadh
target_customers = 11
```

This is direct proof of CDC:

```text
source INSERT
 -> PostgreSQL logical WAL
 -> AWS DMS CDC
 -> target RDS row appears
```

---

## 13. Final reconciliation

Final RDS counts:

```text
customers         11
shipments         50
shipment_events   150
```

Stage 2 acceptance:

```text
RDS target available              PASS
Source endpoint                   PASS
Target endpoint                   PASS
Full Load                         PASS
Tables loaded                     3/3
Tables errored                    0
Initial counts                    10 / 50 / 150
Controlled CDC insert             PASS
Final counts                      11 / 50 / 150
```

## What to explain in an interview

Do not recite syntax. Explain the layers:

```text
CDC readiness      -> logical WAL / slots / senders
Network reachability -> listen address + pg_hba + SG-to-SG
DMS control plane  -> dms-vpc-role
Target protection  -> private RDS + TLS
Migration engine   -> DMS replication instance
Initial state      -> Full Load
Ongoing state      -> CDC
Acceptance         -> independent SQL reconciliation
```

A strong answer also mentions the three real troubleshooting events:

1. `dms-vpc-role` failure -> IAM prerequisite.
2. target `no encryption` failure -> enable TLS on endpoint.
3. target password failure -> synchronize credentials, not loosen networking.

That progression demonstrates layer-by-layer troubleshooting rather than trial-and-error.