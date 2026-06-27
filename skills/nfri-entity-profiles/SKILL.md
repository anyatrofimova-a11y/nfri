---
name: nfri-entity-profiles
description: >
  Ship Ciridae-depth entity profiles on click — executive analysis, axis rationale, score
  framework, full sub-factor prose, methodology at point of use, and provenance. Use when
  editing profiles.json, entity_copy.json, build_entity_profiles.py, renderProfileBody in
  client.py, profile research/synthesis bots, or when a user says entity drill-down lacks
  natural-language explanation.
---

# NFRI entity profiles (Ciridae-depth drill-down)

Reference pattern: a narrative-led public index firm/company page — executive thesis, factor
scorecards, per-axis rationale, full sub-score drill-down with named definitions. NFRI must
match that reading depth and surpass it with fusion transparency and evidence tiers.

Full architecture: `contract/ENTITY_ANALYSIS_ARCHITECTURE.md`, `harness/frontend/ENTITY_PROFILES.md`,
bot contract: `contract/profile_writing.json`.

## Content stack (never collapse layers)

| Layer | Owner | Writes |
|-------|-------|--------|
| L0 measurement | `harness/measure_*.py` | register → deterministic ratings, `measured_value` |
| L1 research | expand-layer skills + research bots | 10 sub-factor rationales in `data/records.scored.json` |
| L2 synthesis | profile_editor / portfolio_analyst | `contract/entity_copy.json` |
| L3 gloss | `contract/rubric.json` → `D.sfGloss` | sub-factor definitions (shared tooltips) |
| L4 scores | `harness/scoring.py` ONLY | axis scores, MoS, quadrant |
| L5 presentation | `build_entity_profiles` + `renderProfileBody` | `site/data/profiles.json` + profile panel |

**Hard rule:** bots write rationales and narrative; code writes scores.

## Profile panel blocks (all must render when data exists)

When `#/carrier/:id` opens, `renderProfileBody` must show in order:

1. **Analysis** — `executive_summary` (80–120 word entity thesis from `entity_copy.json`)
2. **Score row** — Exp / Prep / MoS / measured %
3. **Axis decomposition** — latent vs deterministic bars
4. **Score framework tables** — E1–E5 and P1–P5 with eff, weight, tier (Ciridae durability/opportunity pattern)
5. **Axis rationale** — one paragraph each for exposure and preparedness
6. **Register facts** — L3 `asset_link` (gate, curtailment, backup)
7. **Portfolio** — `portfolio_narrative` + asset swarm (L1)
8. **Products & placements** — chips from `placements[]`
9. **Sub-factor cards** — full rationale (no char cap), `measured_value`, tier, λ, sources, cites
10. **Methodology strip** — fusion one-liner + links to `methodology.html`
11. **Provenance** — tier breakdown, confidence, last_checked, notes

Drawer fallback (`openDrawer`) stays for slim `D.pts[]` when profiles.json entry missing.

## Data contracts

### Sub-factor (research bots → `records.scored.json`)

```json
{
  "rating_0_4": 3,
  "rationale": "2–4 sentences: entity-specific fact + underwriting implication.",
  "sources": ["https://..."],
  "citation_ids": ["PRA-PPP"],
  "evidence_tier": "disclosed",
  "measured_value": { "share": 0.017, "relevant_gwp": 17.6, "total_gwp": 1048.7 },
  "confidence": "medium"
}
```

- Rationale ≥ 40 chars, entity-specific (not index boilerplate)
- `rating ≥ 1` → ≥ 1 working source URL
- If tier = assessed, say so in prose

### Synthesis overlay (`contract/entity_copy.json`)

```json
{
  "qts-blackstone-cambois-blyth": {
    "executive_summary": "…",
    "axis_rationale": { "exposure": "…", "preparedness": "…" },
    "portfolio_narrative": "…",
    "placements": [{ "id": "…", "label": "…", "url": "…" }]
  }
}
```

Merged at build in `build_entity_profiles()` — never hand-edit `profiles.json`.

### Build pipeline

```bash
python3 harness/score_and_validate.py
python3 harness/build_frontend.py   # writes site/data/profiles.json from records.scored.json
python3 harness/profile_harness.py --strict
```

Profiles **must** be built from `data/records.scored.json` (blend intact), not `records.optimized.json`.

## Bot deployment

```bash
python3 harness/agent_deploy.py --profiles
python3 harness/apply_synthesis.py    # merge synthesis batches → entity_copy.json
python3 harness/profile_harness.py --build
```

| Bot | Output |
|-----|--------|
| `carrier_researcher` / `asset_researcher` | sub-factor rationales |
| `profile_editor` | executive_summary + axis_rationale |
| `portfolio_analyst` | portfolio_narrative |
| `placement_mapper` | placements[] |

Skills: `.claude/skills/expand-layer1-carriers`, `expand-layer3-assets`.

## UI non-negotiables

- No `alert()` for citations — use drawer citation panel (`citePop`)
- Sub-factor ⓘ tooltips from `D.sfGloss` (rubric questions)
- Show `measured_value` callout when register/filing exists
- Profile panel width ≥ 880px; full prose visible without truncation
- Hash route `#/carrier/:id` shareable; scatter/table/card clicks → same panel

## Exit checks

```bash
python3 harness/profile_harness.py --strict
python3 harness/build_frontend.py
grep -c 'profile-exec' site/index.html   # profile render paths present
```

- Every L1 entity: `executive_summary` in `entity_copy.json`
- Every scored entity: 10 sub-factors with rationale ≥ 40 chars
- `profiles.json` includes `executive_summary` where overlay exists
- `renderProfileBody` renders all blocks listed above

## Surpass Ciridae (NFRI moat — show, don't tell)

- Fusion math (lat / det / λ / eff) on every sub-factor line
- Evidence tier badge on every line
- Register callouts when measured
- In-force rail links rules that re-price sub-factors
- Honest PROVISIONAL gate when measured share < 60%
