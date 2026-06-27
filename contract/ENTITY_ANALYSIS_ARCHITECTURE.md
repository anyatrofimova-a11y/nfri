# Entity analysis bot architecture — match Ciridae depth, surpass on honesty

How to deploy parallel research/synthesis bots so every entity profile reads like a Ciridae firm page — executive thesis, factor scorecards, full rationales, methodology at point of use — while keeping NFRI’s register fusion and publication gate as the differentiator.

**Deploy manifest:** `python3 harness/agent_deploy.py --profiles`  
**Verify loop:** `python3 harness/profile_harness.py --strict`  
**Contract:** `contract/profile_writing.json`

---

## 1. What Ciridae does (and what we keep)

| Ciridae surface | What the reader gets | NFRI analogue today | Gap |
|-----------------|----------------------|---------------------|-----|
| Fund / firm list | Sortable table + AI score pill | `#table`, `#benchmark`, fund cards | OK |
| Company profile header | Name, sector, sponsor | `#profile-hero` | OK |
| Executive summary | 80–120 word investment thesis | Missing | **Bot: profile_editor** |
| Durability / Opportunity tables | Factor × score + tooltips | Sub-factor cards in `#profile` | Needs **score framework table** UI |
| Factor rationale block | “Durability Rationale” prose | Per-card `rationale` only | Needs **axis_rationale** + longer copy |
| Sub-score drill-down | Full D1–D5 / O1–O4 on click | `sfBlock` with lat/det/eff | OK structure; thin copy on many entities |
| Methodology | Implicit in factor names | `methodology.html` + drawer | Need **inline gloss + links** on profile |
| Outcome validation | 6M comp returns | Measured share proxy | P0: registers / disclosed GWP |

**Surpass Ciridae (NFRI moat):**

1. **Fusion transparency** — every line shows latent, deterministic, λ, effective rating (Ciridae shows one number).
2. **Evidence tier** — measured / disclosed / derived / assessed badge (Ciridae hides provenance).
3. **Register callouts** — `measured_value` when ECR/TEC/filing exists.
4. **In-force rail** — which CMP/GC rules re-price *this* entity’s sub-factors.
5. **Downloadable row** — same profile projects to CSV/JSON with full provenance.

---

## 2. Content stack (four layers — never collapse)

```
┌─────────────────────────────────────────────────────────────┐
│ L4  PRESENTATION  build_entity_profiles → profiles.json      │
│     + client renderProfileBody (Ciridae-style layout)        │
├─────────────────────────────────────────────────────────────┤
│ L3  SYNTHESIS     entity_copy.json (exec summary, portfolio)│
│     Bots: profile_editor, portfolio_analyst, placement_mapper│
├─────────────────────────────────────────────────────────────┤
│ L2  SCORING       harness/scoring.py ONLY (arithmetic)       │
│     Exposure, Preparedness, MoS, quadrant                    │
├─────────────────────────────────────────────────────────────┤
│ L1  RESEARCH      records.scored.json sub-factors            │
│     Bots: carrier/asset/syndicate/reinsurance_researcher     │
├─────────────────────────────────────────────────────────────┤
│ L0  MEASUREMENT   harness/measure_*.py (registers → det)     │
└─────────────────────────────────────────────────────────────┘
```

**Hard rule:** Bots write **rationales and narrative**; code writes **scores**. Same discipline as the index manifesto.

---

## 3. Bot roster

| Bot | Pass | Writes | Ciridae job |
|-----|------|--------|-------------|
| `carrier_researcher` | l1_research | 10 sub-factors × L1 | Company-page depth per carrier |
| `syndicate_researcher` | l1_research | Lloyd's-specific book/product | Syndicate stamp context |
| `asset_researcher` | l3_research | asset_link + exposure subs | Asset overview + gate facts |
| `reinsurance_researcher` | l4_research | tail aggregation subs | Reinsurer cat book |
| `profile_editor` | synthesis | executive_summary, axis_rationale | Exec summary + “Rationale” blocks |
| `portfolio_analyst` | portfolio | portfolio_narrative | Swarm / book interpretation |
| `placement_mapper` | portfolio | placements[] from KG | Product chips (Nimbus, Parametrix…) |
| `actuary` | gloss (once) | profile_methodology_gloss.json | Factor tooltips |
| `data_steward` | audit | validation fixes | Source/tier QA |

Skills already wired for L1/L3 research: `.claude/skills/expand-layer1-carriers`, `expand-layer3-assets`. Profile bots **consume** their output; they do not rescore.

---

## 4. Deployment loop (parallel passes)

```bash
# 1. Manifest — which bots, which batches
python3 harness/agent_deploy.py --profiles

# 2. Fan out (example: 10 carriers per subagent)
#    Each subagent: read profile_writing.json bot brief + entity batch
#    Patch data/records.scored.json + contract/entity_copy.json

# 3. Rescore + validate (deterministic)
python3 harness/score_and_validate.py
python3 harness/score_and_validate.py  # 0 problems gate

# 4. Rebuild profiles + site
python3 harness/build_frontend.py

# 5. Profile QA
python3 harness/profile_harness.py --strict
```

### Pass schedule (115 entities)

| Pass | Batch | Parallel agents | Est. |
|------|-------|-----------------|------|
| l1_research | 10 L1 / agent | 4 | ~40 entities |
| l3_research | 15 L3 / agent | 2 | ~24 assets |
| l2_mga | 10 L2 / agent | 2 | ~35 MGAs/brokers |
| synthesis | 20 / agent | 6 | all scored |
| portfolio | 15 L1 / agent | 3 | carriers w/ links |
| audit | 50 / agent | 2 | full universe |

Run **measure_*** harnesses before research passes when registers update (raises L5 measured share).

---

## 5. Data contracts

### `data/records.scored.json` (research bots)

Per sub-factor (already in schema):

```json
{
  "rating_0_4": 3,
  "rationale": "2–4 sentences: entity-specific fact + underwriting implication.",
  "sources": ["https://..."],
  "citation_ids": ["PRA-PPP", "RATING-AMBEST-FSR"],
  "evidence_tier": "disclosed",
  "measured_value": 0.42,
  "confidence": "medium"
}
```

### `contract/entity_copy.json` (synthesis bots) — **new**

```json
{
  "beazley": {
    "executive_summary": "…",
    "axis_rationale": {
      "exposure": "…",
      "preparedness": "…"
    },
    "portfolio_narrative": "…",
    "placements": [{ "id": "MGA-PARAMETRIX-SLA", "label": "Parametrix SLA cover", "url": "…" }]
  }
}
```

Merged at build time in `build_entity_profiles()` → `profiles.json`.

### `contract/profile_methodology_gloss.json` (actuary bot, once)

Shared tooltips: sub-factor id → `{ "definition": "…", "anchor": "sub-factors#book-concentration" }`.

---

## 6. Profile UI target (Ciridae layout + NFRI honesty)

Upgrade `#profile` panel zones (single implementation, drawer uses subset):

```
┌─ HERO ─────────────────────────────────────────────┐
│ Logo · Name · L1 · parent · MoS · quad · meas%   │
├─ EXEC SUMMARY (profile_editor) ────────────────────┤
│ 80–120 word thesis paragraph                      │
├─ SCORE FRAMEWORK (tables) ───────────────────────┤
│ Exposure E1–E5  │  Preparedness P1–P5             │
│ eff · w · tier  │  eff · w · tier   [i] gloss     │
├─ AXIS RATIONALE ──────────────────────────────────┤
│ Two short paragraphs (Ciridae "Rationale" blocks)  │
├─ SUB-FACTOR CARDS (existing sfBlock, enhanced) ────┤
│ measured_value callout · cite → KG panel           │
├─ PORTFOLIO (L1) ───────────────────────────────────┤
│ Swarm SVG + portfolio_narrative                    │
├─ PLACEMENTS ───────────────────────────────────────┤
│ Product chips from KG                              │
├─ IN-FORCE (entities affected) ─────────────────────┤
│ Rail subset repricing this record                  │
├─ METHODOLOGY STRIP ────────────────────────────────┤
│ Fusion one-liner · link to methodology.html        │
└─ PROVENANCE ───────────────────────────────────────┘
```

**Priority UI tasks** (after bot content lands):

1. `renderProfileBody` → add exec summary + framework tables + axis rationale slots.
2. Replace `citePop` alert → `openKgCite(id)` side panel.
3. `build_entity_pages.py` → static share URLs.

---

## 7. Harness gates

| Gate | Script | Fails when |
|------|--------|------------|
| Schema + sources | `score_and_validate.py` | rating ≥1 without URL |
| Profile depth | `profile_harness.py` | missing exec summary (L1), rationale &lt; 40 chars |
| Copy overlay sync | `profile_harness.py` | entity_copy id not in profiles |
| Build projection | `build_frontend.py` | profiles.json stale vs scored |
| Narrative IA | `verify_index_narrative.py` | profile route broken |

Add to `run_loop.py --check` after profile_harness exists.

---

## 8. Phased rollout

### Sprint A — Contracts + harness (1 day)

- [x] `contract/profile_writing.json`
- [x] This architecture doc
- [ ] `contract/entity_copy.json` (empty scaffold)
- [ ] `harness/profile_harness.py`
- [ ] `agent_deploy.py --profiles`

### Sprint B — L1 research depth (2–3 days, parallel bots)

- Fan out `carrier_researcher` on all L1/Lloyd's
- Run measure_book + measure_capital where filings exist
- Target: every L1 sub-factor rationale ≥ 2 sentences, ≥ 1 cite

### Sprint C — Synthesis + UI (2 days)

- `profile_editor` → populate `entity_copy.json`
- Upgrade `renderProfileBody` Ciridae layout
- Citation KG panel

### Sprint D — Surpass (ongoing)

- `entity_links.json` real edges → portfolio_analyst
- L5 measured share → regression credibility
- Static `site/carrier/{id}.html`
- Outcome column when `book_inputs.json` populated

---

## 9. Example bot prompt (carrier_researcher)

```
You are carrier_researcher for NFRI.
Read: contract/rubric.json, contract/citations.json, skills/nfri-data-discipline/SKILL.md
Entity batch: [ids…]
For each entity, for each of 10 sub-factors:
  - Set rating_0_4 (latent anchor) with confidence
  - Write rationale 2–4 sentences (entity-specific)
  - Add ≥1 working source URL + citation_ids
  - Do NOT write scores.exposure_0_100 or margin_of_safety
Output: JSON patch list applied to data/records.scored.json
Exit: score_and_validate.py reports 0 problems for batch
```

---

## 10. Success metrics

| Metric | Ciridae | NFRI target |
|--------|---------|-------------|
| Exec summary on L1 | Yes | 100% L1 |
| Sub-factor prose | Full page | ≥ 40 chars × 10 × entity |
| Methodology visible | Tooltips | Tooltips + tier + fusion + link |
| Provenance | Opaque | Source URL + tier on every line |
| Shareable URL | Yes | `#/carrier/id` → static HTML |
| Score integrity | LLM-heavy | Code-only axis scores |

---

**Next command:** `python3 harness/agent_deploy.py --profiles` then fan out Pass `l1_research` on the worst-covered carriers (lowest measured share first).
