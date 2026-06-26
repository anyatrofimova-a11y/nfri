# Stage 2 — Compound loss N × S

**Status:** scaffold  
**Spec:** `PRICING_MODEL_SPEC.md` § Stage 2

## Question
What is E[L] and the tail of aggregate revenue / SLA shortfall?

## Primary citations
- `ACT-COMP-LOSS` — frequency × severity
- `ACAD-CCM-NF-LOAD` — welfare loss under curtailment rules
- `ACAD-EXPONENTIAL-PARETO-SLA-PREMIUM` — SLA long-outage tail

## Inputs from
Stage 1 — curtailment intensity

## Research slots
| Slot | Content |
|------|---------|
| Frequency model | Events/year from Stage 1 |
| Severity model | MWh × VoLL / PPA strike |
| Dependence | Grid stress correlation across sites |

→ Copy `_RESEARCH_TEMPLATE.md` to `research.md`
