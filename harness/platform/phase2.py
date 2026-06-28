#!/usr/bin/env python3
"""Phase 2 — Accumulation graph orchestrator (BUILD_SEQUENCE.md).

Runs graph geography enrichment, industry stress, graph acceptance, index API export.

  python3 harness/platform/phase2.py              # full pipeline
  python3 harness/platform/phase2.py --check-only # exit gates only

Exit: industry stress 9/9 PASS; graph_acceptance --strict; index API graph + propagate export.
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
GRAPH_FIX = os.path.join(DATA, "fixtures", "graph_edges.json")
MEASURED = os.path.join(DATA, "records.measured.json")


def run(cmd: list[str], label: str) -> bool:
    print(f"\n=== {label} ===")
    p = subprocess.run(cmd, cwd=ROOT)
    ok = p.returncode == 0
    if not ok:
        print(f"FAIL: {label}")
    return ok


def enrich_graph_fixture() -> None:
    sys.path.insert(0, os.path.join(HARNESS, "platform"))
    from graph import enrich_graph_geography  # noqa: E402

    enriched = enrich_graph_geography()
    json.dump(enriched, open(GRAPH_FIX, "w"), indent=2, ensure_ascii=False)
    zones = sum(1 for n in enriched.get("nodes", []) if n.get("constraint_zone"))
    print(f"graph_edges.json: {len(enriched.get('nodes', []))} nodes, {zones} with constraint_zone")


def stress_summary() -> tuple[str, int, int]:
    path = os.path.join(DATA, "industry_stress_report.json")
    if not os.path.isfile(path):
        return "FAIL", 0, 9
    report = json.load(open(path, encoding="utf-8"))
    results = report.get("results", [])
    n_pass = sum(1 for r in results if r.get("status") == "PASS")
    rds = next((r for r in results if r["id"] == "RDS-CORRELATED-CURTAILMENT"), None)
    rds_status = rds.get("status", "FAIL") if rds else "FAIL"
    all_pass = n_pass == len(results) and results
    return rds_status, n_pass, len(results)


def write_phase2_report(results: dict) -> None:
    path = os.path.join(DATA, "phase2_report.txt")
    lines = [
        "NFRI PHASE 2 — ACCUMULATION GRAPH",
        "=" * 56,
        f"as_of: {date.today().isoformat()}",
        "",
    ]
    for k, v in results.items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("Playbook: BUILD_SEQUENCE.md Phase 2")
    text = "\n".join(lines)
    open(path, "w", encoding="utf-8").write(text)
    print(text)


def main() -> int:
    check_only = "--check-only" in sys.argv
    results: dict = {}

    if not check_only:
        run(
            [PY, os.path.join(HARNESS, "bootstrap_measured_universe.py"), "--stress-cohort", "--force"],
            "bootstrap measured universe (stress cohort: gate + brokers)",
        )
        run([PY, os.path.join(HARNESS, "measure_product.py"), "--live"], "measure product_fit (disclosed)")
        print("\n=== enrich graph geography ===")
        enrich_graph_fixture()
        run([PY, os.path.join(HARNESS, "industry_stress.py"), MEASURED], "industry stress suite")
        run([PY, os.path.join(HARNESS, "platform", "index_api.py"), "--export"], "index API static export")

    ok_stress = run([PY, os.path.join(HARNESS, "industry_stress.py"), MEASURED], "industry stress (exit gate)")
    rds_status, n_pass, n_total = stress_summary()
    results["RDS-CORRELATED-CURTAILMENT"] = rds_status
    results["industry_stress"] = f"{n_pass}/{n_total} PASS"

    ok_graph = run(
        [PY, os.path.join(HARNESS, "platform", "graph_acceptance.py"), "--strict"],
        "graph acceptance --strict",
    )
    results["graph_acceptance"] = "PASS" if ok_graph else "FAIL"

    api_graph = os.path.join(ROOT, "site", "api", "v1", "graph.json")
    api_prop = os.path.join(ROOT, "site", "api", "v1", "graph_propagate.example.json")
    results["index_api_graph"] = "PASS" if os.path.isfile(api_graph) else "FAIL"
    results["index_api_propagate"] = "PASS" if os.path.isfile(api_prop) else "FAIL"

    if not check_only and not os.path.isfile(api_prop):
        run([PY, os.path.join(HARNESS, "platform", "index_api.py"), "--export"], "index API export (retry)")

    phase2_pass = (
        ok_stress
        and ok_graph
        and results["index_api_graph"] == "PASS"
        and results["index_api_propagate"] == "PASS"
        and rds_status == "PASS"
    )
    results["PHASE_2_EXIT"] = "PASS" if phase2_pass else "FAIL"

    write_phase2_report(results)
    return 0 if phase2_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
