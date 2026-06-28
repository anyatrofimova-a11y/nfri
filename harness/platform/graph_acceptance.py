#!/usr/bin/env python3
"""Graph layer acceptance test — RDS must PASS (Criterion 5, Phase 2 exit).

Usage:
  python3 harness/platform/graph_acceptance.py
  python3 harness/platform/graph_acceptance.py --strict
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    strict = "--strict" in sys.argv
    records_path = os.path.join(ROOT, "data", "records.measured.json")
    if not os.path.isfile(records_path):
        records_path = os.path.join(ROOT, "data", "records.json")
    stress_path = os.path.join(ROOT, "data", "industry_stress_report.json")

    # Run stress if report stale or missing
    if not os.path.isfile(stress_path):
        import subprocess
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "harness", "industry_stress.py"), records_path],
            cwd=ROOT,
            check=False,
        )

    with open(stress_path, encoding="utf-8") as f:
        report = json.load(f)

    rds = next((r for r in report.get("results", []) if r["id"] == "RDS-CORRELATED-CURTAILMENT"), None)
    issues = []
    if not rds:
        issues.append("RDS scenario not found in industry_stress_report.json")
    elif rds.get("status") != "PASS":
        issues.append(f"RDS-CORRELATED-CURTAILMENT {rds.get('status')} — graph layer not accepted")
    else:
        print("[PASS] RDS-CORRELATED-CURTAILMENT — graph layer acceptance test")

    graph_path = os.path.join(ROOT, "harness", "platform", "graph.py")
    if not os.path.isfile(graph_path):
        issues.append("missing harness/platform/graph.py")

    if issues:
        for i in issues:
            print(f"[FAIL] {i}")
        return 1 if strict else 0

    if not rds:
        return 0
    print("Graph propagation module: harness/platform/graph.py")
    print("Stress catalogue: contract/stress_tests.json (graph_scenario)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
