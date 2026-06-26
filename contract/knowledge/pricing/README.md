# Pricing pipeline — knowledge drop zone

Cross-cutting research for **Layer 2 (Pricing)**. Stage-specific notes live under `contract/products/pricing/stages/<stage>/`.

| Stage | Folder | Graph node |
|-------|--------|------------|
| 1 Curtailment intensity | `stages/01_curtailment_intensity/` | `pricing-01-curtailment` |
| 2 Compound loss | `stages/02_compound_loss/` | `pricing-02-compound` |
| 3 Expectile payout | `stages/03_expectile_payout/` | `pricing-03-expectile` |
| 4 Hybrid tower | `stages/04_hybrid_tower/` | `pricing-04-hybrid` |
| 5 Premium + capital | `stages/05_premium_capital/` | `pricing-05-premium` |

## Workflow

1. Add extract: `contract/knowledge/pricing/<topic>.md`
2. Cite in `contract/citations.json` if new source
3. Link node in `graph.json` (topic: `pricing_pipeline`)
4. Wire formula into `PRICING_MODEL_SPEC.md` + `pricing_model.json`
5. `python3 harness/knowledge_graph.py path pricing-01-curtailment pricing-05-premium`

## Index ↔ Pricing bridge

| Index sub-factor | Pricing stage |
|------------------|---------------|
| `non_firm_intensity` | Stage 1 |
| `trigger_gap` | Stage 3, 4 |
| `pricing_modelling` (index) | Stage 2, 5 |
| `aggregation_correlation` | Stage 2 (correlated loss) |
