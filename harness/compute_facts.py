"""Live facts for contract/compute_manifesto.json ({{fact:KEY}} tokens)."""
from __future__ import annotations

import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pct(n: int, total: int) -> str:
    return f"{round(n / total * 100)}%" if total else "0%"


def load_snapshot(root: str | None = None) -> dict:
    root = root or ROOT
    path = os.path.join(root, "data", "compute_indices", "snapshot.json")
    if not os.path.isfile(path):
        return {}
    return json.load(open(path)).get("summary") or {}


def compute_cmui_facts(records: list[dict], snapshot: dict | None = None) -> dict:
    """Return {KEY: value} for compute manifesto {{fact:KEY}} tokens."""
    snapshot = snapshot if snapshot is not None else load_snapshot()
    scored = [r for r in records if r.get("scores")]
    total = len(scored)
    if not total:
        return {
            "total": 0,
            "spot_median": snapshot.get("spot_median_usd", "—"),
            "n_quotes": snapshot.get("n_quotes", 0),
            "primary_source": snapshot.get("primary_source", "—"),
        }

    quad = Counter((r["scores"] or {}).get("quadrant") for r in scored)
    layers = Counter(r.get("layer") for r in scored)

    cut_exp, cut_prep = 50.0, 50.0
    cal = (scored[0]["scores"] or {}).get("calibration", "")
    m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", cal)
    if m:
        cut_exp, cut_prep = float(m.group(1)), float(m.group(2))

    mos_vals = [r["scores"]["margin_of_safety"] for r in scored]
    by_mos = sorted(scored, key=lambda r: r["scores"]["margin_of_safety"])

    return {
        "total": total,
        "l1": layers.get(1, 0),
        "l2": layers.get(2, 0),
        "l3": layers.get(3, 0),
        "exposed_count": quad.get("exposed", 0),
        "whitespace_count": quad.get("whitespace", 0),
        "earning_count": quad.get("earning_it", 0),
        "sidelined_count": quad.get("sidelined", 0),
        "exposed_pct": _pct(quad.get("exposed", 0), total),
        "whitespace_pct": _pct(quad.get("whitespace", 0), total),
        "cut_exp": cut_exp,
        "cut_prep": cut_prep,
        "mos_min": min(mos_vals) if mos_vals else 0,
        "mos_max": max(mos_vals) if mos_vals else 0,
        "mos_median": round(sorted(mos_vals)[len(mos_vals) // 2], 1) if mos_vals else 0,
        "top_mos_name": by_mos[-1]["name"] if by_mos else "—",
        "low_mos_name": by_mos[0]["name"] if by_mos else "—",
        "spot_median": snapshot.get("spot_median_usd", "—"),
        "spot_min": snapshot.get("spot_min_usd", "—"),
        "spot_max": snapshot.get("spot_max_usd", "—"),
        "n_quotes": snapshot.get("n_quotes", 0),
        "tightness_proxy": snapshot.get("tightness_proxy", "—"),
        "cv_cross": snapshot.get("cv_cross_section", "—"),
        "primary_source": snapshot.get("primary_source", "—"),
        "chip_model": snapshot.get("chip_model", "H100"),
    }
