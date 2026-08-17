# MADAR — Legacy Migration & Data Center Exit

## Phase 03 of the MADAR Cloud Transformation

MADAR Logistics & Digital Operations has already established an AWS foundation and validated a cloud-native event-driven workload. The company now faces a different problem: its core shipment-management estate still depends on aging infrastructure in the legacy data center.

This phase treats migration as an **engineering engagement**, not as an EC2 deployment exercise.

> The VMware environment built for this project is a representative lab of MADAR's pre-existing legacy estate. It is created now so the migration can be executed and measured safely; the company story does not claim that the legacy estate appeared after AWS adoption.

## Mission

Plan and execute a controlled migration of a representative MADAR logistics workload from a VMware-based legacy environment toward AWS while preserving application behavior, data integrity, operational recoverability, and a credible rollback path.

## Business pressure

MADAR's legacy environment is becoming harder to justify because of aging infrastructure, growth, operational overhead, weak recovery confidence, deployment friction, and an eventual data-center exit requirement.

The migration team must answer a harder question than "how do we move a server?":

**What should move, what should change, what should remain temporarily, what should be retired, and how can MADAR prove that cutover is safe?**

## Representative source estate

```text
Branches / Warehouses / Operations
              |
              v
       VMware Legacy Lab
              |
     +--------+---------+
     |        |         |
 Application Database  Operational Files
     |        |         |
     +--- scheduled jobs / integrations
```

The physical lab is intentionally compact enough to run on limited local hardware. Multiple logical legacy roles may coexist on one VM. Documentation will distinguish **logical production roles** from the **representative lab topology**.

## Engineering lifecycle

`Discovery → Inventory → Dependency Mapping → Assessment → Migration Strategy → Target Design → Readiness → Migration → Validation → Cutover → Rollback Validation → Optimization → Cleanup`

## Success is not "AWS resources exist"

The phase is complete only when important claims have evidence, including:

- source workload works before migration,
- source data baseline is recorded,
- dependencies are understood,
- migration strategy is justified per component,
- target infrastructure is reproducible,
- migrated data is reconciled,
- application behavior is validated,
- cutover criteria are satisfied,
- rollback/abort conditions are defined and exercised where practical,
- security and observability controls are checked,
- cost and quotas are reviewed,
- temporary cloud resources are destroyed,
- residual resources are checked.

## Repository map

- `CURRENT-STATE.md` — start here each session.
- `docs/01-business-case.md` — why MADAR is exiting the legacy environment.
- `docs/02-source-estate.md` — logical estate and representative VMware lab.
- `docs/03-discovery-assessment.md` — inventory and dependency assessment.
- `docs/04-migration-strategy.md` — component-level strategy and trade-offs.
- `docs/05-target-architecture.md` — target architecture after assessment.
- `docs/06-validation-plan.md` — integrity and functional validation.
- `checklists/` — readiness, cutover, rollback, closeout.
- `decisions/` — architecture decision records.
- `runbooks/` — repeatable operational procedures.
- `evidence/` — evidence index and later screenshots/output.
- `legacy-lab/` — source lab configuration, seed data and scripts.
- `terraform/` — AWS Infrastructure as Code when target design is approved.

## Cost discipline

Paid AWS resources should exist only during intentional implementation/test windows. Prepare locally first, deploy when ready, validate aggressively, capture evidence, then destroy and verify cleanup.

## Integrity rule

MADAR is fictional. Tests, code, failures, outputs, decisions and evidence must be technically authentic. Controlled failures must be labeled as controlled exercises; they must not be presented as real production incidents.
