#!/usr/bin/env python3
"""Propagate L3 non_firm_compute_exposure to carrier non_firm_intensity via asset_link.

Where covered_assets is known, average linked asset interaction indices.
Where unknown, use portfolio mean of L3 interactions with confidence penalty.

  python3 harness/link_propagation.py --live
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

from measure_utils import CARRIER_TYPES, PRODUCT_ENTITY_TYPES, ROOT, load_records, save_records

TODAY = date.today().isoformat()
CITATION_IDS = ["ACAD-CCM-NF-LOAD", "NESO-CONSTRAINT-COSTS", "ACT-CREDIBILITY"]
PROPAGATE_TYPES = CARRIER_TYPES | PRODUCT_ENTITY_TYPES


def index_to_rating(index: float) -> int:
    for mx, rating in ((0.01, 0), (0.05, 1), (0.15, 2), (0.35, 3), (1.01, 4)):
        if index <= mx:
            return rating
    return 4


def l3_interactions(recs: list) -> dict[str, dict]:
    out = {}
    for r in recs:
        if r.get("layer") != 3:
            continue
        comp = r["exposure_inputs"].get("non_firm_compute_exposure", {})
        mv = comp.get("measured_value") or {}
        idx = mv.get("interaction_index")
        if idx is None:
            continue
        out[r["entity_id"]] = {"index": float(idx), "record": r, "comp": comp}
    return out


def portfolio_mean(l3: dict) -> float | None:
    if not l3:
        return None
    return sum(v["index"] for v in l3.values()) / len(l3)


def build_propagated(index: float, method: str, detail: str, confidence: str) -> dict:
    rating = index_to_rating(index)
    return {
        "rating_0_4": rating,
        "latent_rating_0_4": rating,
        "deterministic_rating_0_4": rating,
        "measured_value": round(index, 4),
        "unit": "propagated interaction_index",
        "as_of": TODAY,
        "evidence_tier": "derived",
        "source_type": "propagated",
        "rationale": f"Propagated non_firm_compute_exposure ({method}): {detail} → I={index:.4f}, rating={rating}.",
        "sources": ["https://www.neso.energy/industry-information/constraint-costs"],
        "confidence": confidence,
        "citation_ids": CITATION_IDS,
        "propagation_method": method,
    }


def main() -> int:
    mode = "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    by_id = {r["entity_id"]: r for r in recs}
    l3 = l3_interactions(recs)
    mean_idx = portfolio_mean(l3)

    changed = []
    for rec in recs:
        if rec["entity_type"] not in PROPAGATE_TYPES:
            continue
        if rec.get("layer") == 3:
            continue
        al = rec.get("asset_link") or {}
        covered = [a for a in (al.get("covered_assets") or []) if a in l3]
        if covered:
            index = sum(l3[a]["index"] for a in covered) / len(covered)
            method = "covered_assets_mean"
            detail = f"mean of {len(covered)} linked assets: {', '.join(covered)}"
            confidence = "high" if len(covered) >= 2 else "medium"
        elif mean_idx is not None:
            index = mean_idx
            method = "l3_portfolio_mean"
            detail = f"no public covered_assets; L3 portfolio mean over {len(l3)} assets"
            confidence = "low"
        else:
            continue
        old_sf = rec["exposure_inputs"]["non_firm_intensity"]
        lat = int(old_sf.get("latent_rating_0_4", old_sf.get("rating_0_4", 2)))
        propagated = build_propagated(index, method, detail, confidence)
        propagated["latent_rating_0_4"] = lat
        propagated["rating_0_4"] = lat
        rec["exposure_inputs"]["non_firm_intensity"] = propagated
        if al is not None:
            rec["asset_link"] = al
        changed.append((rec["entity_id"], lat, rec["exposure_inputs"]["non_firm_intensity"]["deterministic_rating_0_4"], method))

    save_records(recs, mode, out_path)

    print(f"=== LINK propagation → non_firm_intensity ({mode}) ===")
    print(f"base: {base_label}  L3 interactions: {len(l3)}  portfolio_mean={mean_idx}\n")
    for eid, old, new, method in changed:
        print(f"  {eid:<26} rating {old} -> {new}   ({method})")
    print(f"\ncarriers/MGAs/reinsurers updated: {len(changed)}")
    print(f"wrote: data/{os.path.basename(out_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
