#!/usr/bin/env python3
"""Verify methodology surfaces stay in sync with risk_model.json and each other.

Checks:
  - Sub-factor weights in methodology contracts match risk_model.json
  - λ tier table matches risk_model fusion block
  - methodology_tab TOC sections match methodology_writing.json
  - scatter_methodology quadrants align with argument.json framework cells
  - scatter layers align with methodology_tab layers block

Usage:
  python3 harness/verify_methodology.py            # print report, exit 0 if clean
  python3 harness/verify_methodology.py --strict # exit 1 on any failure
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")

QUAD_ORDER = ("exposed", "earning_it", "whitespace", "sidelined")
LAYER_KEYS = ("1", "2", "3")


def _load(name: str) -> dict:
    path = os.path.join(CT, name)
    if not os.path.exists(path):
        return {}
    return json.load(open(path))


def _weights_from_risk_model(rm: dict) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {"exposure": {}, "preparedness": {}}
    for axis in ("exposure", "preparedness"):
        subs = (rm.get("axis_formulas") or {}).get(axis, {}).get("sub_factors") or {}
        for key, spec in subs.items():
            if key.startswith("_") or "include_layers" in spec:
                continue
            w = spec.get("weight")
            if w is not None:
                out[axis][key] = float(w)
    return out


def _weights_from_chart(contract: dict) -> dict[str, float]:
    """Extract name→weight from a chart kind=weights block."""
    weights: dict[str, float] = {}
    for b in contract.get("blocks", []):
        if b.get("type") == "chart" and b.get("kind") == "weights":
            for bar in b.get("bars", []):
                weights[bar["name"]] = float(bar["weight"])
        if b.get("type") == "section":
            for bb in b.get("blocks", []):
                if bb.get("type") == "chart" and bb.get("kind") == "weights":
                    for bar in bb.get("bars", []):
                        weights[bar["name"]] = float(bar["weight"])
    return weights


def _lambda_from_contract(contract: dict) -> dict[str, float]:
    tiers: dict[str, float] = {}
    tier_map = {
        "measured": "measured", "derived": "derived", "disclosed": "disclosed", "assessed": "assessed",
    }

    def walk(blocks):
        for b in blocks or []:
            if b.get("type") == "table" and "λ" in (b.get("caption") or ""):
                for row in b.get("rows", []):
                    if len(row) < 2:
                        continue
                    label = re.sub(r"<[^>]+>", "", row[0]).lower()
                    for key, name in tier_map.items():
                        if name in label:
                            try:
                                tiers[key] = float(row[1])
                            except ValueError:
                                pass
            if b.get("type") == "section":
                walk(b.get("blocks", []))

    walk(contract.get("blocks", []))
    return tiers


def _section_ids(contract: dict) -> list[str]:
    ids = []
    for b in contract.get("blocks", []):
        if b.get("type") == "section" and b.get("id"):
            ids.append(b["id"])
        if b.get("type") == "toc":
            for it in b.get("items", []):
                if it.get("id"):
                    ids.append(it["id"])
    return list(dict.fromkeys(ids))


def _framework_quads(argument: dict) -> dict[str, str]:
    out = {}
    for b in argument.get("blocks", []):
        if b.get("type") == "framework":
            for cell in b.get("cells", []):
                q = cell.get("quad")
                if q:
                    out[q] = re.sub(r"<[^>]+>", "", cell.get("note", "")).strip()
    return out


def _layer_names_tab(tab: dict) -> dict[str, str]:
    names = {}
    for b in tab.get("blocks", []):
        if b.get("type") == "section" and b.get("id") == "layers":
            for bb in b.get("blocks", []):
                if bb.get("type") == "layers":
                    for i, item in enumerate(bb.get("items", []), 1):
                        tag = item.get("tag", "").replace("L", "")
                        if tag.isdigit():
                            names[tag] = item.get("name", "")
    return names


def verify() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    rm = _load("risk_model.json")
    tab = _load("methodology_tab.json")
    index_m = _load("methodology.json")
    scatter = _load("scatter_methodology.json")
    argument = _load("argument.json")
    writing = _load("methodology_writing.json")

    rm_w = _weights_from_risk_model(rm)
    chart_w = _weights_from_chart(tab)
    rm_flat = {**rm_w["exposure"], **rm_w["preparedness"]}

    label_to_key = {
        "Book concentration": "book_concentration",
        "Non-firm intensity": "non_firm_intensity",
        "Aggregation / corr.": "aggregation_correlation",
        "Trigger gap": "trigger_gap",
        "Tenor mismatch": "tenor_mismatch",
        "Data & monitoring": "data_monitoring",
        "Product fit": "product_fit",
        "Underwriting exp.": "underwriting_expertise",
        "Capital & reins.": "capital_reinsurance",
        "Pricing & modelling": "pricing_modelling",
    }
    for label, w in chart_w.items():
        key = label_to_key.get(label, label)
        expected = rm_flat.get(key)
        if expected is None:
            warnings.append(f"weights chart: unknown bar '{label}'")
        elif abs(w - expected) > 0.001:
            errors.append(f"weights mismatch {label}: chart={w} risk_model={expected}")

    exp_sum = sum(rm_w["exposure"].values())
    prep_sum = sum(rm_w["preparedness"].values())
    for axis, s in (("exposure", exp_sum), ("preparedness", prep_sum)):
        if abs(s - 1.0) > 0.001:
            errors.append(f"risk_model {axis} weights sum to {s:.3f}, not 1.00")

    rm_lam = {
        k: v["value"]
        for k, v in (rm.get("fusion") or {}).get("lambda_by_tier", {}).items()
        if k != "unknown"
    }
    tab_lam = _lambda_from_contract(tab)
    for tier, val in rm_lam.items():
        got = tab_lam.get(tier)
        if got is None:
            warnings.append(f"λ tier '{tier}' not found in methodology_tab table")
        elif abs(got - val) > 0.001:
            errors.append(f"λ mismatch {tier}: tab={got} risk_model={val}")

    if writing:
        spec_ids = {s["id"] for s in writing.get("sections", []) if "methodology_tab" in s.get("surfaces", [])}
        spec_ids -= {"scatter_quadrants", "scatter_layers"}
        tab_ids = set(_section_ids(tab))
        missing = spec_ids - tab_ids
        extra = tab_ids - spec_ids
        if missing:
            errors.append(f"methodology_tab missing sections: {', '.join(sorted(missing))}")
        if extra:
            warnings.append(f"methodology_tab extra sections (ok): {', '.join(sorted(extra))}")

    fw = _framework_quads(argument)
    for q in QUAD_ORDER:
        if q not in scatter.get("quadrant", {}):
            errors.append(f"scatter_methodology missing quadrant '{q}'")
        elif q not in fw:
            warnings.append(f"argument.framework missing quadrant '{q}'")

    tab_layers = _layer_names_tab(tab)
    scatter_layers = scatter.get("layer", {})
    for lk in LAYER_KEYS:
        if lk not in scatter_layers:
            errors.append(f"scatter_methodology missing layer '{lk}'")
        elif lk in tab_layers and scatter_layers[lk].get("title") != tab_layers[lk]:
            warnings.append(
                f"layer {lk} title drift: scatter='{scatter_layers[lk].get('title')}' "
                f"tab='{tab_layers[lk]}'"
            )

    if not index_m.get("blocks"):
        warnings.append("contract/methodology.json empty or missing blocks")

    return errors, warnings


def main() -> int:
    strict = "--strict" in sys.argv
    errors, warnings = verify()
    print("METHODOLOGY SYNC — risk_model ↔ contracts ↔ scatter")
    print("=" * 60)
    if not errors and not warnings:
        print("  OK  all sync checks pass")
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  FAIL  {e}")
    print("=" * 60)
    print(f"errors: {len(errors)} · warnings: {len(warnings)}")
    if errors:
        print("fix: align contract/methodology_tab.json + scatter_methodology.json with risk_model.json")
    if strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
