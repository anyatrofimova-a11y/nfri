# Methodology viz architecture — `#two-axes`

## Problem (before)

The **Two axes** section on `methodology.html` stacked four competing visuals in one prose column:

1. Inline formula paragraph (mixed with body text, inconsistent type scale)
2. Live quadrant scatter (`thesis-wide` negative margins bleeding into the sticky TOC)
3. Static SVG quadrant bar chart (duplicate of scatter legend)
4. MoS-by-layer bar chart (empty when JS boot failed)

Symptoms: ghost TOC labels overlapping the formula; empty gray chart mounts; redundant quadrant counts.

**Root cause:** `client.py` ran index-only boot (`#eval-chips`) on every page. On methodology, that threw before `initMethodologyPage()` → charts never mounted.

---

## Information architecture (after)

Single narrative column, no wide bleed, one chart per claim:

| Block | Role | Chart |
|-------|------|-------|
| **Prose lede** | Defines E, P, MoS, median cuts | — |
| **Formula callout** (`.meth-formula`) | Canonical axis math, isolated from TOC | — |
| **Scatter** (readonly) | Universe on E×P; quadrant counts in caption | `quadrant_scatter` |
| **Layer bars** | Where MoS concentrates by L1–L4 | `mos_by_layer` |

Removed: static `chart/quadrants` SVG — counts live in scatter caption + index.

Cross-link: scatter figure includes **Open interactive index →** (`index.html#index`).

---

## Layout rules

1. **No `thesis-wide` on methodology** — `_viz` respects `"wide": false`; charts stay inside the 42rem article column.
2. **Formula is a block type** — `formula` in `build_essays.py`, not a loose `<p>` with `<code>`.
3. **Viz lede + caption + optional link** — `_viz` renders `.meth-viz-lede`, `.ch-cap`, `.meth-viz-link`.
4. **Z-index** — `.thesis-article { z-index: 1 }`, `.thesis-toc { z-index: 2 }` so wide charts on other pages cannot paint over TOC.

---

## JS boot split

```
site--thesis      → initThesisCharts()
site--methodology → initMethodologyPage()
(default index)   → bootIndexPage()  // eval-chips, refreshIndex, terminal, nav
```

`drawThesisScatter` guards on `D.pts`, not `D.thesisCharts`.

---

## Contract shape (`methodology_tab.json`)

```json
{ "type": "formula", "expr": "...", "gloss": "..." }
{
  "type": "viz",
  "chart": "quadrant_scatter",
  "readonly": true,
  "wide": false,
  "lede": "...",
  "caption": "...",
  "link": { "label": "...", "href": "index.html#index" }
}
```

---

## Rebuild

```bash
python3 harness/build_methodology.py
python3 harness/build_frontend.py
```

Verify: open `methodology.html#two-axes` — scatter + layer bars render; no TOC overlap; no duplicate quadrant SVG.
