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

    # --- carrier_quad_stack (L1 only, top by count=1 each) ---
    carriers = sorted([p for p in pts if p["layer"] == 1], key=lambda p: p["name"])
    quad_stack = []
    for c in carriers[:20]:
        quad_stack.append({
            "id": c["id"],
            "name": c["name"],
            "quad": c["quad"],
            "mos": c["mos"],
        })
    # Group quadrant counts per carrier (each carrier is one entity — show universe quad mix as stacked bars by carrier quadrant assignment)
    stack_bars = []
    for c in carriers[:15]:
        counts = Counter({q: 0 for q in QUAD_ORDER})
        counts[c["quad"]] = 1
        stack_bars.append({"id": c["id"], "name": c["name"], "counts": dict(counts), "n": 1})

    # --- carrier_swarm ---
    assets = [p for p in pts if p["layer"] == 3]
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

    return {
        "quadrant_scatter": {"pts": pts, "readonly": True},
        "mos_regression": {"pts": reg_pts, "stats": stats},
        "mos_by_layer": {"bars": layer_bars},
        "mos_by_segment": {"bars": segment_bars},
        "carrier_swarm": {
            "carriers": carrier_opts,
            "assets": [{"id": a["id"], "name": a["name"], "mos": a["mos"], "quad": a["quad"]} for a in assets],
            "default": carrier_opts[0]["id"] if carrier_opts else "",
        },
        "carrier_quad_stack": {"bars": stack_bars},
        "inforce_rail": {},
        "tiers": dict(tiers),
        "quadrants": dict(quads),
        "products": products,
    }
