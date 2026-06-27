# Methodology tab — architecture

Dedicated **Methodology** view within the Princeps NFRI index — sibling to `index.html` (live explorer) and `on-non-firm-risk.html` (transformation thesis).

## Site map

| Tab (nav) | Output | Contract | Role |
|-----------|--------|----------|------|
| Live index | `site/index.html` | `argument`, `analysis`, … | Benchmark, cards, scatter, entity drill-down |
| **Methodology** | `site/methodology.html` | `contract/methodology_tab.json` | Scoring model, fusion, layers, pipeline, gate |
| On transformation | `site/on-non-firm-risk.html` | `on_transformation.json` | Long-form thesis + embedded charts |

Shared: one CSS bundle (`css.py`), one JS bundle (`client.py`), one payload shape (`D.pts`, `D.evals`, `D.share`, …).

## Page anatomy (thesis shell)

```
gate-bar          ← brand + site nav (Index · Methodology · Transformation)
gate-banner       ← live L5 share + entity count
thesis-shell
  thesis-toc      ← sticky Contents (scroll-spy)
  thesis-article
    masthead      ← METHODOLOGY · subtitle · date
    § premise     ← one-paragraph summary + pull quote
    § two-axes    ← E/P formula, MoS, quadrants
    § sub-factors ← tables + weight chart (live)
    § fusion      ← λ blend + evidence tiers
    § layers      ← L1–L5 value chain
    § pipeline    ← harness flow (ingest → score → eval → publish)
    § gate        ← publication gate + tier chart
    § evals       ← L0–L8 chips (live from eval report)
    § sources     ← register / filing map (from data contract)
footer            ← back link to live index
drawer            ← shared entity drill-down (click scatter if embedded later)
```

## Orchestration harness

One command ties verification, deploy manifests, and build:

```bash
python3 harness/methodology_harness.py --strict   # sync check (risk_model ↔ contracts)
python3 harness/methodology_harness.py --build    # + write site/methodology.html
python3 harness/agent_deploy.py --methodology     # Felix-style parallel pass manifest
```

| Artifact | Role |
|----------|------|
| `contract/methodology_writing.json` | Section map, bots, parallel passes, surface registry |
| `harness/verify_methodology.py` | Weight / λ / section / scatter sync vs `risk_model.json` |
| `harness/methodology_harness.py` | CLI entry — verify → lint → build |
| `harness/run_loop.py` | Includes **Methodology sync** gate in `--check` mode |

Surfaces governed together:

| Surface | Contract | Output |
|---------|----------|--------|
| Index essay | `methodology.json` | `#methodology` |
| Methodology tab | `methodology_tab.json` | `methodology.html` |
| Scatter drawer | `scatter_methodology.json` | `D.scatterMethod` |
| Data sources | `data.json` | `#data` (shared sources block) |

## Data vs presentation split

| Layer | Owns |
|-------|------|
| **Data** | `contract/methodology_tab.json`, `methodology.json`, `data.json`, `rubric.json`, `compute_facts`, `parse_eval_report`, `build_methodology.py` |
| **Presentation** | `methodology_template.py`, `methodology_assemble.py`, `THESIS_CSS` (reuse), `client.py` (`initMethodologyPage`) |

Build seam (same as thesis):

```python
# harness/build_frontend.py → main()
build_methodology_page(records=records, pts=pts, share=share, payload_base=payload)
```

## Content contract rules

1. **No harness mechanics in manifesto/analysis** — pipeline detail lives here only (`analysis_writing.json` already enforces this).
2. **Live numbers** — use `{{fact:*}}` tokens; gate share from `authoritative_share`, never stale eval text.
3. **Model sync** — sub-factor weights / λ tiers must match `contract/risk_model.json` + `MODEL_SPEC.md` (same rule as `methodology.json`).
4. **Charts** — static SVG via `build_essays` where possible; live eval/rail via `viz` mounts + `client.py`.

## Adding a methodology section

1. Add TOC item + `section` block to `contract/methodology_tab.json`
2. If new chart primitive: add to `build_essays._chart` or `client.py` + document in this file
3. Rebuild: `python3 harness/build_frontend.py`
4. Verify: `python3 harness/style_check.py contract/methodology_tab.json`

## Phase 2 (not in scaffold)

- Embed readonly quadrant scatter on methodology page (`viz quadrant_scatter readonly`)
- `#/methodology` hash route on single-page app (optional; sibling HTML preferred for now)
- Pull full `METHODOLOGY.md` §3–§8 into contract blocks incrementally
