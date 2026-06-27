#!/usr/bin/env python3
"""One-shot patch: thin rationales + optimize-safe delta apply helper."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.json")

THIN_FIXES: dict[tuple[str, str], str] = {
    ("vantage-cwl1-newport", "underwriting_expertise"): (
        "Asset operator, not an underwriter — preparedness on this axis reflects operational "
        "resilience (design, backup, monitoring), not carrier underwriting authority."
    ),
    ("stellium-newcastle", "underwriting_expertise"): (
        "Colocation developer/operator without underwriting licence; no internal risk-transfer "
        "or pricing function — operational preparedness only."
    ),
    ("stellium-newcastle", "pricing_modelling"): (
        "No disclosed curtailment-probability or grid-constraint model at asset level; "
        "tenant SLAs are commercial, not actuarially priced availability cover."
    ),
    ("nscale-loughton-essex", "product_fit"): (
        "No parametric, NDBI or SLA-mirror insurance product on the asset or sponsor balance sheet — "
        "availability risk sits with future tenants and construction-phase CAR only."
    ),
    ("nscale-loughton-essex", "underwriting_expertise"): (
        "Greenfield AI-campus developer without underwriting authority; preparedness is "
        "engineering and delivery capability, not insurance risk selection."
    ),
    ("nscale-loughton-essex", "pricing_modelling"): (
        "No public curtailment-pricing or constraint-probability methodology; "
        "queue position and energisation timing are project risks, not modelled insurance inputs."
    ),
    ("qts-blackstone-cambois-blyth", "product_fit"): (
        "No evidenced parametric grid-availability or NDBI product on the campus — "
        "pre-construction insurance is CAR/DSU; operational availability cover absent."
    ),
    ("qts-blackstone-cambois-blyth", "underwriting_expertise"): (
        "Blackstone/QTS development platform is not a risk carrier; underwriting preparedness "
        "does not apply — operational grid and tenant contracts only."
    ),
    ("qts-blackstone-cambois-blyth", "pricing_modelling"): (
        "No asset-level model for curtailment frequency or constraint-cost pass-through; "
        "merchant grid access terms are undisclosed for pricing."
    ),
    ("whitelee-wind-farm-eaglesham-moor", "underwriting_expertise"): (
        "Operational wind asset owned by a generator, not an insurer — no underwriting "
        "function; preparedness reflects O&M and merchant hedging only."
    ),
    ("zenobe-capenhurst-chester", "underwriting_expertise"): (
        "BESS operator without insurance underwriting licence; grid services revenue "
        "is merchant-traded, not reinsured at asset level."
    ),
    ("statera-thurrock-storage-essex", "underwriting_expertise"): (
        "BESS owner-operator (Statera/EQT) is not a carrier; no internal underwriting "
        "or risk-transfer desk on the asset."
    ),
    ("asset-aws-london-slough", "capital_reinsurance"): (
        "Hyperscale parent balance sheet (Amazon) backs capex and operations — not rated "
        "insurance capital; treated as assessed corporate credit, not reinsurance stack."
    ),
    ("asset-aws-london-slough", "pricing_modelling"): (
        "Asset entity carries no insurance pricing or curtailment model — tenant and "
        "corporate risk teams manage availability commercially, outside NFRI carrier rubric."
    ),
    ("asset-google-waltham-cross", "pricing_modelling"): (
        "Single-campus operator with no disclosed curtailment-pricing methodology; "
        "Shell PPA and grid connection terms are commercial, not actuarial inputs."
    ),
    ("asset-pivot-power-energy-superhub-oxford", "underwriting_expertise"): (
        "EDF/Pivot Power BESS is an asset operator, not an insurer — preparedness reflects "
        "merchant trading and grid services, not underwriting expertise."
    ),
    ("asset-gresham-house-thurcroft-bess", "underwriting_expertise"): (
        "Gresham House fund-owned BESS site is not a risk carrier; no underwriting "
        "authority or internal risk-transfer function at asset level."
    ),
    ("asset-field-auchteraw-bess", "underwriting_expertise"): (
        "Field Energy BESS developer/operator without insurance licence; B4-boundary "
        "curtailment exposure is merchant, not underwritten at asset."
    ),
}


def main() -> int:
    recs = json.load(open(RECORDS))
    n = 0
    for r in recs:
        eid = r["entity_id"]
        for axis in ("exposure_inputs", "preparedness_inputs"):
            inp = r.get(axis) or {}
            for key, block in inp.items():
                fix = THIN_FIXES.get((eid, key))
                if fix:
                    block["rationale"] = fix
                    n += 1
    json.dump(recs, open(RECORDS, "w"), indent=2, ensure_ascii=False)
    print(f"Patched {n} thin rationales → {RECORDS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
