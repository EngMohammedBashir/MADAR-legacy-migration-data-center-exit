# MADAR Legacy Shipment Application

This directory contains the representative source workload used by Phase 03 before any AWS target architecture is approved.

## Components

- `app.py` — Flask application and JSON API backed by PostgreSQL.
- `schema.sql` — reproducible relational schema for customers, shipments and shipment events.
- `seed_data.py` — deterministic fictional logistics dataset generator.
- `requirements.txt` — pinned Python application dependencies.
- `templates/dashboard.html` — light enterprise operations dashboard.
- `static/css/style.css` — dashboard styling.
- `static/images/madar-hero-truck.png` — local hero image used by the running lab UI; add intentionally after checking image licensing/provenance.

## Source topology

```text
Windows host browser
        |
        | HTTP :8080
        v
MADAR-LEGACY-01
        |
        +-- Flask application
        |       |
        |       +-- /api/health
        |       +-- /api/summary
        |       +-- /api/customers
        |       +-- /api/shipments
        |       +-- /api/shipments/<id>/events
        |
        +-- PostgreSQL 16
                |
                +-- customers
                +-- shipments
                +-- shipment_events
```

## Security rule

The database password is intentionally **not stored in source code**. The lab process expects:

```bash
export MADAR_DB_PASSWORD='<lab-password>'
```

Do not commit the actual value. The repository `.gitignore` excludes `.env`, keys, local virtual environments and other secret-bearing files.

## Python environment

Ubuntu 24.04 blocked direct system-wide `pip` installation under PEP 668. The lab deliberately did not use `--break-system-packages`; an isolated virtual environment was created instead:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database setup

The database and application role are created administratively outside source code. Example flow, with the password supplied interactively or securely rather than committed:

```sql
CREATE USER madar_app WITH PASSWORD '<lab-password>';
CREATE DATABASE madar_legacy OWNER madar_app;
```

Apply the schema as the application owner:

```bash
psql -h localhost -U madar_app -d madar_legacy -f schema.sql
```

## Deterministic seed

The seed generator resets only the three lab tables, restarts identities and regenerates a fixed dataset with fixed timestamps and workflow-consistent events:

```text
Customers: 10
Shipments: 50
Shipment events: 150
```

Run:

```bash
export MADAR_DB_PASSWORD='<lab-password>'
python seed_data.py
```

Verify independently from PostgreSQL:

```sql
SELECT
  (SELECT COUNT(*) FROM customers) AS customers,
  (SELECT COUNT(*) FROM shipments) AS shipments,
  (SELECT COUNT(*) FROM shipment_events) AS events;
```

Expected baseline:

```text
10 | 50 | 150
```

## Run application

```bash
source .venv/bin/activate
export MADAR_DB_PASSWORD='<lab-password>'
python app.py
```

The representative lab currently listens on `0.0.0.0:8080` so the Windows host can exercise it through the VMware NAT network.

## Important migration behavior

There is no mock-data fallback. If PostgreSQL is unavailable, health checks fail and the application surfaces the dependency failure rather than displaying fabricated operational data. That behavior is deliberate because Phase 03 needs trustworthy migration validation.
