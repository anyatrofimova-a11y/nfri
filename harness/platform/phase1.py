#!/usr/bin/env python3
"""Phase 1 — Index credibility orchestrator (BUILD_SEQUENCE.md).

Runs the Felix Phase 1 pipeline: value-chain seats, live measurement, document-AI
validation, L5 in-force sync, scoring, eval, frontend build, exit report.

  python3 harness/platform/phase1.py              # full pipeline (network for registers)
  python3 harness/platform/phase1.py --check-only # exit gates only, no writes except report
  python3 harness/platform/phase1.py --skip-live  # skip measure_all (offline)

Exit: L5 blended ≥60%, build_frontend OK, fixtures_check strict, ADR-003 (no scores from extractions).
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
GATE = 0.60


def run(cmd: list[str], label: str, optional: bool = False) -> bool:
    print(f"\n=== {label} ===")
    p = subprocess.run(cmd, cwd=ROOT)
    ok = p.returncode == 0
    if not ok and not optional:
        print(f"FAIL: {label}")
    return ok


def read_l5() -> tuple[float, str]:
    path = os.path.join(DATA, "eval_report.txt")
    if not os.path.isfile(path):
        return 0.0, "FAIL"
    text = open(path, encoding="utf-8").read()
    import re
    m = re.search(r"BLENDED measured\+disclosed share = (\d+)%", text)
    share = int(m.group(1)) / 100 if m else 0.0
    status = "PASS" if "L5  [PASS]" in text or share >= GATE else "FAIL"
    return share, status


def value_chain_coverage(path: str) -> tuple[int, int]:
    recs = json.load(open(path, encoding="utf-8"))
    n = sum(1 for r in recs if r.get("value_chain_seat"))
    return n, len(recs)


def write_phase1_report(results: dict) -> None:
    path = os.path.join(DATA, "phase1_report.txt")
    lines = [
        "NFRI PHASE 1 — INDEX CREDIBILITY",
        "=" * 56,
        f"as_of: {date.today().isoformat()}",
        "",
    ]
    for k, v in results.items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("Playbook: BUILD_SEQUENCE.md")
    text = "\n".join(lines)
    open(path, "w", encoding="utf-8").write(text)
    print(text)


def main() -> int:
    check_only = "--check-only" in sys.argv
    skip_live = "--skip-live" in sys.argv or check_only
    results: dict = {}

    if not check_only:
        run([PY, os.path.join(HARNESS, "platform", "value_chain.py"), "--backfill"], "value_chain_seat backfill")
        run([PY, os.path.join(HARNESS, "platform", "value_chain.py"), "--backfill", os.path.join(DATA, "records.measured.json")], "value_chain on measured", optional=True)

        if not skip_live:
            if not run([PY, os.path.join(HARNESS, "measure_all.py"), "--live"], "live measurement (measure_all)"):
                return 1
            run([PY, os.path.join(HARNESS, "platform", "provenance_backfill.py")], "provenance tier backfill (honest)", optional=True)
            run([PY, os.path.join(HARNESS, "platform", "document_ai.py"), "--apply"], "document-AI extractions → inputs only")
            run([PY, os.path.join(HARNESS, "platform", "l5_in_force.py"), "--sync"], "L5 in-force register feed")
        else:
            print("\n=== skip live measurement ===")

        if not skip_live:
            subprocess.run([PY, os.path.join(HARNESS, "publication_gate.py")], cwd=ROOT)
        else:
            subprocess.run([PY, os.path.join(HARNESS, "publication_gate.py"), "--check-only"], cwd=ROOT)

        run([PY, os.path.join(HARNESS, "score_and_validate.py")], "score and validate", optional=True)
        run([PY, os.path.join(HARNESS, "build_frontend.py")], "frontend build")
        run([PY, os.path.join(HARNESS, "platform", "index_api.py"), "--export"], "index API static export")

    # Exit gates
    share, l5 = read_l5()
    results["L5_blended_share"] = f"{share:.0%}"
    results["L5_status"] = l5

    vc_n, vc_t = value_chain_coverage(os.path.join(DATA, "records.json"))
    results["value_chain_seat"] = f"{vc_n}/{vc_t}"

    ok_fix = run([PY, os.path.join(HARNESS, "platform", "fixtures_check.py"), "--strict"], "fixtures_check strict")
    results["fixtures_check"] = "PASS" if ok_fix else "FAIL"

    ok_doc = run([PY, os.path.join(HARNESS, "platform", "document_ai.py"), "--verify"], "ADR-003 document_ai verify")
    results["document_ai_verify"] = "PASS" if ok_doc else "FAIL"

    site_index = os.path.join(ROOT, "site", "index.html")
    results["frontend_built"] = "PASS" if os.path.isfile(site_index) else "FAIL"

    api_dir = os.path.join(ROOT, "site", "api", "v1")
    results["index_api_export"] = "PASS" if os.path.isdir(api_dir) else "FAIL"

    in_force = os.path.join(DATA, "l5_in_force.json")
    results["l5_in_force_feed"] = "PASS" if os.path.isfile(in_force) else "FAIL"

    phase1_pass = (
        l5 == "PASS"
        and results["fixtures_check"] == "PASS"
        and results["document_ai_verify"] == "PASS"
        and results["frontend_built"] == "PASS"
    )
    results["PHASE_1_EXIT"] = "PASS" if phase1_pass else "FAIL"

    write_phase1_report(results)
    return 0 if phase1_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
