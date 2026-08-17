# ADR 0001 — Use a Single-VM Representative Legacy Lab

**Status:** Accepted for initial source lab  
**Date:** 2026-08-18

## Context

The logical MADAR legacy estate contains application, database, file, batch and identity/integration responsibilities. The available local host has 8 GB RAM and limited free SSD capacity.

Running several Windows Server VMs solely to imitate physical separation would consume resources without improving the migration learning objective enough to justify the cost.

## Decision

Build one lightweight local VM and consolidate several logical workload roles inside it for the initial migration lab.

Documentation will always distinguish:

- **logical company topology**, and
- **physical representative lab topology**.

## VM starting envelope

Final values will be selected during setup, but the initial target is approximately:

- 2 vCPU,
- 2.5–3 GB RAM,
- 20–25 GB dynamically allocated disk,
- lightweight guest OS/runtime.

## Consequences

### Positive

- feasible on current hardware,
- faster setup and teardown,
- enough state and dependencies for genuine migration/integrity exercises,
- leaves host resources for browser, PowerShell, Terraform and AWS tooling.

### Negative

- does not reproduce inter-server east/west network behavior,
- does not reproduce a real Active Directory topology,
- cannot be used to claim enterprise-scale performance results.

## Mitigation

Represent missing enterprise boundaries in the logical architecture and explicitly state which behaviors were actually tested versus modeled.

## Revisit condition

Revisit if a later migration test genuinely requires separate hosts, directory services, replication behavior, or network segmentation.
