# Thesis research architecture (T1–T5)

Five Ciridae-framed investigations. Each track has **contract inputs**, **agent enrichment batches**, and a **deterministic report** — agents enrich data; `thesis_research.py` computes findings (no LLM in the report path).

Registry: `data/thesis/manifest.json`

## Tracks

| ID | Question | Contract inputs | Agent batch | Report |
|----|----------|-----------------|-------------|--------|
| **T1** | MoS lift when assessed book → disclosed GWP | `book_inputs.json`, `measure_book.py` | `batches/T1_book_mining.json` | `T1_measurement_lift.md` |
| **T2** | Who closes parametric basis risk among L1? | `trigger_inputs.json`, `measure_trigger.py` | `batches/T2_trigger_research.json` | `T2_trigger_gap.md` |
| **T3** | Constraint hotspots vs non_firm on L3 | `asset_geo_tags.json`, `l3_research/` | `batches/T3_geo_tags.json` | `T3_grid_constraint.md` |
| **T4** | Carrier MoS vs linked-asset mean | `entity_links.json`, `profiles.json` | `batches/T4_entity_links.json` | `T4_portfolio_divergence.md` |
| **T5** | Whitespace: optionality or thin evidence? | `entity_copy.json`, provenance | `batches/T5_whitespace_audit.json` | `T5_whitespace_evidence.md` |

## Data flow

```
Agent batches (data/thesis/batches/T*.json)
        ↓ apply_thesis_batches.py --apply
contract/*.json  (book, trigger, geo, links)
        ↓ integrate_entities.py          ← banks book + trigger into records.json
        ↓ measure_book.py --live
        ↓ measure_trigger.py --live
        ↓ score_and_validate.py
records.scored.json
        ↓ thesis_research.py             ← counterfactual T1 uses l1_research anchors
data/thesis/T*.json + T*.md + THESIS_SUMMARY.md
        ↓ build_frontend.py              (optional site refresh)
```

**T1 counterfactual:** research book anchor from `data/l1_research/batch*.json` vs disclosed GWP rating from `book_inputs`. Rescores with only `book_concentration` swapped (latent path) so ΔMoS isolates book measurement lift.

**T4 links:** `entity_links.json` supersedes legacy `asset_coverage_links.json` for thesis analysis. Portfolio mean comes from `site/data/profiles.json`.

## Commands

```bash
# Status — tracks, batch presence, report timestamps
python3 harness/thesis_orchestrator.py status

# Merge agent batches into contract (dry-run without --apply)
python3 harness/apply_thesis_batches.py
python3 harness/apply_thesis_batches.py --apply

# Full enrichment → measure → report pipeline
python3 harness/thesis_orchestrator.py apply all

# Reports only (after score)
python3 harness/thesis_research.py           # all five
python3 harness/thesis_research.py --t3      # single track
```

## Agent deployment pattern

One subagent per track (or per batch within a track):

1. Read contract + scored records for gaps
2. Write **sourced** rows only to `data/thesis/batches/T*_*.json`
3. Parent runs `apply_thesis_batches.py --apply` + `thesis_orchestrator.py apply`
4. Human reads `data/thesis/THESIS_SUMMARY.md`

Batch shapes:

```json
// T1 / T2
{ "inputs": { "<entity_id>": { ... } } }

// T3
{ "entities": { "<entity_id>": { "dno", "constraint_zone", "sources", "rationale" } } }

// T4
{ "links": { "<entity_id>": { "covered_assets", "link_type", "confidence", "sources" } } }

// T5
{ "entities": { "<entity_id>": { "classification", "measured_pct", "verdict" } } }
```

## Current headline results (2026-06-27)

- **T1:** 22 disclosed books; mean ΔMoS **+8.5** (disclosure lowers concentration vs research anchor); 5 quad flips
- **T2:** 14/39 L1 close trigger gap; 25 wide gap
- **T3:** Hotspot nf **2.67** vs other tagged **1.40** (n=9 vs 15)
- **T4:** Mean |carrier − portfolio| **20.6** pts; 26 large divergences
- **T5:** Whitespace mean measured **12.2%**; 62% thin (<20%)

## Open enrichment

| Track | Gap |
|-------|-----|
| T1 | 13 carriers in `book_inputs` carrier list without named energy GWP (reinsurers, SFCR-only) |
| T2 | 13 L1 still missing from `trigger_inputs` |
| T3 | Register refs added for hotspots; demand-side ECR rows sparse for SSEN DC |
| T4 | Expand named links beyond 17 carriers |
| T5 | Re-run after L5 measured share rises |

## Related

- Profile passes: `contract/PROFILE_ORCHESTRATION.md`
- Measurement / L5 gate: `harness/measure_orchestrator.py`
- Entity analysis: `contract/ENTITY_ANALYSIS_ARCHITECTURE.md`
