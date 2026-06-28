# ADR-001: Four platform surfaces

**Status:** accepted  
**Date:** 2026-06-27  
**Context:** Parallel platform sprints (0–7) require hard service boundaries so streams merge without coupling.

## Decision

The platform comprises **four separable surfaces**, each with its own artifact trail:

| Surface | Artifact | Scoring? |
|---------|----------|----------|
| **Index** | `harness/scoring.py`, `contract/risk_model.json` | Yes — deterministic E×P→MoS |
| **Knowledge** | `contract/knowledge/graph.json`, citations | No — evidence only |
| **Pricing** | `harness/pricing/`, `contract/products/pricing/` | Yes — premium math only |
| **Active Availability** | Telemetry + alerts + embed API | No — mitigation events; may link to policies |

## Consequences

- No premium formulas in `risk_model.json`.
- No MoS computation in pricing or document-AI pipelines.
- Active Availability may call index and pricing APIs but does not mutate scores inline.
- Each surface deployable independently behind IC-04 / IC-06 / IC-07.

## References

- `PLATFORM_ARCHITECTURE.md` §1
- `PARALLEL_EXECUTION.md` §3
