---
name: expand-layer1-carriers
description: >
  Research and wire NEW Layer-1 carriers (insurers and Lloyd's syndicates) into the NFRI dataset
  and live interface. Use when asked to expand the carrier universe, add insurers / syndicates /
  MGAs that write energy, power, property or specialty for data-centre and grid-scale energy risk.
  Enforces the no-synthetic-data policy and the canonical contract schema.
---

# Expand Layer-1 carriers (insurers / Lloyd's syndicates) into NFRI

A repeatable recipe for adding real UK / London-market carriers to the index without breaking the
contract, the scorer, or the publication gate. Distilled from the 2026-06 carrier expansion
(+20 insurers & syndicates: Lancashire, Apollo, Inigo, Beat, Ark, Atrium, Chaucer, Faraday,
Newline, Antares, AEGIS, Talbot, Allied World, Travelers, CNA Hardy, AIG UK, BHSI, HDI, AXIS, Sompo).

## 0. Golden rules
- **NO SYNTHETIC DATA.** Every sub-factor with `rating_0_4 >= 1` MUST carry at least one real,
  working source URL. `harness/integrate_entities.py` rejects records that violate this.
- **Do not skip the existing universe.** Pull `data/records.json` ids first and exclude anything
  already present (Beazley, Hiscox, AXA XL, Chubb, Zurich, Munich Re, Allianz, Aviva, RSA, QBE,
  Convex, Liberty Specialty, Tokio Marine Kiln, MS Amlin, Aspen, Markel, Canopius, Brit, …).
- **Conservative ratings**, one-sentence rationales; when unsure rate low and `confidence: "low"`,
  but still cite something. Rating 0 with empty `sources` only when genuinely nothing applies.

## 1. Research (fan-out)
- Split the target list into ~5-carrier batches and run parallel research subagents; each returns a
  strict JSON array and OMITS any entity it cannot source.
- For each carrier capture: financial-strength rating (AM Best / S&P / Fitch — cite the actual
  page), whether they write energy/power/property/specialty, any **named** energy/power
  underwriting team, any **evidenced** parametric / availability / non-damage product, and book mix.
- Verify URLs resolve. Source domains by evidence tier (see `harness/evals.py` `tier_of`):
  - **measured/disclosed** (raise the L5 gate): `ambest.com`, `spglobal.com`, `fitchratings.com`,
    `moodys.com`, `*.gov.uk`, Companies House, FCA, `lloyds.com` rating pages.
  - **assessed** (assistive press): `reinsurancene.ws`, `insurancebusinessmag.com`,
    `insurancejournal.com`, `businessinsurance.com`, Lloyd's syndicate accounts PDFs, carrier
    product pages.
  - **unscorable** (do NOT rely on alone): `wikipedia.org`, press releases (`prnewswire.com`,
    `businesswire.com`), pure company own-marketing.

## 2. Canonical schema — match `contract/entity.schema.json`
Carrier records are written to `data/records.json`. Shape per record:
- `entity_type`: **`insurer` | `lloyds_syndicate`** (also `mga` / `broker` / `reinsurer` exist).
- `layer`: **1**. `hq_country`: `"UK"` (or the real HQ country). `parent_group`: group or `""`.
- `exposure_inputs`: `book_concentration`, `non_firm_intensity`, `aggregation_correlation`,
  `trigger_gap`, `tenor_mismatch`. (The 6th key `non_firm_compute_exposure` is **L3-only** —
  never add it to a carrier; `include_layers:[3]` and the axis helpers renormalise over present keys.)
- `preparedness_inputs`: `data_monitoring`, `product_fit`, `underwriting_expertise`,
  `capital_reinsurance`, `pricing_modelling`.
- Each sub-factor: `{rating_0_4, rationale, sources:[...], confidence}`. `asset_link: null`.

### Carrier rating guidance (0-4)
EXPOSURE (higher = more exposed): `book_concentration` (share of book in energy/power/DC/specialty;
named specialist line = 3-4) · `non_firm_intensity` (exposure to interruptible/curtailable-power
assets; upstream oil&gas = low, renewables/BESS/power-gen = 2-3) · `aggregation_correlation`
(concentration on shared grid geography; globally diversified = low) · `trigger_gap` (damage-only
cover with no availability/parametric = 3-4; has parametric = low) · `tenor_mismatch` (long tenor /
thin history = high; annual well-evidenced = low).
PREPAREDNESS (higher = more prepared): `data_monitoring` · `product_fit` (**evidenced** parametric /
availability / non-damage product — most damage-only carriers are 1; weather-index/parametric raises
it) · `underwriting_expertise` (named specialist energy/power team = 3-4) · `capital_reinsurance`
(financial-strength rating — AM Best A+ / S&P AA- → 3-4, cite it; Lloyd's chain-of-security = 4) ·
`pricing_modelling` (published methodology).
> Most London-market energy carriers are **damage-trigger reliant**: expect `trigger_gap` 3-4 and
> `product_fit` 1 unless a parametric/availability wording is actually evidenced.

## 3. Wire into the harness + interface (terminal pipeline)
Stage the canonical records as a JSON array under `data/` (keep this **source file** — it is durable
even if a concurrent write clobbers `records.json`; just re-run step 1 to recover):
```bash
# 1) merge (idempotent; dedupes by entity_id; enforces no-synthetic; banks disclosed capital)
python3 harness/integrate_entities.py data/expansion_carriers.json
# 2) score (layer-aware fusion scorer) + optimize (assessed-tier median cut-lines)
python3 harness/score_and_validate.py
python3 harness/optimize.py            # canonical = ingest_live.py when live registers/filings are available
# 3) build the substantiated exposure map artifact + standalone viz
python3 harness/build_exposure_map.py  # -> data/exposure_map.json + site/data/exposure_map.json
python3 harness/build_frontend.py
# 4) verify
python3 harness/evals.py data/records.optimized.json   # watch L5 (gate), L4 (calibration), L6 (math)
```
- Adding assessed-tier carriers legitimately **lowers** the L5 blended measured share; the index
  stays **PROVISIONAL** until rebased on measured FSR/SFCR/Lloyd's filings
  (`RUNBOOK_LIVE.md` §3-4 → `contract/capital_inputs.json`, `contract/book_inputs.json`).
- **Visualisation:** `site/exposure-map.html` (self-contained) renders the carrier exposure×prep
  matrix with new carriers highlighted, plus L3 assets mapped to NESO constraint boundaries. It
  reads `site/data/exposure_map.json` — regenerate with `build_exposure_map.py` after any merge.

## 4. Environment notes
- Repo runs on **Python 3.9** — new harness files using PEP 604 (`str | None`) need
  `from __future__ import annotations`.
- A concurrent editor (Cursor) may be refining harness files and rewriting `data/records.json`;
  **re-read immediately before editing**, keep your `data/*.json` source array, and re-run
  `integrate_entities.py` to re-merge if your carriers get dropped.
