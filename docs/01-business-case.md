# Business Case — Data Center Exit

## Situation

MADAR's logistics operation depends on a legacy shipment-management workload hosted in a traditional virtualized environment. The platform still works, but continued dependence on it creates increasing operational risk and constrains modernization.

## Business drivers

- Aging infrastructure and lifecycle pressure.
- Increasing shipment volume and business dependence.
- Weak confidence in recovery compared with desired cloud operating practices.
- Manual infrastructure and deployment operations.
- Difficulty scaling individual components independently.
- Growing need for stronger observability, security controls and repeatability.
- Eventual data-center exit.

## Constraint

The shipment workflow cannot simply disappear during migration. Warehouse and operations teams need continuity, and business data must remain trustworthy.

## Executive objective

Exit the selected legacy workload safely, not quickly at any cost.

## Engineering objectives

- understand the source before changing it,
- reduce unknown dependencies,
- classify components rather than blindly lift-and-shift everything,
- preserve data integrity,
- minimize cutover risk,
- establish rollback/abort criteria,
- make the target reproducible,
- improve operability after migration,
- avoid unnecessary AWS spend during the lab.

## Definition of failure

The migration is unsuccessful if the target exists but MADAR cannot demonstrate correct data, correct application behavior, safe operations, or recovery/rollback readiness.

## Narrative handoff

Successful migration is expected to increase the number of cloud systems and workforce access paths. That may create the business justification for the following transformation phase: centralized enterprise identity and workforce SSO.
