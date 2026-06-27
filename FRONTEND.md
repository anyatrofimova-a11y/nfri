# FRONTEND.md — how the site is built (data vs presentation)

The NFRI site has **two layers that compose**, not two competing frontends. This file records
the split so it doesn't get re-litigated, and the one rule that keeps Cowork and Cursor from
colliding.

## The split

| Layer | Owns | Files |
|---|---|---|
| **Data + content + evidence** | Records → payload, scoring read-through, live facts, the honest publication-gate number, all narrative content, citations, charts, register discipline | `harness/build_frontend.py` (data half: `load_records`, `build_points`, `compute_facts`, `compute_charts`, `authoritative_share`), `harness/build_essays.py` (contracts → HTML, `{{cite}}`/`{{fact}}` tokens, numbered bibliography, SVG charts), `contract/{argument,analysis,findings,methodology,data}.json`, `contract/voice.json`, `harness/style_check.py` |
| **Presentation + interaction** | Visual system, page shell, motion, chrome, multi-page roadmap | `harness/frontend/` (`assemble.py`, `template.py`, `css.py`, `chrome.py`, `client.py`, `styles/`), `harness/design_system.py`, `contract/design_system.json` |

`harness/frontend/ARCHITECTURE.md` is the authority for the presentation layer. This file is the
authority for the seam between the two.

## The seam (one integration point)

`build_frontend.main()` computes everything in the data layer, then hands it to the presentation
layer in a single call:

```python
html = assemble_page(
    ds=design_system, payload=payload, essays=essays,
    foundations=foundations, prose_css=ESSAY_CSS, fonts_url=fonts_url,
)
```

- `payload` — points, cut-lines, evals, `share`, graph, cites, rail, `n` (data layer)
- `essays` — `{argument, analysis, findings, methodology, data}` rendered by `build_essays` (data layer)
- `foundations` — the numbered bibliography (data layer)
- everything visual — tokens, zones, chrome, client JS (presentation layer)

If you add a **section**: author/edit its `contract/*.json`, render it via `build_essays`, then add
its slot in `template.py` + wire it in `assemble.py`. If you add a **visual primitive**: it goes in
`styles/` via the `css.py` pipeline — never inline `<style>` in `template.py`, never CSS in
`build_frontend.py`.

## The honest gate number

The banner share is computed by `authoritative_share(records)` in `build_frontend.py` —
weight-adjusted measured/disclosed share **computed directly on the rendered universe** (reads the
true tiers from `data/records.measured.json`). Do **not** revert this to reading a number out of
`data/eval_report.txt`: that report can be computed on a different entity cohort and will show a
stale/wrong-universe figure (this already happened — it showed 43% for a 44-entity cohort while the
real 115-entity figure was 16%). One universe, one number, computed on what's on screen.

## The one rule: don't both edit the seam at once

`build_frontend.py` and `build_essays.py` are the shared seam. They are the **only** files both
sides touch. Concurrent edits there are what cause the merge/lock churn.

- **Cowork (data/content):** owns `build_essays.py`, the essay/voice contracts, `compute_*`,
  `authoritative_share`, `style_check.py`. Edit these freely.
- **Cursor (presentation):** owns everything under `harness/frontend/`, `design_system.py`,
  `design_system.json`. Edit these freely.
- **`build_frontend.py` (the seam):** change it **one side at a time**. Pull, make the change,
  rebuild, commit, push — before the other side touches it. If both need a change, say so in the
  commit and let the other rebase rather than edit in parallel.

## Build + verify

```bash
python3 harness/build_frontend.py        # data + essays → assemble → site/index.html (+ design-system.html)
python3 harness/style_check.py           # register lint on the essay contracts (all should pass)
# sanity:
grep -c "{{cite:\|{{fact:" site/index.html                              # → 0 (all tokens resolved)
grep -ric "felix\|ciridae\|stocker\|ai-transformation" site/ contract/ harness/   # → 0 (no external names)
```

## Non-negotiables

1. **No synthetic data.** Every rating is measured / disclosed / derived / assessed; assessed is
   marked; nothing below the 60% gate is published as a measurement (banner reads PROVISIONAL).
2. **No external names on the surface.** No author/firm/index names in anything under
   `site/`, `contract/`, or `harness/`. The register is described abstractly in `contract/voice.json`.
3. **Content lives in contracts, never in HTML.** Edit the JSON; the HTML is generated.
