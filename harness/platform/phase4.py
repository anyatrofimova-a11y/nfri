#!/usr/bin/env python3
"""Phase 4 — Active bundling + CSaaS embed orchestrator (BUILD_SEQUENCE.md).

Runs telemetry ingest, embed API export, active bundle demo, and exit gates.

  python3 harness/platform/phase4.py              # full pipeline
  python3 harness/platform/phase4.py --check-only # exit gates only
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
HARNESS = os.path.join(ROOT, "harness")
DATA = os.path.join(ROOT, "data")
PLATFORM = os.path.join(HARNESS, "platform")


def run(cmd: list[str], label: str, optional: bool = False) -> bool:
    print(f"\n=== {label} ===")
    p = subprocess.run(cmd, cwd=ROOT)
    ok = p.returncode == 0
    if not ok and not optional:
        print(f"FAIL: {label}")
    return ok


def write_phase4_report(results: dict) -> None:
    path = os.path.join(DATA, "phase4_report.txt")
    lines = [
        "NFRI PHASE 4 — ACTIVE BUNDLING + CSaaS EMBED",
        "=" * 56,
        f"as_of: {date.today().isoformat()}",
        "",
    ]
    for k, v in results.items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("Playbook: BUILD_SEQUENCE.md · ADR-002 broker handoff")
    text = "\n".join(lines)
    open(path, "w", encoding="utf-8").write(text)
    print(text)


def main() -> int:
    check_only = "--check-only" in sys.argv
    results: dict = {}

    if not check_only:
        run([PY, os.path.join(PLATFORM, "telemetry_ingest.py"), "--ingest"], "telemetry ingest")
        run([PY, os.path.join(PLATFORM, "embed_api.py"), "--export"], "embed API static export")

    ok_demo = run([PY, os.path.join(PLATFORM, "active_bundle.py")], "active bundle demo")
    results["active_bundle_demo"] = "PASS" if ok_demo else "FAIL"

    ok_embed = run([PY, os.path.join(PLATFORM, "embed_api.py"), "--verify"], "embed API verify (ADR-002)")
    results["embed_api_verify"] = "PASS" if ok_embed else "FAIL"

    ok_fix = run([PY, os.path.join(PLATFORM, "fixtures_check.py"), "--strict"], "fixtures_check strict")
    results["fixtures_check"] = "PASS" if ok_fix else "FAIL"

    embed_dir = os.path.join(ROOT, "site", "api", "v1", "embed")
    results["embed_static_export"] = (
        "PASS" if os.path.isfile(os.path.join(embed_dir, "policy-offer.example.json")) else "FAIL"
    )

    alerts_path = os.path.join(DATA, "alerts.json")
    results["telemetry_alerts"] = "PASS" if os.path.isfile(alerts_path) else "FAIL"

    tel_fix = os.path.join(ROOT, "data", "fixtures", "telemetry_sample.json")
    if os.path.isfile(tel_fix):
        import json
        tel = json.load(open(tel_fix, encoding="utf-8"))
        results["telemetry_fixture_demo"] = "FIXTURE_DEMO" if tel.get("FIXTURE_DEMO") else "live-ready"

    phase4_pass = (
        results["active_bundle_demo"] == "PASS"
        and results["embed_api_verify"] == "PASS"
        and results["fixtures_check"] == "PASS"
    )
    results["PHASE_4_EXIT"] = "PASS" if phase4_pass else "FAIL"

    write_phase4_report(results)
    return 0 if phase4_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
