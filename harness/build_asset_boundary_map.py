#!/usr/bin/env python3
"""Build contract/asset_boundary_map.json from asset_geo_tags + L3 universe.

  python3 harness/build_asset_boundary_map.py
  python3 harness/build_asset_boundary_map.py --write
"""
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, "contract", "asset_geo_tags.json")
RECORDS = os.path.join(ROOT, "data", "records.json")
OUT = os.path.join(ROOT, "contract", "asset_boundary_map.json")

ZONE_TO_BOUNDARY = {
    "ssen_west_london": "southern",
    "london_docklands": "east_england",
    "south_wales": "south_wales",
    "scotland_wind": "scotland",
    "north_england": "unknown",
    "nged_midlands": "unknown",
    "south_east_solar": "east_england",
}

DNO_TO_BOUNDARY = {
    "ukpn": "east_england",
    "ssen": "southern",
    "nged": "south_wales",
    "npg": "unknown",
    "spen": "scotland",
}

# Site-specific overrides (constraint_boundary.json keys)
OVERRIDES = {
    "asset-ark": "south_west",
    "asset-culham-aigz": "southern",
    "asset-kao-harlow": "east_england",
    "asset-latos-bridgend": "south_wales",
    "harmony-energy-pillswood-hull": "scotland",
    "gate-burton-energy-park-lincolnshire": "unknown",
}


def boundary_for(eid: str, geo: dict) -> str:
    if eid in OVERRIDES:
        return OVERRIDES[eid]
    spec = geo.get("entities", {}).get(eid, {})
    zone = spec.get("constraint_zone")
    if zone and zone in ZONE_TO_BOUNDARY:
        return ZONE_TO_BOUNDARY[zone]
    dno = (spec.get("dno") or "").lower()
    return DNO_TO_BOUNDARY.get(dno, "unknown")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    geo = json.load(open(GEO)) if os.path.isfile(GEO) else {"entities": {}}
    records = json.load(open(RECORDS))
    l3 = [r for r in records if r.get("layer") == 3]
    assets = {r["entity_id"]: boundary_for(r["entity_id"], geo) for r in l3}

    doc = {
        "__LIVE__": True,
        "purpose": "Maps Layer-3 asset entity_id → constraint_boundary.json key for curtailment_prob term.",
        "citation_ids": ["NESO-CONSTRAINT-COSTS", "DCUSA-ECR"],
        "assets": assets,
    }

    if args.write:
        json.dump(doc, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {OUT} ({len(assets)} L3 assets)")
    else:
        print(json.dumps(assets, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
