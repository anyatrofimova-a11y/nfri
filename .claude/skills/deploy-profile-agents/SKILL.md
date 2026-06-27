---
name: deploy-profile-agents
description: >
  Fan out Ciridae-depth entity profile bots — research rationales, synthesis copy, portfolio
  narratives. Use when entity profiles lack natural-language analysis, executive summaries,
  or axis rationale; or when running profile_writing.json deployment passes.
---

# Deploy profile analysis agents

Orchestrates parallel bots so every entity click reads like a full firm page.

## Read first

- `contract/PROFILE_OPTIMIZATION.md` — **optimization ladder + fan-out pattern**
- `contract/profile_writing.json` — bot roster, profile blocks
- `skills/nfri-entity-profiles/SKILL.md`

## One-command workflow

```bash
python3 harness/profile_orchestrator.py gaps      # full gap report
python3 harness/profile_orchestrator.py fanout    # N pending batches → deploy N agents
python3 harness/profile_orchestrator.py prompt entity_analysis batch1
python3 harness/profile_orchestrator.py apply all
python3 harness/profile_orchestrator.py rebuild
```

Gap report file: `data/profile_gap_report.txt`

## Deploy manifest

```bash
python3 harness/agent_deploy.py --profiles
python3 harness/bot_deploy.py --measurement   # L5 gate track (parallel)
```

## Priority ladder (fan out in parallel within tier)

| Priority | Pass | Agents |
|----------|------|--------|
| **P0** | entity_analysis batch1–3 | 3 |
| **P0** | sfcr_mining batch1–3 | 3 |
| **P1** | l4_research batch1–2 | 2 |
| **P1** | thin_rationales | 1 |
| **P2** | placements, book_mining, capital_mining | as needed |

## After batches land

```bash
python3 harness/apply_entity_analysis.py --all
python3 harness/apply_l1_patches.py data/l4_research/batch*.json
python3 harness/score_and_validate.py
python3 harness/build_frontend.py
python3 harness/profile_harness.py --strict
```

Measurement track (parallel, not blocking narrative):

```bash
python3 harness/measure_orchestrator.py apply all
```

## Verify in browser

Open `index.html#/carrier/qts-blackstone-cambois-blyth` (or any L1 carrier):

- **Analysis** paragraph at top
- Exposure / Preparedness **framework tables**
- **Axis rationale** paragraphs before sub-factor cards
- Each sub-factor card shows full **rationale** + tier + sources
