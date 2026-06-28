# ADR-002: Value-chain seat on insurance entities

**Status:** accepted  
**Date:** 2026-06-27  
**Context:** Felix value-chain decomposition (risk × distribution × pricing × balance sheet) is encoded in NFRI stress tests as structural invariants.

## Decision

Every insurance-facing record carries `value_chain_seat`:

```
asset | mga | broker | carrier | reinsurer
```

Layer-3 facilities use `asset`. L1–L2 entities use their operational seat. Stress tests assert seat-appropriate sub-factor ordering (e.g. brokers lower `capital_reinsurance` than carriers).

Schema: `contract/platform/schemas/facility.schema.json`  
Industry mapping: `contract/MODEL_SPEC.md` §8.1 (`IND-VALUECHAIN`, `IND-BROKING`, `IND-BROKER-CHAIN`)

## Consequences

- Graph edges include `placement`, `cedant_exposure`, `accumulation_group`.
- CSaaS embed (Sprint 6) routes through `broker_id` on policy linkage — no consumer-direct bypass.
- Facility ontology links to NFRI `entity_id` without duplicating scored records.

## References

- `contract/stress_tests.json` — `PLACEMENT-CHAIN-INTEGRITY`, `MGA-CAPITAL-PULL`
