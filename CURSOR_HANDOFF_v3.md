# CURSOR HANDOFF v3 — measured-tier blockers

_Produced from the sync/gate side (`~/Developer/nfri`, branch `framework`). This file is the
authoritative to-do for the Cursor/Cowork side (`~/Documents/nfri`). Fix items at **source**;
they get overwritten on the next sync otherwise._

## TL;DR

The v2 site sync is in place, but **the publication pipeline does not currently pass gates**, and
`L5` (the measured-share publication gate) **cannot even be evaluated** because `evals.py` crashes.
Two real blockers, both authored at source, must be fixed before `run_loop.py --full` is meaningful.

`run_loop.py --check` → `gates: FAIL` (flaps 2/5–4/5 clean depending on which dataset evals hits).

---

## BLOCKER 1 — `evals.py` crashes on any non-L3 dataset (layer-awareness bug)  *[Cursor, harness]*

```
evals.py:63  KeyError: 'non_firm_compute_exposure'
```

**Root cause.** `non_firm_compute_exposure` is an **L3-only** sub-factor
(`rubric.json` → `exposure.non_firm_compute_exposure.include_layers = [3]`). In
`data/records.measured.json` only 4/37 records (the L3 ones) carry it; the other 33
(layers 1, 2, 4) do not. But `evals.py:63-64` applies the **full** `RUBRIC["exposure"]`
to every record via a hard subscript:

```python
def axis(inp,cfg): return round(sum(c["weight"]*(inp[k]["rating_0_4"]/4) for k,c in cfg.items())*100,1)
...
runs = [[(axis(r["exposure_inputs"],RUBRIC["exposure"]), ...) for r in RECS] ...]
```

So it dies on the first non-L3 record. This is why the eval gate "flaps": it only passes on
`records.measured_demo.json` (L3-heavy); it crashes on `records.measured.json` and
`records.optimized.json`.

**Fix.** `scoring.py` already solves this — reuse it. `active_axis_config(rec, axis_cfg)` honors
`include_layers` and does the L3 `non_firm_intensity`↔`non_firm_compute_exposure` swap (keeping the
0.25 weight slot filled so the axis still normalizes to 1.0). Make `evals.py` per-record:

```python
from scoring import active_axis_config
def axis(rec, ax_key, cfg):
    inp = rec[ax_key]
    active = active_axis_config(rec, cfg)
    return round(sum(c["weight"]*(inp[k]["rating_0_4"]/4) for k,c in active.items())*100,1)
# callers: axis(r,"exposure_inputs",RUBRIC["exposure"]), axis(r,"preparedness_inputs",RUBRIC["preparedness"])
```

Also fix the golden-fixture check (`evals.py:105-106`) the same way, or it will mis-normalize.

---

## BLOCKER 2 — `V1 citation integrity`: 2 dangling references  *[Cursor, contract data — needs REAL sources]*

```
verify_model_spec.py:  68 referenced, 66 defined; 2 UNRESOLVED
  INDUSTRY-DC-COMPUTE-DEMAND   referenced in risk_model — not in citations.json
  NESO-CONSTRAINT-COSTS        referenced in risk_model — not in citations.json
```

Referenced in `contract/risk_model.json` (lines 68, 74, 218) and
`contract/constraint_boundary.json` (throughout), but defined in **neither** the source nor
destination `contract/citations.json` (verified: `grep -c` = 0 in both trees, files byte-identical
— this is an authoring gap, not a sync error).

**Fix.** Add both entries to `contract/citations.json` with **real** provenance (title / author or
publisher / URL / year), matching the existing schema. Do **not** stub these — L5 is the
no-synthetic provenance gate, and fabricated refs defeat the entire model.
- `NESO-CONSTRAINT-COSTS` → NESO published constraint-cost figures (Monthly Balancing Services
  Summary / constraint cost reporting).
- `INDUSTRY-DC-COMPUTE-DEMAND` → the data-centre compute-demand source the risk model is leaning on.

---

## The 5-step plan — status

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Populate `contract/book_inputs.json` with real SFCR/Lloyd's figures (≥5–10 carriers) | **Cursor/Cowork** | ⏳ pending — needs real data, will not fabricate |
| 2 | `harness/measure_aggregation.py` → derived tier from boundary HHI | **Cursor** | ⏳ pending |
| 3 | `measure_non_firm.py` TEC fallback for `asset-culham-aigz` | **Cursor** | ⏳ pending |
| 4 | `measure_all.py --live` && `evals.py data/records.measured.json` | sync side | ⚠️ ran — `measure_all` OK (37 records), `evals` **crashes** (Blocker 1) |
| 5 | When `L5 ≥ 60%`: `run_loop.py --full` → `build_frontend.py` | sync side | ⛔ **not run** — L5 unmeasurable until Blocker 1 fixed; current blended share ≈ 1% (PROVISIONAL) |

**Definition (for tasks 2/3):** `non_firm_compute_exposure = load_norm(import_MW) × non_firm_share × curtailment_prob`.

## Done on the sync side this session
- Synced v2 contract/harness/knowledge from source; rebuilt `site/index.html` (443 KB, 55 entities).
- Ran `measure_all.py --live` → regenerated `data/records.measured.json` (37 records).
- Diagnosed both blockers above; no fabricated data or citations introduced.

## What unblocks a clean publish
1. Cursor fixes Blocker 1 (evals layer-awareness) and Blocker 2 (2 real citations) at source.
2. Cursor lands tasks 1–3 (real book inputs + aggregation + TEC fallback).
3. Re-sync → `run_loop.py --check` should reach `5/5 clean, gates: PASS`.
4. Only then is `L5 ≥ 60%` reachable → run task 5 (`--full`) and publish.
