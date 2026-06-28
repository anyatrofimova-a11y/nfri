# On Non-Firm Risk — thesis page architecture

Long-form thesis page mirroring [a public long-form thesis index]: manifesto prose **interleaved with embedded interactive charts** that carry the argument, culminating in **carrier-level** and **product/transformation** sections.

Companion: `ENTITY_PROFILES.md` (drill-down), `contract/on_transformation.json` (content contract), `PRODUCT_MODEL.md` §1–5.

---

## 1. Reference page anatomy (on-transformation)

Single scrolling essay (~15 embedded charts). Fixed **Contents** nav. Section flow:

| § | Heading | Viz | Argument job |
|---|---------|-----|--------------|
| — | ON TRANSFORMATION | — | Title, authors, date |
| 1 | INTRODUCTION | — | Phase shift narrative; link to prior essay |
| 2 | DURABILITY / OPPORTUNITY | — | Define D1–D5, O1–O4 (text rubric) |
| 3 | 5,425 COMPANIES: THE FOUR QUADRANTS | **Interactive scatter** | Universe on 2×2; quadrant counts; click dot |
| 4 | MARGIN OF SAFETY VS PUBLIC COMP RETURNS | **Regression scatter** | MoS predicts comps; slope + R² + CI inline |
| 5 | MARGIN OF SAFETY BY VERTICAL | **Clickable bar chart** | 26 verticals; click bar → filter |
| 6 | FIRM-LEVEL DATA | — | Section break |
| 7 | MoS vs comp returns (firm) | **Scatter, n=95** | Firm aggregation; dot size = portfolio |
| 8 | DIVERSIFIED FIRM'S PROBLEM | **Swarm + firm selector** | Per-firm asset dots; click → company |
| 9 | PORTFOLIO SPLIT BY FIRM | **Stacked bar, top 50** | Quadrant % by fund |
| 10 | WHY NOW | — | Close; Hail Marys in play |

**Design grammar:** editorial typography (Playfair-style display + prose column), `H2`/`H3` all-caps kickers, pull quotes, chart titles as `H3`, stats under chart (slope, R², n).

---

## 2. NFRI page: ON NON-FIRM RISK

**URL:** `site/on-non-firm-risk.html` (static sibling) or `index.html#on-transformation` (phase 1 anchor)

**Title:** ON NON-FIRM RISK · The Non-Firm Power Insurance Risk Index

**Voice:** `contract/voice_guide.json` + manifesto register (market-essay register + eval rigor).

### Section map (1:1 with reference structure)

| § | NFRI heading | Viz | Data source |
|---|--------------|-----|-------------|
| — | ON NON-FIRM RISK | — | `on_transformation.json` meta |
| 1 | INTRODUCTION | — | Blocks from `argument.json` lead + `manifesto.json` cinematic |
| 2 | EXPOSURE | — | `contract/rubric.json` exposure sub-factors E1–E5 |
| 3 | PREPAREDNESS | — | Rubric P1–P5 |
| 4 | **N ENTITIES: THE FOUR QUADRANTS** | Live scatter (readonly) | `D.pts`, median cuts from `D.cal` |
| 5 | **MARGIN OF SAFETY VS MEASURED SHARE** | Regression scatter | x = MoS, y = measured%; annotate R² |
| 6 | **MARGIN OF SAFETY BY LAYER** | Bar chart | L1 carrier / L2 MGA+broker / L3 asset / L4 reinsurer |
| 7 | **MARGIN OF SAFETY BY BOOK SEGMENT** | Bar chart (clickable) | energy / DC / parametric / marine — tag entities |
| 8 | CARRIER-LEVEL DATA | — | Section kicker |
| 9 | MoS vs measured (carriers only) | Scatter L1 | Same as §5 filtered L1 |
| 10 | **THE DIVERSIFIED CARRIER'S PROBLEM** | Swarm + carrier select | Per-carrier linked L3 MoS dots |
| 11 | **BOOK SPLIT BY CARRIER** | Stacked bar top N | Quadrant % per carrier (reference portfolio split) |
| 12 | **THE TRIGGER GAP** | Before/after diagram | Damage-BI vs parametric availability (static SVG) |
| 13 | ON TRANSFORMATION | — | Product / new cover thesis |
| 14 | NEW COVER RAIL | Product cards | Marsh Nimbus, Aon DCLP, Parametrix, Princeps wedge |
| 15 | WHY NOW | In-force rail embed | CMP434/448, queue stats |
| 16 | EVAL BEFORE PUBLISH | L0–L8 chips | Same as index status |

§13–14 are **NFRI-specific** — the reference closes on market timing; we close on **the cover that does not exist yet** and the index as wedge to write it.

---

## 3. Chart primitives (reuse + extend)

### Already in NFRI

| Primitive | Location | Reuse |
|-----------|----------|-------|
| 2×2 scatter | `client.py` `drawScatter` | Embed with `data-readonly="1"`, smaller viewBox |
| Tier / quadrant bar | `build_essays.py` `_chart_tiers`, `_chart_quadrants` | Static in prose sections |
| In-force rail | `client.py` rail | Embed §15 |
| Eval chips | `client.py` evals | Embed §16 |

### New primitives (add to `client.py` + `compute_charts`)

| ID | Type | Spec |
|----|------|------|
| `mos_regression` | Scatter + trendline | Each dot = entity; x=MoS, y=measuredShare or proxy; show slope, R², n |
| `mos_by_layer` | Horizontal bar | Mean MoS per layer; error bar = std dev |
| `mos_by_segment` | Bar + click | Segment tag on entity; click → filter scatter |
| `carrier_swarm` | Dot strip | Select carrier; plot linked assets on MoS axis; firm avg dashed |
| `carrier_quad_stack` | Stacked bar 100% | Top 20 carriers by linked asset count |
| `trigger_gap` | Static SVG | Two-column: damage trigger path vs curtailment path |

**Stats annotation pattern** (copy reference):

```
Slope: +0.42% per point
95% CI: [+0.40, +0.44]
R²: 0.33
(n = 118)
```

Compute in Python (`compute_charts` or `compute_regressions`) → pass in payload as `D.thesisCharts` to avoid client-side stats bugs.

---

## 4. Content contract

**File:** `contract/on_transformation.json`

Same block grammar as `argument.json` / `analysis.json`, plus new block types:

```json
{ "type": "toc", "items": ["introduction", "exposure", "..."] }
{ "type": "section", "id": "introduction", "kicker": "INTRODUCTION" }
{ "type": "viz", "chart": "quadrant_scatter", "caption": "...", "readonly": true }
{ "type": "viz", "chart": "mos_regression", "x": "mos", "y": "measured_share" }
{ "type": "viz", "chart": "carrier_swarm", "default_carrier": "beazley" }
{ "type": "product_rail", "products": ["BROK-MARSH-NIMBUS", "MGA-PARAMETRIX-SLA"] }
```

Render pipeline:

```
contract/on_transformation.json
 → build_essays.render_section(..., ctx={ charts: compute_charts, thesis: compute_thesis_charts, facts })
 → harness/build_on_transformation.py
 → site/on-non-firm-risk.html
```

Or: single `build_frontend.py --pages index,on-transformation` emitting both HTML files from shared CSS/JS bundle.

---

## 5. Page shell (separate from index)

On-transformation uses **editorial layout** — full-bleed prose, not gray panel sections:

```html
<body class="site site--thesis">
 <nav class="thesis-toc">…</nav>
 <article class="thesis-article">
  <header class="thesis-masthead">…</header>
  <!-- rendered blocks -->
 </article>
</body>
```

CSS: new file `harness/frontend/styles/thesis.py` imported from `css.py`:

- Narrow prose column (~42rem) centered
- Charts break out to ~960px `.thesis-wide`
- Sticky TOC left rail on desktop (reference `H4 Contents`)
- Same tokens as index — one design system

JS: load shared bundle + `thesis.js` region:

- `initThesisCharts` — mount interactive viz from `D.thesisCharts`
- `initThesisTOC` — scroll-spy section links
- Profile clicks from swarm → `#/carrier/{id}` (see ENTITY_PROFILES.md)

---

## 6. Transformation / new product section (§13–14)

This is the **Princeps wedge** — not in the reference, but the logical close:

**Prose beats:**

1. The index maps **who** carries non-firm risk and **who** can underwrite it.
2. The gap between them is not a hazard score problem — it is a **wording and trigger** problem.
3. Parametric availability, SLA mirrors, and curtailment indices exist in fragments (product rail cites).
4. No carrier yet holds the **full stack**: register-native measurement + basis-minimised trigger + aggregation-aware pricing.
5. The index is the due-diligence instrument for writing that cover — eval-gated, register-measured.

**Viz:**

- **Product rail** (horizontal cards) — same component as index `#rail` but filtered to broker/MGA products
- **2×2 with "whitespace" highlighted** — animated or filtered view showing deployable capacity
- Optional: **five-lever stack** from `manifesto.json` `industrial_steps` as numbered figure

---

## 7. Navigation integration

| From | To |
|------|-----|
| Index nav | "On non-firm risk" → `/on-non-firm-risk.html` |
| Manifesto Part II | Same link |
| Carrier profile | "See thesis" → on-transformation §8 |
| on-transformation swarm dot | Carrier / asset profile |

Update `chrome.py` nav:

```python
("On non-firm risk", "on-non-firm-risk.html"), # or #on-transformation
```

---

## 8. Implementation phases

### Phase A — Static thesis (ship narrative + static charts)

- `contract/on_transformation.json` with intro + rubric + static tier/quadrant charts
- `build_essays` renders prose; no interactive embeds yet
- Separate HTML page, shared CSS

### Phase B — Embedded live scatter + regression

- `compute_thesis_charts` in build_frontend
- Client embeds readonly scatter + mos_regression
- Publication gate banner on thesis page too

### Phase C — Carrier-level block

- Requires `ENTITY_PROFILES` asset links + `carrier_swarm` + `carrier_quad_stack`
- Carrier selector dropdown (top 20 by name)

### Phase D — Product / transformation close

- Product rail block type
- Cross-link to KG nodes and contract citations

---

## 9. Data prerequisites

| Chart | Minimum data |
|-------|----------------|
| MoS regression | Measured share per entity (needs blend in scored records) |
| By layer | `layer` field populated |
| By segment | Entity tags in `contract/entity_tags.json` (new) |
| Carrier swarm | `asset_link` or `contract/carrier_assets.json` edges |
| Quad stack | Linked assets with scores |
| Book split | `book_inputs.json` disclosed GWP for ≥6 carriers (publication gate) |

**Segment tags (new contract):** map `entity_id` → primary segment for bar chart:

```json
{ "beazley": ["renewable", "parametric"], "marsh": ["broker", "dc_facility"] }
```

---

## 10. Success criteria

A reader landing on `/on-non-firm-risk` should:

1. Understand Exposure × Preparedness without opening methodology
2. See the **whole universe** on one interactive scatter (reference §3)
3. Believe the **MoS metric correlates with something measurable** (reference §4 — we use measured share / disclosed book)
4. Drill into **at least one carrier** and see linked assets (reference §8)
5. Leave with the **transformation thesis** — index as wedge to new parametric availability cover

Match reference **visual density**: target ≥8 embedded figures on first publish, ≥12 when carrier block ships.
