# NFRI Data Policy — No Synthetic Data

This policy is part of the contract. The validator enforces it; records that violate it do not ship.

## 1. The rule

**No synthetic data.** No value in the index may be invented, guessed, or produced by a model "from prior knowledge." Every value is one of:

- a **measured** figure read from a primary register or dataset,
- a **disclosed** figure read from a regulated filing, rating, or audited statement,
- a value **derived** by a transparent computation over measured/disclosed inputs, or
- an **assessed** signal — an explicit, sourced *judgment* about a qualitative attribute, clearly labelled as such and never dressed up as a measurement.

An LLM may **extract** and **classify**; it may **assess** a qualitative attribute *with cited evidence*. It may **never** originate a number, a rating, or a fact that is not traceable to a source a third party can re-check.

## 2. Evidence tiers

Every sub-factor input carries an `evidence_tier` and a `source_type`. The tier determines how the value may be used and the maximum confidence it may claim.

| Tier | Meaning | Allowed `source_type` | Requires | Max confidence |
|---|---|---|---|---|
| **measured** | A figure read directly from a primary register/dataset | `register` | `measured_value`, `unit`, `as_of`, primary URL | high |
| **disclosed** | A figure from a regulated filing / rating / audited statement | `filing`, `regulatory`, `rating` | specific figure, `as_of`, primary URL | high |
| **derived** | Transparent computation over measured/disclosed inputs | `derived` | the formula + input ids | high |
| **assessed** | A sourced qualitative judgment (no measurement exists) | `disclosure`, `press` | quoted evidence + URL | **medium** |
| *(rejected)* | Vendor marketing, wikis, or unsourced model opinion | `vendor_marketing`, `inference` | — | **not scorable** |

## 3. Source-type hierarchy (what counts as primary)

1. **register** — `api.neso.energy`, `neso.energy/data-portal`, `*.gov.uk`, `ofgem.gov.uk`, Elexon BSC registers
2. **regulatory / filing** — `register.fca.org.uk`, `data.fca.org.uk`, Companies House (`*.company-information.service.gov.uk`), FCA National Storage Mechanism, Solvency II SFCRs
3. **rating** — AM Best, S&P, Moody's, Fitch financial-strength ratings
4. **disclosure** — company audited annual report / investor relations (own-domain but audited)
5. **press** — trade/industry press (assistive only; never measured/disclosed)
6. **vendor_marketing / wiki / inference** — the entity's own product pages, third-party wikis, or model priors → **not scorable**

## 4. Hard constraints the validator enforces

- A sub-factor with `evidence_tier` ∈ {measured, disclosed, derived} **must** carry a `source_type` from tiers 1–4 **and** an `as_of` date; a `measured` input must also carry `measured_value` + `unit`. Otherwise → **fail**.
- A sub-factor whose only sources are tier-6 (vendor/wiki) or which has no source is **not scorable** and must be set to `assessed` with `confidence:"low"` *or* excluded.
- `confidence:"high"` is forbidden on `assessed` inputs.
- Every entity reports a **measured share**: the fraction of axis weight resting on measured/disclosed/derived inputs. Publication gate: **blended measured/disclosed share ≥ 0.6**, i.e. the mean of the two axes' shares (target; the prototype is ~0.0 and is therefore explicitly PROVISIONAL). *Blended, not per-axis: the Preparedness axis caps at 0.40 measurable weight because `data_monitoring` + `underwriting_expertise` + `pricing_modelling` (0.60 combined) are irreducibly `assessed`, so a per-axis 60% gate is unsatisfiable on Preparedness by construction. The blended gate is enforced in `harness/evals.py` (L5).*
- Asset `gate_status` may be `firm`/`gate_1`/`gate_2` only if traceable to a NESO register row; otherwise `unknown` (never inferred-as-firm).

## 5. Status of the current prototype

The 15-entity prototype is **assessed-tier throughout** (measured share = 0.0). It demonstrates the harness mechanics and the rubric, and its *direction* is defensible, but it is **not a publishable measurement** and is labelled PROVISIONAL until re-based on the measured features in `feature_dictionary.md`.
