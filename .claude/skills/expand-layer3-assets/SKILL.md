---
name: expand-layer3-assets
description: >
  Research and wire NEW Layer-3 assets (UK data centres, energy & storage/BESS) into the NFRI
  dataset and live interface. Use when asked to expand the universe with real entities, add
  data-centre / wind / solar / battery assets, or grow the non-firm-power risk index. Enforces
  the no-synthetic-data policy and the canonical contract schema.
---

# Expand Layer-3 assets (data centres / energy / storage) into NFRI

A repeatable recipe for adding real UK Layer-3 assets to the index without breaking the contract,
the scorer, or the publication gate. Distilled from the 2026-06 non-firm expansion (+21 assets).

## 0. Golden rules
- **NO SYNTHETIC DATA.** Every sub-factor with `rating_0_4 >= 1` MUST carry at least one real,
  working source URL. `harness/integrate_entities.py` rejects records that violate this.
- **Never invent firmness.** If gate/firmness is not evidenced, set `gate_status: "unknown"` and
  mark that sub-factor `confidence: "low"`. Do not guess Gate 1/2.
- **Conservative ratings**, one-sentence rationales, cite everything with rating >= 1.

## 1. Research (fan-out)
- Split the target list into batches (e.g. hyperscaler DCs / colo DCs / BESS / generation) and run
  parallel research subagents; each returns a strict JSON array and OMITS any entity it cannot source.
- Verify URLs resolve. Good source domains by evidence tier (see `harness/evals.py` `tier_of`):
  - **measured/disclosed** (raise the L5 gate): `neso.energy`, `*.gov.uk`, `ofgem.gov.uk`,
    `opendatasoft.com`, `data.ssen.co.uk`, `connecteddata.nationalgrid.co.uk`, Companies House, FCA, rating agencies.
  - **assessed** (assistive press): `datacenterdynamics.com`, `renews.biz`, `energy-storage.news`,
    `itpro.com`, `datacentrenews.uk`, `colo-x.com`, `reuters.com`.
  - **unscorable** (do NOT rely on alone for a measured claim): `wikipedia.org`, press releases
    (`prnewswire.com`, `businesswire.com`), company own-marketing.

## 2. Canonical schema — match `contract/entity.schema.json` exactly
Layer-3 research records are written to `data/records.json`. Common gotchas that differ from a
naive schema:
- `entity_type` enum (assets): **`data_centre` | `energy_asset` | `storage_asset`**. (BESS =
  `storage_asset`; it was added to the enum, to `stress_test.py` ASSET_TYPES — keep them in sync.)
- `hq_country`: use **`"GB"`** to match sibling assets (not "UK").
- `asset_link`:
  - `gate_status` enum: **`gate_1 | gate_2 | firm | non_firm | unknown | null`** (snake_case, not "Gate 1").
  - `backup_generation` is a **boolean** (`true`/`false`/`null`) — map yes→true, partial→true, no→false, unknown→null.
  - include `covered_assets: []`.
- `provenance` **requires** `researched_by`, `last_checked`, `method` (`"llm_research"`). The
  `provenance.evidence` block is stamped automatically by `integrate_entities.py`.
- Each sub-factor: `{rating_0_4, rationale, sources:[...], confidence}`.
- **Rubric quirk:** the Exposure axis has a 6th, L3-only key `non_firm_compute_exposure` that
  *replaces* `non_firm_intensity` at layer 3 (`include_layers:[3]`). Research records carry
  `non_firm_intensity`; the authoritative scorer (`harness/scoring.py`) handles the swap, and the
  axis helpers renormalise over present keys. Do NOT add `non_firm_compute_exposure` by hand.

### Asset rating guidance (0-4)
EXPOSURE (higher = more exposed): `book_concentration` (single campus/site = high) ·
`non_firm_intensity` (firm=0, fully non-firm/queued=4, unknown→2 low-confidence) ·
`aggregation_correlation` (one GSP/constraint boundary, e.g. Slough or B6 = high) ·
`trigger_gap` (damage-only cover, no availability/parametric = 3-4) · `tenor_mismatch` (long
finance horizon vs short curtailment history = 3-4 for new builds).
PREPAREDNESS (higher = more resilient): `data_monitoring` (DCIM/SCADA/BM participation) ·
`product_fit` (availability/parametric cover — usually 0-1; strong UPS+diesel/BESS raises it) ·
`underwriting_expertise` (1 for an asset) · `capital_reinsurance` (hyperscaler/utility/listed
fund = 3-4, small developer = 1-2) · `pricing_modelling` (1 for an asset).

## 3. Wire into the harness + interface (terminal pipeline)
Stage the canonical records as a JSON array under `data/`, then:
```bash
# 1) merge (idempotent; dedupes by entity_id; enforces no-synthetic)
python3 harness/integrate_entities.py data/<new_assets>.json    # add --no-bank to skip capital/book banking
# 2) refresh the optimized set the frontend reads (CANONICAL = live registers; measured tiers):
python3 harness/ingest_live.py                                  # writes data/records.optimized.json + dataset.csv
#    offline fallback (assessed-tier only): python3 harness/optimize.py
# 3) rebuild the static site (also copies site/data/* downloads)
python3 harness/build_frontend.py
# 4) verify
python3 harness/evals.py                                        # watch L5 (publication gate), L2/L4
```
- The frontend reads `data/records.optimized.json` if present, else `records.scored.json`
  (`build_frontend.load_records`). Regenerating optimized via `optimize.py` alone **drops** the
  live measured/disclosed tiers (share falls to ~assessed) — prefer `ingest_live.py`, or bank
  disclosed values into `records.json` first (`integrate_entities.py` without `--no-bank`).
- Adding assessed-tier research entities legitimately **lowers** the L5 blended measured share; the
  index stays **PROVISIONAL** until rebased on measured sources. That is expected, not a regression.

## 4. Environment notes
- Repo runs on **Python 3.9** — any new harness file using PEP 604 (`str | None`) annotations needs
  `from __future__ import annotations` at the top.
- A concurrent editor may be refining harness files; re-read immediately before editing.
