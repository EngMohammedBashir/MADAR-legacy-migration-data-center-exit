# Phase 03 — Current State

**Status:** PLANNING / SOURCE-LAB PREPARATION  
**AWS paid-resource window:** NOT STARTED  
**Current objective:** build and baseline the representative legacy workload before choosing the final AWS target.

## Story position

MADAR already had a traditional estate before its AWS journey. Phase 01 established cloud foundations. Phase 02 proved a new event-driven cloud-native workload. Management now has enough confidence to address the remaining legacy shipment-management estate and prepare for data-center exit.

## Local hardware constraint

The migration lab host has approximately:

- 8 GB RAM,
- Intel Core i3-N305,
- hardware virtualization enabled,
- approximately 48 GB free local storage at preflight,
- Hyper-V features disabled at preflight.

Therefore the lab will favor **one lightweight VM with several logical legacy roles** instead of pretending to run a full multi-server enterprise data center locally.

## Next session — exact starting point

1. Select/install the local hypervisor.
2. Select a lightweight guest OS appropriate for the representative workload.
3. Create one VM with conservative CPU/RAM/disk allocation.
4. Install the representative MADAR application/database/file/batch components.
5. Generate deterministic synthetic logistics data.
6. Prove the source workload works.
7. Capture the source baseline before designing the final AWS destination.

## Important hold point

**Do not run Terraform apply yet.**

The target architecture must be selected after discovery and assessment. Terraform scaffolding may be prepared, but cloud resources should not be created simply because a service seems useful.

## Tomorrow's opening question

> What exactly does the legacy workload depend on, and what evidence would make us confident enough to move it?

## Exit criteria for source-lab stage

- VM boots reliably.
- workload is reachable and functional.
- database contains deterministic seed records.
- operational files exist and can be checksummed.
- scheduled/background operation is demonstrated.
- inventory and dependencies are documented.
- baseline counts/checksums are captured.
- snapshot/backup point exists before migration changes.

## Blockers

None currently. Hypervisor and guest OS still need to be selected/installed.
