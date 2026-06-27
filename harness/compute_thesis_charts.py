#!/usr/bin/env python3
"""Pre-compute chart payloads for the on-transformation thesis page.

Stats (slope, R², CI) are computed in Python and passed as D.thesisCharts so the
client only renders — matching the ai-transformation.fyi annotation pattern.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

LAYER_LABEL = {1: "Carriers", 2: "MGAs & brokers", 3: "Assets", 4: "Reinsurers"}
QUAD_ORDER = ["earning_it", "whitespace", "sidelined", "exposed"]
SEGMENT_LABEL = {
    "carrier": "Carriers",
    "broker_mga": "Brokers & MGAs",
    "energy_asset": "Energy assets",
    "data_centre": "Data centres",
    "parametric": "Parametric / SLA",
    "reinsurer": "Reinsurers",
    "other": "Other",
}


def _load_entity_tags(root=None):
    import os
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "contract", "entity_tags.json")
    if os.path.exists(path):
        return json.load(open(path))
    return {"entities": {}, "segments": {}}


def _infer_segment(p: dict, tag_map: dict) -> str:
    eid = p.get("id", "")
    if eid in tag_map:
        tags = tag_map[eid]
        if "data_centre" in tags:
            return "data_centre"
        if "parametric" in tags:
            return "parametric"
        if "energy" in tags:
            return "energy_asset"
        if "broker" in tags:
            return "broker_mga"
        if "reinsurance" in tags:
            return "reinsurer"
    layer = p.get("layer")
    et = (p.get("type") or "").lower()
    name = (p.get("name") or "").lower()
    if layer == 1:
        return "carrier"
    if layer == 2:
        return "broker_mga"
    if layer == 4:
        return "reinsurer"
    if layer == 3:
        if "data" in name or "dc" in et or "centre" in name:
            return "data_centre"
        return "energy_asset"
    return "other"


def _meas(p: dict) -> float:
    return (p.get("detExp", 0) + p.get("detPrep", 0)) / 2


def _linreg(xs: list[float], ys: list[float]) -> dict:
    n = len(xs)
    if n < 2:
        return {"slope": 0.0, "intercept": 0.0, "r2": 0.0, "n": n, "ci_lo": 0.0, "ci_hi": 0.0}
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    slope = num / den if den else 0.0
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    # Standard error of slope (simple OLS)
    if n > 2 and den:
        se = math.sqrt(ss_res / (n - 2) / den)
        ci = 1.96 * se
    else:
        ci = 0.0
    return {
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "r2": round(r2, 3),
        "n": n,
        "ci_lo": round(slope - ci, 4),
        "ci_hi": round(slope + ci, 4),
    }


def _load_coverage_links(root=None) -> dict:
    import os
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "contract", "asset_coverage_links.json")
    if os.path.exists(path):
        return json.load(open(path)).get("links", {})
    return {}


def _asset_payload(p: dict) -> dict:
    return {"id": p["id"], "name": p["name"], "mos": p["mos"], "quad": p["quad"]}


def _build_by_carrier(pts: list[dict], coverage: dict) -> dict[str, list[dict]]:
    by_id = {p["id"]: p for p in pts}
    out: dict[str, list[dict]] = {}
    for entity_id, spec in coverage.items():
        parent = by_id.get(entity_id)
        if not parent:
            continue
        linked = []
        for aid in spec.get("covered_assets") or []:
            asset = by_id.get(aid)
            if asset and asset.get("layer") == 3:
                linked.append(_asset_payload(asset))
        if linked:
            out[entity_id] = linked
    return out


def _quad_fractions(linked: list[dict]) -> dict[str, float]:
    counts = Counter(a["quad"] for a in linked)
    n = len(linked)
    return {q: round(counts.get(q, 0) / n, 3) for q in QUAD_ORDER}


def compute_thesis_charts(pts: list[dict], graph: dict | None = None) -> dict:
    """Return chart-ready structures keyed by chart id."""
    graph = graph or {}

    # --- mos_regression ---
    reg_pts = []
    for p in pts:
        reg_pts.append({
            "id": p["id"],
            "name": p["name"],
            "x": p["mos"],
            "y": round(_meas(p), 3),
            "quad": p["quad"],
            "layer": p["layer"],
        })
    xs = [p["x"] for p in reg_pts]
    ys = [p["y"] for p in reg_pts]
    stats = _linreg(xs, ys)

    # --- mos_by_layer ---
    by_layer: dict[int, list[float]] = defaultdict(list)
    for p in pts:
        by_layer[p["layer"]].append(p["mos"])
    layer_bars = []
    for layer in sorted(by_layer):
        vals = by_layer[layer]
        layer_bars.append({
            "layer": layer,
            "label": LAYER_LABEL.get(layer, f"L{layer}"),
            "mean": round(sum(vals) / len(vals), 1),
            "std": round((sum((v - sum(vals) / len(vals)) ** 2 for v in vals) / len(vals)) ** 0.5, 1)
            if len(vals) > 1 else 0,
            "n": len(vals),
        })

    # --- mos_by_segment ---
    tag_spec = _load_entity_tags()
    tag_map = tag_spec.get("entities", {})
    by_seg: dict[str, list[float]] = defaultdict(list)
    for p in pts:
        seg = _infer_segment(p, tag_map)
        by_seg[seg].append(p["mos"])
    seg_order = ["carrier", "broker_mga", "energy_asset", "data_centre", "parametric", "reinsurer", "other"]
    segment_bars = []
    for seg in seg_order:
        vals = by_seg.get(seg, [])
        if not vals:
            continue
        segment_bars.append({
            "segment": seg,
            "label": SEGMENT_LABEL.get(seg, seg),
            "mean": round(sum(vals) / len(vals), 1),
            "n": len(vals),
        })

    # --- carrier_swarm + quad stack (linked L3 assets via coverage map) ---
    carriers = sorted([p for p in pts if p["layer"] == 1], key=lambda p: p["name"])
    assets = [p for p in pts if p["layer"] == 3]
    coverage = _load_coverage_links()
    by_carrier = _build_by_carrier(pts, coverage)

    swarm_entities = []
    seen = set()
    for entity_id in sorted(by_carrier, key=lambda e: (-len(by_carrier[e]), e)):
        p = next((x for x in pts if x["id"] == entity_id), None)
        if not p or entity_id in seen:
            continue
        seen.add(entity_id)
        swarm_entities.append({"id": p["id"], "name": p["name"], "mos": p["mos"], "n": len(by_carrier[entity_id])})
    default_swarm = swarm_entities[0]["id"] if swarm_entities else (carriers[0]["id"] if carriers else "")

    stack_bars = []
    for ent in swarm_entities[:12]:
        linked = by_carrier.get(ent["id"], [])
        stack_bars.append({
            "id": ent["id"],
            "name": ent["name"],
            "counts": _quad_fractions(linked),
            "n": len(linked),
        })

    carrier_opts = [{"id": c["id"], "name": c["name"], "mos": c["mos"]} for c in carriers]

    # --- tier + quadrant static (for intro sections) ---
    tiers = Counter()
    quads = Counter()
    for p in pts:
        quads[p["quad"]] += 1

    # --- products for rail ---
    products = []
    for n in graph.get("nodes", []):
        if n.get("type") != "product":
            continue
        cid = n.get("citation_id", "")
        products.append({
            "id": n["id"],
            "label": n.get("label", n["id"]),
            "citation_id": cid,
            "url": n.get("url", ""),
            "year": n.get("year"),
            "topics": n.get("topics", []),
        })

    # --- strategy_map (L1 carriers on exposure × preparedness) ---
    l1_carriers = [p for p in pts if p["layer"] == 1]
    strategy_pts = [
        {
            "id": p["id"],
            "name": p["name"],
            "exp": p["exp"],
            "prep": p["prep"],
            "quad": p["quad"],
            "mos": p["mos"],
            "conf": p.get("conf", "low"),
        }
        for p in l1_carriers
    ]

    # --- alpha_targets (whitespace quadrant, ranked by MoS gap) ---
    whitespace = [p for p in pts if p["quad"] == "whitespace"]
    alpha_rows = [
        {
            "id": p["id"],
            "name": p["name"],
            "gap": round(p["mos"], 1),
            "prep": round(p["prep"], 1),
            "exp": round(p["exp"], 1),
            "meas": round(_meas(p) * 100),
        }
        for p in sorted(whitespace, key=lambda x: x["mos"], reverse=True)[:12]
    ]

    # --- compare_pool (L1 carriers for head-to-head) ---
    compare_entities = [
        {
            "id": p["id"],
            "name": p["name"],
            "mos": round(p["mos"], 1),
            "exp": round(p["exp"], 1),
            "prep": round(p["prep"], 1),
            "meas": round(_meas(p) * 100),
            "quad": p["quad"],
        }
        for p in sorted(l1_carriers, key=lambda x: x["name"])
    ]

    return {
        "quadrant_scatter": {"pts": pts, "readonly": True},
        "mos_regression": {"pts": reg_pts, "stats": stats},
        "mos_by_layer": {"bars": layer_bars},
        "mos_by_segment": {"bars": segment_bars},
        "strategy_map": {"pts": strategy_pts},
        "alpha_targets": {"rows": alpha_rows},
        "compare_pool": {"entities": compare_entities},
        "carrier_swarm": {
            "carriers": swarm_entities if swarm_entities else carrier_opts,
            "byCarrier": by_carrier,
            "assets": [_asset_payload(a) for a in assets],
            "default": default_swarm,
        },
        "carrier_quad_stack": {"bars": stack_bars},
        "inforce_rail": {},
        "tiers": dict(tiers),
        "quadrants": dict(quads),
        "products": products,
    }
