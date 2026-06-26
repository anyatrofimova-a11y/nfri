# NFRI pricing harness (scaffold)

Implementation home for **Layer 2 — Pricing pipeline**. Index scoring stays in `harness/scoring.py`.

| Stage | Script | Status |
|-------|--------|--------|
| 1 Curtailment intensity | `curtailment_intensity.py` | not started |
| 2 Compound loss | `compound_loss.py` | not started |
| 3 Expectile payout | `expectile_payout.py` | not started |
| 4 Hybrid tower | `hybrid_tower.py` | not started |
| 5 Premium + capital | `premium_capital.py` | not started |
| Verify | `verify_pricing_spec.py` | stub (P1–P2) |
| Basis-risk monitor | `basis_risk_monitor.py` | reads `commercial/basis_risk_monitoring.json` |

**Commercial offerings:** `harness/product_readiness.py` (parent harness)

```bash
python3 harness/pricing/verify_pricing_spec.py
```

Spec: `contract/products/pricing/PRICING_MODEL_SPEC.md`
