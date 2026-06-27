---
name: deploy-on-transformation-agents
description: >
  Deploy parallel thesis-writing bots (Felix/on-transformation pattern) to draft or refresh
  contract/on_transformation.json. Use when extending the transformation argument page,
  adding viz narrative, or running transformation agents like ai-transformation.fyi.
---

# Deploy on-transformation agents

Repeatable recipe for fanning out thesis subagents against `contract/on_transformation.json`,
using the section map, viz inventory, and parallel passes in `contract/on_transformation_writing.json`.

## 0. Read first
- `harness/frontend/ON_TRANSFORMATION.md` — page anatomy, chart primitives, phases A–D
- `contract/on_transformation_writing.json` — sections, bots, viz_inventory, felix_moves
- `contract/on_transformation.json` — live thesis contract
- `contract/voice_guide.json` — register and tone
- `PRODUCT_MODEL.md` §1–5 — index-as-wedge thesis

## 1. Print deployment manifest
```bash
python3 harness/agent_deploy.py --transformation
# or machine-readable:
python3 harness/agent_deploy.py --transformation --json
```

Three parallel passes (run concurrently):

| Pass | Bots | Target sections |
|------|------|-----------------|
| `rubric_and_intro` | historian, underwriter, actuary | Introduction, Exposure, Preparedness |
| `data_viz_narrative` | actuary, commercial_strategist, cat_modeler | Quadrants through carrier swarm |
| `transformation_close` | product_designer, regulatory_scout, commercial_strategist | On transformation, Why now |

## 2. Fan-out (one subagent per pass)
Each subagent prompt must include:
- Pass name and assigned `bot_briefs` from the manifest
- Relevant `sections[]` entries with required `viz` blocks — **do not remove viz blocks**
- `felix_moves` (wrong question, two-axis tension, universe scatter, transformation wedge)
- Hard bans from each bot's `ban` field
- Cite density: ≥1 `{{cite:KEY}}` per paragraph where factual
- Fact tokens: `{{fact:total}}`, `{{fact:l1}}` etc. for live counts

Each subagent returns **JSON blocks only** for its sections, matching block types:
`section`, `p`, `pull`, `rubric_axis`, `viz`, `breakdown_tabs`, `manifesto`, `product_rail`, `eval_gate`

**Viz rule:** prose that cites a statistic must sit adjacent to its `viz` block (same section).

## 3. Merge rules
- Preserve section order and `id` values from `on_transformation_writing.json`
- Preserve top-level `toc` and `masthead` blocks unchanged unless user requests nav changes
- `transformation` section uses `breakdown_tabs` with tabs: wedge / five levers / in market
- Do not hand-edit `site/on-non-firm-risk.html` — rebuild only via harness
- Index-as-wedge ratio ≥70% market mechanics

## 4. Verify
```bash
python3 harness/build_essays.py contract/on_transformation.json --check
python3 harness/style_check.py --strict
python3 harness/build_frontend.py
python3 -m http.server 8080 --directory site
# Open /on-non-firm-risk.html — target ≥8 embedded figures
```

Fix until style_check passes, citations resolve, and all viz mounts render.

## 5. When to re-deploy
- New chart phase ships (carrier swarm, product rail data)
- Major universe expansion changes regression stats
- User asks to deepen transformation close or why-now section

## Reference pattern
[ai-transformation.fyi/on-transformation](https://ai-transformation.fyi/on-transformation): sticky Contents,
scrolling essay interleaved with charts, MoS regression, vertical/layer bars, firm-level swarm,
transformation close. NFRI maps Durability→Exposure, Opportunity→Preparedness, comps→measured share.
