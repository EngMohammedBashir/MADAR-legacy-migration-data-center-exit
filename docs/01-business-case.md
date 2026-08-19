# Business Case — Data Center Exit

## Situation

MADAR's representative logistics operation depends on a shipment-management workload hosted on VMware. The workload still functions, but its application, PostgreSQL database, operational files and scheduled processing are coupled to one virtual machine. Continued dependence on the legacy environment limits independent scaling, managed-service adoption, repeatable recovery and eventual data-center exit.

## Business drivers

- retire dependence on legacy virtualized infrastructure,
- preserve shipment workflow continuity during migration,
- increase confidence in recoverability and data integrity,
- separate application compute from stateful database operations,
- move database operations toward managed RDS,
- establish repeatable cloud security/identity boundaries,
- improve observability, backup and operational discipline,
- avoid uncontrolled AWS spend while proving the migration design.

## Constraint

The migration cannot trade continuity or data integrity for speed. A target that boots but contains incorrect shipment state is a failed migration.

The lab also operates under an AWS **Free Plan** constraint. The project therefore treats account-plan limits and hidden service-managed infrastructure as architecture constraints rather than billing details to ignore.

## Executive objective

**Exit the selected legacy workload safely, with evidence.**

The objective is not "move a VM at any cost." The objective is to understand the source, establish rollback, migrate the workload, prove business data and application behavior, then modernize stateful components deliberately.

## Engineering objectives

- discover the source before designing the target,
- classify logical components instead of blindly treating the VM as one indivisible system,
- preserve independent database/file recovery points,
- migrate the existing VMware image as a real rehost proof,
- replatform PostgreSQL to RDS after the EC2 landing point is accepted,
- validate files and scheduled processing,
- define explicit failure/rollback criteria,
- use least-privilege IAM/service delegation,
- document failures and architecture decisions rather than hiding them,
- remove temporary migration resources after evidence/acceptance.

## Real constraint discovered during execution

AWS Transform MGN successfully replicated the 25 GiB source, but test launch introduced a service-managed `m5.large` conversion server that the Free Plan rejected. CloudTrail and AWS Transform confirmed that this instance type is outside customer control.

The business/engineering response was not to repeatedly retry the wrong configuration or upgrade the account simply to make the demo green. The rehost mechanism was changed to EC2 VM Import/Export while preserving the target business outcome.

This is representative of a real migration program: implementation details can change while the business requirement, data-integrity requirement and risk boundaries remain stable.

## Definition of success

The phase succeeds only when MADAR can demonstrate:

```text
existing VMware workload
        -> accepted EC2 landing point
        -> correct application behavior
        -> reconciled PostgreSQL state
        -> validated operational files
        -> RDS database replatform proof
        -> understood rollback
        -> reviewed security/cost
        -> cleanup of temporary migration resources
```

## Definition of failure

The migration is unsuccessful if any critical condition remains unexplained, including:

- target cannot boot reliably,
- management/network path is unsafe or unavailable,
- PostgreSQL/database state differs unexpectedly,
- shipment application read/write behavior fails,
- required operational files/jobs are missing,
- rollback is destroyed before acceptance,
- temporary resources create uncontrolled cost/security exposure.

## Portfolio / reviewer value

The phase is intentionally documented as an engineering case study rather than a service checklist. It demonstrates source discovery, Linux/VMware readiness, data protection, IAM/service roles, AWS migration tooling, CloudTrail troubleshooting, architecture pivots, validation and cost governance.

## Narrative handoff

After the workload and database move into AWS, the growing number of cloud systems and operator access paths creates a natural trigger for the following transformation phase: centralized enterprise identity and workforce SSO.