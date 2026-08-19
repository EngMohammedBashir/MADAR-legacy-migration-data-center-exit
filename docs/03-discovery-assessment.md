# Discovery & Assessment

## Goal

Understand enough about the workload to make migration decisions with evidence rather than assumptions, then preserve a clear distinction between the **original discovered source** and the **final pre-export migration state**.

## Verified source inventory

| Area | Original discovered state |
|---|---|
| Host | `madar-legacy-01`, Ubuntu Server 24.04.4 LTS |
| Compute | 2 vCPU, ~2.4 GiB RAM |
| Kernel/arch | `6.8.0-138-generic`, `x86_64` |
| Disk | 25 GiB GPT virtual disk |
| Boot | BIOS + GRUB2 |
| Root storage | LVM + ext4, ~23 GiB logical volume |
| Application | Flask/Python, TCP 8080 |
| Database | PostgreSQL 16.14 |
| Database listener | TCP 5432 on `127.0.0.1` only |
| Administration | SSH TCP 22 |
| Scheduled processing | cron; daily report at 02:00 Asia/Riyadh |
| Operational files | exports/reports/manifests/logs under the lab data area |
| Source network | VMware NAT, `192.168.14.128/24`, gateway `192.168.14.2` |
| Original NIC name | `ens33` |
| Deterministic DB baseline | 10 customers / 50 shipments / 150 events |
| Recoverability | PostgreSQL custom-format dump + operational-file/config backups |

## Verified dependency map

```text
Operations user
      |
      | HTTP :8080
      v
Flask / Python application
      |
      | PostgreSQL :5432 localhost
      v
PostgreSQL 16
      ^
      |
cron -> report script
      |
      +---- queries PostgreSQL
      +---- writes timestamped operational reports
                     |
                     v
              local filesystem

SSH :22 -> source administration
```

## Key coupling discovered

1. Flask and PostgreSQL are co-located and the application assumes a local database endpoint.
2. PostgreSQL is intentionally loopback-only, so direct DMS access from AWS is not naturally available from the VMware NAT lab.
3. The scheduled report job depends on both PostgreSQL and persistent local files.
4. Operational files are workload state and require validation during migration.
5. Moving only the Flask process would leave important state/dependencies behind.
6. The VM image also contains hypervisor-sensitive boot/network/storage assumptions that must be validated before a full-machine rehost.

## Component assessment

| Component | Statefulness | Initial disposition | Final direction |
|---|---|---|---|
| Flask/Ubuntu runtime | Low/medium | Rehost | EC2 via VM Import/Export |
| PostgreSQL | High | Replatform after landing | DMS Full Load + CDC -> RDS PostgreSQL |
| Operational files | High operational state | Replatform | validated copy -> S3 |
| Scheduled report job | Low code / stateful output | Retain then reconfigure | target DB/storage path |
| SSH administration | Operational | retain during migration | move toward SSM where practical |

## Migration-readiness assessment added after MGN blocker

The original discovery was sufficient for service selection, but VM Import/Export required deeper guest-OS checks. Those checks were performed before export:

```text
Boot
├── GRUB installed/rechecked on /dev/sda
├── kernel/initramfs present
└── BIOS + GPT/LVM layout verified

Network
├── ENA driver present
├── original ens33 dependency removed
├── eth0 + DHCP configured
└── reboot/route/Internet/DNS validated

Storage
├── NVMe driver present
├── xen block support present
└── LVM/ext4 verified

Services/state
├── SSH enabled + active
├── PostgreSQL enabled + active
├── madar_legacy present
├── zero failed systemd units
└── final logical PostgreSQL backup validated
```

This delta matters because discovery asks "what exists?" while migration readiness asks "what will break when the virtual hardware changes?"

## MGN assessment result

MGN block replication proved that the source could replicate successfully to AWS, but test launch exposed an account/service constraint unrelated to source health. CloudTrail showed the managed conversion stage attempted `m5.large`; the current Free Plan rejected that instance type. AWS Transform confirmed that conversion compute is not customer-configurable.

Assessment conclusion: the source VM is migration-capable, but MGN test/cutover is not compatible with the current account-plan constraint. The accepted rehost mechanism changed to VM Import/Export.

## Evidence captured

Evidence spans:

- original source runtime/dependency discovery,
- deterministic application/data baseline,
- scheduled-job and file-state proof,
- PostgreSQL/file recoverability,
- MGN replication and CloudTrail root cause,
- EC2 guest compatibility preparation,
- clean VMware export inspection,
- S3/IAM VM-import staging.

## Discovery conclusion

The important architectural conclusion remains that the source is not one indivisible "server problem." It contains multiple logical components plus hypervisor-dependent guest behavior. The migration therefore separates rehost, database replatform, file migration and operational modernization into independently validated stages.