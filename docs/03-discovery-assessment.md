# Discovery & Assessment

## Goal

Understand enough about the workload to make migration decisions with evidence rather than assumptions.

## Discovery tree

```text
Legacy workload
├── Compute
│   ├── OS/runtime
│   ├── CPU/RAM/storage
│   ├── services
│   └── startup behavior
├── Application
│   ├── ports
│   ├── configuration
│   ├── local paths
│   └── external endpoints
├── Data
│   ├── database
│   ├── files
│   ├── growth
│   └── consistency requirements
├── Identity
│   ├── users
│   ├── service identities
│   └── directory assumptions
├── Network
│   ├── inbound/outbound flows
│   ├── DNS
│   ├── firewall assumptions
│   └── partner allowlists
└── Operations
    ├── backups
    ├── batch jobs
    ├── monitoring
    ├── deployment
    └── recovery
```

## Questions to answer before target design

- Which components are tightly coupled?
- Which dependencies use hostnames versus hard-coded IP/path values?
- Which state must be consistent at cutover?
- Can the application tolerate a database endpoint change?
- Can files move independently of the database?
- Which operations require downtime?
- Which credentials or identities are machine-specific?
- What would prevent rollback?
- What can be retired rather than migrated?

## Evidence expected

Store sanitized outputs/screenshots under `evidence/` showing source configuration and baseline behavior. Do not expose secrets or unnecessary identifiers.

## Assessment output

Discovery should end with a component table containing:

`Component | Criticality | Dependencies | Statefulness | Migration strategy candidate | Downtime sensitivity | Validation method | Rollback method`
