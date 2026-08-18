# Phase 03 — Current State

**Status:** SOURCE LAB BUILD — BASE VM READY / RUNTIME + DATABASE INSTALLED  
**AWS paid-resource window:** NOT STARTED  
**Current objective:** finish the representative legacy workload, seed deterministic data, prove source behavior, and capture the pre-migration baseline before selecting the final AWS target.

## Story position

MADAR already had a traditional estate before its AWS journey. Phase 01 established cloud foundations. Phase 02 proved a new event-driven cloud-native workload. Management now has enough confidence to address the remaining legacy shipment-management estate and prepare for data-center exit.

## Local hardware constraint

The migration lab host has approximately:

- 8 GB RAM,
- Intel Core i3-N305,
- hardware virtualization enabled,
- approximately 48 GB free local storage at preflight,
- Hyper-V features disabled at preflight.

The lab therefore uses **one lightweight VM with several logical legacy roles** rather than pretending to run a full multi-server enterprise data center locally.

## Source-lab implementation completed so far

### Hypervisor and VM

- VMware Workstation Pro **26H1** installed and verified.
- Representative VM created as `MADAR-LEGACY-01`.
- Guest OS: **Ubuntu Server 24.04.4 LTS**.
- VM allocation: **2 vCPU**, **2560 MB RAM**, **25 GB dynamically allocated virtual disk**.
- Networking: **VMware NAT**.
- Guest interface observed as `ens33` with DHCP address `192.168.14.128/24` during this session.

### Guest baseline and remote administration

- Hostname: `madar-legacy-01`.
- Administrative lab user: `madaradmin`.
- OpenSSH Server installed and verified active.
- Remote SSH access from the Windows host verified successfully.
- Post-reboot validation confirmed the VM booted cleanly and SSH remained active.

### Storage correction

Ubuntu's guided LVM layout initially exposed only about 11.5 GB to `/` even though the VM disk was 25 GB. The remaining space was available in the LVM volume group.

The logical volume and ext4 filesystem were expanded to consume the remaining free LVM space. The root filesystem now reports approximately **23 GB**, with `VFree = 0` in `ubuntu-vg`.

### Base OS patching

- `apt update` completed.
- `apt upgrade -y` completed.
- Verification reported no immediately applicable package updates.
- A guest reboot was performed when required.
- Post-reboot health checks passed.

### Runtime and database dependencies

Installed and verified:

- Python **3.12.3**,
- pip **24.0**,
- PostgreSQL **16.14**,
- `postgresql-contrib`,
- PostgreSQL systemd service: **active**.

The PostgreSQL application database/user/schema have **not yet been created**. The shipment application has **not yet been deployed**.

## Evidence captured during this milestone

Screenshots captured locally using the agreed `madar-...` naming convention include:

- `madar-legacy-vm-system-baseline.png`
- `madar-legacy-vm-network-ssh.png`
- `madar-lvm-storage-expanded.png`
- `madar-base-os-patched.png`
- `madar-post-reboot-validation.png`
- `madar-runtime-postgresql-installed.png`

These remain local evidence until intentionally added to the repository evidence structure.

## Exact next action

1. Enter PostgreSQL as the local `postgres` administration identity.
2. Create the application database and least-purpose lab database role.
3. Create the initial relational schema for customers, shipments, and shipment events.
4. Install the Python application dependencies in an isolated virtual environment.
5. Deploy the minimal shipment-management API/application.
6. Create the operational-file area.
7. Configure a scheduled/background job.
8. Generate deterministic synthetic data and files.
9. Prove read/write/background behavior.
10. Capture row counts, aggregates, file counts, SHA-256 manifest, and source evidence.
11. Create the pre-migration snapshot/backup point.
12. Begin formal discovery and only then select the migration strategy and AWS target architecture.

## Important hold point

**Do not run Terraform apply yet.**

The target architecture must be selected after discovery and assessment. Terraform scaffolding may be prepared, but cloud resources should not be created simply because a service seems useful.

## Exit criteria for source-lab stage

- VM boots reliably. ✅
- workload is reachable and functional.
- database contains deterministic seed records.
- operational files exist and can be checksummed.
- scheduled/background operation is demonstrated.
- inventory and dependencies are documented.
- baseline counts/checksums are captured.
- snapshot/backup point exists before migration changes.

## Blockers

None currently. The base VM, guest OS, networking, SSH, storage, patching, Python runtime, and PostgreSQL engine are ready. The next blocker would only arise if database/application setup fails or resource pressure exceeds the local host constraint.
