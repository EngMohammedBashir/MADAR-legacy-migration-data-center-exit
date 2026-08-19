# MADAR Legacy Shipment Application

This directory contains the representative source application used by Phase 03 to prove discovery, migration, reconciliation and cutover behavior.

## Components

- `app.py` — Flask application and JSON API backed by PostgreSQL.
- `schema.sql` — reproducible schema for customers, shipments and shipment events.
- `seed_data.py` — deterministic fictional logistics dataset generator.
- `requirements.txt` — Python dependencies.
- `templates/dashboard.html` — lightweight operations dashboard.
- `static/` — UI assets.

## Source topology

```text
Operator/browser
      |
      | HTTP :8080
      v
MADAR-LEGACY-01
├── Flask application
│   ├── /api/health
│   ├── /api/summary
│   ├── /api/customers
│   ├── /api/shipments
│   └── /api/shipments/<id>/events
└── PostgreSQL 16
    ├── customers
    ├── shipments
    └── shipment_events
```

The application and database are intentionally co-located in the legacy source. The migration first rehosts the existing VM to EC2; PostgreSQL is then replatformed separately to RDS through DMS.

## Security rule

The database password is not stored in source code. The lab process expects a runtime value such as:

```bash
export MADAR_DB_PASSWORD='<lab-password>'
```

Do not commit the actual value. Repository ignore rules exclude secret-bearing environment files, keys and local virtual environments.

## Python environment

Ubuntu 24.04 enforces externally managed Python packaging (PEP 668). The lab uses an isolated virtual environment rather than altering the system Python environment:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database setup

The database and application role are created administratively outside source code:

```sql
CREATE USER madar_app WITH PASSWORD '<lab-password>';
CREATE DATABASE madar_legacy OWNER madar_app;
```

Apply schema:

```bash
psql -h localhost -U madar_app -d madar_legacy -f schema.sql
```

## Deterministic seed

The seed resets the three lab tables, restarts identities and regenerates a fixed workload:

```text
Customers        10
Shipments        50
Shipment events  150
```

This deterministic state is the migration manifest used for reconciliation.

Run:

```bash
export MADAR_DB_PASSWORD='<lab-password>'
python seed_data.py
```

Independent PostgreSQL verification:

```sql
SELECT
  (SELECT COUNT(*) FROM customers) AS customers,
  (SELECT COUNT(*) FROM shipments) AS shipments,
  (SELECT COUNT(*) FROM shipment_events) AS events;
```

## Run application

```bash
source .venv/bin/activate
export MADAR_DB_PASSWORD='<lab-password>'
python app.py
```

The source lab listens on `0.0.0.0:8080` so the operator can exercise it through the controlled lab network.

## Migration behavior that matters

There is no mock-data fallback. If PostgreSQL is unavailable, application health/read behavior exposes the dependency failure instead of fabricating a successful dashboard. That makes the application useful for migration validation.

A controlled PATCH operation has already proven the transactional write path: shipment state changes and the corresponding shipment event commit together. The deterministic seed was then rerun so migration starts from the known `10 / 50 / 150` baseline.

After the VM is imported to EC2, the same endpoints and data behavior become acceptance tests. After DMS/RDS replatforming, the application is reconfigured to the RDS endpoint and the same tests prove that application behavior survived the database move.