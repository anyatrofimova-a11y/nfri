# NFRI product scaffold

Two-layer product architecture. **Layer 1 (Index)** is built and running. **Layer 2 (Pricing)** is the scaffold below — fit research and knowledge here, then implement stage by stage.

```
Registers (TEC / ECR / filings)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
┌───────────────────┐              ┌────────────────────────────┐
│  LAYER 1 — INDEX  │              │  LAYER 2 — PRICING         │
│  (built)          │              │  (scaffold → build)        │
│                   │              │                            │
│  Knowledge graph  │──feeds──────▶│  1 Curtailment intensity   │
│  + citations      │              │  2 Compound loss N×S       │
│        │          │              │  3 Expectile payout g*     │
│        ▼          │              │  4 Hybrid tower            │
│  NFRI E×P → MoS   │──selects────▶│  5 Premium + capital load  │
│  Industry stress  │   portfolio  │                            │
└───────────────────┘              └────────────────────────────┘
```

| Layer | Question it answers | Primary artifact | Status |
|-------|---------------------|------------------|--------|
| **Index** | Who is exposed? Who can underwrite it? | `contract/MODEL_SPEC.md`, `harness/scoring.py` | Built (L5 provisional) |
| **Pricing** | What is fair premium / optimal trigger / payout? | `contract/products/pricing/` | Scaffold |

---

## How to use this scaffold

1. **Drop research** into the stage folder (`research.md` + `sources/`).
2. **Add citations** to `contract/citations.json` (stable ID).
3. **Add graph nodes** to `contract/knowledge/graph.json` (topic: `pricing_pipeline`).
4. **Wire formulas** into `contract/products/pricing/pricing_model.json`.
5. **Implement** in `harness/pricing/<stage>.py` when ready.
6. **Verify** with `python3 harness/pricing/verify_pricing_spec.py` (stub today).
7. **Commercial readiness** — `python3 harness/product_readiness.py` (four offerings; see below).

Index and Pricing share **registers** and **citations** but have **separate specs** — do not mix premium math into `risk_model.json`.

---

## Commercial offerings (readiness harness)

Four offerings that require substantial build before market. Criteria live in `contract/products/commercial_offerings.json`; artifacts in `contract/products/commercial/` and `governance/`.

| Offering | ID | Key artifacts to populate |
|----------|-----|---------------------------|
| Rated parametric + filed premium | `OFFERING-PARAMETRIC-FILED` | `loss_pairs.json`, Stage 3 calibration, `premium_filing.json`, `actuarial_signoff.json`, `wordings/trigger_schedule.json` |
| Curtailment cover at scale | `OFFERING-CURTAILMENT-SCALE` | Live L3 register pull, L5 ≥60%, `trigger_enforceability.json`, `basis_risk_monitoring.json` |
| Market alternative (vs Nimbus/Parametrix) | `OFFERING-MARKET-ALTERNATIVE` | `capacity_ledger.json` (nfri_program.bound), `loss_ratio.json`, `price_benchmark.json`, `distribution.json` |
| IOSCO-grade benchmark | `OFFERING-IOSCO-BENCHMARK` | `benchmark_governance.json`, `index_history/` (≥12 months) |

```bash
python3 harness/product_readiness.py        # human report + JSON
python3 harness/product_readiness.py --strict  # exit 1 if any offering 0% ready
```

---

## Directory map

```
contract/products/
  README.md                 ← layer overview
  index/                    ← pointers to existing NFRI index
  pricing/
    PRICING_MODEL_SPEC.md   ← human spec (fill per stage)
    pricing_model.json      ← machine-readable pipeline
    stages/                 ← one folder per pipeline stage
      01_curtailment_intensity/
      02_compound_loss/
      03_expectile_payout/
      04_hybrid_tower/
      05_premium_capital/

contract/knowledge/
  pricing/                  ← cross-cutting pricing research notes
  graph.json                ← add nodes under topic pricing_pipeline

harness/pricing/            ← implementation (stubs → code)
```

---

## Build order (recommended)

| Phase | Stage | Unblocks |
|-------|-------|----------|
| A | `01_curtailment_intensity` | Measured exposure → stochastic curtailment |
| B | `02_compound_loss` | Frequency × severity for revenue shortfall |
| C | `03_expectile_payout` | Basis-risk-minimizing parametric schedule |
| D | `04_hybrid_tower` | Indemnity cap + parametric tail product shape |
| E | `05_premium_capital` | Rate, load, reinsurance need |
| — | Index L5 → 60% | Parallel — measured data for credible portfolio selection |

---

## Links

- Index thesis: `PRODUCT_MODEL.md`
- Index formalism: `contract/MODEL_SPEC.md`
- Pricing formalism: `contract/products/pricing/PRICING_MODEL_SPEC.md`
- Knowledge graph CLI: `python3 harness/knowledge_graph.py topic pricing_pipeline`
- Collaboration: `CLAUDE_HANDOFF.md`
