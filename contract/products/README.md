# NFRI product layers

| Layer | Question | Spec | Harness |
|-------|----------|------|---------|
| **Index** | Who is exposed / prepared? | `contract/MODEL_SPEC.md` | `harness/scoring.py`, `harness/evals.py` |
| **Pricing** | Fair premium / trigger / payout? | `contract/products/pricing/` | `harness/pricing/` |
| **Commercial** | Ready to sell / file / benchmark? | `contract/products/commercial_offerings.json` | `harness/product_readiness.py` |
| **Governance** | IOSCO-grade administrator? | `contract/products/governance/` | `product_readiness.py` (IG*) |

Master map: `PRODUCT_SCAFFOLD.md`

## Commercial offerings (readiness gates)

| ID | Offering | Populate via |
|----|----------|--------------|
| `OFFERING-PARAMETRIC-FILED` | Rated parametric + filed premium | `commercial/premium_filing.json`, `wordings/`, `actuarial_signoff.json`, pricing Stage 3, `loss_pairs.json` |
| `OFFERING-CURTAILMENT-SCALE` | Curtailment cover at scale | live ingest, L3 measured `non_firm`, `trigger_enforceability.json`, `basis_risk_monitoring.json` |
| `OFFERING-MARKET-ALTERNATIVE` | vs Nimbus / Parametrix | `capacity_ledger.json`, `loss_ratio.json`, `price_benchmark.json`, `distribution.json` |
| `OFFERING-IOSCO-BENCHMARK` | IOSCO-grade index | `governance/benchmark_governance.json`, `governance/index_history/` |

```bash
python3 harness/product_readiness.py
python3 harness/run_loop.py --check   # includes commercial readiness (informational)
```
