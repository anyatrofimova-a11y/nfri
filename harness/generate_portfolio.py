#!/usr/bin/env python3
"""Generate portfolio pass patches (portfolio_narrative + placements).

Reads site/data/profiles.json swarm stats, entity_tags, asset_coverage_links.
Writes data/portfolio/batch*.json for apply_synthesis.py --all-portfolio.

  python3 harness/generate_portfolio.py --all
  python3 harness/generate_portfolio.py --batch batch1
"
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "site", "data", "profiles.json")
MANIFEST = os.path.join(ROOT, "data", "portfolio", "manifest.json")
OUT_DIR = os.path.join(ROOT, "data", "portfolio")
TAGS = os.path.join(ROOT, "contract", "entity_tags.json")
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
    "broker": [],
}


def _placements(eid: str, tag_map: dict) -> list:
    tags = set(tag_map.get(eid, []))
    chips = []
    seen = set()
    for tag in tags:
        for chip in PRODUCT_BY_TAG.get(tag, []):
            if chip["id"] not in seen:
                seen.add(chip["id"])
                chips.append(dict(chip))
    return chips[:6]


def _narrative(eid: str, p: dict, coverage: dict) -> str:
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
    cov = (coverage.get("links") or {}).get(eid)
    if cov and cov.get("covered_assets"):
        named = ", ".join(cov["covered_assets"][:3])
        parts.append(f"Named placement evidence links this carrier to {named} (coverage overlay).")
    else:
        parts.append("Links are segment-tag inferred until entity_links.json is populated from placement research.")
    return " ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", action="append")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    profiles = json.load(open(PROFILES))
    batches = json.load(open(MANIFEST))["batches"]
    tag_map = json.load(open(TAGS)).get("entities", {}) if os.path.isfile(TAGS) else {}
    coverage = json.load(open(COVERAGE)) if os.path.isfile(COVERAGE) else {"links": {}}

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
            narr = _narrative(eid, p, coverage)
            if not narr:
                continue
            entities[eid] = {
                "portfolio_narrative": narr,
                "placements": _placements(eid, tag_map),
            }
        out = {"pass": "portfolio", "batch": bk, "entities": entities}
        path = os.path.join(OUT_DIR, f"{bk}.json")
        json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {path} ({len(entities)} entities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
