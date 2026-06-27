#!/usr/bin/env python3
"""Build a substantiated exposure-map artifact from scored records.

Joins the scored universe (data/records.scored.json) with the authoritative NESO
constraint-boundary curtailment probabilities (contract/constraint_boundary.json +
contract/asset_boundary_map.json) to produce site/data/exposure_map.json — the data
behind the standalone exposure-map visualisation (site/exposure-map.html).

No synthetic values: every number is read from a scored record or a real boundary map.
Unmapped Layer-3 assets keep the national-mean curtailment probability and are flagged
(`boundary_mapped: false`); a coarse `nation` is inferred from the location string for
display grouping only and never feeds a score.

  python3 harness/build_exposure_map.py
"""
from __future__ import annotations
import json, os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(ROOT, p)))

# the 20 carriers/syndicates added in the Layer-1 expansion pass (canonical ids, for highlighting)
NEW_CARRIERS = {
    "lancashire-3010","apollo-1969","inigo-1301","beat-4242","ark-4020","atrium-609","chaucer-1084",
    "faraday-435","newline-1218","antares-1274","aegis-london-1225","talbot-1183","allied-world-2232",
    "travelers-5000","cna-hardy-382","aig-uk","bhsi-uk","hdi-global-uk","axis-1686","sompo-intl-energy-uk",
}

def infer_nation(name: str) -> str:
    n = name.lower()
    if any(t in n for t in ("scotland","shetland","angus","fort augustus","auchteraw","seagreen","viking")):
        return "Scotland"
    if any(t in n for t in ("wales","newport","cardiff","bridgend")):
        return "Wales"
    return "England"

def rating(rec, axis, key):
    sf = rec.get(axis, {}).get(key)
    return sf.get("rating_0_4") if isinstance(sf, dict) else None

def first_source(rec, axis, key):
    sf = rec.get(axis, {}).get(key, {})
    srcs = sf.get("sources") or []
    return srcs[0] if srcs else None

def main():
    recs = load("data/records.scored.json")
    boundaries = load("contract/constraint_boundary.json")["boundaries"]
    amap = load("contract/asset_boundary_map.json")["assets"]
    nat_mean = boundaries.get("unknown", {}).get("curtailment_prob_norm")

    assets, carriers = [], []
    bstat = {k: {"label": v.get("label", k), "curtailment_prob_norm": v.get("curtailment_prob_norm"),
                 "asset_count": 0, "exposure_sum": 0.0} for k, v in boundaries.items()}

    for r in recs:
        sc = r.get("scores", {})
        exp, prep = sc.get("exposure_0_100"), sc.get("preparedness_0_100")
        if r.get("layer") == 3:
            bkey = amap.get(r["entity_id"], "unknown")
            bmeta = boundaries.get(bkey, boundaries.get("unknown", {}))
            assets.append({
                "entity_id": r["entity_id"], "name": r["name"], "entity_type": r.get("entity_type"),
                "boundary": bkey, "boundary_label": bmeta.get("label", bkey),
                "boundary_mapped": r["entity_id"] in amap,
                "curtailment_prob_norm": bmeta.get("curtailment_prob_norm", nat_mean),
                "nation": infer_nation(r["name"]),
                "non_firm_intensity": rating(r, "exposure_inputs", "non_firm_intensity"),
                "aggregation_correlation": rating(r, "exposure_inputs", "aggregation_correlation"),
                "exposure": exp, "preparedness": prep,
                "margin_of_safety": sc.get("margin_of_safety"), "quadrant": sc.get("quadrant"),
                "source": first_source(r, "exposure_inputs", "non_firm_intensity"),
            })
            if bkey in bstat and exp is not None:
                bstat[bkey]["asset_count"] += 1
                bstat[bkey]["exposure_sum"] += exp
        elif r.get("layer") == 1:
            carriers.append({
                "entity_id": r["entity_id"], "name": r["name"], "entity_type": r.get("entity_type"),
                "parent_group": r.get("parent_group", ""), "is_new": r["entity_id"] in NEW_CARRIERS,
                "exposure": exp, "preparedness": prep,
                "margin_of_safety": sc.get("margin_of_safety"), "quadrant": sc.get("quadrant"),
                "overall_confidence": sc.get("overall_confidence"),
                "book_concentration": rating(r, "exposure_inputs", "book_concentration"),
                "trigger_gap": rating(r, "exposure_inputs", "trigger_gap"),
                "product_fit": rating(r, "preparedness_inputs", "product_fit"),
                "capital_reinsurance": rating(r, "preparedness_inputs", "capital_reinsurance"),
                "underwriting_expertise": rating(r, "preparedness_inputs", "underwriting_expertise"),
                "source": first_source(r, "exposure_inputs", "book_concentration"),
            })

    bsummary = []
    for k, s in bstat.items():
        if k == "unknown" or not s["asset_count"]:
            continue  # unmapped assets carry the national mean — not a real boundary ranking row
        bsummary.append({"boundary": k, "label": s["label"],
                         "curtailment_prob_norm": s["curtailment_prob_norm"],
                         "asset_count": s["asset_count"],
                         "mean_asset_exposure": round(s["exposure_sum"]/s["asset_count"], 1)})
    bsummary.sort(key=lambda x: (x["curtailment_prob_norm"] or 0), reverse=True)
    unmapped_assets = sum(1 for a in assets if not a["boundary_mapped"])

    median_exp = sorted(c["exposure"] for c in carriers if c["exposure"] is not None)
    median_prep = sorted(c["preparedness"] for c in carriers if c["preparedness"] is not None)
    def med(a): return a[len(a)//2] if a else None

    out = {
        "generated": date.today().isoformat(),
        "model_version": "0.2",
        "universe_size": len(recs),
        "carrier_count": len(carriers), "new_carrier_count": sum(c["is_new"] for c in carriers),
        "asset_count": len(assets), "unmapped_asset_count": unmapped_assets,
        "carrier_median_exposure": med(median_exp), "carrier_median_preparedness": med(median_prep),
        "boundaries": bsummary,
        "assets": sorted(assets, key=lambda a: (a["exposure"] is None, -(a["exposure"] or 0))),
        "carriers": sorted(carriers, key=lambda c: (c["margin_of_safety"] is None, c["margin_of_safety"] or 0)),
    }
    for p in ("data/exposure_map.json", "site/data/exposure_map.json"):
        fp = os.path.join(ROOT, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        json.dump(out, open(fp, "w"), indent=2, ensure_ascii=False)

    print(f"exposure_map: {len(carriers)} carriers ({out['new_carrier_count']} new), {len(assets)} L3 assets, "
          f"{len(bsummary)} constraint boundaries; median carrier exp={out['carrier_median_exposure']} "
          f"prep={out['carrier_median_preparedness']}")
    print("wrote data/exposure_map.json + site/data/exposure_map.json")

if __name__ == "__main__":
    main()
