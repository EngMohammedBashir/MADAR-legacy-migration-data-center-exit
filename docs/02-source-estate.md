# Source Estate — Logical vs Representative Lab Topology

## Logical MADAR legacy estate

The company narrative separates responsibilities even though the lab consolidates them on one VM:

| Logical role | Responsibility | Migration concern |
|---|---|---|
| Shipment application | Internal shipment workflow | Runtime/configuration/network dependencies |
| Operational database | Customers, shipments, status/history | Integrity, consistency, cutover and recovery |
| Operational files | CSV exports/reports/manifests | Paths, permissions, object mapping, checksums |
| Batch processing | Scheduled status/report generation | Scheduling, credentials, target DB/storage path |
| Administration | Linux/SSH operations | Identity, management path, least privilege |
| Future enterprise identity | Workforce authentication | Later transformation-phase concern |

## Representative VMware lab

Local hardware is deliberately constrained, so several logical legacy roles are consolidated on one VMware VM. This is a migration test topology, not a claim about a real production data center.

```text
Windows workstation
   |
   +-- VMware Workstation Pro
          |
          +-- MADAR-LEGACY-01
                ├-- Ubuntu Server 24.04.4 LTS
                ├-- Flask shipment application / TCP 8080
                ├-- PostgreSQL 16.14 / madar_legacy
                ├-- operational exports/reports/manifests
                └-- scheduled report job
```

## Verified VM baseline

```text
vCPU               2
RAM                ~2.4 GiB guest-visible
Virtual disk       25 GiB
Partition table    GPT
Boot               BIOS + GRUB2
/boot              2 GiB ext4
root               ~23 GiB LVM/ext4
Kernel             6.8.0-138-generic
Architecture       x86_64
Source network     VMware NAT / DHCP
Source IP          192.168.14.128/24 during lab
PostgreSQL         16.14
Application        Flask 3.1.3
```

During discovery the VMware NIC appeared as `ens33`. For the accepted VM Import/Export path, the guest was deliberately prepared to use `eth0` with DHCP and reboot-tested before export. Both facts are retained: `ens33` describes the original discovered state; `eth0` describes the final pre-export migration state.

## Synthetic business data

The workload uses fictional deterministic records only. The migration baseline is:

```text
Customers        10
Shipments        50
Shipment events  150
```

The application also generates operational CSV/report artifacts and a scheduled report output. No real customer or personal data is used.

## Why the baseline matters

Migration without a baseline is like a logistics company moving hundreds of parcels without a manifest: arrival of the truck does not prove every parcel arrived correctly.

The baseline therefore includes:

- VM/OS/runtime versions,
- disk/boot/network topology,
- listening ports and services,
- database schema/version and row counts,
- representative application behavior,
- scheduled processing,
- file count/content integrity,
- independent PostgreSQL/file recovery artifacts,
- migration-specific source configuration changes,
- rollback source state.

## Source-to-target decomposition

Although the lab begins as one VM, migration disposition is selected per logical component:

```text
Ubuntu + Flask      -> rehost to EC2
PostgreSQL          -> replatform to RDS after EC2 acceptance
Operational files   -> replatform to S3
Scheduled job       -> retain/reconfigure against target dependencies
Administration      -> move toward AWS-native management where practical
```

This distinction prevents the representative single-VM lab from being mistaken for the desired final architecture.