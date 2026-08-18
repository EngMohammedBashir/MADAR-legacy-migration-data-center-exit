# Source Lab Operations Runbook

This runbook records the repeatable operator actions used during the MADAR source-lab baseline. Secrets are intentionally omitted.

## Mental model

`SSH -> application/database -> files -> scheduled job -> validation -> backup`

## Connect and orient

```bash
ssh madaradmin@<source-ip>
cd ~/madar-legacy-app
source .venv/bin/activate
```

## Application

```bash
python app.py
```

Health path: `GET /api/health` on port `8080`.

## PostgreSQL

```bash
psql -h localhost -U madar_app -d madar_legacy
```

Baseline validation:

```sql
SELECT
  (SELECT COUNT(*) FROM customers) AS customers,
  (SELECT COUNT(*) FROM shipments) AS shipments,
  (SELECT COUNT(*) FROM shipment_events) AS events;
```

Expected deterministic baseline: `10 / 50 / 150`.

## Operational files

Source operational data lives under `~/madar-legacy-data/` with `exports/`, `reports/`, `manifests/`, and `logs/` roles.

Verify an integrity manifest:

```bash
sha256sum -c manifests/source-sha256.txt
```

## Scheduled operation

The report script is versioned at `legacy-lab/scripts/generate_operations_report.sh` and the lab copy is executable on the VM. It queries PostgreSQL and emits a timestamped shipment-status CSV plus a success log entry.

A two-minute cron schedule was used only as a controlled proof that Linux executed the job without an interactive shell. The retained lab schedule is daily at 02:00 Asia/Riyadh time.

Check schedule:

```bash
crontab -l
```

Check results:

```bash
ls -lt ~/madar-legacy-data/reports/ | head
tail ~/madar-legacy-data/logs/background-job.log
```

## Application write-path proof

`PATCH /api/shipments/<id>/status` performs a transactional shipment status update and inserts the corresponding shipment event. The proof changed shipment 3 from `IN_TRANSIT` to `DELIVERED`, producing event 151. The deterministic seed was then rerun so the migration baseline returned to `10 / 50 / 150` and shipment 3 returned to `IN_TRANSIT`.

## Pre-migration database backup

```bash
pg_dump -h localhost -U madar_app -d madar_legacy -F c \
  -f ~/madar-backups/madar_legacy_pre_migration.dump
pg_restore --list ~/madar-backups/madar_legacy_pre_migration.dump | head
sha256sum ~/madar-backups/madar_legacy_pre_migration.dump
```

## Operational-file backup

```bash
tar -czf ~/madar-backups/madar_operational_files_pre_migration.tar.gz \
  -C ~/madar-legacy-data exports reports manifests

tar -tzf ~/madar-backups/madar_operational_files_pre_migration.tar.gz | head
sha256sum ~/madar-backups/madar_operational_files_pre_migration.tar.gz
```

## Security notes

- Never commit `.pgpass`, `.env`, passwords, dumps containing sensitive real data, or private keys.
- `.pgpass` on Unix must be restricted to the owning user (`chmod 600`).
- The lab data is fictional; binary evidence is reviewed before public upload.
- Backup files remain local evidence unless deliberately sanitized and published.
