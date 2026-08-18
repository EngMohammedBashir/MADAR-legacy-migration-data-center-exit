# Phase 03 Source-Lab Build Log

This document records the implementation steps used to create and baseline the representative MADAR legacy source environment before any AWS migration target is approved.

The purpose is not merely to list commands. Each command is tied to an engineering question: what exists, why it is configured that way, what changed, and how the result was verified.

## 1. Local virtualization decision

The lab host has limited resources: approximately 8 GB RAM, Intel Core i3-N305, and limited free SSD capacity. To avoid an unrealistic multi-VM topology, the source estate is represented by one lightweight VM carrying several logical legacy roles.

Selected hypervisor:

```text
VMware Workstation Pro 26H1
```

Selected guest:

```text
Ubuntu Server 24.04.4 LTS
```

Representative VM:

```text
Name: MADAR-LEGACY-01
vCPU: 2
RAM: 2560 MB
Disk: 25 GB dynamically allocated
Network: VMware NAT
```

The VM is intentionally conservative so the Windows host remains usable while still supporting an application, relational database, files, and a background process.

## 2. Guest identity and baseline inspection

After Ubuntu installation, the VM was inspected before application deployment.

### Host and OS identity

```bash
hostnamectl
cat /etc/os-release
```

Why:

- `hostnamectl` confirms the server identity, virtualization platform, kernel, and architecture.
- `/etc/os-release` records the exact Linux distribution and release.

Observed baseline included:

```text
Hostname: madar-legacy-01
Virtualization: vmware
Operating System: Ubuntu 24.04.4 LTS
Architecture: x86-64
```

### CPU

```bash
nproc
lscpu | grep -E '^Model name|^CPU\(s\)'
```

Why:

- `nproc` shows how many processing units the guest can use.
- `lscpu` provides CPU metadata visible inside the VM.

Observed:

```text
2 vCPU
Intel Core i3-N305 host CPU presented to the guest
```

### Memory

```bash
free -h
```

Why:

`free -h` shows guest RAM and swap in human-readable units and verifies that the conservative VMware RAM allocation reached the guest.

Observed guest RAM was approximately 2.4 GiB, corresponding to the configured 2560 MB allocation.

### Disk and block layout

```bash
df -h /
lsblk
```

Why:

- `df -h /` shows usable capacity of the mounted root filesystem.
- `lsblk` shows the underlying virtual disk, partitions, and LVM layout.

The virtual disk was 25 GB, but Ubuntu's guided LVM layout initially exposed only about 11.5 GB to the root logical volume.

## 3. Networking and SSH

VMware NAT was used so the legacy VM can reach package repositories and be managed from the host without being directly bridged onto the physical LAN.

Guest network inspection:

```bash
ip -br addr
```

Observed during this session:

```text
ens33 UP 192.168.14.128/24
```

The address is DHCP-provided by the VMware NAT network and is not treated as a permanent production address.

SSH status check:

```bash
systemctl is-active ssh
```

Observed:

```text
active
```

Remote administration from Windows PowerShell:

```powershell
ssh madaradmin@192.168.14.128
```

Why:

SSH moves normal administration away from the VMware console and gives the lab a more realistic server-management path.

## 4. LVM root-filesystem expansion

Initial LVM inspection:

```bash
sudo vgs
```

Observed:

```text
VG: ubuntu-vg
VSize: <23 GB
VFree: 11.50 GB
```

This showed that roughly half of the LVM volume group was not yet assigned to the root logical volume.

Logical-volume expansion:

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
```

Meaning:

- `lvextend` expands a logical volume.
- `-l +100%FREE` consumes all free extents remaining in the volume group.
- `/dev/ubuntu-vg/ubuntu-lv` is the root logical volume being expanded.

Filesystem expansion:

```bash
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
```

Why a second command is needed:

Expanding the logical volume makes the block device larger. The ext4 filesystem must also be expanded to use the new space.

Verification:

```bash
df -h /
sudo vgs
sudo lvs
```

Verified result:

```text
Root filesystem: approximately 23 GB
Available space after expansion: approximately 17 GB at the time of capture
ubuntu-vg VFree: 0
```

## 5. Base OS patching

Package index refresh:

```bash
sudo apt update
```

Purpose:

Refresh the local package metadata from configured Ubuntu repositories. This does not itself install package upgrades.

Package upgrade:

```bash
sudo apt upgrade -y
```

Purpose:

Install currently available upgrades. `-y` automatically accepts the standard confirmation prompt.

Verification:

```bash
apt list --upgradable 2>/dev/null
```

A reboot requirement was also checked using:

```bash
if [ -f /var/run/reboot-required ]; then echo "YES"; else echo "NO"; fi
```

The guest reported a reboot was required, so only the VM was rebooted:

```bash
sudo reboot
```

Post-reboot validation:

```bash
hostname
uptime
systemctl is-active ssh
df -h /
```

This verified that the server returned successfully, SSH remained active, and the expanded storage persisted.

## 6. Runtime and relational database dependencies

Initial checks:

```bash
python3 --version
pip3 --version
psql --version
```

Observed before installation:

```text
Python 3.12.3 present
pip3 not installed
psql not installed
```

Dependency installation:

```bash
sudo apt install -y python3-pip postgresql postgresql-contrib
```

Why these packages:

- `python3-pip` provides Python package management for the planned application runtime.
- `postgresql` provides the persistent relational database engine required by the lab.
- `postgresql-contrib` supplies useful PostgreSQL extensions/tools while keeping the database stack conventional and migration-relevant.

Verification:

```bash
python3 --version
pip3 --version
psql --version
systemctl is-active postgresql
```

Verified versions/state:

```text
Python 3.12.3
pip 24.0
PostgreSQL 16.14
PostgreSQL service: active
```

## 7. Why PostgreSQL instead of SQLite

SQLite would be lightweight, but the purpose of Phase 03 is to practice discovery, dependency mapping, migration assessment, reconciliation, and cutover behavior against a representative legacy estate.

A standalone PostgreSQL service gives the lab a real database process, service lifecycle, authentication boundary, network/configuration dependency, schema, and migration decision to assess later. This makes the source environment more useful without exceeding the laptop constraint.

## 8. Evidence naming used for this milestone

Local screenshots captured so far:

```text
madar-legacy-vm-system-baseline.png
madar-legacy-vm-network-ssh.png
madar-lvm-storage-expanded.png
madar-base-os-patched.png
madar-post-reboot-validation.png
madar-runtime-postgresql-installed.png
```

The evidence is intentionally concise: each screenshot should prove a meaningful result rather than document every command typed.

## 9. Current hold point

Do not create AWS infrastructure yet.

The source workload still needs:

1. application database/role/schema,
2. shipment application/API,
3. operational files,
4. scheduled/background process,
5. deterministic synthetic data,
6. source read/write/background proof,
7. counts, aggregates, file manifest, and checksums,
8. pre-migration snapshot/backup,
9. formal discovery and dependency mapping.

Only after that evidence exists should MADAR approve a migration strategy and AWS target architecture.
