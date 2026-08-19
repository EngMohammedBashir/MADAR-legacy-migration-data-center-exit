# Phase 03 Repository Scope

This repository is the **implementation record for MADAR Phase 03 — Legacy Migration & Data Center Exit**.

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
- evidence index and implementation checklists,
- migration-day runbooks,
- cutover, rollback and cleanup procedures,
- Phase 03 technical closeout.

## What is intentionally not in this repository

Terraform was originally considered as a possible implementation layer, but **it was not used in the executed migration path**. The unused Terraform placeholder has therefore been removed instead of presenting IaC that did not actually provision the demonstrated resources.

The real implementation used:

```text
Ubuntu shell / PostgreSQL CLI
Windows PowerShell
AWS CLI / AWS CloudShell
AWS console evidence where useful
```

This repository also does not own:

- the complete MADAR company transformation story,
- cross-phase roadmap ownership,
- unrelated future-phase implementation,
- transformation-wide risk/architecture history except where directly relevant to Phase 03.

Those belong in the master repository:

`EngMohammedBashir/MADAR-cloud-transformation`

## Promotion rule

Detailed work stays here. Only high-level outcomes are promoted to the master repository: approved migration strategy, target architecture, material transformation risks, cutover outcome, Phase 03 completion, and the trigger for the next phase.

```text
MASTER
story / roadmap / cross-phase decisions
        ↑ high-level outcomes only
        |
PHASE 03
implementation / evidence / code / runbooks / migration
```
