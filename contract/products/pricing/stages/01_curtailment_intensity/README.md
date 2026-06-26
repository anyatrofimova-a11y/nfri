# Stage 1 — Curtailment intensity

**Status:** scaffold  
**Spec:** `PRICING_MODEL_SPEC.md` § Stage 1

## Question
What is P(curtailment) and E[MW curtailed | event] by site/zone?

## Primary citations
- `ACAD-BOEHME-NONFIRM` — OPF curtailment simulation
- `ACAD-DESANTI-FCA-QUEUE` — ProRata / LIFO allocation rules
- `NESO-TEC`, `DCUSA-ECR` — register fields
- `ACAD-DAMICO-WIND` — joint generation–price template (adapt for curtailment)

## Research slots
| Slot | Content | File |
|------|---------|------|
| Literature | Non-firm curtailment predictability | `sources/.gitkeep` |
| Register mapping | TEC Gate → intensity proxy | fill in `research.md` |
| Calibration | Historical constraint events | `data/` when available |

## Outputs (when built)
`curtailment_frequency`, `curtailment_severity_mwh`, `curtailment_duration_hours`

---

→ Copy `_RESEARCH_TEMPLATE.md` to `research.md` and start filling.
