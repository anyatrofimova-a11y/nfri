---
name: deploy-profile-agents
description: >
  Fan out Ciridae-depth entity profile bots — research rationales, synthesis copy, portfolio
  narratives. Use when entity profiles lack natural-language analysis, executive summaries,
  or axis rationale; or when running profile_writing.json deployment passes.
---

# Deploy profile analysis agents

Orchestrates parallel bots so every entity click reads like a full firm page: executive thesis,
axis rationale, score framework, and 10 sub-factor cards with sourced prose.

## Read first

- `contract/profile_writing.json` — bot roster, profile blocks, exit checks
- `contract/ENTITY_ANALYSIS_ARCHITECTURE.md`
- `skills/nfri-entity-profiles/SKILL.md`
- `skills/nfri-data-discipline/SKILL.md`

## Deploy manifest

```bash
python3 harness/profile_harness.py --check
python3 harness/agent_deploy.py --profiles
```

## Pass schedule (run in order)

1. **l1_research** — `carrier_researcher` / `syndicate_researcher` on L1 (10 entities/agent)
2. **l3_research** — `asset_researcher` on L3 assets (15/agent)
3. **l4_research** — `reinsurance_researcher` on L4
4. **synthesis** — `profile_editor` on all scored → `contract/entity_copy.json`
5. **portfolio** — `portfolio_analyst` + `placement_mapper` on L1 with linked assets
6. **audit** — `data_steward` source/tier QA

After each research pass:

```bash
python3 harness/score_and_validate.py   # 0 problems
python3 harness/apply_l1_patches.py     # or apply_l3_patches / apply_synthesis as appropriate
```

## Synthesis merge

```bash
python3 harness/apply_synthesis.py      # batches in data/synthesis/ → entity_copy.json
python3 harness/build_frontend.py       # rebuild profiles.json
python3 harness/profile_harness.py --strict
```

## profile_editor prompt shape

For each entity batch:

- Read scored record + all 10 sub-factor rationales
- Write `executive_summary` (3–4 sentences: book posture, non-firm shape, prep gap/strength, provisional caveat if assessed-heavy)
- Write `axis_rationale.exposure` and `axis_rationale.preparedness` (cite strongest measured sub-factor)
- Do NOT rewrite axis scores or MoS

## Success criteria

| Metric | Target |
|--------|--------|
| L1 executive_summary | 100% |
| Sub-factor rationale | ≥ 40 chars × 10 × entity |
| L1 portfolio_narrative | carriers with linked assets |
| profiles.json sync | rebuild after every merge |
| UI | Analysis + rationale blocks visible on click |

## Verify in browser

Open `index.html#/carrier/qts-blackstone-cambois-blyth` (or any L1 carrier):

- **Analysis** paragraph at top
- Exposure / Preparedness **framework tables**
- **Axis rationale** paragraphs before sub-factor cards
- Each sub-factor card shows full **rationale** + tier + sources
