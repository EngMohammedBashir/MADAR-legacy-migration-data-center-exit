# Phase 03 Repository Scope

This repository is the **implementation record for MADAR Phase 03 — Legacy Migration & Data Center Exit**.

## This repository owns

- representative source-lab implementation,
- Flask application and UI,
- PostgreSQL schema and deterministic seed data,
- source operational files/scripts,
- scheduled/background jobs,
- detailed command/runbooks,
- evidence index and implementation checklists,
- discovery inventory and dependency map,
- migration assessment and ADRs,
- AWS target architecture for Phase 03,
- Terraform/IaC for the approved target,
- migration execution and timing,
- database/file reconciliation,
- cutover and rollback procedures,
- controlled failure exercises,
- cleanup and Phase 03 technical closeout.

## This repository does not own

- the complete MADAR company transformation story,
- cross-phase roadmap ownership,
- future-phase implementation,
- transformation-wide risk/architecture history except where directly relevant to Phase 03.

Those belong in the master repository:

`EngMohammedBashir/MADAR-cloud-transformation`

## Promotion rule

Detailed work stays here. Only high-level outcomes are promoted to the master repository: approved migration strategy, high-level target architecture, material transformation risks, cutover outcome, Phase 03 completion, and the trigger for the next phase.

```text
MASTER
story / roadmap / cross-phase decisions
        ↑ high-level outcomes only
        |
PHASE 03
implementation / evidence / code / IaC / runbooks / migration
```
