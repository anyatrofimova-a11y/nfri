# Cursor handoff v2 — the whitepaper site + essay engine (Cowork → Cursor)

**Read this with `CLAUDE_HANDOFF.md`.** That doc covers the scoring harness (scoring.py,
optimize.py, evals L0–L8, the publication gate). This doc covers the **front-end as a
whitepaper**: the narrative essays, the citation/fact systems, the charts, and how it all
regenerates. The repo + git is still the only bridge between Cowork and Cursor.

| | |
|---|---|
| Repo | https://github.com/anyatrofimova-a11y/nfri · branch `framework` |
| Build the site | `python3 harness/build_frontend.py` → `site/index.html` |
| Full loop | `python3 harness/run_loop.py --full` (ingest → score → optimize → eval → build) |

---

## What changed this arc

The site is no longer a chart with a caption. It is a **narrative-led research index** — an
abstract, a sustained industry analysis that proposes the model, a live findings section, a
methodology, a data appendix, and a numbered academic bibliography — with the interactive 2×2
explorer in the middle. All long-form copy is **content-as-data**: editable JSON contracts,
rendered by one engine. **No prose is hand-written in HTML.**

### Page order (`build_frontend.py` TEMPLATE)
```
hero → Abstract(#argument) → Analysis(#analysis) → Index 2×2(#index) → Entities(#table)
     → Findings(#findings) → In-force(#rail) → Methodology(#methodology) → Data(#data)
     → Foundations(#foundations) → Knowledge graph(#knowledge) → Evals(#method)
```

---

## The essay engine — `harness/build_essays.py`

One pure renderer for every prose section. `render_section(contract, ctx)` walks a contract's
`blocks` and returns HTML, then runs two token passes.

### Block types
`kicker · h · lead(dropcap) · p · pull · list · stat · framework(2×2) · layers(value-chain)
· table · sources(tiered cards) · chart · refs`

### Inline tokens (resolved in `render_section`)
- **`{{cite:KEY}}`** or **`{{cite:KEY1,KEY2}}`** → numbered superscript footnote(s) linking to
  the Foundations bibliography. Keys must exist in `contract/citations.json`; unknown keys are
  dropped silently (no dangling refs). Numbering is by **first appearance** across sections in
  reading order (`collect_cite_order`), so it is stable and contiguous 1..N.
- **`{{fact:KEY}}`** → a **live figure** computed from the scored universe at build time
  (`compute_facts` in `build_frontend.py`). This is how the Findings section stays true to the
  data: e.g. `{{fact:exposed_count}}`, `{{fact:exposed_names}}`, `{{fact:top_mos_name}}`,
  `{{fact:measured_pct}}`. Add a new fact by extending `compute_facts`.

> Note: `_`-prefixed contract keys (e.g. `_doc`) are **excluded** from citation scanning so
> example tokens in documentation strings don't pollute numbering.

### Charts (server-side inline SVG, no JS)
`chart` block with `kind`:
- `weights` — static; bars come from `block.bars` (sub-factor weights). Used in Methodology.
- `tiers` — evidence-tier coverage across the universe; data from `ctx["charts"]["tiers"]`. Data section.
- `quadrants` — quadrant distribution; data from `ctx["charts"]["quadrants"]`. Findings section.

`compute_charts(records)` builds the tier/quadrant data; `compute_facts(records, share)` builds
the fact map. Both are in `build_frontend.py`.

### Bibliography
`render_foundations(ctx)` emits the numbered list (`<ol class="fn-list">`) from
`contract/citations.json`, **only** the references actually cited, in citation order, each with
authors/year/title/type/link and the `use` note. Anchors are `id="ref-KEY"`; footnote markers
link to them.

### Styling
`ESSAY_CSS` (one string, exported) is injected once into the page `<style>`. Sections carry
`class="essay"`; everything is scoped so it composes with the explorer's existing styles.

---

## The contracts (`contract/*.json`) — edit these, not the HTML

| File | Section | Notes |
|---|---|---|
| `argument.json` | Abstract | Thesis + the model in brief. Light citations. |
| `analysis.json` | Analysis | **The whitepaper.** Problem → economics → mechanics → *why cat/cyber models don't fit* → *the proposed model* → value chain → re-pricing → opportunity. 15 citations. |
| `findings.json` | Findings | "What the data shows." Uses `{{fact:}}` tokens + the quadrant chart. Honest about PROVISIONAL. |
| `methodology.json` | Methodology | Two axes, rubric weight tables, λ-by-tier fusion, evidence tiers, gate, weights chart. |
| `data.json` | Data | Source cards (NESO/ECR/CH/FCA/FSR/SFCR), computation table, tier chart. |

Each contract has a `_doc`, `version`, `as_of`, `grounding`. Validate any contract with:
```bash
python3 harness/build_essays.py contract/analysis.json --check    # block summary + cited keys
python3 harness/build_essays.py contract/analysis.json --preview  # standalone site/analysis.preview.html
```

---

## Substantiation & honesty rules (unchanged, now enforced in copy)

- Every quantitative claim in the essays is either traced to a `{{cite:}}` in the verified
  registry or a `{{fact:}}` from the live data. No free-floating numbers.
- The **publication gate** still governs: the banner reads PROVISIONAL until blended
  measured+disclosed ≥ 60%. Findings says so explicitly and re-derives on every build.
- **External references are scrubbed from the site by policy.** Do not reintroduce names of
  other indices/authors into anything under `site/` or the rendered contracts. (The internal
  `ALIGNMENT_*` memo is the only place that comparison lives and must not be committed to a
  public site build.)

### Citation registry change to be aware of
Four personal-blog citations were re-sourced and **renamed**:
`FELIX-BUNDLING→IND-VALUECHAIN`, `FELIX-BROKING→IND-BROKING`,
`FELIX-CANNIBALS→IND-BROKER-CHAIN`, `LEVINE-TRANCHING→FIN-TRANCHING`. The graph node
`felix-bundling→ind-valuechain`. `verify_model_spec.py` passes (0 fail) with the new keys.

---

## Open items for Cursor

1. **Make Findings land at the gate.** Once `optimize.py` keeps `scores.blend` (see
   `BUGS_FOR_CURSOR.md`), `compute_facts`/`compute_charts` will report real measured shares and
   the Findings magnitudes become publishable. This is the single highest-value fix.
2. **Run the live registers** (`RUNBOOK_LIVE.md`) so `{{fact:measured_pct}}` climbs past 60% and
   the banner flips to publishable.
3. **Universe breadth** — the 55-entity set is in `data/records.json`; once it flows through
   optimize→build, the Findings counts and the 2×2 populate to transformation-index density.

---

## Build / verify checklist

```bash
git pull origin framework
python3 harness/build_essays.py contract/analysis.json --check     # contracts renderable
python3 harness/build_frontend.py                                  # regenerate site/
python3 harness/run_loop.py --check                                # L0–L8 + integrity gates
# sanity: 0 unresolved tokens, contiguous bibliography
grep -c "{{cite:\|{{fact:" site/index.html        # → 0
```
