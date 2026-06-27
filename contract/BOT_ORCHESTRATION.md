# Bot orchestration — measurement + profile parallel deployment

Two orchestration planes share one bot registry pattern. **Measurement bots** move L5 measured share; **profile bots** add Ciridae-depth narrative without rescoring.

## Command map

| Goal | Status | Deploy manifest | Apply + gate |
|------|--------|-----------------|--------------|
| L5 publication gate | `measure_orchestrator.py status` | `bot_deploy.py --measurement` | `measure_orchestrator.py apply all` → `gate` |
| Entity profiles | `profile_orchestrator.py status` | `bot_deploy.py --profiles` | `profile_orchestrator.py apply all` → `rebuild` |
| Essay / thesis bots | — | `agent_deploy.py --analysis` | thesis_orchestrator |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ L5 MEASUREMENT PLANE (moves blended measured share → ≥60%)       │
├─────────────────────────────────────────────────────────────────┤
│ Pass              │ Bot(s)              │ Writes                │
│ book_mining       │ syndicate_researcher│ book_inputs (Lloyd's) │
│ sfcr_mining       │ filing_analyst      │ book_inputs (SFCR)    │
│ register_pull     │ register_miner      │ non_firm measured     │
│ trigger_mining    │ trigger_researcher  │ trigger_inputs        │
│ capital_mining    │ capital_analyst     │ capital_inputs        │
│ bank_and_measure  │ (harness)           │ records.measured.json │
├─────────────────────────────────────────────────────────────────┤
│ L4 PROFILE PLANE (narrative depth — does not rescore)           │
├─────────────────────────────────────────────────────────────────┤
│ l1/l3/l4_research │ carrier/asset/…     │ records.scored        │
│ synthesis         │ profile_editor      │ entity_copy.json      │
│ portfolio         │ portfolio_analyst   │ entity_copy.json      │
│ entity_analysis   │ cover_stack_analyst │ entity_analysis.json  │
│ audit             │ data_steward        │ tier QA               │
└─────────────────────────────────────────────────────────────────┘
```

Contract sources:
- Measurement bots → `contract/measurement_writing.json`
- Profile bots → `contract/profile_writing.json`
- Entity deep dive schema → `contract/entity_analysis.json`

Batch manifests live under `data/<pass>/manifest.json`.

## Fan-out workflow

```bash
# 1. See what's blocking L5
python3 harness/measure_orchestrator.py status

# 2. Print pass schedule + batch progress
python3 harness/bot_deploy.py --measurement

# 3. Generate subagent prompt (paste into parallel Cursor agents)
python3 harness/bot_deploy.py --prompt sfcr_mining batch1
python3 harness/bot_deploy.py --prompt entity_analysis batch1

# 4. Merge + measure + gate
python3 harness/measure_orchestrator.py apply all
python3 harness/measure_orchestrator.py gate
```

## Current priorities (2026-06-27)

| Priority | Pass | Batches | Impact |
|----------|------|---------|--------|
| **P0** | sfcr_mining | 3 × 5 gate carriers | +book_concentration on 15 missing gate cohort carriers |
| **P1** | book_mining batch4 | chaucer, allied-world, ark, beat, aegis | Syndicate bank completion |
| **P2** | entity_analysis | 3 × 8 L3 assets | Profile depth (grid, cover stack, risk) |
| **P3** | capital_mining | 2 × 10 | Preparedness axis lift |
| **P4** | register_pull | L3 register re-pull | non_firm_intensity measured |

## Bot rules (all passes)

1. **No synthetic values** — omit entity if disclosure missing
2. **Scores from code** — bots write inputs/rationales only
3. **Batch output** → merge script → `apply all` — never hand-edit scored records for measurements
4. **Subagent prompt** always via `bot_deploy.py --prompt <pass> <batch>`

## Registry

Full bot roster: `contract/measurement_writing.json` + `contract/profile_writing.json`  
Pass schedule: `data/profile_passes/manifest.json`
