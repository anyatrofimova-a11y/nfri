# Cowork → Cursor handoff #2 (2026-06-26): the non-firm × AI-compute INTERACTION term

The harness scores the *components* of the thesis but does **not yet price the interaction**:
a high-compute AI campus on a non-firm (Gate-1) connection in a constrained region is
*multiplicatively* worse than the additive sum of its sub-factor ratings. Right now sub-factors
are additive and entities scored independently, so that coupling is invisible.

## Proposed: derived asset-level interaction feature (risk_model.json + MODEL_SPEC.md)

    non_firm_compute_exposure  =  load_norm(import_MW)  ×  non_firm_share  ×  curtailment_prob

- **import_MW** — compute/demand magnitude, MEASURED from the DNO ECR (already pulled by
  measure_non_firm). Normalise (e.g. log or /500MW cap) to a 0..1 load factor. This is the missing
  "AI/compute demand intensity" term — today a hyperscale campus and a small colo score identically.
- **non_firm_share** — MEASURED (ECR flex flag / TEC Gate). Already computed.
- **curtailment_prob** — NEW measured source: NESO constraint-cost / curtailment-volume by boundary
  (neso.energy data portal). Maps the asset's GSP/boundary → expected curtailment frequency. This is
  the "how often the interruption bites" term; aggregation HHI only captures clustering, not likelihood.

Result is a derived 0-4 (or 0-1) feature that *prices the coupling*, replacing/augmenting the flat
`non_firm_intensity` for L3 assets. Fully measured/derived → raises measured share AND captures the thesis.

## Propagate to insurers (the linker)
Asset `non_firm_compute_exposure` should flow up to carriers via `asset_link.covered_assets`. Coverage
linkage is mostly non-public, so where unknown, propagate a *book-weighted regional average* with a
confidence penalty rather than leaving it assessed. That makes the insurer's exposure a function of the
interaction, not a standalone guess.

## Also queued (handoff #1): trigger_gap / product_fit port
`contract/trigger_inputs.json` is now banked (33 entities, verified non-damage product counts). It feeds
BOTH trigger_gap (exposure, inverse: n=0→4 … ≥4→0) and product_fit (preparedness, direct: n→min(n,4)),
each `disclosed`-tier like measure_capital — no fusion-model change. Reference impls:
`~/Documents/nfri/harness/measure_trigger.py` + `measure_product.py`. Wiring these into `measure_all.py`
roughly doubles disclosed coverage on the books already scored.

## Suggested citations to add
`ACAD-CCM-NF-LOAD` (non-firm load), `NESO-CONSTRAINT-COSTS`, `INDUSTRY-DC-COMPUTE-DEMAND`.
