---
name: deploy-research-agents
description: >
  Deploy parallel research-mining bots to harvest claims from grid registers, insurtech blogs,
  parametric products, and academic papers into contract/knowledge/research_bank.json.
  Use before refreshing analysis.json for parallel-agent depth, or when asked to mine substacks/blogs/theses.
---

# Deploy research agents (parallel-agent mining → analysis ammo)

Fan-out subagents against `contract/research_mining.json` to populate
`contract/knowledge/research_bank.json` and optional `contract/knowledge/sources/*.md` extracts.

## 0. Read first
- `contract/market_essay_style.json` — techniques + section_map (internal; never author names on site)
- `contract/research_mining.json` — source catalog, bots, parallel passes
- `contract/knowledge/research_bank.json` — existing snippets (dedupe by `id`)
- `contract/citations.json` — only use existing cite_keys or add new entries before merge
- `contract/knowledge/README.md` — graph integration path

## 1. Print manifest
```bash
python3 harness/research_mining.py --manifest
python3 harness/research_mining.py --manifest --json
python3 harness/research_mining.py --bank-summary
python3 harness/research_mining.py --prompt grid_evidence
```

Five parallel passes (run concurrently):

| Pass | Sources | Bots | Deliver |
|------|---------|------|---------|
| `essay_style` | essay-style-reference | style_archivist | style_notes + technique tags |
| `grid_evidence` | grid-registers-uk, constraint-costs, academic-nonfirm | grid_register_miner, academic_miner | definitions + economics snippets |
| `insurance_market` | instech, LMA, Swiss Re, EPIC | ndbi_miner, wording_miner, market_sizing_miner | mechanics + incumbents |
| `parametric_products` | Parametrix, Descartes, basis-risk papers | product_miner, actuarial_miner | product.json + objection |
| `field_anecdotes` | instech, dc market, constraints | anecdote_miner, commentary_miner | field_notes (anonymised) |

## 2. Fan-out (one subagent per pass)
Each subagent prompt must include:
- Full `--prompt <pass>` output from harness
- `snippet_schema.required`: id, source_id, bot, claim, cite_keys
- Tag `technique` from `market_essay_style.json` where applicable
- Set `use_in` to analysis section paths (e.g. `analysis/the_economics`)
- Hard ban: external blog author names in `claim`; no verbatim marketing copy

Return JSON:
```json
{
  "snippets": [ { "id": "...", "source_id": "...", "bot": "...", "claim": "...", "cite_keys": ["..."], "status": "candidate" } ],
  "argument_moves": ["..."],
  "style_notes": [{ "technique": "...", "nfri_application": "...", "section": "..." }]
}
```

## 3. Merge
```bash
python3 harness/research_mining.py --merge /tmp/pass_grid_evidence.json
python3 harness/research_mining.py --bank-summary
```

Promote `status: approved` snippets manually after cite verification.
Optional: add graph nodes per `contract/knowledge/README.md`.

## 4. Downstream — refresh analysis
```bash
python3 harness/agent_deploy.py --analysis --json
# Each analysis pass should pull relevant snippets by use_in
python3 harness/style_check.py --strict
python3 harness/build_frontend.py
```

## 5. Essay technique checklist (analysis opening)
Before merging analysis agents, verify opening sections include:
- [ ] `market_size_stack` (≥2 sources, dated numbers)
- [ ] `historical_canonical_parallel` (damage-BI century vs curtailment)
- [ ] `expert_disagreement_catalog` OR `open_questions_list` in objection
- [ ] `generational_taxonomy` (BI 1.0 → parametric 3.0)
- [ ] `field_notes` with anonymised placement vignettes
- [ ] `methodology_transparency` (measured share, register vs assessed)

Reference: `contract/market_essay_style.json` `section_map`.
