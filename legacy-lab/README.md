# MADAR Legacy Lab

## Purpose

Create a small but real source workload that can be inventoried, migrated, broken, reconciled and recovered.

## Planned workload characteristics

The exact software stack will be selected during setup based on guest OS footprint and migration value. The lab must provide:

- a reachable shipment-management application or API,
- a persistent relational database,
- operational files stored outside the database,
- a scheduled/background process,
- configuration containing dependencies that can be discovered and later changed,
- deterministic synthetic data.

## Data model — planned minimum

### Customers

`customer_id, company_name, region`

### Shipments

`shipment_id, customer_id, origin, destination, status, created_at, updated_at`

### Shipment events

`event_id, shipment_id, event_type, event_time`

### Operational files

Representative POD/manifest/invoice-like text/PDF artifacts tied to shipment IDs.

## Deterministic seed rule

Use a fixed random seed or deterministic generator so the source dataset can be regenerated and independently verified.

Target starting scale should be large enough to make reconciliation meaningful but small enough for the laptop and low-cost AWS tests. Final count will be chosen during implementation.

## Baseline outputs

Scripts should eventually produce machine-readable baseline files under a local generated/output directory that is either sanitized before commit or excluded via `.gitignore` when environment-specific.

Expected outputs include:

- database row counts,
- representative aggregates,
- file count,
- file SHA-256 manifest,
- application smoke-test result.

## Tomorrow's build order

1. Install/select hypervisor.
2. Create VM.
3. Install guest OS.
4. Configure networking.
5. Install runtime/database dependencies.
6. Deploy minimal workload.
7. Seed data/files.
8. Run smoke test.
9. Generate baseline.
10. Snapshot source.
11. Begin formal discovery.
