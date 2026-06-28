# Index narrative redesign — gstack schedule

**Problem:** `site/index.html` opens on benchmark + explore + terminal (7 chart panels) before the thesis. A first-time reader hits instruments with no story. Charts lack the ai-transformation.fyi pattern: prose → viz → annotated stats → “so what”.

**Target:** Working paper that *argues*, then *shows*. Same data, different reading order and chart chrome.

**Reference:** [ai-transformation.fyi/on-transformation](https://ai-transformation.fyi/on-transformation) — Contents nav, sequential essay, one chart per beat, inline slope/R²/n, pull quotes between viz blocks. **Grammar spec:** `contract/thesis_presentation.json`.

**Design law:** `DESIGN.md` — institutional editorial, not terminal dump. Terminal density is an *appendix*, not the front door.

---

## Premises (confirm before build)

| # | Premise | If wrong |
|---|---------|----------|
| P1 | Readers need 2–3 screens of thesis before any ranked table | Reorder alone fails; need hero + abstract on index |
| P2 | One primary viz per scroll beat beats a 7-panel grid | Terminal stays, but collapsed behind “Open analytics” |
| P3 | Every chart needs 3 sentences: what, how read, so what | Without copy contract, devs ship bare SVG again |
| P4 | `on-non-firm-risk.html` is the long thesis; index is manifesto + live slice | Don’t duplicate full 15-chart essay on index |
| P5 | Downloads / gate banner stay visible but subordinate to narrative | Move status strip below thesis hook, not above it |

---

## Current vs target information architecture

### Today (index.html)

```
Hero → status/downloads
  → Benchmark (dark terminal)
  → Explore cards
  → Terminal (7 panels)
  → Argument (abstract)      ← thesis starts here
  → Analysis → Scatter → Table → Findings → Rail → Methodology → Data → KG → Evals
```

### Target (v1)

```
Hero (title + one-line thesis + link to full essay)
  → Contents (sticky): Thesis · Universe · Rankings · Evidence · Downloads

ACT I — THESIS (prose, ~3 sections)
  1. Abstract + why now        (argument.json — already written)
  2. The frame (E×P, MoS)      + static quadrant diagram
  3. Findings frame           (four predictions listed before stats; link to #findings)

ACT II — THE UNIVERSE (one hero viz + narrative)
  4. “115 entities, four quadrants” — scatter ONLY, readonly, with prose beat:
     - What each axis means (2 sentences)
     - What the cuts mean (1 sentence)
     - What to click (1 sentence)
  5. Optional: embedded MoS-by-layer bar WITH paragraph interpreting it
     (not the full terminal grid)

ACT III — EXPLORE (progressive disclosure)
  6. Search + fund-style cards (discovery)
  7. Ranked table (MoS) — single table, not table + benchmark + terminal
  8. “Deeper analytics” accordion → benchmark rail OR terminal (pick one surface, not both above fold)

ACT IV — TRUST
  9. In-force rail (short)
  10. Methodology teaser → methodology.html
  11. Knowledge graph
  12. Eval chips + downloads footer
```

**Remove from above-the-fold:** duplicate methodology prose section (link only), full terminal grid, benchmark+terminal both visible.

---

## Chart narrative contract (new)

Add to `contract/design_system.json` or new `contract/chart_copy.json`:

Each viz block in template carries:

```json
{
  "id": "scatter_hero",
  "kicker": "THE UNIVERSE",
  "title": "Exposure vs preparedness",
  "lede": "Each dot is one scored entity. Position is the argument; colour is the quadrant.",
  "read": "Dots high on Preparedness but left on Exposure sit in whitespace — capable but under-deployed.",
  "stats": "Median cuts: exposure ≥ {cutExp}, preparedness ≥ {cutPrep}. n = {n}.",
  "so_what": "The cluster in whitespace is where parametric capacity could land first.",
  "chart": "quadrant_scatter"
}
```

Rendered pattern (ai-transformation.fyi):

1. Kicker + H2  
2. Lead paragraph (2–3 sentences)  
3. Chart mount  
4. Stats line (mono, tabular)  
5. “So what” paragraph (1–2 sentences)  
6. Optional footnote / link to methodology anchor  

**Implementation:** extend `build_essays.py` with `type: "viz"` blocks OR add `section-head` + `viz-copy` slots in `template.py` filled from JSON at build time.

---

## Phased schedule

Estimates: **human** = your review/editing time · **CC** = agent implementation in this repo.

### Phase 0 — Design lock (½ day human, ~45 min CC)

| Step | Output | gstack skill |
|------|--------|--------------|
| 0.1 | Confirm target IA (this doc) | — |
| 0.2 | Wireframe: 5 scroll beats on paper or `gstack-design-html` | `/design-consultation` |
| 0.3 | `chart_copy.json` schema + copy for scatter, regression, layer bar | `/plan-design-review` (UI scope) |

**Exit:** Approved section order + chart copy for 3 primary viz.

---

### Phase 1 — Reorder shell, no new charts (1 hr CC)

| Task | Files |
|------|-------|
| Move `#argument`, `#analysis` (teaser), `#findings` (teaser) above all panels | `template.py` |
| Move status-strip downloads below thesis hook or into footer band | `template.py`, `chrome.py` |
| Collapse `#terminal` into `<details id="analytics-deep">` default closed | `template.py`, `explore.py` |
| Hide `#benchmark` behind same accordion OR demote to tab inside accordion | `template.py` |
| Update nav / dock: Manifesto · Universe · Rankings · Evidence | `chrome.py` |
| Slim `#methodology` prose → 1 paragraph + link to `methodology.html` | `contract/methodology.json` or template |

**Exit:** Page reads thesis-first; data panels not visible until scroll ~3 screens or user expands “Analytics”.

**Verify:** `/qa` — scroll from top, confirm no benchmark before abstract.

---

### Phase 2 — Chart narrative layer (2–3 hr CC)

| Task | Files |
|------|-------|
| Add `contract/chart_copy.json` | new |
| `build_frontend.py` inject `D.chartCopy` + stats strings from payload | `build_frontend.py` |
| Render viz-copy wrapper around `#plot`, `#term-regression`, scoreboard | `template.py`, `client.py` |
| Post-render stats under charts (`term-reg-stats` pattern everywhere) | `client.py` |
| Interleave one static prose block before scatter (from argument framework cell) | already in argument.json |

**Exit:** Every above-fold chart has lede + stats + so-what visible without opening drawer.

---

### Phase 3 — De-overwhelm terminal (1–2 hr CC)

| Task | Rationale |
|------|-----------|
| Replace 7-panel grid with **tabbed analytics**: Overview · Segments · Carriers · Compare | One viz visible at a time |
| Overview tab = scatter thumbnail + regression + 1 sentence each | Ciridae density without grid shock |
| Segments tab = layer + segment scoreboards (existing) | |
| Carriers tab = swarm + quad stack | |
| Compare tab = alpha + head-to-head | |
| Default tab on first open: Overview only | |

**Files:** `template.py`, `explore.py`, `client.py` (`initIndexTerminal` → tab controller)

---

### Phase 4 — Essay integration (2 hr CC, optional human edit)

| Task | Notes |
|------|-------|
| Hero CTA: “Read the full thesis →” `on-non-firm-risk.html` | |
| Embed readonly mini-scatter on thesis page only; index links out | avoid duplicate 15 charts on index |
| Sticky Contents component on index (subset of thesis TOC) | copy from `methodology.html` / thesis pattern |
| Welcome modal (if present): point to thesis first, data second | `WELCOME_MODAL` slot |

---

### Phase 5 — Review & ship

| Step | gstack skill |
|------|--------------|
| Visual pass on `:8765` | `/design-review` |
| Scroll order + accordion behavior | `/qa` |
| Regress profiles, search, `#/carrier/` | `/qa-only` checklist |
| PR | `/ship` |

---

## gstack loop (recommended order)

```
/office-hours or this schedule (shape)
    → /plan-design-review  (IA + chart copy + progressive disclosure)
    → /plan-eng-review     (template reorder, chart_copy contract, tab refactor)
    → implement Phases 1–3
    → /design-review       (live site)
    → /qa
    → /ship
```

Optional: `/autoplan` on this file if you want CEO+Design+Eng auto-review before implementation.

---

## Success metrics

| Metric | Target |
|--------|--------|
| First content block | Thesis abstract (not benchmark) |
| Charts above fold | ≤ 1 (scatter hero) |
| Panels with narrative wrapper | 100% of visible charts |
| Terminal panels visible by default | 0 (accordion/tabs closed) |
| Time to “what is MoS?” | < 30 seconds scroll, no click |
| Duplicate methodology prose on index | Removed (link only) |

---

## NOT in scope (defer)

- Dark Bloomberg terminal skin (see `CIRIDAE_GAP.md` P1)
- NL query layer over dataset
- Merging index and `on-non-firm-risk.html` into one URL
- L5 gate / measured share work (parallel track in `CURSOR_HANDOFF_v4.md`)

---

## Immediate next action

**Phases 1–4 implemented** (2026-06-26). Verify with:

```bash
python3 harness/build_frontend.py
python3 harness/verify_index_narrative.py --strict
python3 harness/run_loop.py --check   # includes Index narrative IA gate
```

**Optional next:** Phase 5 visual QA on `:8765`, `/ship` for PR.
