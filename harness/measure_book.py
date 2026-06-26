#!/usr/bin/env python3
"""Disclosed book_concentration for risk-carriers — energy/power premium share.

Pipeline:  disclosed gross written premium (total)  +  premium in energy/power
           (& any named data-centre/tech) lines
        -> share = relevant_gwp / total_gwp
        -> 0-4 lookup
        -> DISCLOSED-tier book_concentration sub-factor with provenance.

Sources (per entity, each carrying its own primary URL + as_of):
  - Lloyd's syndicate annual report 'class of business' table (has an 'Energy' class), or
  - company segmental reporting / SFCR S.05.01 premiums by line of business.

RIGOUR NOTE: Solvency II LoB categories (Fire/Property, Marine) do NOT isolate 'energy/
power/data-centre', so they over-include. This feature is therefore only computed where the
entity DISCLOSES a named energy/power (or DC/tech) premium figure; otherwise book_concentration
stays `assessed`. Applies to risk-carriers only (insurers / syndicates / reinsurers).

Modes: --live reads contract/book_inputs.json ; --fixture reads the quarantined fixture and
writes data/records.measured_demo.json (flagged FIXTURE_DEMO, never the index).
"""
from __future__ import annotations
import json, os, sys, datetime

from measure_utils import CARRIER_TYPES, ROOT, load_records, save_records

TODAY = datetime.date.today().isoformat()

def share_to_rating(s):
    return 0 if s < 0.02 else 1 if s < 0.06 else 2 if s < 0.15 else 3 if s < 0.30 else 4

def build_subfactor(row, mode):
    total = float(row["total_gwp"])
    relevant = float(row.get("energy_power_gwp", 0)) + float(row.get("datacentre_tech_gwp", 0))
    share = relevant / total if total else 0.0
    srcs = [s for s in (row.get("source"), row.get("source2")) if s]
    return {
        "rating_0_4": share_to_rating(share),
        "measured_value": {"relevant_gwp": relevant, "total_gwp": total, "share": round(share, 3),
                           "currency": row.get("currency", "GBP"), "lines_counted": row.get("lines_counted")},
        "unit": "energy/power GWP share",
        "as_of": row.get("as_of", TODAY),
        "evidence_tier": "disclosed" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "disclosure",
        "rationale": (f"Disclosed energy/power premium share = {relevant}/{total} "
                      f"{row.get('currency','GBP')}m ({share:.0%}); lines: {row.get('lines_counted')}. "
                      f"Proxy via disclosed class-of-business; over-includes if lines are broad."),
        "sources": srcs or ["(fixture placeholder)"],
        "confidence": ("high" if row.get("energy_power_gwp") and srcs else "medium") if mode == "live" else "low",
    }

def main():
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    inputs_path = (os.path.join(ROOT, "harness", "fixtures", "book_fixture.json") if mode == "fixture"
                   else os.path.join(ROOT, "contract", "book_inputs.json"))
    inputs = json.load(open(inputs_path)).get("inputs", {})

    changed = []
    for r in recs:
        if r["entity_type"] not in CARRIER_TYPES:
            continue
        row = inputs.get(r["entity_id"])
        if not row:
            continue
        old = r["exposure_inputs"]["book_concentration"]["rating_0_4"]
        r["exposure_inputs"]["book_concentration"] = build_subfactor(row, mode)
        changed.append((r["entity_id"], old, r["exposure_inputs"]["book_concentration"]["rating_0_4"], row))

    save_records(recs, mode, out_path)

    print(f"=== MEASURE book_concentration ({mode}) ===")
    print(f"base: {base_label}  inputs: {os.path.basename(inputs_path)}\n")
    for eid, old, new, row in changed:
        sh = (float(row.get('energy_power_gwp',0))+float(row.get('datacentre_tech_gwp',0)))/float(row['total_gwp'])
        print(f"  {eid:<22} rating {old} -> {new}   energy share {sh:.0%}  ({row.get('energy_power_gwp')}/{row['total_gwp']} {row.get('currency','GBP')}m)")
    carriers = [r for r in recs if r["entity_type"] in CARRIER_TYPES]
    print(f"\ncarriers updated: {len(changed)}/{len(carriers)}  (intermediaries/assets left assessed)")
    print(f"wrote: data/{os.path.basename(out_path)}")
    if mode == "fixture":
        print("\nNOTE: fixture mode is a UNIT TEST; placeholder values, flagged FIXTURE_DEMO, never the index.")

if __name__ == "__main__":
    main()
