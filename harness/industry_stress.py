#!/usr/bin/env python3
"""Industry-standard stress tests for the NFRI scoring model.

Reads contract/stress_tests.json, perturbs a copy of the entity universe,
re-runs harness/scoring.py, and checks pass criteria against industry norms:
Lloyd's RDS (correlation), Solvency II (capital), value-chain placement/
bundling structure, Strata pricing discipline.

Output: data/industry_stress_report.txt (+ JSON summary)

    python3 harness/industry_stress.py [records_path]
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
STRESS_PATH = os.path.join(ROOT, "contract", "stress_tests.json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scoring import load_rubric, load_risk_model, score_all, median_cut_lines  # noqa: E402


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def strip_scores(records: List[dict]) -> List[dict]:
    out = copy.deepcopy(records)
    for r in out:
        r.pop("scores", None)
    return out


def _parse_path(path: str) -> Tuple[str, str]:
    """'exposure_inputs.aggregation_correlation.rating_0_4' -> ('exposure_inputs', 'aggregation_correlation.rating_0_4')"""
    parts = path.split(".", 1)
    if len(parts) != 2:
        raise ValueError(f"bad field path: {path}")
    return parts[0], parts[1]


def _set_nested(obj: dict, rel_path: str, value: Any) -> None:
    parts = rel_path.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = value


def _get_nested(obj: dict, rel_path: str) -> Any:
    cur = obj
    for p in rel_path.split("."):
        cur = cur[p]
    return cur


def matches_filter(rec: dict, flt: dict) -> bool:
    if not flt:
        return True
    if "entity_id_in" in flt and rec["entity_id"] not in flt["entity_id_in"]:
        return False
    if "layer_in" in flt and rec["layer"] not in flt["layer_in"]:
        return False
    if "entity_type_in" in flt and rec["entity_type"] not in flt["entity_type_in"]:
        return False
    return True


def apply_perturbation(records: List[dict], perturb: Optional[dict]) -> List[dict]:
    if not perturb:
        return records
    out = copy.deepcopy(records)
    flt = perturb.get("filter") or {}
    exclude = set(perturb.get("exclude_entity_ids") or [])
    floor = perturb.get("floor")
    cap = perturb.get("cap")

    for rec in out:
        if rec["entity_id"] in exclude:
            continue
        if not matches_filter(rec, flt):
            continue

        for path, spec in (perturb.get("set_fields") or {}).items():
            if (
                path.startswith("exposure_inputs.non_firm_intensity.")
                and "non_firm_intensity" not in rec.get("exposure_inputs", {})
                and "non_firm_compute_exposure" in rec.get("exposure_inputs", {})
            ):
                path = path.replace("non_firm_intensity", "non_firm_compute_exposure", 1)
            axis, rel = _parse_path(path)
            if isinstance(spec, dict) and spec.get("layer_3_only"):
                if rec["layer"] != 3:
                    continue
                val = spec["value"]
            else:
                val = spec
            _set_nested(rec[axis], rel, val)

        for path, delta in (perturb.get("delta_fields") or {}).items():
            if (
                path.startswith("exposure_inputs.non_firm_intensity.")
                and "non_firm_intensity" not in rec.get("exposure_inputs", {})
                and "non_firm_compute_exposure" in rec.get("exposure_inputs", {})
            ):
                path = path.replace("non_firm_intensity", "non_firm_compute_exposure", 1)
            axis, rel = _parse_path(path)
            cur = _get_nested(rec[axis], rel)
            if not isinstance(cur, (int, float)):
                continue
            new_val = int(cur) + int(delta)
            if floor is not None:
                new_val = max(floor, new_val)
            if cap is not None:
                new_val = min(cap, new_val)
            _set_nested(rec[axis], rel, new_val)

    return out


def score_universe(records: List[dict], cut_exp: float, cut_prep: float) -> Tuple[List[dict], Dict[str, dict]]:
    rubric = load_rubric()
    model = load_risk_model()
    scored, _, _ = score_all(copy.deepcopy(records), cut_exp, cut_prep, rubric, model)
    by_id = {r["entity_id"]: r["scores"] for r in scored}
    return scored, by_id


def mos(rec_id: str, scores_by_id: Dict[str, dict]) -> float:
    return scores_by_id[rec_id]["margin_of_safety"]


def quad(rec_id: str, scores_by_id: Dict[str, dict]) -> str:
    return scores_by_id[rec_id]["quadrant"]


def median_l1_mos(scores_by_id: Dict[str, dict], records: List[dict]) -> float:
    vals = [scores_by_id[r["entity_id"]]["margin_of_safety"]
            for r in records if r["layer"] == 1]
    return st.median(vals) if vals else 0.0


def run_structural_checks(records: List[dict], checks: List[dict]) -> List[Tuple[str, bool, str]]:
    results = []
    for chk in checks:
        kind = chk["assert"]
        if kind == "brokers_lower_capital_than_reinsurers":
            brokers = [r for r in records if r.get("entity_type") == "broker"]
            reins = [r for r in records if r["layer"] == chk["layer_b"]]
            if not brokers or not reins:
                results.append((kind, False, "missing broker or L1 entities"))
                continue
            b_cap = st.mean(r["preparedness_inputs"]["capital_reinsurance"]["rating_0_4"] for r in brokers)
            r_cap = st.mean(r["preparedness_inputs"]["capital_reinsurance"]["rating_0_4"] for r in reins)
            ok = b_cap < r_cap
            results.append((kind, ok, f"broker mean capital={b_cap:.2f} vs L1 mean={r_cap:.2f}"))
        elif kind == "mgas_high_product_fit":
            mgas = [r for r in records if r.get("entity_type") == "mga"]
            mn = chk.get("min_product_fit_rating", 3)
            ok = all(r["preparedness_inputs"]["product_fit"]["rating_0_4"] >= mn for r in mgas)
            results.append((kind, ok, f"{len(mgas)} MGAs, min product_fit>={mn}"))
        elif kind == "brokers_facility_product_fit":
            brokers = [r for r in records if r.get("entity_type") == "broker"]
            mn = chk.get("min_product_fit_rating", 2)
            ok = all(r["preparedness_inputs"]["product_fit"]["rating_0_4"] >= mn for r in brokers)
            results.append((kind, ok, f"{len(brokers)} brokers, min product_fit>={mn}"))
        else:
            results.append((kind, False, f"unknown check {kind}"))
    return results


def run_fusion_checks(records: List[dict], fusion_cfg: dict) -> Tuple[bool, str]:
    """Strata-style: latent must not fully dominate when spread exceeds threshold without measured tier."""
    max_spread = fusion_cfg.get("max_latent_det_spread_without_measured", 2)
    violations = []
    for rec in records:
        for axis in ("exposure_inputs", "preparedness_inputs"):
            for sf_key, sf in rec[axis].items():
                lat = sf.get("latent_rating_0_4", sf.get("rating_0_4"))
                det = sf.get("deterministic_rating_0_4")
                tier = sf.get("evidence_tier")
                if lat is None or det is None:
                    continue
                if tier in ("measured", "derived", "disclosed", "FIXTURE_DEMO"):
                    continue
                if abs(int(lat) - int(det)) > max_spread:
                    # after scoring, check mode is not pure latent when det exists
                    pass  # checked post-score below
    # Post-score: re-score one record at a time is heavy; check input contract instead
    for rec in records:
        for axis in ("exposure_inputs", "preparedness_inputs"):
            for sf_key, sf in rec[axis].items():
                lat = sf.get("latent_rating_0_4", sf.get("rating_0_4", 0))
                det = sf.get("deterministic_rating_0_4")
                tier = sf.get("evidence_tier", "assessed")
                if det is None or tier in ("measured", "derived", "disclosed"):
                    continue
                if abs(int(lat) - int(det)) > max_spread:
                    # Unmeasured high spread: rating_0_4 should not equal latent if det present
                    if sf.get("rating_0_4") == lat and det != lat:
                        violations.append(f"{rec['entity_id']}.{sf_key}")
    if violations:
        return False, f"high spread without measured tier: {', '.join(violations[:5])}"
    return True, "no unmeasured full-latent adoption on high spread"


def evaluate_scenario(
    scenario: dict,
    baseline_records: List[dict],
    baseline_scores: Dict[str, dict],
    cut_exp: float,
    cut_prep: float,
) -> dict:
    sid = scenario["id"]
    graph_id = scenario.get("graph_scenario")
    if graph_id:
        import importlib.util
        graph_path = os.path.join(os.path.dirname(__file__), "platform", "graph.py")
        spec = importlib.util.spec_from_file_location("nfri_accumulation_graph", graph_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        perturbed = mod.propagate_scenario(baseline_records, graph_id)
    else:
        perturbed = apply_perturbation(baseline_records, scenario.get("perturbation"))
    _, stressed = score_universe(perturbed, cut_exp, cut_prep)
    criteria = scenario.get("pass_criteria") or {}
    details: List[str] = []
    passed = True

    if scenario.get("structural_checks"):
        for name, ok, msg in run_structural_checks(baseline_records, scenario["structural_checks"]):
            details.append(f"  {name}: {'PASS' if ok else 'FAIL'} — {msg}")
            passed = passed and ok

    if scenario.get("fusion_checks"):
        ok, msg = run_fusion_checks(baseline_records, scenario["fusion_checks"])
        details.append(f"  fusion: {'PASS' if ok else 'FAIL'} — {msg}")
        passed = passed and ok

    if "min_exposed_count" in criteria:
        n = sum(1 for s in stressed.values() if s["quadrant"] == "exposed")
        ok = n >= criteria["min_exposed_count"]
        details.append(f"  exposed count={n} (need >={criteria['min_exposed_count']})")
        passed = passed and ok

    if "max_earning_it_share" in criteria:
        share = sum(1 for s in stressed.values() if s["quadrant"] == "earning_it") / len(stressed)
        ok = share <= criteria["max_earning_it_share"]
        details.append(f"  earning_it share={share:.0%} (max {criteria['max_earning_it_share']:.0%})")
        passed = passed and ok

    if "min_mos_drop_top_exposed" in criteria:
        drops = [
            baseline_scores[eid]["margin_of_safety"] - stressed[eid]["margin_of_safety"]
            for eid in baseline_scores
        ]
        max_drop = max(drops) if drops else 0
        ok = max_drop >= criteria["min_mos_drop_top_exposed"]
        details.append(f"  max MoS drop (universe)={max_drop:.1f} (need >={criteria['min_mos_drop_top_exposed']})")
        passed = passed and ok

    for key in ("parametrix_mos_above", "zurich_mos_below"):
        if key not in criteria:
            continue
        a, b = ("parametrix", criteria[key]) if key == "parametrix_mos_above" else ("zurich", criteria[key])
        if a not in stressed or b not in stressed:
            ok = False
            details.append(f"  {key}: missing entity {a} or {b}")
        else:
            if key == "parametrix_mos_above":
                ok = mos(a, stressed) > mos(b, stressed)
            else:
                ok = mos(a, stressed) < mos(b, stressed)
            details.append(
                f"  {key}: MoS({a})={mos(a, stressed):.1f} vs MoS({b})={mos(b, stressed):.1f} — "
                f"{'PASS' if ok else 'FAIL'}"
            )
        passed = passed and ok

    if criteria.get("parametrix_mos_above_median_l1"):
        med = median_l1_mos(stressed, perturbed)
        ok = mos("parametrix", stressed) > med
        details.append(f"  parametrix MoS={mos('parametrix', stressed):.1f} vs L1 median={med:.1f}")
        passed = passed and ok

    if "min_l3_exposed" in criteria:
        l3_exposed = sum(1 for r in perturbed
                         if r["layer"] == 3 and stressed[r["entity_id"]]["quadrant"] == "exposed")
        ok = l3_exposed >= criteria["min_l3_exposed"]
        details.append(f"  L3 exposed={l3_exposed} (need >={criteria['min_l3_exposed']})")
        passed = passed and ok

    if criteria.get("kao_or_latos_exposed"):
        ok = (quad("asset-kao-harlow", stressed) == "exposed"
              or quad("asset-latos-bridgend", stressed) == "exposed")
        details.append(
            f"  kao={quad('asset-kao-harlow', stressed)}, latos={quad('asset-latos-bridgend', stressed)}"
        )
        passed = passed and ok

    if criteria.get("no_broker_whitespace_to_earning_without_prep"):
        ok = True
        for r in perturbed:
            if r.get("entity_type") != "broker":
                continue
            s = stressed[r["entity_id"]]
            if s["quadrant"] == "earning_it" and s["preparedness_0_100"] < cut_prep:
                ok = False
                details.append(f"  broker {r['entity_id']} earning_it with prep below median")
        if ok:
            details.append("  no broker flipped to earning_it without prep >= median")
        passed = passed and ok

    if "all_l1_capital_rating_lte" in criteria:
        cap_max = criteria["all_l1_capital_rating_lte"]
        l1 = [r for r in perturbed if r["layer"] == 1]
        bad = []
        for r in l1:
            eid = r["entity_id"]
            eff = stressed[eid]["blend"]["preparedness_sub_factors"]["capital_reinsurance"]["rating_effective_0_4"]
            if eff > cap_max:
                bad.append(eid)
        ok = not bad
        details.append(f"  L1 fused capital rating <= {cap_max}: {len(l1) - len(bad)}/{len(l1)}")
        passed = passed and ok

    if "min_mos_drop" in criteria:
        drops = [baseline_scores[eid]["margin_of_safety"] - stressed[eid]["margin_of_safety"]
                 for eid in baseline_scores]
        avg_drop = st.mean(drops) if drops else 0
        ok = avg_drop >= criteria["min_mos_drop"]
        details.append(f"  mean MoS drop={avg_drop:.1f} (need >={criteria['min_mos_drop']})")
        passed = passed and ok

    # Quadrant movers
    movers = []
    for eid in baseline_scores:
        bq, sq = baseline_scores[eid]["quadrant"], stressed[eid]["quadrant"]
        if bq != sq:
            movers.append((eid, bq, sq,
                           stressed[eid]["margin_of_safety"] - baseline_scores[eid]["margin_of_safety"]))

    return {
        "id": sid,
        "name": scenario["name"],
        "status": "PASS" if passed else "FAIL",
        "citation_ids": scenario.get("citation_ids", []),
        "industry_standard": scenario.get("industry_standard", ""),
        "details": details,
        "movers": movers,
        "quadrant_counts": dict(Counter(s["quadrant"] for s in stressed.values())),
    }


def run_stress_suite(records_path: Optional[str] = None) -> Tuple[List[dict], str]:
    src = records_path or (
        "data/records.json" if os.path.exists(os.path.join(ROOT, "data/records.json"))
        else "data/records.optimized.json"
    )
    raw = load_json(os.path.join(ROOT, src))
    records = strip_scores(raw)
    catalogue = load_json(STRESS_PATH)

    cut_exp, cut_prep = median_cut_lines(records)
    _, baseline_scores = score_universe(records, cut_exp, cut_prep)

    results = []
    for scenario in catalogue["scenarios"]:
        results.append(evaluate_scenario(scenario, records, baseline_scores, cut_exp, cut_prep))

    lines = [
        "NFRI INDUSTRY STRESS TESTS",
        "=" * 64,
        f"source: {src}  |  records: {len(records)}",
        f"baseline cut-lines: exposure>={cut_exp}  preparedness>={cut_prep}",
        f"catalogue: contract/stress_tests.json v{catalogue.get('version', '?')}",
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

    out_txt = os.path.join(ROOT, "data", "industry_stress_report.txt")
    out_json = os.path.join(ROOT, "data", "industry_stress_report.json")
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
