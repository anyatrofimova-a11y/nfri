# Profile pass orchestration

Central registry for parallel profile bots. Scores stay in `harness/scoring.py`; bots write rationales and narrative overlays only.

## Pass schedule

| Pass | Status | Entities | Batch dir | Apply |
|------|--------|----------|-----------|-------|
| **l1_research** | complete | 39 L1 | `data/l1_research/` | `apply_l1_patches.py --all` → `score_and_validate.py` |
| **synthesis** | complete | 115 | `data/synthesis/` | `apply_synthesis.py --all` → `build_frontend.py` |
| **portfolio** | in progress | 39 L1 | `data/portfolio/` | `apply_synthesis.py --all-portfolio` → `build_frontend.py` |
| **l3_research** | pending | 24 L3 | `data/l3_research/` | `apply_l3_patches.py --all` → `score_and_validate.py` |
| **l4_research** | pending | 17 L4 | `data/l4_research/` | `apply_l1_patches.py` (shared merger) |
| **audit** | pending | 115 | `data/audit/` | data_steward fixes |

Registry: `data/profile_passes/manifest.json`

## Commands

```bash
# Status dashboard
python3 harness/profile_orchestrator.py status

# List batch entity ids for a pass
python3 harness/profile_orchestrator.py batches portfolio

# Generate portfolio patches (swarm narrative + placement chips)
python3 harness/generate_portfolio.py --all

# Merge + rebuild
python3 harness/profile_orchestrator.py apply portfolio
python3 harness/profile_orchestrator.py rebuild

# QA
python3 harness/profile_harness.py --strict
```

## Batch sizing

| Pass | Per subagent | Parallel agents |
|------|--------------|-----------------|
| l1_research | 10 | 4 |
| l3_research | 12 | 2 |
| l4_research | 10 | 2 |
| synthesis | 20 | 6 |
| portfolio | 13 | 3 |

## Data flow

```
records.json  ← l1/l3/l4 research patches
     ↓ score_and_validate.py
records.scored.json
     ↓ build_entity_profiles + entity_copy.json overlay
profiles.json  →  #/carrier/:id UI
```

`contract/entity_copy.json` fields:

- `executive_summary`, `axis_rationale` — profile_editor (synthesis)
- `portfolio_narrative`, `placements` — portfolio_analyst + placement_mapper

## Portfolio pass (current)

Batches follow l1 priority (flagship carriers first):

- **batch1** (13): axa-xl, beazley, hiscox, chubb, convex, zurich, munich-re, liberty, ms-amlin, tmk, canopius, brit, markel
- **batch2** (13): aspen, allianz, aviva, qbe, rsa, talbot, lancashire, inigo, chaucer, travelers, axis, allied-world, apollo
- **batch3** (13): remaining L1

Narrative: swarm min/max/mean vs carrier MoS + tail asset names.  
Placements: chips from `entity_tags.json` → KG product nodes (expand via `contract/knowledge/graph.json`).

## Next passes

1. **book_mining** — populate `contract/book_inputs.json` from Lloyd's class tables (parallel batches in `data/book_mining/manifest.json`)
2. **register_pull** — extend `ASSET_ROUTE` + `asset_boundary_map.json`; `measure_non_firm.py --live`
3. **l3_research** — deepen asset rationales (24 assets)
4. **l4_research** — reinsurance aggregation subs (17 entities)
5. **audit** — data_steward source/tier QA at scale

## Thesis research (T1–T5)

Analytical tracks (separate from profile narrative passes). Full architecture: **`contract/THESIS_ARCHITECTURE.md`**

```bash
python3 harness/thesis_orchestrator.py status
python3 harness/thesis_orchestrator.py apply all    # batches → contract → measure → reports
python3 harness/thesis_research.py --t1             # single report
```

Reports: `data/thesis/THESIS_SUMMARY.md`

## Measurement orchestration (L5 gate ≥60%)

Narrative bots do **not** move measured share. Full bot architecture: **`contract/BOT_ORCHESTRATION.md`**

```bash
python3 harness/measure_orchestrator.py status
python3 harness/bot_deploy.py --measurement
python3 harness/bot_deploy.py --prompt sfcr_mining batch1   # subagent prompt
python3 harness/measure_orchestrator.py apply all
python3 harness/measure_orchestrator.py gate
```

| Pass | Bot | Target | Priority |
|------|-----|--------|----------|
| book_mining | syndicate_researcher | book_inputs (Lloyd's) | P1 — batch3/4 remaining |
| sfcr_mining | filing_analyst | book_inputs (SFCR) | **P0** — 15 gate carriers |
| register_pull | register_miner | non_firm measured | P4 |
| trigger_mining | trigger_researcher | trigger_inputs | P3 — 4 L3 assets |
| capital_mining | capital_analyst | capital_inputs | P3 |
| entity_analysis | cover_stack_analyst | entity_analysis.json | Profile depth (23 L3) |

Highest-weight levers: `book_inputs.json` (w0.30 exposure) → `measure_non_firm` on L3 (w0.25) → capital/trigger inputs.

Contract: `contract/profile_writing.json` · Architecture: `contract/ENTITY_ANALYSIS_ARCHITECTURE.md`
