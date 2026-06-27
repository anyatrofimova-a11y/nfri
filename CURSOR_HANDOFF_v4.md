# CURSOR HANDOFF v4 — what's left to a clean publish

_Produced from the sync/gate side (`~/Developer/nfri`, branch `framework`). Authored **read-only**:
no code was touched this pass because another editor was live in the repo (per the
`one-editor-at-a-time` rule in `FRONTEND.md`). Fix items at **source** (`~/Documents/nfri`);
they get overwritten on the next sync otherwise._

## TL;DR

**Both v3 blockers are resolved** — `evals.py` no longer crashes and citation integrity is clean.
The universe grew **37 → 115 records**. What remains is **not code** — it is **real-data coverage**.
The publication gate is at **19%** blended measured/disclosed share against a **≥60%** bar, and two
industry-stress scenarios fail on thin `product_fit` coverage. Neither can be closed without real
disclosed/measured inputs (no-synthetic policy holds).

`run_loop.py --check` → **4/6 stages clean, gates: FAIL**.

---

## Resolved since v3 (no action needed — recorded for the trail)

- ✅ **Blocker 1 (evals layer-awareness crash).** Fixed at HEAD via a "skip layer-absent sub-factor"
  patch (`... for k,c in cfg.items() if k in inp`) at `evals.py:63`, the matching `if k not in r[ax]:
  continue` in the L5 loop, and a layer-filtered golden fixture (`evals.py:105`). Verified correct
  for current data: every L3 record carries `non_firm_intensity`, none carry
  `non_firm_compute_exposure`, so each axis still normalises to 1.0. **See caveat below.**
- ✅ **Blocker 2 (2 dangling citations).** `NESO-CONSTRAINT-COSTS` and `INDUSTRY-DC-COMPUTE-DEMAND`
  now resolve — `verify_model_spec.py` is **7 pass / 0 warn / 0 fail**.
- ✅ Universe expanded to **115 records** (L1: 39, L2: 35, L3: 24, L4: 17); new `publication_gate.py`
  stage wired into `run_loop`.

---

## CAVEAT on the Blocker-1 fix — latent 1.25 over-count  *[Cursor, harness — pre-empt before task 3]*

The skip-missing patch is correct **only while the two twin sub-factors never co-exist on one record**.
`non_firm_intensity` (w=0.25) and `non_firm_compute_exposure` (w=0.25, `include_layers=[3]`) share one
0.25 slot; the full rubric therefore sums to **1.25**. Today no record holds both, so every axis sums
to 1.0. But the moment **task 3** populates `non_firm_compute_exposure` for an L3 asset (e.g.
`asset-culham-aigz`) **while `non_firm_intensity` is still present**, that record's exposure axis sums
to **1.25 → score caps at 125, not 100**, silently inflating L3 exposure.

**Fix (cheap, do it now):** route `evals.py`'s `axis()` through
`scoring.active_axis_config(rec, cfg)` — it already honours `include_layers`, performs the L3
`intensity ↔ compute_exposure` swap, and **renormalises weights to 1.0**. That makes the over-count
structurally impossible instead of relying on "the twins happen not to co-exist."

---

## BLOCKER A — Publication gate L5 at 19% (need ≥60%)  *[Cursor/Cowork, real data]*

```
GAP ANALYSIS (L5 publication gate)
  blended share: 19%   (gate ≥60%)   gap: 41%   entities: 115
  book_concentration disclosed: 2/24 carriers
  non_firm_intensity measured:  4/24 L3 assets
```

Top unmet sub-factor weight (summed across entities): `book_concentration` 33.0,
`data_monitoring` 28.2, `underwriting_expertise` 22.8, `non_firm_intensity` 17.8,
`pricing_modelling` 17.1, `product_fit` 16.0. Several cohorts sit at **0%** measured share
(`howden`, `marsh`, `wtw`, `nephila`, `fidelis-mgu`).

**Levers (no synthetic data), highest weight first:**
1. Populate `contract/book_inputs.json` — named energy/power GWP from Lloyd's class tables / SFCR
   (currently only **2/24 carriers** disclosed → this single factor is 33.0 of unmet weight).
2. Extend `ASSET_ROUTE` + `asset_boundary_map.json`; re-run `measure_non_firm.py --live`
   (only **4/24 L3 assets** measured).
3. Broaden `trigger_inputs` + `capital_inputs` coverage across the gate cohort.

---

## BLOCKER B — Industry stress L7: 2/9 scenarios fail  *[Cursor/Cowork, real data]*

```
[FAIL] RDS-CORRELATED-CURTAILMENT
[FAIL] PLACEMENT-CHAIN-INTEGRITY
   mgas_high_product_fit:        FAIL — 21 MGAs, min product_fit ≥ 3
   brokers_facility_product_fit: FAIL — 14 brokers, min product_fit ≥ 2
SUMMARY: 7 pass, 2 fail / 9 scenarios
```

`PLACEMENT-CHAIN-INTEGRITY` fails because MGA/broker `product_fit` ratings are thinner than the
scenario floor — same root cause as Blocker A (coverage), scoped to the placement-chain cohort.
`RDS-CORRELATED-CURTAILMENT` needs the correlated-curtailment exposure inputs filled on the affected
L3 assets. **Do not lower the thresholds to pass** — close the data, or document why the floor is wrong.

---

## What unblocks a clean publish

1. Cursor lands the Blocker-1 caveat fix (`active_axis_config` in `evals.py`) — pre-empts task 3.
2. Cursor/Cowork closes Blocker A (real `book_inputs.json` + `measure_non_firm.py --live`) until
   `L5 ≥ 60%`, which also lifts the `product_fit`/coverage cohorts behind Blocker B.
3. Re-sync → `run_loop.py --check` should reach **6/6 clean, gates: PASS**.
4. Only then run `run_loop.py --full` → `build_frontend.py` and publish.

## Done on the sync side this pass
- Verified both v3 blockers resolved; confirmed the Blocker-1 fix is correct for current data and
  identified the latent 1.25 over-count.
- Captured exact remaining gate gaps (L5 19%, L7 2/9) from a read-only `--check`; regenerated report
  artifacts restored to HEAD. **No code or data authored** (one-editor-at-a-time was in effect).
