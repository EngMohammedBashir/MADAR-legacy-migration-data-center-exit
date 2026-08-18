# Discovery & Assessment

## Goal

Understand enough about the workload to make migration decisions with evidence rather than assumptions.

## Verified source inventory

| Area | Verified source state |
|---|---|
| Host | `madar-legacy-01`, Ubuntu Server 24.04.4 LTS |
| Compute | 2 vCPU, 2.4 GiB RAM |
| Root storage | 23 GiB filesystem, ~5.4 GiB used during discovery |
| Application | Flask/Python process (`python app.py`) |
| Application listener | TCP 8080 on `0.0.0.0` |
| Database | PostgreSQL 16.14 |
| Database listener | TCP 5432 on `127.0.0.1` only |
| Administration | SSH TCP 22 |
| Scheduled processing | `cron` active; daily report job at 02:00 Asia/Riyadh |
| Operational files | exports, reports, manifests and logs under `~/madar-legacy-data` |
| Source network | `192.168.14.128/24`, default gateway `192.168.14.2` in the representative VMware NAT lab |
| Deterministic DB baseline | 10 customers / 50 shipments / 150 shipment events |
| Recoverability | PostgreSQL custom-format dump + operational-file archive, both integrity checked |

## Verified dependency map

```text
Operations user
      |
      | HTTP :8080
      v
Flask / Python application
      |
      | PostgreSQL :5432 (currently localhost)
      v
PostgreSQL 16
      ^
      |
cron -> generate_operations_report.sh
      |
      +---- queries PostgreSQL
      |
      +---- writes timestamped CSV reports
                    |
                    v
        local operational filesystem

SSH :22 -> source host administration
```

### Key coupling discovered

1. The application and PostgreSQL are co-located today; the application therefore assumes a local database endpoint.
2. PostgreSQL is not directly exposed to the source LAN; it listens only on loopback.
3. The scheduled report job depends on PostgreSQL and writes persistent output to the local filesystem.
4. Operational files are therefore part of workload state and cannot be ignored during migration.
5. Moving only the Flask process would leave database, scheduled processing and file-state dependencies behind.

## Component assessment

| Component | Criticality | Dependencies | Statefulness | Strategy candidate | Downtime sensitivity | Validation | Rollback |
|---|---|---|---|---|---|---|---|
| Flask application/runtime | High | PostgreSQL endpoint, Python dependencies | Low | Rehost initially | Medium | health/API/read/write tests | Return traffic to source app |
| PostgreSQL | High | Application + scheduled report job | High | Replatform to managed PostgreSQL | High | counts, aggregates, representative rows, write test | Source DB remains authoritative until acceptance |
| Operational CSV/files | Medium | Scheduled job and operational evidence | High | Replatform to object storage where semantics permit | Medium | file count + SHA-256/content checks | Preserve source archive/files |
| Scheduled report job | Medium | PostgreSQL + report destination | Low code / stateful output | Modest replatform after migration | Low/Medium | execute job and inspect output/log | Retain source cron until cutover acceptance |
| SSH administration | Operational | Host/network | Low | Replace target administration with SSM where practical | Low | management-session test | Source SSH retained during migration window |

## Evidence captured

The runtime discovery evidence records:

- 2 vCPU and 2.4 GiB RAM,
- root filesystem capacity/usage,
- PostgreSQL and Flask processes,
- active PostgreSQL, cron and SSH services,
- listeners on 22, 5432 and 8080,
- PostgreSQL bound to loopback while Flask is network reachable.

Local evidence filename:

`madar-source-discovery-runtime-dependencies.png`

Earlier evidence also proves the deterministic dataset, operational files, cron execution, transactional application write path, restored baseline and pre-migration backups.

## Discovery conclusions

Discovery is sufficient to move from generic hypotheses to a migration-strategy decision for the representative lab. Remaining implementation-specific checks (for example exact target endpoint configuration and AWS connectivity) belong to target readiness rather than source discovery.

The central architectural conclusion is that this is not one indivisible VM. It contains multiple logical workload components with different state and operational characteristics, so migration disposition should be selected per component.
