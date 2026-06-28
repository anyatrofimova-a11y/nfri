#!/usr/bin/env python3
"""NFRI pricing pipeline — verifier (P1–P5 gates + stress invariant)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

PRICING_MODEL = ROOT / "contract" / "products" / "pricing" / "pricing_model.json"
CITATIONS = ROOT / "contract" / "citations.json"
LOSS_PAIRS = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.json"
LOSS_SCHEMA = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.schema.json"
STAGE3 = ROOT / "contract/products/pricing/stages/03_expectile_payout/calibration.json"
STAGE2 = ROOT / "contract/products/pricing/stages/02_compound_loss/output.json"
STAGE5 = ROOT / "contract/products/pricing/stages/05_premium_capital/output.json"
RECORDS = ROOT / "data/records.measured.json"
STRESS_PATH = ROOT / "contract/stress_tests.json"
GBP_TO_USD = 1.27


def check_p3() -> tuple[str, str]:
    if not STAGE3.exists():
        return "FAIL", "missing stage 3 calibration.json"
    cal = json.loads(STAGE3.read_text())
    pf = cal.get("payout_function") or {}
    gamma = cal.get("gamma")
    mse = cal.get("basis_risk_mse")
    missing = [k for k in ("payout_function", "basis_risk_mse", "gamma") if cal.get(k) is None]
    if missing:
        return "FAIL", f"missing fields: {', '.join(missing)}"
    if pf.get("type") != "linear_expectile" or float(gamma) <= 0:
        return "FAIL", "payout not elicitable (gamma must be > 0)"
    pairs = cal.get("calibration_pairs", 0)
    if pairs < 1:
        return "FAIL", "no register calibration pairs"
    return "PASS", f"γ={gamma} MSE={mse:,.0f} pairs={pairs}"


def check_p4() -> tuple[str, str]:
    if not STAGE2.exists() or not STAGE5.exists():
        return "FAIL", "missing stage 2 or 5 output"
    s2 = json.loads(STAGE2.read_text())
    s5 = json.loads(STAGE5.read_text())
    el_gbp = sum(float(a.get("E_L_gbp", 0)) for a in s2.get("assets", []))
    pure_usd = float(s5.get("portfolio", {}).get("pure_premium_usd", 0))
    el_usd = el_gbp * GBP_TO_USD
    if el_usd <= 0:
        return "FAIL", "portfolio E[L]=0"
    rel_err = abs(pure_usd - el_usd) / el_usd
    if rel_err > 0.02:
        return "FAIL", f"pure USD {pure_usd:,.0f} vs EL USD {el_usd:,.0f} (err {rel_err:.1%})"
    return "PASS", f"pure premium within 2% of compound EL ({rel_err:.2%} err)"


def check_p5() -> tuple[str, str]:
    if not STAGE2.exists() or not RECORDS.exists():
        return "FAIL", "missing stage 2 or records.measured.json"
    s2 = json.loads(STAGE2.read_text())
    records = json.loads(RECORDS.read_text())
    by_id = {r["entity_id"]: r for r in records}
    priced = [a["entity_id"] for a in s2.get("assets", [])]
    if not priced:
        return "FAIL", "no priced assets"
    missing = [eid for eid in priced if eid not in by_id]
    if missing:
        return "FAIL", f"{len(missing)} entities not in index records"
    no_mos = []
    for eid in priced:
        rec = by_id[eid]
        if rec.get("layer") != 3:
            no_mos.append(eid)
            continue
        scores = rec.get("scores") or {}
        if scores.get("margin_of_safety") is None:
            no_mos.append(eid)
    if no_mos:
        return "FAIL", f"{len(no_mos)} L3 assets missing MoS trace"
    return "PASS", f"{len(priced)} assets traceable to NFRI MoS in records.measured.json"


def check_stress_invariant() -> tuple[str, str]:
    """Parametrix MoS > Chubb under MGA-CAPITAL-PULL (BUILD_SEQUENCE Phase 3)."""
    from industry_stress import (  # noqa: E402
        apply_perturbation,
        evaluate_scenario,
        load_json as stress_load,
        median_cut_lines,
        score_universe,
        strip_scores,
    )

    scenarios = stress_load(str(STRESS_PATH))["scenarios"]
    scenario = next(s for s in scenarios if s["id"] == "MGA-CAPITAL-PULL")
    records_path = RECORDS if RECORDS.exists() else ROOT / "data" / "records.json"
    records = strip_scores(stress_load(str(records_path)))
    cut_exp, cut_prep = median_cut_lines(records)
    _, baseline_scores = score_universe(records, cut_exp, cut_prep)
    result = evaluate_scenario(scenario, records, baseline_scores, cut_exp, cut_prep)
    detail = next((d for d in result["details"] if "parametrix_mos_above" in d), result["status"])
    return ("PASS" if result["status"] == "PASS" else "FAIL"), detail.strip()


def main() -> int:
    checks: list[tuple[str, str, str]] = []
    model = json.loads(PRICING_MODEL.read_text())
    cites = json.loads(CITATIONS.read_text())["references"]

    missing = []
    for stage in model["pipeline"]:
        for cid in stage.get("primary_citations", []):
            if cid not in cites:
                missing.append(f"{stage['id']}:{cid}")
    checks.append((
        "P1 stage citations resolve",
        "PASS" if not missing else "FAIL",
        "all resolve" if not missing else ", ".join(missing[:5]),
    ))

    pairs_ok = LOSS_PAIRS.exists() and LOSS_SCHEMA.exists()
    pair_count = 0
    register_pairs = 0
    if pairs_ok:
        data = json.loads(LOSS_PAIRS.read_text())
        pair_count = len(data.get("pairs", []))
        register_pairs = sum(1 for p in data.get("pairs", []) if p.get("source", "").startswith("register"))
    checks.append((
        "P2 loss_pairs scaffold",
        "PASS" if pairs_ok and pair_count > 0 else ("FAIL" if not pairs_ok else "WARN"),
        f"{pair_count} pairs ({register_pairs} register-measured)" if pairs_ok else "missing files",
    ))

    status, detail = check_p3()
    checks.append(("P3 payout coherence", status, detail))

    status, detail = check_p4()
    checks.append(("P4 premium vs EL", status, detail))

    status, detail = check_p5()
    checks.append(("P5 index traceability", status, detail))

    status, detail = check_stress_invariant()
    checks.append(("P6 MGA-CAPITAL-PULL invariant", status, detail))

    print("NFRI PRICING SPEC VERIFICATION")
    print("=" * 64)
    fails = 0
    warns = 0
    for name, status, detail in checks:
        print(f"  [{status:4}] {name}")
        print(f"         {detail}")
        if status == "FAIL":
            fails += 1
        elif status == "WARN":
            warns += 1
    print("=" * 64)
    print(f"SUMMARY: {sum(1 for _, s, _ in checks if s == 'PASS')} pass, "
          f"{warns} warn, {fails} fail")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
