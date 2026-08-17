# Source Estate — Logical vs Lab Topology

## Logical MADAR legacy estate

The company narrative treats these as separate responsibilities even when the lab consolidates them:

| Logical role | Responsibility | Migration concern |
|---|---|---|
| Shipment application | Internal shipment workflow | Runtime/configuration/network dependencies |
| Operational database | Shipments, customers, status/history | Integrity, compatibility, cutover consistency |
| File service | PODs, manifests, invoices | Paths, permissions, checksums, bulk transfer |
| Batch processing | Nightly/status/report jobs | Scheduling, idempotency, credentials |
| Corporate identity | Existing workforce identity | Authentication dependency; Phase 4 candidate |
| Partner integration | External carrier/partner exchange | Endpoint, allowlist, credentials, DNS/network |

## Representative VMware lab

Local hardware is intentionally constrained, so Phase 03 will initially represent several roles on **one lightweight VM**.

```text
Windows Host
   |
   +-- VMware / local hypervisor
          |
          +-- MADAR-LEGACY-01
                |-- shipment application
                |-- lightweight database
                |-- /data or equivalent operational files
                |-- scheduled/background job
```

This is deliberate consolidation for migration experimentation. It is **not** presented as MADAR's actual production topology.

## Synthetic business data

The lab should generate deterministic fictional records such as:

- customers,
- shipments,
- origin/destination,
- shipment status,
- timestamps,
- driver/reference IDs,
- operational amounts/weights where useful,
- POD/manifest/invoice-like files.

No real customer or personal data should be used.

## Source baseline

Before migration, record at minimum:

- VM configuration,
- OS/runtime versions,
- application version/commit,
- listening ports,
- services/processes,
- scheduled jobs,
- database schema/version,
- table row counts,
- selected aggregate values,
- file count,
- total file size,
- SHA-256 manifest for operational files,
- application smoke-test result,
- dependency map,
- source snapshot/backup identifier.

## Why the baseline matters

Migration without a baseline is like a shipping company moving 500 boxes without a manifest: arriving at the destination tells us nothing about whether box 417 disappeared.
