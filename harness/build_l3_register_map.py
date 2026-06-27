#!/usr/bin/env python3
"""Build contract/l3_register_map.json — ECR/TEC search terms for all L3 assets.

  python3 harness/build_l3_register_map.py
  python3 harness/build_l3_register_map.py --write
"""
from __future__ import annotations

import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.json")
GEO = os.path.join(ROOT, "contract", "asset_geo_tags.json")
OUT = os.path.join(ROOT, "contract", "l3_register_map.json")

LEGACY = {
    "asset-kao-harlow": ["Harlow", "Kao Data", "Edinburgh Way Harlow"],
    "asset-ark": ["Corsham", "Spring Park Corsham", "Ark Data"],
    "asset-latos-bridgend": ["Bridgend", "Latos", "Cardiff Rover"],
    "asset-culham-aigz": ["Culham", "UKAEA Culham"],
}

# Transmission / named register anchors (TEC-first in measure_non_firm.py)
TEC_TERMS = {
    "asset-culham-aigz": ["Culham"],
    "gate-burton-energy-park-lincolnshire": ["Gate Burton", "Cottam"],
    "harmony-energy-pillswood-hull": ["Pillswood", "Creyke Beck"],
    "whitelee-wind-farm-eaglesham-moor": ["Whitelee", "Eaglesham"],
    "seagreen-offshore-wind-farm-angus": ["Seagreen"],
    "cleve-hill-solar-park-kent": ["Cleve Hill", "Graveney"],
    "coalburn-1-bess-south-lanarkshire": ["Coalburn"],
    "zenobe-capenhurst-chester": ["Capenhurst", "Zenobe"],
    "statera-thurrock-storage-essex": ["Tilbury", "Thurrock", "Statera"],
}

STOP = {
    "the", "and", "for", "park", "farm", "energy", "data", "centre", "center",
    "campus", "series", "offshore", "wind", "solar", "storage", "bess", "uk",
    "global", "centers", "centres", "group", "london", "west", "north", "south",
}


def _dedupe(terms: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for t in terms:
        key = t.lower()
        if key in seen or key in STOP or len(key) < 3:
            continue
        seen.add(key)
        out.append(t)
    return out


def _terms_from_record(rec: dict, geo_ent: dict | None) -> list[str]:
    eid = rec["entity_id"]
    if eid in LEGACY:
        return LEGACY[eid]
    if eid in TEC_TERMS:
        return TEC_TERMS[eid]

    name = rec.get("name") or ""
    terms: list[str] = []

    if geo_ent:
        ref = geo_ent.get("register_ref") or ""
        for chunk in re.split(r"[;/]", ref):
            chunk = chunk.strip()
            if ":" in chunk:
                chunk = chunk.split(":", 1)[1]
            for tok in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", chunk):
                if tok.lower() not in STOP:
                    terms.append(tok)

    if "—" in name:
        loc = name.split("—", 1)[1].strip()
        terms.extend(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", loc))
    elif " - " in name:
        loc = name.split(" - ", 1)[1].strip()
        terms.extend(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", loc))

    parts = eid.replace("asset-", "").split("-")
    for p in parts:
        if len(p) > 2 and p.lower() not in STOP:
            terms.append(p.replace("-", " ").title() if "-" in p else p)

    for tok in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", name.split("—")[0].split("(")[0]):
        if tok.lower() not in STOP:
            terms.append(tok)

    return _dedupe(terms)[:10]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    records = json.load(open(RECORDS))
    geo = json.load(open(GEO)).get("entities", {}) if os.path.isfile(GEO) else {}
    assets = {}
    for r in records:
        if r.get("layer") != 3:
            continue
        eid = r["entity_id"]
        terms = _terms_from_record(r, geo.get(eid))
        entry = {"terms": terms, "name": r.get("name", "")}
        if eid in TEC_TERMS:
            entry["register"] = "tec"
        assets[eid] = entry

    doc = {
        "_doc": "L3 asset → register search terms for measure_non_firm.py --live",
        "assets": assets,
    }

    if args.write:
        json.dump(doc, open(OUT, "w"), indent=2, ensure_ascii=False)
        tec_n = sum(1 for v in assets.values() if v.get("register") == "tec")
        print(f"wrote {OUT} ({len(assets)} assets, {tec_n} TEC-priority)")
    else:
        print(json.dumps({k: v["terms"] for k, v in assets.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
