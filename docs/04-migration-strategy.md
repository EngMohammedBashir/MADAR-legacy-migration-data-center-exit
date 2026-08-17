# Migration Strategy Framework

No component receives a strategy merely because a particular AWS service would look impressive.

## Strategy vocabulary

Consider the appropriate migration disposition per component: rehost, replatform, refactor, repurchase, relocate, retain, or retire.

## Initial hypotheses — not final decisions

| Component | Initial hypothesis | Why not final yet |
|---|---|---|
| Shipment application | Rehost or modest replatform | Runtime/dependency discovery incomplete |
| Database | Replatform candidate | Compatibility, cost and migration mechanics must be tested |
| Operational files | Replatform candidate | Access semantics and path/permission dependencies unknown |
| Batch job | Replatform/refactor candidate | Job behavior and coupling must be measured |
| Corporate directory | Retain temporarily | Identity modernization belongs to a justified later phase unless migration requires it now |
| Obsolete components | Retire where proven unused | Usage evidence required |

## Decision criteria

Score options against:

- migration speed,
- downtime,
- compatibility,
- operational burden,
- security,
- recoverability,
- scalability,
- cost,
- lock-in/trade-offs,
- future modernization path.

## Anti-pattern

`Legacy VM → EC2` is not automatically a migration strategy. It is one possible implementation of rehosting and may simply move technical debt to a different building.

## Required output

Before AWS implementation, create an ADR recording the chosen strategy for the workload and the alternatives explicitly rejected.
