---
name: continuous-data-expansion
description: Orchestrate NFRI data expansion and refinement — measurement bots, profile depth, universe merge, register pulls, and site rebuild. Use when expanding entities, improving L5 gate, running parallel research batches, or refreshing the index after new data lands.
---

# Continuous data expansion

## Entry point

```bash
python3 harness/data_orchestrator.py status
python3 harness/data_orchestrator.py priority --measure   # sfcr + book auto-miner + register pull
python3 harness/data_orchestrator.py next
python3 harness/data_orchestrator.py fanout   # parallel agent batches
python3 harness/data_orchestrator.py apply all # merge + rebuild
python3 harness/data_orchestrator.py cycle --measure  # register refresh + site
python3 harness/data_orchestrator.py report   # data/expansion_status.json
```

## Two planes (never mix scoring rules)

| Plane | Moves | Orchestrator | Bots |
|-------|-------|--------------|------|
| **Measurement** | L5 gate (measured/disclosed tier share) | `measure_orchestrator.py` | `bot_deploy.py --measurement` |
| **Profile** | Narrative depth (no rescore unless inputs change) | `profile_orchestrator.py` | `bot_deploy.py --profiles` |

Unified coordinator: **`data_orchestrator.py`**. Canonical rebuild: **`publish_pipeline.py`**.

## Weekly cycle

1. **Discover** — `status` + `next` (reads `data/profile_passes/manifest.json` optimization ladder).
2. **Fan out** — one subagent per pending batch (`bot_deploy.py --prompt <pass> <batch>`).
3. **Merge** — bots write batch JSON only; harness merges:
   - Mining → `extract_book_inputs.py` / `integrate_entities.py`
   - Research → `apply_l1_patches.py` / `apply_l3_patches.py`
   - Profiles → `apply_synthesis.py` / `apply_entity_analysis.py`
4. **Measure** (optional, network) — `cycle --measure` runs `measure_all.py --live` → `records.measured.json`.
5. **Publish** — `integrate_entities.py` → `score_and_validate.py` → `build_frontend.py`.
6. **Verify** — `python3 harness/run_loop.py --check` (non-destructive gates).

## Expand universe

New researched entities arrive as JSON arrays:

```bash
python3 harness/data_orchestrator.py expand data/l1_research/batch4.json
```

This runs `integrate_entities.py` (banks disclosed inputs) then full rebuild. **Adding assessed-tier entities lowers L5 share** — expected until register tiers land.

## Publish path (do not use optimize.py for site)

The site reads **`records.json` + measured overlay + `score_all()`** (`build_frontend.load_records`).  
`records.optimized.json` is legacy; do not rebuild the public index from it alone.

Correct chain after any data change:

```bash
python3 harness/publish_pipeline.py rebuild          # bank → score → build
python3 harness/publish_pipeline.py rebuild --measure  # + live registers
```

## Priority ladder (manifest)

P0: `entity_analysis`, `sfcr_mining` — biggest Ciridae gap + gate lift  
P1: `l4_research`, `thin_rationales`  
P2: `placements`, `book_mining`  
P3: `register_pull`, `audit`

## Bot rules

1. **No synthetic values** — omit entity if disclosure missing (`contract/DATA_POLICY.md`).
2. **Scores from code** — bots write inputs/rationales/tiers only.
3. **Batch → merge script → apply** — never hand-edit `records.scored.json` for measurements.
4. Re-read target harness file before editing (concurrent agents).

## Gate metric

Blended measured/disclosed share ≥ **60%** on the **full scored universe** (115 entities).  
Current build uses evidence-tier weight share per axis (`authoritative_share` in `build_frontend.py`).

## Docs

- `DATA_ORCHESTRATION.md` — triage strategy + continuous loop
- `contract/BOT_ORCHESTRATION.md` — bot registry
- `RUNBOOK_LIVE.md` — register pull details
- `data/profile_passes/manifest.json` — pass status + batches
