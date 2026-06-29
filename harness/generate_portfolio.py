#!/usr/bin/env python3
"""Generate portfolio pass patches (portfolio_narrative + placements).

Reads site/data/profiles.json swarm stats, entity_tags, entity_links + asset_coverage_links.
Writes data/portfolio/batch*.json for apply_synthesis.py --all-portfolio.

  python3 harness/generate_portfolio.py --all
  python3 harness/generate_portfolio.py --batch batch1
"""
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "site", "data", "profiles.json")
RECORDS = os.path.join(ROOT, "data", "records.scored.json")
MANIFEST = os.path.join(ROOT, "data", "portfolio", "manifest.json")
OUT_DIR = os.path.join(ROOT, "data", "portfolio")
PLACEMENTS_DIR = os.path.join(ROOT, "data", "placements")
TAGS = os.path.join(ROOT, "contract", "entity_tags.json")
ENTITY_LINKS = os.path.join(ROOT, "contract", "entity_links.json")
COVERAGE = os.path.join(ROOT, "contract", "asset_coverage_links.json")

# KG-aligned product chips (placement_mapper scaffold — expand from graph.json)
PRODUCT_BY_TAG = {
    "parametric": [
        {"id": "parametrix-sla-dc", "label": "Parametrix SLA (DC)", "url": "https://www.parametrixinsurance.com/solutions-sla-insurance-data-centers"},
        {"id": "arbol-energy", "label": "Arbol parametric (energy)", "url": "https://www.arbol.io/solutions/energy"},
        {"id": "axa-climate", "label": "AXA Climate parametric", "url": "https://climate.axa/"}],
    "data_centre": [
        {"id": "marsh-nimbus", "label": "Marsh Nimbus (DC facility)", "url": "https://www.marsh.com/en/services/infrastructure/data-centers.html"},
        {"id": "descartes-dc", "label": "Descartes parametric DC", "url": "https://descartesunderwriting.com/"}],
    "energy": [
        {"id": "kwh-analytics", "label": "kWh Analytics (renewables data)", "url": "https://www.kwhanalytics.com/"},
        {"id": "gcube-renewables", "label": "GCube renewables", "url": "https://www.tmhcc.com/en-us/products/renewables"}],
    "broker": [
        {"id": "marsh-nimbus", "label": "Marsh Nimbus (DC facility)", "url": "https://www.marsh.com/en/services/infrastructure/data-centers.html"},
        {"id": "descartes-dc", "label": "Descartes parametric DC", "url": "https://descartesunderwriting.com/"},
        {"id": "kwh-analytics", "label": "kWh Analytics (renewables data)", "url": "https://www.kwhanalytics.com/"}],
    "reinsurance": [
        {"id": "gcube-renewables", "label": "GCube renewables", "url": "https://www.tmhcc.com/en-us/products/renewables"},
        {"id": "kwh-analytics", "label": "kWh Analytics (renewables data)", "url": "https://www.kwhanalytics.com/"}],
}


def _infer_tags(eid: str, layer: int, entity_type: str, tag_map: dict) -> list[str]:
    if eid in tag_map:
        return list(tag_map[eid])
    et = (entity_type or "").lower()
    if layer == 1:
        return ["parametric", "energy"] if "mga" in et else ["energy", "parametric"]
    if layer == 2:
        return ["broker", "data_centre", "energy"]
    if layer == 3:
        if et == "data_centre":
            return ["data_centre"]
        return ["energy"]
    if layer == 4:
        return ["reinsurance", "energy"]
    return ["energy"]


def _load_link_map() -> dict:
    """Merge entity_links (primary) with legacy asset_coverage_links."""
    links: dict = {}
    if os.path.isfile(COVERAGE):
        links.update(json.load(open(COVERAGE)).get("links") or {})
    if os.path.isfile(ENTITY_LINKS):
        links.update(json.load(open(ENTITY_LINKS)).get("links") or {})
    return links


def _asset_label(eid: str, profiles: dict) -> str:
    p = profiles.get(eid) or {}
    name = (p.get("name") or "").strip()
    if name:
        return name
    return eid.replace("-", " ").replace("_", " ").title()


def _linked_asset_chips(eid: str, link_map: dict, profiles: dict, *, limit: int = 6) -> list:
    """Named L3 asset chips from researched entity_links / coverage evidence."""
    cov = link_map.get(eid) or {}
    assets = cov.get("covered_assets") or []
    if not assets:
        return []
    src = (cov.get("sources") or ["#"])[0]
    return [
        {
            "id": aid,
            "label": _asset_label(aid, profiles),
            "url": src,
            "link_type": cov.get("link_type", "named_placement"),
        }
        for aid in assets[:limit]
    ]


def _product_chips(eid: str, tag_map: dict, *, layer: int = 1, entity_type: str = "") -> list:
    tags = set(_infer_tags(eid, layer, entity_type, tag_map))
    chips = []
    seen = set()
    for tag in tags:
        for chip in PRODUCT_BY_TAG.get(tag, []):
            if chip["id"] not in seen:
                seen.add(chip["id"])
                chips.append(dict(chip))
    return chips[:6]


def _placements(
    eid: str,
    tag_map: dict,
    link_map: dict,
    profiles: dict,
    *,
    layer: int = 1,
    entity_type: str = "",
) -> list:
    linked = _linked_asset_chips(eid, link_map, profiles)
    if linked:
        return linked
    return _product_chips(eid, tag_map, layer=layer, entity_type=entity_type)


def _narrative(eid: str, p: dict, link_map: dict, profiles: dict) -> str:
    port = p.get("portfolio") or {}
    n = port.get("n", 0)
    if not n:
        return
    cm = p.get("mos", 0)
    avg = port.get("mosAvg", cm)
    mn, mx = port.get("mosMin", cm), port.get("mosMax", cm)
    assets = port.get("assets") or []
    worst = min(assets, key=lambda a: a["mos"]) if assets else None
    best = max(assets, key=lambda a: a["mos"]) if assets else None
    gap = round(cm - avg, 1)
    parts = [
        f"On the current segment-linked slice, {p['name']} maps {n} L3 assets with portfolio MoS "
        f"from {mn:+.1f} to {mx:+.1f} (mean {avg:+.1f}) against a carrier headline MoS of {cm:+.1f}."
    ]
    if abs(gap) >= 5:
        direction = "compresses" if gap < 0 else "widens"
        parts.append(
            f"Headline margin {direction} versus the linked book by {abs(gap):.1f} points — "
            f"{'the carrier looks safer than its prototype assets' if gap > 0 else 'tail assets drag the book shape'}."
        )
    if worst and best and worst["id"] != best["id"]:
        parts.append(
            f"Tail risk concentrates at {worst['name']} (MoS {worst['mos']:+.1f}, {worst['quad'].replace('_', ' ')}); "
            f"best shape at {best['name']} (MoS {best['mos']:+.1f})."
        )
    cov = link_map.get(eid)
    if cov and cov.get("covered_assets"):
        named = ", ".join(_asset_label(a, profiles) for a in cov["covered_assets"][:3])
        conf = cov.get("confidence", "medium")
        parts.append(f"Named placement evidence ({conf} confidence) links this carrier to {named}.")
    else:
        parts.append("Links are segment-tag inferred until entity_links.json is populated from placement research.")
    return " ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", action="append")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--placements-all", action="store_true", help="placement chips for every scored entity")
    args = ap.parse_args()

    if args.placements_all:
        recs = [r for r in json.load(open(RECORDS)) if r.get("scores")]
        profiles = json.load(open(PROFILES))
        tag_map = json.load(open(TAGS)).get("entities", {}) if os.path.isfile(TAGS) else {}
        link_map = _load_link_map()
        entities = {}
        for r in recs:
            eid = r["entity_id"]
            chips = _placements(
                eid,
                tag_map,
                link_map,
                profiles,
                layer=r.get("layer", 0),
                entity_type=r.get("entity_type", ""),
            )
            if chips:
                entities[eid] = {"placements": chips}
        os.makedirs(PLACEMENTS_DIR, exist_ok=True)
        out_path = os.path.join(PLACEMENTS_DIR, "all.json")
        json.dump({"pass": "placements", "entities": entities}, open(out_path, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {out_path} ({len(entities)} entities)")
        if not args.all and not args.batch:
            return 0

    profiles = json.load(open(PROFILES))
    batches = json.load(open(MANIFEST))["batches"]
    tag_map = json.load(open(TAGS)).get("entities", {}) if os.path.isfile(TAGS) else {}
    link_map = _load_link_map()

    keys = sorted(batches.keys()) if args.all else (args.batch or [])
    if not keys:
        print("Specify --all or --batch", file=__import__("sys").stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for bk in keys:
        ids = batches.get(bk, [])
        entities = {}
        for eid in ids:
            p = profiles.get(eid)
            if not p or p.get("layer") != 1:
                continue
            narr = _narrative(eid, p, link_map, profiles)
            if not narr:
                continue
            entities[eid] = {
                "portfolio_narrative": narr,
                "placements": _placements(
                    eid, tag_map, link_map, profiles, layer=1, entity_type=p.get("type", "")
                ),
            }
        out = {"pass": "portfolio", "batch": bk, "entities": entities}
        path = os.path.join(OUT_DIR, f"{bk}.json")
        json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {path} ({len(entities)} entities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
