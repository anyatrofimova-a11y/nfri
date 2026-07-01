#!/usr/bin/env python3
"""CMUI model-spec integrity verifier.

Checks contract/COMPUTE_MODEL_SPEC.md, compute_risk_model.json, compute_rubric.json,
and compute_citations.json agree — citation resolution, weight sums, rubric alignment.

Output: data/compute_model_verification.txt (+ nonzero exit on FAIL)

    python3 harness/verify_compute_model_spec.py
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p: str) -> dict:
    return json.load(open(os.path.join(ROOT, p)))


results: list[tuple[str, str, str]] = []


def rec(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))


def walk_citation_ids(obj) -> set[str]:
    out: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "citation_ids" and isinstance(v, list):
                out |= {x for x in v if isinstance(x, str)}
            elif k == "citation_id" and isinstance(v, str):
                out.add(v)
            else:
                out |= walk_citation_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= walk_citation_ids(v)
    return out


def main() -> int:
    cmui_cites = load("contract/compute_citations.json")["references"]
    nfri_cites = load("contract/citations.json")["references"]
    all_cites = {**nfri_cites, **cmui_cites}

    risk = load("contract/compute_risk_model.json")
    rubric = load("contract/compute_rubric.json")
    stress = load("contract/compute_stress_tests.json")
    spec = open(os.path.join(ROOT, "contract/COMPUTE_MODEL_SPEC.md")).read()

    ref_risk = walk_citation_ids(risk)
    ref_rubric = walk_citation_ids(rubric)
    ref_stress = walk_citation_ids(stress)
    scenario_ids = {s["id"] for s in stress["scenarios"]}
    ref_spec = set(re.findall(r"`([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)`", spec)) - scenario_ids
    referenced = ref_risk | ref_rubric | ref_stress | ref_spec
    defined = set(all_cites)

    missing = sorted(referenced - defined)
    rec(
        "V1 citation integrity",
        "PASS" if not missing else "FAIL",
        f"{len(referenced)} referenced, {len(defined)} defined; "
        + ("all resolve" if not missing else f"{len(missing)} UNRESOLVED: {', '.join(missing[:12])}"),
    )

    for axis in ("exposure", "preparedness"):
        model_sfs = set(risk["axis_formulas"][axis]["sub_factors"])
        rubric_sfs = set(rubric[axis])
        if model_sfs != rubric_sfs:
            rec(f"V2 rubric keys ({axis})", "FAIL", f"model={sorted(model_sfs)} rubric={sorted(rubric_sfs)}")
        else:
            rec(f"V2 rubric keys ({axis})", "PASS", f"{len(model_sfs)} sub-factors aligned")

    for axis in ("exposure", "preparedness"):
        weights = [sf["weight"] for sf in risk["axis_formulas"][axis]["sub_factors"].values()]
        total = round(sum(weights), 4)
        ok = abs(total - 1.0) < 0.001
        rec(f"V3 weight sum ({axis})", "PASS" if ok else "FAIL", f"sum={total}")

    rub_w = {
        axis: round(sum(rubric[axis][k]["weight"] for k in rubric[axis]), 4)
        for axis in ("exposure", "preparedness")
    }
    for axis, total in rub_w.items():
        ok = abs(total - 1.0) < 0.001
        rec(f"V4 rubric weight sum ({axis})", "PASS" if ok else "FAIL", f"sum={total}")

    thresh_keys = set(risk.get("deterministic_mappings", {}))
    needed = {
        "capacity_at_risk_thresholds",
        "tightness_sensitivity_thresholds",
        "price_basis_gap_thresholds",
        "price_volatility_exposure_thresholds",
        "shock_calendar_exposure_thresholds",
        "depreciation_tenor_mismatch_thresholds",
        "grid_compute_coupling_index",
        "index_hedge_coverage_thresholds",
        "data_monitoring_tier_map",
        "pricing_modelling_tier_map",
    }
    missing_thresh = sorted(needed - thresh_keys)
    rec(
        "V5 deterministic mappings",
        "PASS" if not missing_thresh else "FAIL",
        "complete" if not missing_thresh else f"missing: {missing_thresh}",
    )

    lines = ["CMUI MODEL VERIFICATION", "=" * 64, ""]
    n_fail = 0
    for name, status, detail in results:
        lines.append(f"[{status}] {name}")
        lines.append(f"  {detail}")
        if status == "FAIL":
            n_fail += 1
    lines.append("")
    lines.append("=" * 64)
    lines.append(f"SUMMARY: {len(results) - n_fail} pass, {n_fail} fail / {len(results)} checks")

    report = "\n".join(lines)
    out = os.path.join(ROOT, "data", "compute_model_verification.txt")
    open(out, "w").write(report)
    print(report)
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
