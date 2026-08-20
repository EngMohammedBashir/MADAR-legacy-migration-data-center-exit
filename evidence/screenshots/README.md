# Phase 03 — Final Cutover & Closeout Screenshots

This folder contains the curated closeout screenshots for the final migration story. Historical execution evidence remains in the parent `evidence/` directory so existing technical references stay stable.

## Final reviewer sequence

| # | Evidence | What it proves |
|---|---|---|
| 1 | [Before cutover — on-premises dashboard](../before-cutover-on-premises-dashboard.png) | Application was still presented as the legacy/on-premises estate before final cutover. |
| 2 | [Browser pre-cutover validation](../browser-pre-cutover-validation.png) | User-facing application remained reachable immediately before the final switch. |
| 3 | [After cutover — AWS dashboard](../after-cutover-aws-dashboard.png) | Same workload was serving successfully after the application database configuration was switched to AWS/RDS. |
| 4 | [Local PostgreSQL disabled — RDS proof](../local-postgres-disabled-rds-cutover-proof.png) | Local PostgreSQL was stopped while Flask health and business summary remained healthy, independently proving the application no longer depended on the local database. |
| 5 | [Final AWS cleanup audit](../final-aws-cleanup-audit.png) | Temporary EC2/RDS/DMS/EBS/network resources were removed while selected recovery/data assets were intentionally retained. |

## Why links instead of duplicated binaries?

The uploaded PNGs remain in `evidence/` as the canonical binary artifacts. This subfolder is the curated reviewer path: it organizes the final screenshots without duplicating large image blobs or breaking existing links.

## Final retained assets

The closeout audit intentionally retained:

- imported AMI `ami-0cbd2e9ec0d6f9168`,
- backing EBS snapshot `snap-0920a020c47fb6447`,
- operational-data bucket `madar-operational-files-197821101770`.

Temporary migration infrastructure was removed after acceptance.