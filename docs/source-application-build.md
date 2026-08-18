# Source Application & Database Build Record

This record continues the Phase 03 source-lab build after the base VM/runtime milestone. It documents the relational database, deterministic seed, Python isolation, Flask application and validation behavior used by the representative legacy workload.

## 1. PostgreSQL application identity and database

Administrative entry:

```bash
sudo -u postgres psql
```

The application was deliberately separated from the PostgreSQL superuser. The lab created:

```text
Role:     madar_app
Database: madar_legacy
```

The password was supplied during the lab session and is intentionally absent from repository source.

Representative SQL flow:

```sql
CREATE USER madar_app WITH PASSWORD '<lab-password>';
CREATE DATABASE madar_legacy OWNER madar_app;
```

Verification commands:

```text
\du
\l
```

Application-account connectivity was then tested directly:

```bash
psql -h localhost -U madar_app -d madar_legacy
```

The connection negotiated TLS locally and proved that the non-superuser application identity could authenticate to its own database.

## 2. Relational schema

The schema consists of three related tables:

```text
customers
    |
    | 1:N
    v
shipments
    |
    | 1:N
    v
shipment_events
```

The implementation is now reproducible through:

```text
legacy-lab/app/schema.sql
```

Verification:

```text
\dt
```

Expected application tables:

```text
customers
shipments
shipment_events
```

## 3. Manual SQL smoke test

Before automation, a small manual sequence validated fundamental relational behavior:

- inserted one customer,
- selected the customer,
- inserted a shipment linked by `customer_id`,
- identified and removed one accidental duplicate shipment using `DELETE ... WHERE`,
- inserted a shipment event,
- selected the resulting event.

This was a learning/build smoke test only. The manual rows were later replaced by the seed process.

## 4. Python package isolation

A direct system-wide installation attempt:

```bash
pip3 install psycopg2-binary
```

was blocked by Ubuntu's externally-managed Python environment (PEP 668).

The lab did **not** use:

```text
--break-system-packages
```

Instead it installed venv support and created an isolated application environment:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

Application dependencies:

```text
Flask 3.1.3
psycopg2-binary 2.9.12
```

Pinned versions are stored in `legacy-lab/app/requirements.txt`.

## 5. Secret handling

The application and seed generator read the database password from:

```text
MADAR_DB_PASSWORD
```

Example session setup:

```bash
export MADAR_DB_PASSWORD='<lab-password>'
```

Verification without printing the secret:

```bash
test -n "$MADAR_DB_PASSWORD" && echo "MADAR_DB_PASSWORD is set"
```

The actual secret is not stored in `app.py`, `seed_data.py`, or repository documentation.

## 6. Deterministic seed dataset

The initial seed smoke test established the target baseline:

```text
Customers:        10
Shipments:        50
Shipment events: 150
```

Independent PostgreSQL verification:

```sql
SELECT
  (SELECT COUNT(*) FROM customers) AS customers,
  (SELECT COUNT(*) FROM shipments) AS shipments,
  (SELECT COUNT(*) FROM shipment_events) AS events;
```

Observed source count baseline:

```text
10 | 50 | 150
```

The repository version of `seed_data.py` was then hardened further so that timestamps are fixed and event history follows the actual shipment workflow. With ten shipments at each status depth, the event count remains exactly:

```text
10 * (1 + 2 + 3 + 4 + 5) = 150
```

The local VM must rerun this corrected repository version before the final migration baseline is frozen.

## 7. Flask source workload

The running representative application exposes:

```text
GET /
GET /api/health
GET /api/summary
GET /api/customers
GET /api/shipments
GET /api/shipments/<id>/events
```

The dashboard is a light enterprise logistics UI with working navigation for:

- Dashboard,
- Shipments,
- Customers,
- System Status.

The shipment table and KPIs are populated from PostgreSQL. Shipment details display a workflow timeline.

## 8. Real dependency behavior — no mock fallback

An early UI prototype included the idea of mock fallback data. That behavior was explicitly rejected for the migration lab.

Final rule:

```text
PostgreSQL healthy   -> real operational data displayed
PostgreSQL unhealthy -> health/dependency failure surfaced
```

This prevents the UI from appearing healthy during a real database outage and makes future migration evidence trustworthy.

## 9. Application run path

From the VM:

```bash
cd ~/madar-legacy-app
source .venv/bin/activate
export MADAR_DB_PASSWORD='<lab-password>'
python app.py
```

The process listens on port `8080` for the representative lab. The Windows host reaches it over the VMware NAT network.

## 10. Hero image handling

The running local UI uses:

```text
static/images/madar-hero-truck.png
```

The binary asset is intentionally not added automatically through the text-only repository update path. Before repository publication, confirm image provenance/licensing and then add the reviewed asset or replace it with an original project-owned graphic.

## 11. Evidence captured locally

Relevant evidence added during this milestone:

```text
madar-postgresql-database-role-created.png
madar-postgresql-schema-created.png
madar-python-venv-psycopg2-ready.png
madar-deterministic-dataset-baseline.png
madar-application-dashboard.png
```

## 12. Remaining source-side work

Before formal migration assessment:

1. sync/rerun the corrected deterministic seed on the VM,
2. create deterministic operational files,
3. generate SHA-256 file manifest and count/size baseline,
4. configure and prove a scheduled/background job,
5. add an application-level write path and prove it,
6. capture representative database aggregates,
7. create a pre-migration backup/snapshot,
8. perform formal dependency discovery.
