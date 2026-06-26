# NFRI — Live Data Runbook

Goal: replace the `--fixture` unit-test values with **real primary-source data** across the
universe, moving the L5 publication gate from ~16% (fixtures) toward **≥ 60%**. Nothing here
invents data — every step reads a register, a filing, or a rating.

## 0. Prerequisites

```bash
pip install requests
cd ~/Documents/nfri
python3 harness/score_and_validate.py && python3 harness/optimize.py   # build records.optimized.json
```

Accounts / keys (all free):
- **DNO Opendatasoft portals** (UK Power Networks, SSEN, Northern Powergrid, NGED) — free registration to query records.
- **NESO Data Portal** — no key; ≤ 1 request/second.
- **Companies House API** — free key at developer.company-information.service.gov.uk.
- **FCA Financial Services Register API** — free key at register.fca.org.uk/Developer.

Order of operations: run each feature's `--live` step below, **then** `python3 harness/evals.py`
and watch L5. Live writes go to `data/records.measured.json` (the publishable file); fixtures
go to `data/records.measured_demo.json` (never publishable).

---

## 1. `non_firm_intensity` — measured (DNO ECR + NESO TEC)

For each Layer-3 asset, the harness pulls the Embedded Capacity Register for its licence area
and computes the MW-weighted share on flexible/non-firm connections.

```bash
python3 harness/measure_non_firm.py --live
```

Routing lives in `ASSET_ROUTE` in `measure_non_firm.py` — `entity_id -> (portal, search term)`.
The Opendatasoft v2.1 query it issues:

```
GET https://ukpowernetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/
    ukpn-embedded-capacity-register/records?where=search("Harlow")&limit=100
```

The field resolver auto-detects `Maximum Import Capacity (MW)`, `Flexible Connection`, and
`Connection Status` — no hard-coded columns. Add assets by extending `ASSET_ROUTE` (UKPN =
London/East/SE; SSEN = Southern/North Scotland; NGED = Mids/SW/Wales; NPg = North East/Yorkshire).

## 2. `aggregation_correlation` — derived (HHI over grid geography)

```bash
python3 harness/measure_aggregation.py --live
```

Pulls the ECR for each asset's **licence area**, groups MW by **Grid Supply Point**, and
computes `HHI = Σ (mw_gsp / mw_total)²`. Same `where=search("<area>")` mechanism; routing in
`ASSET_ROUTE` inside `measure_aggregation.py`.

## 3. `capital_reinsurance` — disclosed (FSR rating + Solvency II SCR)

```bash
cp contract/capital_inputs.example.json contract/capital_inputs.json
# edit: for each carrier/reinsurer add fsr_rating + fsr_scale (ambest|sp) and scr_coverage_pct
python3 harness/measure_capital.py --live
```

Where to get the two numbers:
- **FSR rating** — the rating-agency page (AM Best / S&P). Record the letter grade and which scale.
- **SCR coverage %** — the entity's **Solvency II SFCR** (annual). UK insurers file these; find via
  the company IR page or the FCA National Storage Mechanism. Use Own Funds ÷ SCR × 100.

Lookup is fixed and auditable: `0.6·rating_component + 0.4·scr_component`.

## 4. `book_concentration` — disclosed (energy-premium share)

```bash
cp contract/book_inputs.example.json contract/book_inputs.json
# edit: for each carrier add total_gwp + energy_power_gwp (same currency) from the
#       Lloyd's syndicate 'class of business' table / segmental report
python3 harness/measure_book.py --live
```

Only carriers that disclose a **named energy/power line** get a measured value; others stay
`assessed` (Solvency II LoB can't isolate energy — do not force it).

## 5. `trigger_gap` — disclosed (evidenced non-damage product count)

```bash
cp contract/trigger_inputs.example.json contract/trigger_inputs.json
# edit: for each underwriter/MGA set n_nondamage_products + product names, each evidenced by a
#       filed wording / Lloyd's binding-authority class / regulatory approval (NOT press alone)
python3 harness/measure_trigger.py --live
```

---

## 6. Universe identifiers (for breadth — the real lever)

The gate moves on **breadth**, not more feature types. To run the five features across all 57
entities, resolve each entity's identifiers in `contract/universe.seed.v2.json`:
- **FCA FRN / permissions** — `https://register.fca.org.uk/Developer` (firm search).
- **Companies House number / accounts** — `https://api.company-information.service.gov.uk/`.
- **Lloyd's syndicate / managing agent** — Lloyd's market directory; LMA members list.

Then populate the three `*_inputs.json` files for every carrier/MGA, extend `ASSET_ROUTE` for
every asset, and re-run sections 1–5.

## 7. Verify

```bash
python3 harness/evals.py data/records.measured.json
```

Watch **L5 (publication gate)**: it should climb past **60%** once the five measured/disclosed
features are populated for the bulk of the universe. When it flips to **PASS**, rebuild the
front-end (`python3 harness/build_frontend.py`) and the index is publishable.

> Reminder (DATA_POLICY.md): live values are `measured`/`disclosed`/`derived`; anything resting on
> vendor marketing, wikis, or model priors is **not scorable** and the validator will refuse it.
