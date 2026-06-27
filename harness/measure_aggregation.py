#!/usr/bin/env python3
"""Derived aggregation_correlation from constraint-boundary HHI over linked assets.

For Layer-3 assets: HHI=1.0 on the asset's mapped NESO boundary (single-zone concentration).
For carriers/MGAs with asset_link.covered_assets: MW-weighted HHI across boundary zones.

  python3 harness/measure_aggregation.py --live
  python3 harness/measure_aggregation.py --fixture
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from datetime import date

from measure_utils import PRODUCT_ENTITY_TYPES, ROOT, load_records, save_records

TODAY = date.today().isoformat()
CITATION_IDS = ["ACT-HHI-EIOPA", "ACT-HHI-CAS", "LLOYDS-RDS", "NESO-CONSTRAINT-COSTS"]
BOUNDARY_MAP_PATH = os.path.join(ROOT, "contract", "asset_boundary_map.json")
RISK_MODEL_PATH = os.path.join(ROOT, "contract", "risk_model.json")
TEC_URL = "https://www.neso.energy/data-portal/transmission-entry-capacity-register"


def load_hhi_thresholds() -> list[tuple[float, int]]:
    spec = json.load(open(RISK_MODEL_PATH))["deterministic_mappings"]["hhi_to_aggregation_rating"]["thresholds"]
    return [(float(t["max"]), int(t["rating"])) for t in spec]


def hhi_to_rating(hhi: float, thresholds: list[tuple[float, int]]) -> int:
    for mx, rating in thresholds:
        if hhi <= mx:
            return rating
    return 4


def asset_weight(rec: dict | None) -> float:
    """Import MW from measured non_firm / interaction, else unit weight."""
    if not rec:
        return 1.0
    nf = rec["exposure_inputs"].get("non_firm_intensity", {})
    mv = nf.get("measured_value")
    if isinstance(mv, dict):
        mw = mv.get("mw_total") or mv.get("import_mw")
        if mw:
            return float(mw)
    comp = rec["exposure_inputs"].get("non_firm_compute_exposure", {})
    cmv = (comp.get("measured_value") or {})
    if isinstance(cmv, dict) and cmv.get("import_mw"):
        return float(cmv["import_mw"])
    return 1.0


def compute_hhi(asset_ids: list[str], asset_map: dict, weights: dict[str, float]) -> dict | None:
    zone_mw: dict[str, float] = defaultdict(float)
    for aid in asset_ids:
        bkey = asset_map.get(aid)
        if not bkey:
            continue
        zone_mw[bkey] += max(0.0, weights.get(aid, 1.0))
    if not zone_mw:
        return None
    total = sum(zone_mw.values())
    shares = {z: w / total for z, w in zone_mw.items()}
    hhi = round(sum(s * s for s in shares.values()), 4)
    return {
        "hhi": hhi,
        "zones": {z: round(w, 2) for z, w in zone_mw.items()},
        "zone_shares": {z: round(s, 4) for z, s in shares.items()},
        "n_assets": len(asset_ids),
        "n_zones": len(zone_mw),
    }


def build_subfactor(parts: dict, method: str, detail: str, mode: str) -> dict:
    thresholds = load_hhi_thresholds()
    hhi = parts["hhi"]
    rating = hhi_to_rating(hhi, thresholds)
    return {
        "rating_0_4": rating,
        "latent_rating_0_4": rating,
        "deterministic_rating_0_4": rating,
        "measured_value": parts,
        "unit": "HHI (0-1)",
        "as_of": TODAY,
        "evidence_tier": "derived" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "register_derived",
        "rationale": (
            f"Derived aggregation_correlation ({method}): {detail} "
            f"HHI={hhi:.4f} over {parts['n_zones']} boundary zone(s) → rating {rating}."
        ),
        "sources": [
            "https://www.neso.energy/data-portal/constraint-breakdown",
            TEC_URL,
        ],
        "confidence": "high" if parts["n_zones"] >= 2 and parts["n_assets"] >= 2 else "medium",
        "citation_ids": CITATION_IDS,
        "derivation_method": method,
    }


def main() -> int:
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    asset_map = json.load(open(BOUNDARY_MAP_PATH))["assets"]
    by_id = {r["entity_id"]: r for r in recs}
    weights = {eid: asset_weight(by_id.get(eid)) for eid in asset_map}

    changed = []
    for rec in recs:
        eid = rec["entity_id"]
        layer = rec.get("layer")
        etype = rec.get("entity_type")

        if layer == 3 and eid in asset_map:
            parts = compute_hhi([eid], asset_map, {eid: weights[eid]})
            if not parts:
                continue
            method = "l3_single_boundary"
            detail = f"asset on {asset_map[eid]} boundary;"
        elif etype in PRODUCT_ENTITY_TYPES:
            al = rec.get("asset_link") or {}
            covered = [a for a in (al.get("covered_assets") or []) if a in asset_map]
            if not covered:
                continue
            parts = compute_hhi(covered, asset_map, weights)
            if not parts:
                continue
            method = "covered_assets_boundary_hhi"
            detail = f"MW-weighted over {len(covered)} linked assets ({', '.join(covered)});"
        else:
            continue

        old = rec["exposure_inputs"]["aggregation_correlation"].get("rating_0_4")
        lat = int(rec["exposure_inputs"]["aggregation_correlation"].get("latent_rating_0_4", old or 2))
        sf = build_subfactor(parts, method, detail, mode)
        sf["latent_rating_0_4"] = lat
        sf["rating_0_4"] = lat
        rec["exposure_inputs"]["aggregation_correlation"] = sf
        changed.append((eid, old, lat, sf["deterministic_rating_0_4"], parts["hhi"], method))

    save_records(recs, mode, out_path)

    print(f"=== MEASURE aggregation_correlation ({mode}) ===")
    print(f"base: {base_label}  boundaries: contract/asset_boundary_map.json\n")
    for eid, old, lat, det, hhi, method in changed:
        print(f"  {eid:<26} lat {lat} det {old}->{det}   HHI={hhi:.4f}  ({method})")
    l3_n = sum(1 for r in recs if r.get("layer") == 3 and r["entity_id"] in asset_map)
    linked_n = sum(
        1 for r in recs
        if r.get("entity_type") in PRODUCT_ENTITY_TYPES and (r.get("asset_link") or {}).get("covered_assets")
    )
    print(f"\nentities updated: {len(changed)}  (L3={l3_n}, linked carriers/MGAs={linked_n})")
    print(f"wrote: data/{os.path.basename(out_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
