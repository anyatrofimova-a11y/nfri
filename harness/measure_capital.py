#!/usr/bin/env python3
"""Disclosed capital_reinsurance for risk-carriers (L1 insurers/syndicates, L4 reinsurers).

Pipeline:  AM Best / S&P financial-strength rating  +  Solvency II SCR-coverage ratio
        -> fixed, auditable 0-4 lookup
        -> DISCLOSED-tier capital_reinsurance sub-factor with provenance
           (measured_value={rating, scr_coverage}, as_of, source_type, sources)

Inputs are DISCLOSED facts, each carrying its own primary source + as_of:
  - rating: published FSR (ambest.com / spglobal.com)
  - scr_coverage: Solvency II SCR-coverage ratio from the entity's published SFCR (own funds / SCR)

Only applies to risk-carriers. Brokers/MGAs (intermediaries) have no FSR/SCR, so their
capital_reinsurance stays `assessed` — a deliberate rigor choice, not an omission.

Modes:
  --live     reads contract/capital_inputs.json (you populate it from real filings/ratings)
  --fixture  reads harness/fixtures/capital_fixture.json (placeholder unit-test values);
             writes to data/records.measured_demo.json, flagged FIXTURE_DEMO, never the index.
"""
from __future__ import annotations
import json, os, sys, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
CARRIER_TYPES = {"insurer", "lloyds_syndicate", "reinsurer"}

# ---- rating -> 0-4 component (scale-aware: AM Best A++/A+ are top; S&P AA/AAA are top) ----
def rating_component(rating: str, scale: str) -> int:
    r = re.sub(r"\s*\(.*\)", "", str(rating)).strip().upper()
    scale = (scale or "").lower()
    if scale.startswith("am"):  # AM Best: A++ A+ | A A- | B++ B+ | B B- | ...
        return {"A++":4,"A+":4,"A":3,"A-":3,"B++":2,"B+":2,"B":1,"B-":1}.get(r, 0)
    # S&P / Fitch style: AAA AA+ AA AA- | A+ A A- | BBB | BB ...
    if r.startswith("AAA") or r.startswith("AA"): return 4
    if r.startswith("A"):   return 3
    if r.startswith("BBB"): return 2
    if r.startswith("BB"):  return 1
    return 0

def scr_component(coverage_pct) -> int:
    try: c = float(coverage_pct)
    except (TypeError, ValueError): return None
    return 4 if c >= 200 else 3 if c >= 160 else 2 if c >= 130 else 1 if c >= 100 else 0

def capital_rating(rating, scale, scr):
    rc = rating_component(rating, scale)
    sc = scr_component(scr)
    if sc is None:                 # rating only
        return rc, "rating-only"
    return round(0.6*rc + 0.4*sc), f"0.6*rating({rc}) + 0.4*scr({sc})"

def build_subfactor(row, mode):
    rating, scale, scr = row.get("fsr_rating"), row.get("fsr_scale"), row.get("scr_coverage_pct")
    val, formula = capital_rating(rating, scale, scr)
    srcs = [s for s in (row.get("fsr_source"), row.get("scr_source")) if s]
    conf = "high" if (rating and scr) else "medium" if rating else "low"
    return {
        "rating_0_4": val,
        "measured_value": {"fsr_rating": rating, "fsr_scale": scale, "scr_coverage_pct": scr},
        "unit": "FSR+SCR%",
        "as_of": row.get("as_of", TODAY),
        "evidence_tier": "disclosed" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "rating",
        "rationale": f"Disclosed capital: FSR {rating} ({scale}) + SCR coverage {scr}% -> {formula} = {val}.",
        "sources": srcs or ["(fixture placeholder)"],
        "confidence": conf if mode == "live" else "low",
    }

def main():
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    demo = os.path.join(ROOT, "data", "records.measured_demo.json")
    base = demo if (mode == "fixture" and os.path.exists(demo)) else os.path.join(ROOT, "data", "records.optimized.json")
    recs = json.load(open(base))

    inputs_path = (os.path.join(ROOT, "harness", "fixtures", "capital_fixture.json") if mode == "fixture"
                   else os.path.join(ROOT, "contract", "capital_inputs.json"))
    inputs = json.load(open(inputs_path)).get("inputs", {})

    changed = []
    for r in recs:
        if r["entity_type"] not in CARRIER_TYPES:
            continue
        row = inputs.get(r["entity_id"])
        if not row:
            continue
        old = r["preparedness_inputs"]["capital_reinsurance"]["rating_0_4"]
        r["preparedness_inputs"]["capital_reinsurance"] = build_subfactor(row, mode)
        changed.append((r["entity_id"], old, r["preparedness_inputs"]["capital_reinsurance"]["rating_0_4"], row))

    out = demo if mode == "fixture" else os.path.join(ROOT, "data", "records.measured.json")
    json.dump(recs, open(out, "w"), indent=2, ensure_ascii=False)

    print(f"=== MEASURE capital_reinsurance ({mode}) ===")
    print(f"base: {os.path.basename(base)}  inputs: {os.path.basename(inputs_path)}\n")
    for eid, old, new, row in changed:
        print(f"  {eid:<14} rating {old} -> {new}   FSR={row.get('fsr_rating')} ({row.get('fsr_scale')})  SCR={row.get('scr_coverage_pct')}%")
    carriers = [r for r in recs if r["entity_type"] in CARRIER_TYPES]
    print(f"\ncarriers updated: {len(changed)}/{len(carriers)}  (intermediaries intentionally left assessed)")
    print(f"wrote: data/{os.path.basename(out)}")
    if mode == "fixture":
        print("\nNOTE: fixture mode is a UNIT TEST. Values are placeholders, flagged FIXTURE_DEMO,")
        print("and never enter the index. Populate contract/capital_inputs.json and run --live for real data.")

if __name__ == "__main__":
    main()
