---
name: nfri-frontend
description: Govern how the NFRI site is built and how Cowork and Cursor share the codebase. Use when editing build_frontend.py, build_essays.py, harness/frontend/*, the design system, or any rendering/presentation code, and before committing frontend changes. Encodes the data/presentation split, the single integration seam, and the rule that prevents the two editors from colliding.
---

# NFRI frontend

Full reference: `FRONTEND.md` (repo root) and `harness/frontend/ARCHITECTURE.md`. Design principles:
`DESIGN.md`, `contract/design_principles.json` (Gary Tan + gstack), review workflow in
`skills/nfri-design-review/SKILL.md`. This skill is the working rule set.

## Two layers that compose (not two frontends)
- **Data + content + evidence** — `build_frontend.py` (data half: records → payload, `compute_facts`,
  `compute_charts`, `authoritative_share`), `build_essays.py` (contracts → HTML, `{{cite}}`/`{{fact}}`
  tokens, bibliography, charts), the essay contracts, `voice.json`, `style_check.py`.
- **Presentation + interaction** — `harness/frontend/` (`assemble.py`, `template.py`, `css.py`,
  `chrome.py`, `client.py`, `styles/`), `design_system.py`, `contract/design_system.json`.

`build_frontend.main()` computes the data layer, then calls `assemble_page(...)` to render it. That
call is the **only** integration point.

## The honest gate number
The banner share comes from `authoritative_share(records)` — weight-adjusted measured/disclosed
share computed on the rendered universe (true tiers from `data/records.measured.json`). Never revert
it to reading a percentage out of `data/eval_report.txt`.

## The one rule: don't both edit the seam at once
`build_frontend.py` and `build_essays.py` are the shared seam — the only files both sides touch.
- Cowork owns the data/content/evidence layer; Cursor owns the presentation layer.
- Change the seam **one side at a time**: pull → edit → rebuild → commit → push, before the other
  side touches it. Concurrent edits there cause the merge/lock churn.

## Non-negotiables
1. Obey the data discipline (see `nfri-data-discipline`) — and never state those rules in rendered copy.
2. No external author/firm/index names in anything under `site/`, `contract/`, or `harness/`.
3. Content lives in contracts; the HTML is generated. No inline `<style>` in `template.py`, no CSS in
   `build_frontend.py`.

## Build / verify
```bash
python3 harness/build_frontend.py
python3 harness/style_check.py
grep -ric "felix\|ciridae\|stocker\|ai-transformation" site/ contract/ harness/   # → 0
```
