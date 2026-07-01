#!/usr/bin/env python3
"""Industry stress tests for the CMUI scoring model.

Reads contract/compute_stress_tests.json, perturbs compute_records, re-runs
harness/compute_scoring.py, and checks pass criteria.

Output: data/compute_stress_report.txt (+ JSON summary)

    python3 harness/compute_industry_stress.py [records_path]
"""
from __future__ import annotations

import copy
import json
import os
import statistics as st
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRESS_PATH = os.path.join(ROOT, "contract", "compute_stress_tests.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_scoring import (  # noqa: E402
    load_compute_model,
    load_compute_rubric,
    median_cut_lines,
    score_all,
)
from industry_stress import apply_perturbation  # noqa: E402


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def strip_scores(records: List[dict]) -> List[dict]:
    out = copy.deepcopy(records)
    for r in out:
        r.pop("scores", None)
    return out


def score_universe(
    records: List[dict],
    cut_exp: float,
    cut_prep: float,
) -> Tuple[List[dict], Dict[str, dict]]:
    rubric = load_compute_rubric()
    model = load_compute_model()
    scored, _, _ = score_all(copy.deepcopy(records), cut_exp, cut_prep, rubric, model)
    by_id = {r["entity_id"]: r["scores"] for r in scored}
    return scored, by_id


def mos(entity_id: str, scores_by_id: Dict[str, dict]) -> float:
    return scores_by_id[entity_id]["margin_of_safety"]


def quad(entity_id: str, scores_by_id: Dict[str, dict]) -> str:
    return scores_by_id[entity_id]["quadrant"]


def _mos_drops(
    baseline: Dict[str, dict],
    stressed: Dict[str, dict],
    entity_ids: Optional[List[str]] = None,
) -> List[float]:
    ids = entity_ids or list(baseline)
    return [baseline[eid]["margin_of_safety"] - stressed[eid]["margin_of_safety"] for eid in ids if eid in stressed]


def evaluate_scenario(
    scenario: dict,
    baseline_records: List[dict],
    baseline_scores: Dict[str, dict],
    cut_exp: float,
    cut_prep: float,
) -> dict:
    perturbed = apply_perturbation(baseline_records, scenario.get("perturbation"))
    _, stressed = score_universe(perturbed, cut_exp, cut_prep)
    criteria = scenario.get("pass_criteria") or {}
    details: List[str] = []
    passed = True

    if "min_l3_exposed" in criteria:
        n = sum(
            1 for r in perturbed
            if r["layer"] == 3 and stressed[r["entity_id"]]["quadrant"] == "exposed"
        )
        ok = n >= criteria["min_l3_exposed"]
        details.append(f"  L3 exposed={n} (need >={criteria['min_l3_exposed']})")
        passed = passed and ok

    if "min_median_mos_drop" in criteria:
        drops = _mos_drops(baseline_scores, stressed)
        med = st.median(drops) if drops else 0.0
        ok = med >= criteria["min_median_mos_drop"]
        details.append(f"  median MoS drop={med:.1f} (need >={criteria['min_median_mos_drop']})")
        passed = passed and ok

    if "min_max_mos_drop" in criteria:
        drops = _mos_drops(baseline_scores, stressed)
        mx = max(drops) if drops else 0.0
        ok = mx >= criteria["min_max_mos_drop"]
        details.append(f"  max MoS drop={mx:.1f} (need >={criteria['min_max_mos_drop']})")
        passed = passed and ok

    if "min_mos_drop_entity" in criteria:
        spec = criteria["min_mos_drop_entity"]
        eid = spec["entity_id"]
        drop = baseline_scores[eid]["margin_of_safety"] - stressed[eid]["margin_of_safety"]
        ok = drop >= spec["min_drop"]
        details.append(f"  MoS drop {eid}={drop:.1f} (need >={spec['min_drop']})")
        passed = passed and ok

    if "entity_mos_drop" in criteria:
        spec = criteria["entity_mos_drop"]
        eid = spec["entity_id"]
        drop = baseline_scores[eid]["margin_of_safety"] - stressed[eid]["margin_of_safety"]
        ok = drop >= spec["min_drop"]
        details.append(f"  MoS drop {eid}={drop:.1f} (need >={spec['min_drop']})")
        passed = passed and ok

    if "entity_quadrant" in criteria:
        spec = criteria["entity_quadrant"]
        eid = spec["entity_id"]
        got = quad(eid, stressed)
        ok = got == spec["quadrant"]
        details.append(f"  {eid} quadrant={got} (need {spec['quadrant']})")
        passed = passed and ok

    if "entity_quadrant_in" in criteria:
        spec = criteria["entity_quadrant_in"]
        eid = spec["entity_id"]
        got = quad(eid, stressed)
        allowed = spec["quadrants"]
        ok = got in allowed
        details.append(f"  {eid} quadrant={got} (need one of {allowed})")
        passed = passed and ok

    if "concentration_flag" in criteria:
        spec = criteria["concentration_flag"]
        eid = spec["entity_id"]
        flag = (stressed[eid].get("aggregation") or {}).get("concentration_flag")
        ok = flag == spec["flag"]
        details.append(f"  {eid} concentration_flag={flag!r} (need {spec['flag']!r})")
        passed = passed and ok

    if "parametrix_mos_above" in criteria:
        other = criteria["parametrix_mos_above"]
        if "parametrix" not in stressed or other not in stressed:
            ok = False
            details.append(f"  parametrix_mos_above: missing parametrix or {other}")
        else:
            ok = mos("parametrix", stressed) > mos(other, stressed)
            details.append(
                f"  parametrix MoS={mos('parametrix', stressed):.1f} vs {other}="
                f"{mos(other, stressed):.1f} — {'PASS' if ok else 'FAIL'}"
            )
        passed = passed and ok

    movers = []
    for eid in baseline_scores:
        bq, sq = baseline_scores[eid]["quadrant"], stressed[eid]["quadrant"]
        if bq != sq:
            movers.append((
                eid,
                bq,
                sq,
                stressed[eid]["margin_of_safety"] - baseline_scores[eid]["margin_of_safety"],
            ))

    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "status": "PASS" if passed else "FAIL",
        "citation_ids": scenario.get("citation_ids", []),
        "industry_standard": scenario.get("industry_standard", ""),
        "details": details,
        "movers": movers,
        "quadrant_counts": dict(Counter(s["quadrant"] for s in stressed.values())),
    }


def run_stress_suite(records_path: Optional[str] = None) -> Tuple[List[dict], str]:
    default = os.path.join(ROOT, "data", "compute_records.json")
    scored = os.path.join(ROOT, "data", "compute_records.scored.json")
    src = records_path or (scored if os.path.isfile(scored) else default)
    raw = load_json(src)
    records = strip_scores(raw)
    catalogue = load_json(STRESS_PATH)

    cut_exp, cut_prep = median_cut_lines(records)
    _, baseline_scores = score_universe(records, cut_exp, cut_prep)

    results = [evaluate_scenario(s, records, baseline_scores, cut_exp, cut_prep) for s in catalogue["scenarios"]]

    lines = [
        "CMUI INDUSTRY STRESS TESTS",
        "=" * 64,
        f"source: {src}  |  records: {len(records)}",
        f"baseline cut-lines: exposure>={cut_exp}  preparedness>={cut_prep}",
        f"catalogue: contract/compute_stress_tests.json v{catalogue.get('version', '?')}",
        "",
    ]
    for r in results:
        lines.append(f"[{r['status']}] {r['id']}")
        lines.append(f"  {r['name']}")
        lines.append(f"  standard: {r['industry_standard']}")
        lines.append(f"  citations: {', '.join(r['citation_ids'])}")
        for d in r["details"]:
            lines.append(d)
        if r["movers"]:
            lines.append(f"  quadrant movers ({len(r['movers'])}):")
            for eid, bq, sq, dm in sorted(r["movers"], key=lambda x: x[3])[:8]:
                lines.append(f"    {eid}: {bq} -> {sq}  (MoS Δ{dm:+.1f})")
        lines.append(f"  stressed quadrants: {r['quadrant_counts']}")
        lines.append("")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = len(results) - n_pass
    lines.append("=" * 64)
    lines.append(f"SUMMARY: {n_pass} pass, {n_fail} fail / {len(results)} scenarios")
    if n_fail:
        lines.append("FAILURES: " + ", ".join(r["id"] for r in results if r["status"] == "FAIL"))
    report = "\n".join(lines)

    out_txt = os.path.join(ROOT, "data", "compute_stress_report.txt")
    out_json = os.path.join(ROOT, "data", "compute_stress_report.json")
    with open(out_txt, "w") as f:
        f.write(report)
    with open(out_json, "w") as f:
        json.dump({"cut_lines": {"exposure": cut_exp, "preparedness": cut_prep}, "results": results}, f, indent=2)

    return results, report


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    results, report = run_stress_suite(path)
    print(report)
    return 0 if all(r["status"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
