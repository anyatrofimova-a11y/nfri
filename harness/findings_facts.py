"""Live numeric/text facts for contract/findings.json ({{fact:KEY}} tokens).

Consumed by harness/build_frontend.py and documented in contract/findings_writing.json.
"""
from __future__ import annotations

from collections import Counter


def _name_list(names, limit=4):
    names = list(names)
    if not names:
        return ""
    if len(names) <= limit:
        if len(names) <= 1:
            return names[0]
        return ", ".join(names[:-1]) + " and " + names[-1]
    return ", ".join(names[:limit]) + f" and {len(names) - limit} others"


def _pct(n, total):
    return f"{round(n / total * 100)}%" if total else "0%"


def _layer_label(layer: int) -> str:
    return {1: "Layer 1 (carriers)", 2: "Layer 2 (MGAs/brokers)",
            3: "Layer 3 (assets)", 4: "Layer 4 (tail)"}.get(layer, f"Layer {layer}")


def compute_facts(records, share):
    """Return {KEY: value} for every {{fact:KEY}} token findings may use."""
    scored = [r for r in records if r.get("scores")]
    total = len(scored)
    if not total:
        return {"total": 0}

    quad = Counter((r["scores"] or {}).get("quadrant") for r in scored)
    layers = Counter(r["layer"] for r in scored)
    by_mos = sorted(scored, key=lambda r: r["scores"]["margin_of_safety"])
    mos_vals = [r["scores"]["margin_of_safety"] for r in scored]

    names = {q: [r["name"] for r in scored if r["scores"].get("quadrant") == q]
             for q in ("exposed", "earning_it", "whitespace", "sidelined")}

    def layer_quad(q):
        return Counter(r["layer"] for r in scored if r["scores"].get("quadrant") == q)

    exposed_by_layer = layer_quad("exposed")
    whitespace_by_layer = layer_quad("whitespace")

    # Calibration cut-lines (median exp/prep thresholds)
    cut_exp, cut_prep = 50.0, 50.0
    cal = (scored[0]["scores"] or {}).get("calibration", "")
    if cal:
        import re
        m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", cal)
        if m:
            cut_exp, cut_prep = float(m.group(1)), float(m.group(2))

    # L3 gate cohort (assets only)
    l3 = [r for r in scored if r.get("layer") == 3]
    gate = Counter((r.get("asset_link") or {}).get("gate_status") or "unknown" for r in l3)

    # Heaviest exposed layer
    if exposed_by_layer:
        heaviest_layer = max(exposed_by_layer, key=exposed_by_layer.get)
        heaviest_phrase = f"{_layer_label(heaviest_layer)} ({exposed_by_layer[heaviest_layer]} of {quad.get('exposed', 0)})"
    else:
        heaviest_phrase = "none yet"

    exposed_sorted = sorted(
        (r for r in scored if r["scores"].get("quadrant") == "exposed"),
        key=lambda r: r["scores"]["margin_of_safety"],
    )
    whitespace_sorted = sorted(
        (r for r in scored if r["scores"].get("quadrant") == "whitespace"),
        key=lambda r: r["scores"]["margin_of_safety"],
        reverse=True,
    )

    f = {
        "total": total,
        "exposed_count": quad.get("exposed", 0),
        "earning_count": quad.get("earning_it", 0),
        "whitespace_count": quad.get("whitespace", 0),
        "sidelined_count": quad.get("sidelined", 0),
        "exposed_pct": _pct(quad.get("exposed", 0), total),
        "earning_pct": _pct(quad.get("earning_it", 0), total),
        "whitespace_pct": _pct(quad.get("whitespace", 0), total),
        "sidelined_pct": _pct(quad.get("sidelined", 0), total),
        "exposed_names": _name_list(names["exposed"]) or "none yet",
        "whitespace_names": _name_list(names["whitespace"]) or "none yet",
        "earning_names": _name_list(names["earning_it"]) or "none yet",
        "sidelined_names": _name_list(names["sidelined"]) or "none yet",
        "measured_pct": f"{round(share * 100)}%",
        "n_layers": len([k for k in layers if k]),
        "l1": layers.get(1, 0), "l2": layers.get(2, 0),
        "l3": layers.get(3, 0), "l4": layers.get(4, 0),
        "cut_exp": f"{cut_exp:.1f}",
        "cut_prep": f"{cut_prep:.1f}",
        "median_mos": f"{mos_vals[len(mos_vals) // 2]:.1f}",
        "mos_spread": f"{by_mos[-1]['scores']['margin_of_safety'] - by_mos[0]['scores']['margin_of_safety']:.1f}",
        "exposed_heaviest_layer": heaviest_phrase,
        "exposed_l1": exposed_by_layer.get(1, 0),
        "exposed_l2": exposed_by_layer.get(2, 0),
        "exposed_l3": exposed_by_layer.get(3, 0),
        "exposed_l4": exposed_by_layer.get(4, 0),
        "whitespace_l1": whitespace_by_layer.get(1, 0),
        "whitespace_l2": whitespace_by_layer.get(2, 0),
        "gate_unknown_count": gate.get("unknown", 0),
        "gate_firm_count": gate.get("firm", 0),
        "l3_total": len(l3),
    }

    if by_mos:
        f["low_mos_name"] = by_mos[0]["name"]
        f["low_mos_val"] = by_mos[0]["scores"]["margin_of_safety"]
        f["top_mos_name"] = by_mos[-1]["name"]
        top = by_mos[-1]["scores"]["margin_of_safety"]
        f["top_mos_val"] = f"+{top}" if top >= 0 else str(top)

    if exposed_sorted:
        f["worst_exposed_name"] = exposed_sorted[0]["name"]
        f["worst_exposed_mos"] = exposed_sorted[0]["scores"]["margin_of_safety"]
        f["exposed_l3_names"] = _name_list(
            [r["name"] for r in exposed_sorted if r.get("layer") == 3], limit=5
        ) or "none yet"

    if whitespace_sorted:
        f["top_whitespace_name"] = whitespace_sorted[0]["name"]
        f["top_whitespace_mos"] = whitespace_sorted[0]["scores"]["margin_of_safety"]
        f["whitespace_l1_names"] = _name_list(
            [r["name"] for r in whitespace_sorted if r.get("layer") == 1], limit=4
        ) or "none yet"

    return f
