#!/usr/bin/env python3
"""Phase 3 — Pricing engine orchestrator (BUILD_SEQUENCE.md).

Runs pricing pipeline stages 1–5, verify_pricing_spec, product_readiness, fixture quote + audit.

  python3 harness/platform/phase3.py              # full pipeline + exit gates
  python3 harness/platform/phase3.py --check-only # exit gates only

Exit: verify_pricing_spec pass; product_readiness pass; quote audit trail written.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
HARNESS = os.path.join(ROOT, "harness")
DATA = os.path.join(ROOT, "data")
MEASURED = os.path.join(DATA, "records.measured.json")


def score_measured() -> None:
    """P5 traceability requires MoS on priced L3 assets in records.measured.json."""
    if not os.path.isfile(MEASURED):
        return
    sys.path.insert(0, HARNESS)
    from scoring import score_all  # noqa: E402

    records = json.load(open(MEASURED, encoding="utf-8"))
    for r in records:
        r.pop("scores", None)
    records, cut_exp, cut_prep = score_all(records)
    for r in records:
        if r.get("scores"):
            r["scores"]["calibration"] = f"median exp>={cut_exp} prep>={cut_prep}"
    json.dump(records, open(MEASURED, "w"), indent=2, ensure_ascii=False)


def run(cmd: list[str], label: str) -> bool:
    print(f"\n=== {label} ===")
    p = subprocess.run(cmd, cwd=ROOT)
    ok = p.returncode == 0
    if not ok:
        print(f"FAIL: {label}")
    return ok


def write_phase3_report(results: dict) -> None:
    path = os.path.join(DATA, "phase3_report.txt")
    lines = [
        "NFRI PHASE 3 — PRICING ENGINE",
        "=" * 56,
        f"as_of: {date.today().isoformat()}",
        "",
    ]
    for k, v in results.items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("Playbook: BUILD_SEQUENCE.md § Phase 3")
    text = "\n".join(lines)
    open(path, "w", encoding="utf-8").write(text)
    print(text)


def count_audit_logs() -> int:
    audit_dir = os.path.join(DATA, "pricing", "audit")
    if not os.path.isdir(audit_dir):
        return 0
    return len([f for f in os.listdir(audit_dir) if f.endswith(".json")])


def main() -> int:
    check_only = "--check-only" in sys.argv
    results: dict = {}

    if not check_only:
        if not run([PY, os.path.join(HARNESS, "pricing", "run_pipeline.py")], "pricing pipeline 1–5"):
            results["pipeline"] = "FAIL"
            write_phase3_report(results)
            return 1
        results["pipeline"] = "PASS"

        if not run([PY, os.path.join(HARNESS, "pricing", "quote.py"), "--fixture"], "IC-06 fixture quote + audit"):
            results["quote_fixture"] = "FAIL"
            write_phase3_report(results)
            return 1
        results["quote_fixture"] = "PASS"

    print("\n=== score measured (P5 MoS trace) ===")
    score_measured()
    results["score_measured"] = "PASS"

    ok_verify = run([PY, os.path.join(HARNESS, "pricing", "verify_pricing_spec.py")], "verify_pricing_spec")
    results["verify_pricing_spec"] = "PASS" if ok_verify else "FAIL"

    ok_ready = run([PY, os.path.join(HARNESS, "product_readiness.py")], "product_readiness")
    results["product_readiness"] = "PASS" if ok_ready else "FAIL"

    audit_n = count_audit_logs()
    results["audit_trail_files"] = str(audit_n)
    audit_sample = ""
    audit_dir = os.path.join(DATA, "pricing", "audit")
    if os.path.isdir(audit_dir):
        files = sorted(f for f in os.listdir(audit_dir) if f.endswith(".json"))
        if files:
            audit_sample = os.path.join("data/pricing/audit", files[-1])
    results["audit_sample"] = audit_sample or "none"

    stage5 = os.path.join(ROOT, "contract/products/pricing/stages/05_premium_capital/output.json")
    if os.path.isfile(stage5):
        s5 = json.load(open(stage5, encoding="utf-8"))
        pf = s5.get("portfolio", {})
        results["portfolio_gross_premium_usd"] = str(pf.get("gross_premium_usd", "n/a"))
        results["priced_assets"] = str(pf.get("asset_count", 0))

    phase3_pass = (
        results.get("verify_pricing_spec") == "PASS"
        and results.get("product_readiness") == "PASS"
        and (check_only or results.get("pipeline") == "PASS")
    )
    results["PHASE_3_EXIT"] = "PASS" if phase3_pass else "FAIL"

    write_phase3_report(results)
    return 0 if phase3_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
