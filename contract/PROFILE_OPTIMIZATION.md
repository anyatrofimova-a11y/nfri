# Profile optimization structure

How to run the remaining Ciridae-depth work at maximum parallelism without losing the score/narrative split.

## One command surface

```bash
python3 harness/profile_orchestrator.py gaps      # what's missing
python3 harness/profile_orchestrator.py fanout    # pending batches → N agents
python3 harness/profile_orchestrator.py prompt entity_analysis batch1
python3 harness/profile_orchestrator.py apply all
python3 harness/profile_orchestrator.py rebuild
```

Measurement track (L5 gate — parallel, not sequential blocker for narrative):

```bash
python3 harness/measure_orchestrator.py status
python3 harness/bot_deploy.py --prompt sfcr_mining batch1
python3 harness/measure_orchestrator.py apply all
```

Registry: `data/profile_passes/manifest.json` · Gap report: `data/profile_gap_report.txt`

---

## Current state (assessed)

| Layer | Done | Gap |
|-------|------|-----|
| **Synthesis** | 115/115 exec summary + axis rationale | — |
| **L1/L3 research** | 39 + 24 sub-factor rationales | 17 thin lines (<40 chars) |
| **Portfolio** | 39/39 L1 portfolio narrative | 111/115 missing placement chips |
| **Entity analysis** | 1/24 L3 (nscale template only) | **P0** — grid posture, risk manifestation, cover stack |
| **L4 research** | 0/17 batches | reinsurance aggregation subs |
| **L5 gate** | ~41% measured share | sfcr_mining + book_mining + register_pull |

UI already renders all blocks when data exists (`renderProfileBody` → Analysis, axis rationale, entity_analysis, sub-factors, methodology). **The bottleneck is content, not chrome.**

---

## Optimization ladder

Run passes in priority order; within each priority, **fan out all batches in parallel**.

### P0 — Credibility on asset click

**entity_analysis** (3 batches × 8 L3 assets)

- Output: `data/entity_analysis/batch{N}.json` → `apply_entity_analysis.py` → `contract/entity_analysis.json`
- Template: `entities.nscale-loughton-essex`
- Each asset: `grid_posture`, ≥2 `risk_manifestation[]`, `cover_stack`, `mining`
- Deploy: `python3 harness/bot_deploy.py --prompt entity_analysis batch1|batch2|batch3`

**sfcr_mining** (measurement — raises gate)

- Output: `data/sfcr_mining/batch*.json` → `book_inputs.json`
- Deploy: `python3 harness/bot_deploy.py --prompt sfcr_mining batch1`

### P1 — Depth + prose quality

**l4_research** (2 batches × 17 L4)

- Output: `data/l4_research/batch*.json` → `apply_l1_patches.py --all`
- Deploy: `python3 harness/bot_deploy.py --prompt l4_research batch1|batch2`

**thin_rationales** (17 sub-factors)

- Patch `data/records.scored.json` rationales in place
- Deploy: `python3 harness/profile_orchestrator.py prompt thin_rationales all`

### P2 — Discovery surface

**placements** — `generate_portfolio.py --all` → placement chips for L1/L2 from tags + KG

**book_mining** — remaining Lloyd's iXBRL batches

### P3 — Ops

**register_pull**, **audit**, **capital_mining**, **trigger_mining**

---

## Parallel fan-out pattern

```
                    ┌─ entity_analysis batch1 ─┐
gaps → fanout ──────┼─ entity_analysis batch2 ─┼──→ apply all → rebuild → profile_harness --strict
                    ├─ entity_analysis batch3 ─┤
                    ├─ l4_research batch1 ─────┤
                    ├─ l4_research batch2 ─────┤
                    └─ thin_rationales ────────┘
                              ‖ (parallel track)
                    sfcr_mining / book_mining → measure_orchestrator apply all
```

**Rule:** one subagent per batch file. Never merge batches in a single agent above batch_size from manifest.

---

## Apply chain (after batches land)

```bash
python3 harness/apply_entity_analysis.py --all
python3 harness/apply_l1_patches.py data/l4_research/batch*.json
python3 harness/score_and_validate.py
python3 harness/apply_synthesis.py --all-portfolio   # if placements generated
python3 harness/build_frontend.py
python3 harness/profile_harness.py --strict
```

---

## Exit criteria (Ciridae parity)

| Check | Target |
|-------|--------|
| L3 entity_analysis | 24/24 |
| executive_summary | 115/115 ✓ |
| sub-factor rationale | 0 under 40 chars |
| profile panel on click | Analysis + grid + risk + cover + 10 cards |
| L5 gate | ≥60% (measurement track) |

Skills: `skills/nfri-entity-profiles/SKILL.md`, `.claude/skills/deploy-profile-agents/SKILL.md`
