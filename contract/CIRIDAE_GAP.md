# Ciridae gap map — NFRI index product

Tracks parity with [Ciridae Terminal](https://ciridae-terminal.vercel.app) / ai-transformation.fyi depth. Updated after narrative redesign (Phases 1–4).

## Shipped (this pass)

| Ciridae strength | NFRI implementation |
|------------------|----------------------|
| Thesis-first reading order | `#argument` → `#analysis` → `#findings` before any viz (`INDEX_NARRATIVE_SCHEDULE.md`) |
| Chart narrative (prose → viz → stats → so what) | `contract/chart_copy.json` → `D.chartCopy` + `.viz-block` wrappers |
| Sticky Contents nav | `.index-toc` scroll-spy (ai-transformation.fyi pattern) |
| Progressive disclosure | `#analytics-deep` accordion; tabbed terminal (Overview / Segments / Carriers / Compare) |
| Fund-style entity cards | `#cards` fund cards: Exp/Prep/MoS, measured %, linked-asset MoS range |
| Portfolio swarm | `#term-swarm` + profile swarm; segment-linked L3 assets per L1 carrier |
| MoS vs outcome regression | `#term-regression` with slope / R² / n |
| Sector/layer scoreboards | `#term-scoreboard` tabs: `mos_by_layer`, `mos_by_segment` |
| Full sub-factor profiles | `site/data/profiles.json` + `#/carrier/:id` profile panel |
| Terminal density | Tabbed `#terminal` inside collapsed analytics + `#benchmark` |
| Compare / alpha views | `#term-alpha` whitespace table; `#term-compare` head-to-head |
| Strategy map | `#term-strategy` L1 exp×prep scatter |
| Book split by carrier | `#term-quad-stack` linked-asset quadrant % |

**Verify:** `python3 harness/verify_index_narrative.py --strict`

## Remaining gaps (prioritised)

### P0 — Credibility on first read

1. **Publication gate L5 ≥ 60%** — headline still PROVISIONAL at ~16% measured. Ciridae leads with scale; we lead with honesty but lose trust. See `CURSOR_HANDOFF_v4.md` Blocker A.
2. **Outcome column** — Ciridae has 6M comp returns. NFRI proxy is measured % only. Add disclosed GWP share or register-verified field when `book_inputs.json` populated.
3. **Explicit carrier↔asset edges** — swarm uses segment-tag overlap (`entity_tags.json`). Replace with `contract/entity_links.json` from placement research / KG edges.

### P1 — Terminal parity

4. **Multi-panel dark terminal chrome** — optional `#terminal` skin (ticker, monospace table) without abandoning editorial index.
5. **NL query layer** — Ciridae “AI Query Terminal”. NFRI: templated queries over `D.pts` + profiles (compare, rank whitespace, sector filter) — no LLM scores.
6. **Universe scale narrative** — “115 entities · N syndicates · N assets” stat row in hero; segment counts in scoreboard headers.
7. **Static profile pages** — `site/carrier/{id}.html` for share/SEO (`ENTITY_PROFILES.md` phase 2).

### P2 — Depth

8. **Preserve blend in optimize** — axis decomp in drawer/profile still null when optimized record strips blend; profiles built from scored source (OK) but scatter/table slim payload still thin.
9. **Citation drawer** — replace `citePop` alert with KG detail panel on profile.
10. **Product/placement chips** on L1 profiles from KG edges (Nimbus, DCLP, Parametrix).
11. **Regression variants** — MoS vs disclosed GWP; L1-only carrier regression (thesis §9).
12. **Alpha metric v2** — “prep − measured proxy” gap (capability under-evidenced), not only whitespace MoS.

### P3 — Ops / harness

13. **Profile rebuild gate** — eval L7 check profiles.json sync with scored records.
14. **Logo completeness** — 102/115 logos; syndicate fallbacks documented in `entity_logos.json`.
15. **Download bundle** — profiles.json + entity_links in `/data` downloads strip.

## Architecture notes

- **Payload split**: `D.pts[]` slim for scatter/table; `data/profiles.json` fat on demand; `D.indexCharts` precomputed in Python.
- **Router**: `#/carrier/{entity_id}` opens profile panel; drawer retained for methodology slices.
- **Single chart compute**: `harness/compute_thesis_charts.py` feeds index, thesis, and methodology pages.

## Suggested next sprint

1. Populate `entity_links.json` (20–30 carrier→asset pairs from register research).
2. Raise L5 measured share on L3 assets (registers) — lifts regression and gate.
3. Dark terminal skin toggle + stat ticker on `#benchmark`.
4. `build_entity_pages.py` → static carrier HTML.
