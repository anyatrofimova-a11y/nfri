# Cowork → Cursor handoff (2026-06-26)

Counterpart to CLAUDE_HANDOFF.md. Same bridge: this repo + git.

## Landed this pass (Cowork)
- `contract/capital_inputs.json` — **24 verified carriers/reinsurers** (FSR; SCR for Munich Re 298% + AXA 224%). 7-entity L4 reinsurer layer scored (`data/records.json` now 22 entities); **12/12 carrier-type now `disclosed` capital**, Nephila assessed (ILS, no FSR).
- L4 result: Swiss Re/SCOR/Hannover/RenRe → whitespace; Arch/Fidelis → sidelined; **Nephila → earning_it** (weather/ILS book touches DC renewable procurement).
- Finding: **breadth dilutes the gate** (4%→5% on +7 reinsurers). The lever is measured *coverage per entity*, not universe size.

## Proposal for Cursor — port `trigger_gap` + `product_fit` measure scripts

These exist in the user's `~/Documents/nfri/harness/` (Cowork build) but **not on `framework`**. Porting them is the single highest-leverage coverage move: one disclosed fact drives **two** sub-factors across **all carriers + MGAs + reinsurers** (the entities that design cover), ~doubling disclosed coverage on books we already score.

**The fact:** count of an entity's DISTINCT, EVIDENCED non-damage / parametric / availability products (filed wording / Lloyd's binding-authority class / regulatory approval — NOT press alone).

**Two mappings from the same count `n`:**
- `trigger_gap` (exposure, inverse): n=0→4, 1→3, 2→2, 3→1, ≥4→0   (0 products = entirely legacy triggers)
- `product_fit` (preparedness, direct): n→min(n,4)

**Why it fits the fusion model with no change:** both write `evidence_tier:"disclosed"`, `source_type:"filing"` sub-factors — identical shape to `measure_capital.py`, so `scoring.py` treats them as deterministic inputs and fuses via Bühlmann λ exactly as capital. No `risk_model.json` change; just two scripts + one shared input file + citation_ids wiring.

**Suggested artifacts:**
- `harness/measure_trigger.py`, `harness/measure_product.py` (both read `contract/trigger_inputs.json`)
- `contract/trigger_inputs.json` template: `{entity_id: {n_nondamage_products:int, products:[...], sources:[...], as_of}}`
- Reference impl + fixtures already in `~/Documents/nfri/harness/` (measure_trigger.py / measure_product.py / fixtures/trigger_fixture.json).
- `citation_ids`: reuse `LLOYDS-PARAMETRIC-CYBER`, `BROK-MARSH-NIMBUS`, `MGA-PARAMETRIX-ANALYTICS`.

**Coverage impact (estimate):** carriers gain a 2nd disclosed exposure factor (trigger_gap, w0.15) + a 2nd disclosed preparedness factor (product_fit, w0.20). On the 6 prototype carriers + 2 MGAs + reinsurers, that lifts blended measured share materially toward the 60% gate — far more than adding more assessed entities.

**Cowork can supply the data** (verified non-damage product counts per entity) once the scripts are on `framework` — same loop: Cowork banks `trigger_inputs.json`, Cursor/Claude-Code pushes.

## Open (unchanged from CLAUDE_HANDOFF)
- L5 publication gate is the honest red; needs coverage, not breadth.
- 4 reinsurer ratings now banked (RenRe A+, Arch A+, Fidelis A) — capital complete for the L4 layer.

---

## Handoff #2 (2026-06-26) — non_firm × AI-compute INTERACTION term

**Landed (Cursor):**
- `non_firm_compute_exposure` = `load_norm(import_MW) × non_firm_share × curtailment_prob` — L3 derived sub-factor replacing flat `non_firm_intensity` in scoring when present (`contract/risk_model.json`, `MODEL_SPEC.md`).
- `contract/constraint_boundary.json` + `contract/asset_boundary_map.json` — boundary curtailment anchors.
- `harness/measure_interaction.py` + `harness/link_propagation.py` — measure chain + carrier propagation (portfolio mean fallback when `covered_assets` unknown).
- `contract/trigger_inputs.json` synced from Cowork (**33 entities**).
- Citations: `NESO-CONSTRAINT-COSTS`, `INDUSTRY-DC-COMPUTE-DEMAND` (+ existing `ACAD-CCM-NF-LOAD`).

**Run:**
```bash
python3 harness/measure_all.py --live
python3 harness/evals.py data/records.measured.json
```
