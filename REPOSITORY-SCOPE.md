# Phase 03 Repository Scope

This repository is the **implementation record for MADAR Phase 03 — Legacy Migration & Data Center Exit**.

## Chronology rule

The master MADAR scenario defines a **Pre-Cloud Legacy Baseline** before Phase 01. This repository owns the hands-on VMware implementation used to represent that baseline during Phase 03 migration work.

That distinction is deliberate:

```text
Scenario chronology: legacy estate -> Phase 01 -> Phase 02 -> Phase 03
Lab chronology:      Phase 03 preparation -> build representative source -> migrate
```

Documenting how the lab was built makes the project reproducible; it does not imply that the represented business workload first came into existence during Phase 03.

## This repository owns

- representative VMware source-lab implementation,
- Flask application and UI,
- PostgreSQL schema and deterministic seed data,
- source operational scripts and scheduled/background jobs,
- source discovery and dependency assessment,
- migration strategy and architecture decisions,
- AWS MGN experiment and failure analysis,
- EC2 VM Import/Export execution,
- S3 staging and IAM service-role configuration,
- imported EC2 validation,
- PostgreSQL CDC preparation,
- AWS DMS and Amazon RDS execution,
- data reconciliation and controlled CDC proof,
- operational-file migration to S3 and integrity proof,
- evidence index and implementation checklists,
- migration-day runbooks,
- application cutover and dependency-removal proof,
- rollback and cleanup procedures,
- Phase 03 technical closeout.

## What is intentionally not in this repository

Terraform was originally considered as a possible implementation layer, but **it was not used in the executed migration path**. The unused Terraform placeholder was removed instead of presenting IaC that did not actually provision the demonstrated resources.

The real implementation used:

```text
Ubuntu shell / PostgreSQL CLI
Windows PowerShell
AWS CLI / AWS CloudShell
AWS console evidence where useful
```

This repository also does not own the complete MADAR company transformation story, cross-phase roadmap, unrelated future-phase implementation, or transformation-wide risk/architecture history except where directly relevant to Phase 03.

Those belong in the master repository:

`EngMohammedBashir/MADAR-cloud-transformation`

## Promotion rule

Detailed work stays here. Only high-level outcomes are promoted to the master repository: baseline relationship, accepted migration strategy, target architecture, material transformation risks, cutover outcome, Phase 03 completion and the trigger for the next phase.

```text
MASTER
story / pre-cloud baseline / roadmap / cross-phase decisions
        ↑ high-level outcomes only
        |
PHASE 03
representative source / implementation / evidence / migration / closeout
```
