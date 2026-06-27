---
name: deploy-analysis-agents
description: >
  Deploy parallel analysis-writing bots (Felix-style) to draft or refresh contract/analysis.json
  using contract/analysis_writing.json methodology. Use when asked to extend the industry essay,
  run historian/economist/underwriter passes, or deploy analysis agents like Felix/ai-transformation.
---

# Deploy analysis agents (Felix-style parallel passes)

Repeatable recipe for fanning out industry-essay subagents against `contract/analysis.json`,
using the bot roster and parallel passes in `contract/analysis_writing.json`.

## 0. Read first
- `contract/analysis_writing.json` — sections, bots, macro_arc, anti_meta, felix_moves
- `contract/voice.json` — register, anti_patterns, concept_frames
- `contract/analysis.json` — current live essay
- `METHODOLOGY.md` §6 — harness loops (research → score → build)

## 1. Print deployment manifest
```bash
python3 harness/agent_deploy.py --analysis
# or machine-readable:
python3 harness/agent_deploy.py --analysis --json
```

Three parallel passes (run concurrently):

| Pass | Bots | Target |
|------|------|--------|
| `industry_substance` | historian, mechanic, economist, claims_adjuster, institutionalist | The case, economics, mechanics, incumbents |
| `model_architecture` | cat_modeler, cyber_underwriter, substrate_analyst, actuary, parametric_designer | Objection section |
| `proposal_close` | underwriter, product_designer, regulatory_scout, commercial_strategist | Proposal, value chain, re-pricing, opportunity |

## 2. Fan-out (one subagent per pass)
Each subagent prompt must include:
- Its pass name and assigned `bot_briefs` from the manifest
- The relevant `macro_arc` phases for its sections
- `felix_moves` (especially: wrong question, two-axis tension, honest provisional)
- Hard bans from each bot's `ban` field and `anti_meta` regex targets
- Cite density: ≥1 `{{cite:KEY}}` per paragraph (keys must exist in `contract/citations.json`)

Each subagent returns **JSON blocks only** matching existing `contract/analysis.json` block types:
`kicker`, `h`, `lead`, `p`, `pull`, `framework`, `layers`, `sub_factors`.

## 3. Merge rules
- Preserve section order from `analysis_writing.json` `sections[]` kickers
- Tag each paragraph internally with owning bot id (comment in `_doc` or provenance field — not rendered)
- `the_proposal`: ≤40 words of product/index meta (`product_meta_budget_words`)
- No harness/build/LLM prose (`anti_meta`)
- Industry ratio ≥85%; index is instrument not protagonist

## 4. Verify
```bash
python3 harness/style_check.py --strict
python3 harness/build_frontend.py
```

Fix until style_check passes and citations resolve.

## 5. When to re-deploy
- New regulatory rail entries (CMP434/448, GC0166)
- Major universe expansion (new L1 carriers, L3 assets)
- User asks to deepen a specific section (run single pass only)

## Reference pattern
Felix / ai-transformation.fyi: pick unscored population → encode rubric → two-axis tension →
ship dataset as argument. NFRI analysis essay is the **industry half** of that pattern;
findings agents handle the **data half** (`deploy-findings-agents` skill).
