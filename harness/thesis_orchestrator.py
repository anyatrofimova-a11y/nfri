#!/usr/bin/env python3
"""Thesis track orchestrator — status, apply enrichment, regenerate reports.

  python3 harness/thesis_orchestrator.py status
  python3 harness/thesis_orchestrator.py apply all
  python3 harness/thesis_orchestrator.py apply T1
  python3 harness/thesis_orchestrator.py report
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "thesis", "manifest.json")
PY = sys.executable


def _run(cmd: str | list[str]) -> int:
    if isinstance(cmd, str):
        print(f"→ {cmd}")
        return subprocess.run(cmd, shell=True, cwd=ROOT).returncode
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_status() -> int:
    m = json.load(open(MANIFEST))
    print("THESIS TRACKS")
    print("=" * 60)
    for tid, spec in m.get("tracks", {}).items():
        st = spec.get("status", "pending")
        outs = spec.get("outputs", [])
        ok = all(os.path.isfile(os.path.join(ROOT, p)) for p in outs)
        batches = spec.get("enrichment_batches", [])
        batch_ok = sum(1 for b in batches if os.path.isfile(os.path.join(ROOT, b)))
        print(f"  [{st:10}] {tid}")
        print(f"             reports: {'✓' if ok else '—'}  batches: {batch_ok}/{len(batches)}")
        print(f"             {spec.get('question', '')[:72]}")
    summary = os.path.join(ROOT, "data", "thesis", "THESIS_SUMMARY.md")
    if os.path.isfile(summary):
        print("=" * 60)
        print(f"  summary: data/thesis/THESIS_SUMMARY.md")
    return 0


def cmd_apply(track: str) -> int:
    steps = [
        f"{PY} harness/apply_thesis_batches.py --apply",
        f"{PY} harness/integrate_entities.py",
        f"{PY} harness/measure_book.py --live",
        f"{PY} harness/measure_trigger.py --live",
        f"{PY} harness/score_and_validate.py",
    ]
    for step in steps:
        if _run(step):
            return 1
    if track in ("all", "T5", "T4"):
        _run(f"{PY} harness/build_entity_profiles.py")
    flag = "" if track == "all" else f"--{track.lower()}"
    if _run(f"{PY} harness/thesis_research.py {flag}".strip()):
        return 1
    return _run(f"{PY} harness/build_frontend.py")


def cmd_report() -> int:
    return _run(f"{PY} harness/thesis_research.py")


def main() -> int:
    ap = argparse.ArgumentParser(description="Thesis research orchestrator")
    ap.add_argument("command", choices=["status", "apply", "report"])
    ap.add_argument("track", nargs="?", default="all", help="T1–T5 or all (apply only)")
    args = ap.parse_args()
    if args.command == "status":
        return cmd_status()
    if args.command == "report":
        return cmd_report()
    if args.command == "apply":
        t = args.track.upper()
        if t not in ("ALL", "T1", "T2", "T3", "T4", "T5"):
            print(f"Unknown track: {args.track}", file=sys.stderr)
            return 1
        return cmd_apply("all" if t == "ALL" else t)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
