# Layer 1 — NFRI Index (built)

**Question:** Who accumulates non-firm power risk faster than they can underwrite it?

| Artifact | Path |
|----------|------|
| Model spec | `contract/MODEL_SPEC.md` |
| Machine model | `contract/risk_model.json` |
| Scorer | `harness/scoring.py` |
| Citations | `contract/citations.json` |
| Knowledge graph | `contract/knowledge/graph.json` |
| Stress tests | `contract/stress_tests.json`, `harness/industry_stress.py` |
| Product thesis | `PRODUCT_MODEL.md` |
| Data triage | `DATA_ORCHESTRATION.md`, `RUNBOOK_LIVE.md` |

**Outputs:** Exposure, Preparedness, Margin of Safety, quadrant, citation_ids per sub-factor.

**Feeds Layer 2:** portfolio selection (which entities/assets to price), `trigger_gap`, `non_firm_intensity`, aggregation context.

Do not add premium formulas here — use `../pricing/`.
