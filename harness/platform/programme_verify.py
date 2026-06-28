#!/usr/bin/env python3
"""Programme exit verifier — Phases 1–4 + synthetic-data cross-check.

  python3 harness/platform/programme_verify.py
  python3 harness/platform/programme_verify.py --json

Writes data/programme_verify_report.txt
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


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    summary = tail[-1][:120] if tail else ""
    return p.returncode, summary


def synthetic_check() -> tuple[str, list[str]]:
    issues: list[str] = []
    for path in ("data/records.measured.json", "data/records.json"):
        fp = os.path.join(ROOT, path)
        if not os.path.isfile(fp):
            continue
        recs = json.load(open(fp, encoding="utf-8"))
        n = sum(
            1 for r in recs
            for ax in ("exposure_inputs", "preparedness_inputs")
            for sf in r.get(ax, {}).values()
            if sf.get("evidence_tier") == "FIXTURE_DEMO"
        )
        if n:
            issues.append(f"{path}: {n} FIXTURE_DEMO sub-factors")

    audit_dir = os.path.join(DATA, "pricing", "audit")
    if os.path.isdir(audit_dir):
        for fn in os.listdir(audit_dir):
            if not fn.endswith(".json"):
                continue
            doc = json.load(open(os.path.join(audit_dir, fn), encoding="utf-8"))
            src = (doc.get("response") or doc).get("premium_source", "deterministic")
            if src == "llm":
                issues.append(f"pricing audit {fn}: llm premium_source")

    rc, _ = run([PY, os.path.join(HARNESS, "platform", "document_ai.py"), "--verify"])
    if rc:
        issues.append("ADR-003 document_ai --verify FAIL")

    return ("PASS" if not issues else "FAIL"), issues


def main() -> int:
    as_json = "--json" in sys.argv
    results: dict = {"as_of": date.today().isoformat(), "gates": {}}

    phases = [
        ("phase1", [PY, os.path.join(HARNESS, "platform", "phase1.py"), "--check-only"]),
        ("phase2", [PY, os.path.join(HARNESS, "platform", "phase2.py"), "--check-only"]),
        ("phase3", [PY, os.path.join(HARNESS, "platform", "phase3.py"), "--check-only"]),
        ("phase4", [PY, os.path.join(HARNESS, "platform", "phase4.py"), "--check-only"]),
    ]
    for name, cmd in phases:
        rc, summary = run(cmd)
        key = f"{name}_exit"
        results["gates"][key] = "PASS" if rc == 0 else "FAIL"
        results["gates"][f"{name}_detail"] = summary

    rc, _ = run([PY, os.path.join(HARNESS, "publication_gate.py"), "--check-only"])
    # publication_gate --check-only exits 0 even when L5 FAIL; read eval report
    eval_path = os.path.join(DATA, "eval_report.txt")
    l5_status = "FAIL"
    if os.path.isfile(eval_path):
        text = open(eval_path, encoding="utf-8").read()
        import re
        m = re.search(r"BLENDED measured\+disclosed share = (\d+)%", text)
        share = int(m.group(1)) / 100 if m else 0.0
        l5_status = "PASS" if share >= 0.60 or "L5  [PASS]" in text else "FAIL"
        results["gates"]["L5_blended_share"] = f"{share:.0%}"
    results["gates"]["L5_publication_gate"] = l5_status

    syn, issues = synthetic_check()
    results["gates"]["synthetic_data"] = syn
    results["synthetic_issues"] = issues

    all_phase = all(
        results["gates"].get(f"phase{n}_exit") == "PASS" for n in range(1, 5)
    )
    l5_ok = results["gates"].get("L5_publication_gate") == "PASS"
    results["PROGRAMME_EXIT"] = "PASS" if all_phase and syn == "PASS" and l5_ok else "FAIL"

    report_path = os.path.join(DATA, "programme_verify_report.txt")
    lines = ["NFRI PROGRAMME VERIFY", "=" * 56, f"as_of: {results['as_of']}", ""]
    for k, v in results["gates"].items():
        lines.append(f"{k}: {v}")
    if issues:
        lines.append("")
        lines.append("Synthetic issues:")
        for i in issues:
            lines.append(f"  - {i}")
    lines.append("")
    lines.append(f"PROGRAMME_EXIT: {results['PROGRAMME_EXIT']}")
    text = "\n".join(lines)
    open(report_path, "w", encoding="utf-8").write(text)

    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print(text)
        print(f"\nwrote: {report_path}")

    return 0 if results["PROGRAMME_EXIT"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
