# Source Lab Operations Runbook

This runbook records repeatable operator actions used on the MADAR source VM. Secrets are intentionally omitted.

## Mental model

```text
SSH
 -> application/database
 -> files/background job
 -> baseline/recovery
 -> EC2 compatibility preparation
 -> final validation
 -> clean shutdown/export
```

## Normal source operations

Connect:

```bash
ssh madaradmin@<source-ip>
cd ~/madar-legacy-app
source .venv/bin/activate
```

Application health endpoint:

```text
GET /api/health on TCP 8080
```

PostgreSQL application connection:

```bash
psql -h localhost -U madar_app -d madar_legacy
```

Deterministic baseline query:

```sql
SELECT
  (SELECT COUNT(*) FROM customers) AS customers,
  (SELECT COUNT(*) FROM shipments) AS shipments,
  (SELECT COUNT(*) FROM shipment_events) AS events;
```

Expected baseline:

```text
10 / 50 / 150
```

Operational file integrity:

```bash
sha256sum -c ~/madar-legacy-data/manifests/source-sha256.txt
```

Scheduled-job inspection:

```bash
crontab -l
ls -lt ~/madar-legacy-data/reports/ | head
tail ~/madar-legacy-data/logs/background-job.log
```

## Independent recovery artifacts

Database backup pattern:

```bash
pg_dump -h localhost -U madar_app -d madar_legacy -F c \
  -f ~/madar-backups/madar_legacy_pre_migration.dump
pg_restore --list ~/madar-backups/madar_legacy_pre_migration.dump | head
sha256sum ~/madar-backups/madar_legacy_pre_migration.dump
```

Operational-file backup pattern:

```bash
tar -czf ~/madar-backups/madar_operational_files_pre_migration.tar.gz \
  -C ~/madar-legacy-data exports reports manifests

tar -tzf ~/madar-backups/madar_operational_files_pre_migration.tar.gz | head
```

Final VM-import safety dump used in the current execution:

```bash
sudo -u postgres pg_dump -Fc madar_legacy -f /tmp/madar_legacy_final.dump
sudo mv /tmp/madar_legacy_final.dump /home/madaradmin/madar_legacy_final.dump
sudo chown madaradmin:madaradmin /home/madaradmin/madar_legacy_final.dump
pg_restore -l /home/madaradmin/madar_legacy_final.dump | head -20
```

Observed: custom-format PostgreSQL 16.14 archive with 27 TOC entries and the expected application tables.

## VM Import/Export compatibility preparation

These changes were introduced only after the MGN path was blocked and VM Import/Export became the accepted rehost mechanism.

### Driver checks

```bash
modinfo ena | head
modinfo nvme | head
modinfo xen_blkfront 2>/dev/null | head
lsinitramfs /boot/initrd.img-$(uname -r) | \
  grep -E '/(ena|nvme|xen_blkfront)\.ko' | head
```

Purpose: verify EC2-relevant network/storage support before exporting the guest.

### Preserve network/boot configuration

```bash
sudo cp /etc/default/grub /etc/default/grub.pre-aws
sudo cp -a /etc/netplan /etc/netplan.pre-aws
```

### Interface naming

GRUB configuration:

```text
GRUB_CMDLINE_LINUX="net.ifnames=0"
```

Netplan:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
```

Generate configuration:

```bash
sudo update-grub
sudo netplan generate
```

The change was activated by reboot rather than applying an `eth0` Netplan configuration while the live VMware NIC was still named `ens33`.

### Post-reboot validation

```bash
ip -br addr
ip route
ping -c 3 8.8.8.8
getent hosts aws.amazon.com | head
```

Observed:

```text
eth0 UP 192.168.14.128/24
default via 192.168.14.2
Internet pass
DNS pass
```

### Ensure services start on boot

```bash
sudo systemctl enable ssh
systemctl is-enabled ssh
systemctl is-active ssh
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Expected/observed:

```text
SSH        enabled / active
PostgreSQL enabled / active
```

### Bootloader check

```bash
sudo grub-install --recheck /dev/sda
sudo update-grub
```

Observed:

```text
Installing for i386-pc platform.
Installation finished. No error reported.
```

### Final source health

```bash
systemctl --failed --no-pager
ls -lh /boot/vmlinuz-$(uname -r) /boot/initrd.img-$(uname -r)
ls -lh /home/madaradmin/madar_legacy_final.dump
```

No failed services were observed.

## Clean shutdown rule

After the final validation and database safety dump:

```bash
sudo shutdown -h now
```

Do not make additional workload changes after the final image baseline unless the export is intentionally invalidated and repeated.

## Security notes

- never commit `.pgpass`, `.env`, passwords, dumps, VM images or private keys,
- `.pgpass` must remain restricted to its owner,
- database and VM artifacts contain state and are handled as sensitive migration data,
- source-side backups remain outside Git,
- configuration changes used for cloud compatibility are documented with rollback copies.