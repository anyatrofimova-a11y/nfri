# NFRI disclosed-data collection checklist — fill-in-the-blanks to move L5

*The publication gate (eval L5) is blended measured/disclosed ≥ 60%. The live ECR pull already gives
L3 assets measured `non_firm_intensity`. The remaining lever is **carrier disclosures**:
`capital_reinsurance` (FSR + Solvency II SCR) and `book_concentration` (energy/power premium share).
This is the worksheet for pulling them from real filings — no value is invented (`DATA_POLICY.md`).*

---

## How to populate (two equivalent paths — both merge-safe)

**Path A — edit the JSON directly** (what Cursor used): add a row under `inputs` in
`contract/capital_inputs.json` / `contract/book_inputs.json`.

**Path B — fill the worksheet, then convert:**
```bash
# 1. fill value cells in contract/inputs_worksheet.csv (one row per carrier; lines_counted uses ';')
python3 harness/inputs_from_csv.py        # MERGES into the JSONs — never clobbers existing rows
python3 harness/measure_capital.py --live # FSR/SCR  -> disclosed capital_reinsurance
python3 harness/measure_book.py    --live # premium  -> disclosed book_concentration
python3 harness/ingest_live.py            # re-score the index (also re-pulls ECR) ; rebuilds site
python3 harness/evals.py data/records.optimized.json   # watch L5 move
```
Both `inputs_from_csv.py` and direct editing are safe to run concurrently — the converter only
adds/updates the entity_ids present in the CSV and never deletes a hand-entered row.

## What each field moves (the L5 math)

Per carrier, disclosing both clears most of that carrier's measurable weight:
- `capital_reinsurance` — **0.20 of Preparedness** — FSR (+SCR) → disclosed.
- `book_concentration` — **0.30 of Exposure** — energy/power GWP share → disclosed.

Carriers are 6 of the 15-entity prototype (and 25 of the 57-entity universe). Book is the bigger
lever and is currently **0% done** — prioritise it.

## Field reference

| Field | Where | Notes |
|---|---|---|
| `fsr_rating` | AM Best (`ratings.ambest.com`) or S&P (`spglobal.com/ratings`, or the group's IR "ratings" page) | as published, e.g. `A+`, `AA-` |
| `fsr_scale` | — | `ambest` (A++/A+/A/A-/B++…) or `sp` (AAA/AA+/AA/…/A/BBB…) |
| `scr_coverage_pct` | Solvency II **SFCR** (own funds ÷ SCR ×100), "Capital management"/E.2 section; UK entities also on FCA NSM `data.fca.org.uk/a/nsm` | omit if no clean group ratio (rating-only is allowed → medium confidence) |
| `total_gwp` / `energy_power_gwp` | **Lloyd's syndicate annual report** "class of business" table (has an Energy line) for syndicates; **group segmental note** for insurers/reinsurers | use the NARROWEST named energy/power class; if only broad Property/Commercial, leave blank (book stays assessed — do NOT over-include) |
| `currency` | the filing's reporting currency | GBP (Lloyd's/UK), USD (US/Bermuda), EUR (DE/FR) |
| `lines_counted` | — | exact class names summed, `;`-separated in the CSV |
| `*_source`, `as_of` | primary URL + reporting date | required for disclosed tier |

---

## Capital — status & to-do

**DONE (FSR verified, in `capital_inputs.json`):** Beazley `A+`, Hiscox `A` (AM Best); AXA XL `AA-`
+ SCR 224%, Chubb `AA`, Zurich `AA`, Munich Re `AA` + SCR 298% (S&P). The 4 without SCR are
rating-only → medium confidence.

**To do — SCR for the rating-only four** (raises confidence high):
- **Beazley / Hiscox** — Bermuda group; clean Solvency II SCR not published → leave SCR blank (proxy via Lloyd's market solvency ratio only if documented).
- **Chubb** — US-led group; for the UK/EEA entity use the Chubb European Group SFCR solvency ratio.
- **Zurich** — reports Swiss SST, not SCR%; either map SST or leave blank.

**To do — scale-up carriers** (`fsr_scale` pre-filled in the worksheet): all the AM-Best Lloyd's
syndicates (Liberty, TM Kiln, MS Amlin, Aspen, Markel, Canopius, Brit + Aviva, Convex, Fidelis,
SCOR, RenRe, Arch, Fidelis Re) and S&P groups (Allianz, RSA, QBE Europe, Swiss Re Corso, Hannover).
Lloyd's syndicates share the Lloyd's market FSR (AM Best A / S&P A+ / Fitch AA-) — use that unless the
managing agent's group is separately rated. SCR: each group's SFCR, else rating-only.

## Book — to-do (highest L5 leverage; 0% done)

For each carrier, open the named source, find the energy/power premium line, and the total GWP.

| entity_id | source to open | the line to find | currency |
|---|---|---|---|
| `beazley` | Beazley plc Annual Report → segmental / division GWP | Energy (Marine/Energy & renewables) | USD |
| `hiscox-london-market` | Hiscox Ltd Annual Report → Hiscox London Market segment GWP | Energy / Property within London Market | USD |
| `axa-xl` | AXA Group Annual/URD → AXA XL P&C lines | Natural Resources / Energy | EUR/USD |
| `chubb` | Chubb Ltd 10-K → segment "Global P&C" net premiums | Energy / Marine within commercial | USD |
| `zurich` | Zurich Group Annual Report → Commercial Insurance GWP | Energy / Property mix | USD |
| `munich-re` | Munich Re Group Annual Report → reinsurance P-C segment | Power & Utilities / Renewables | EUR |
| Lloyd's syndicates (Liberty 4472, TM Kiln 510, MS Amlin 2001, Aspen 4711, Markel 3000, Canopius 4444, Brit 2987) | the **Syndicate `<id>` Annual Report** → "Analysis by class of business" | the **Energy** class GWP + syndicate total | GBP |
| Reinsurers (SCOR, Hannover, RenRe, Arch Re, Swiss Re Corso, Fidelis Re) | group annual report → P&C/treaty segment | Energy / Natural Resources / Onshore-Offshore Energy | EUR/USD |

**Caveats (keep us honest):**
- If a carrier only discloses broad Solvency II LoBs (Fire/Property, Marine), they over-include energy → **leave book blank**; `book_concentration` stays `assessed`. Better an honest gap than a wrong "measurement".
- Individual Lloyd's syndicate SCR is not separately public; use the group/Lloyd's-market ratio only with a documented source.
- Every disclosed row needs a primary `*_source` URL + `as_of`; the validator and eval L5 enforce this.

> Done right, the 6 prototype carriers disclosing FSR (+SCR) and energy-premium share lifts their
> measurable Preparedness to ~0.40 and Exposure book weight to 0.30 — the core of the path from
> 4% → 60% (`DATA_ORCHESTRATION.md` §2). L3 non-firm (ECR) and these carrier disclosures together
> are what take the index from PROVISIONAL to publishable.
