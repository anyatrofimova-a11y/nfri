---
name: deploy-findings-agents
description: >
  Deploy parallel findings-writing bots (Felix-style) to draft or refresh contract/findings.json
  using contract/findings_writing.json. Use when asked to extend "what the data shows", add
  fuller/specific findings, layer/quadrant breakdowns, or deploy findings agents like Felix.
---

# Deploy findings agents (Felix-style parallel passes)

Repeatable recipe for fanning out data-read subagents against `contract/findings.json`.
Every claim must bind to live `{{fact:KEY}}` tokens resolved at build time.

## 0. Read first
- `contract/findings_writing.json` — sections, bots, fact_catalog, macro_arc, anti_meta
- `harness/findings_facts.py` — how facts are computed from `data/records.optimized.json`
- `contract/findings.json` — current live findings section
- `contract/voice.json` — register (data-led variant: counts before interpretation)

## 1. Print deployment manifest
```bash
python3 harness/agent_deploy.py --findings
python3 harness/agent_deploy.py --findings --json
```

Three parallel passes:

| Pass | Sections | Bots |
|------|----------|------|
| `scope_and_shape` | overview, quadrant_read | quant_analyst, scope_reader, quadrant_interpreter, tail_reader, whitespace_spotter |
| `layer_and_exposed` | layer_breakdown, exposed_cluster | layer_mapper, exposed_analyst, gate_reader, skeptic |
| `honesty_close` | honesty | provisional_auditor, register_reader |

## 2. Fan-out (one subagent per pass)
Each subagent prompt must include:
- Assigned bot briefs from manifest
- Full `fact_catalog.keys` list — **only use documented keys**
- Current fact values (optional preview):
  ```bash
  python3 -c "
  import json, sys; sys.path.insert(0,'harness')
  from build_frontend import load_records, authoritative_share
  from findings_facts import compute_facts
  r,_=load_records(); share=authoritative_share(r)
  print(json.dumps(compute_facts(r,share), indent=2))
  "
  ```
- `felix_moves`: dataset as argument, two-axis tension, honest provisional, named tails
- Bans: no ranking hype, no false precision at sub-gate measured share, no harness talk

Each subagent returns JSON `blocks[]` using types: `kicker`, `h`, `lead`, `p`, `stat`, `chart`, `pull`.

## 3. Merge rules
- Section kickers must match `findings_writing.json` sections: Findings, By layer, The exposed slice, Reading it honestly
- ≥2 distinct `{{fact:}}` tokens per finding paragraph; ≥8 distinct keys across the contract
- Stat row + quadrant chart in overview (do not remove)
- Gate honesty: never infer firmness; use `gate_unknown_count` / `gate_firm_count`
- Pull quote: structure finding (exposure ≠ preparedness), not a ranking

## 4. Adding new facts
If a finding needs a figure not in `fact_catalog`:
1. Add computation to `harness/findings_facts.py`
2. Document key in `contract/findings_writing.json` `fact_catalog.keys`
3. Use in `contract/findings.json`
4. Rebuild and lint

## 5. Verify
```bash
python3 harness/style_check.py --strict   # checks fact keys + density
python3 harness/build_frontend.py         # resolves {{fact:}} at build time
python3 harness/run_loop.py --check       # full gate if data changed
```

## 6. Pair with analysis agents
- **Analysis agents** (`deploy-analysis-agents`): industry essay — why the peril exists, why incumbents miss it
- **Findings agents** (this skill): what the current slice shows — quadrants, layers, tails, honesty
- Do not duplicate industry argument in findings; do not duplicate live counts in analysis
