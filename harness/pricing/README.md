# NFRI pricing harness (scaffold)

Implementation home for **Layer 2 — Pricing pipeline**. Index scoring stays in `harness/scoring.py`.

| Stage | Script | Status |
|-------|--------|--------|
| 1 Curtailment intensity | `curtailment_intensity.py` | implemented |
| 2 Compound loss | `compound_loss.py` | implemented |
| 3 Expectile payout | `expectile_payout.py` | implemented |
| 4 Hybrid tower | `hybrid_tower.py` | implemented |
| 5 Premium + capital | `premium_capital.py` | implemented |
| Quote (IC-06) | `quote.py` | audit log in `data/pricing/audit/` |
| Verify | `verify_pricing_spec.py` | P1–P6 |
| Basis-risk monitor | `basis_risk_monitor.py` | reads `commercial/basis_risk_monitoring.json` |
| Orchestrator | `../platform/phase3.py` | pipeline + exit gates |

**Commercial offerings:** `harness/product_readiness.py` (parent harness)

```bash
python3 harness/pricing/verify_pricing_spec.py
```

Spec: `contract/products/pricing/PRICING_MODEL_SPEC.md`
