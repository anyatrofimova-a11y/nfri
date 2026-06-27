#!/usr/bin/env python3
"""Canonical publish pipeline — score, bank, measure, and rebuild the public index.

Single source of truth for how data moves from contract inputs → records.json → site/.
All orchestrators (profile, measure, data, run_loop) should call into this module
instead of duplicating score_and_validate → optimize → build_frontend chains.

  python3 harness/publish_pipeline.py rebuild
  python3 harness/publish_pipeline.py rebuild --measure   # live register pulls first
  python3 harness/publish_pipeline.py metrics --json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(ROOT, "harness")
DATA = os.path.join(ROOT, "data")
PY = sys.executable


def _run(script: str, args: list[str] | None = None) -> int:
    path = os.path.join(HARNESS, script)
    if not os.path.isfile(path):
        print(f"missing harness/{script}", file=sys.stderr)
        return 127
    cmd = [PY, path, *(args or [])]
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def bank_disclosed() -> int:
    """Bank contract/*_inputs disclosed values into records.json (idempotent)."""
    return _run("integrate_entities.py")


def score_universe() -> int:
    """Re-score records.json → records.scored.json + dataset.csv."""
    return _run("score_and_validate.py")


def measure_live() -> int:
    """Live register/filing pulls → records.measured.json."""
    return _run("measure_all.py", ["--live"])


def build_site() -> int:
    """Build index, methodology, thesis, design-system (merge + rescore at read time)."""
    return _run("build_frontend.py")


def profile_qa() -> int:
    return _run("profile_harness.py", ["--strict"])


def write_gap_report() -> int:
    return _run("profile_gap_report.py", ["--write", os.path.join(DATA, "profile_gap_report.txt")])


def rebuild(*, measure: bool = False, bank: bool = True, qa: bool = False) -> int:
    """Standard publish path after bot batches land or registers refresh."""
    if measure and measure_live():
        return 1
    if bank and bank_disclosed():
        return 1
    if score_universe():
        return 1
    if build_site():
        return 1
    write_gap_report()
    if qa and profile_qa():
        return 1
    return 0


def publish_metrics() -> dict:
    """Metrics aligned with build_frontend (full universe + measured overlay)."""
    sys.path.insert(0, HARNESS)
    from build_frontend import authoritative_share, build_points, load_records

    records, src = load_records()
    share = authoritative_share(records)
    pts = build_points(records)
    meas_pts = sum(1 for p in pts if (p.get("detExp", 0) + p.get("detPrep", 0)) > 0)
    quads: dict[str, int] = {}
    for p in pts:
        quads[p["quad"]] = quads.get(p["quad"], 0) + 1
    cut = (records[0].get("scores") or {}).get("calibration", "")
    return {
        "records_source": os.path.basename(src),
        "entities": len(records),
        "gate_share": share,
        "gate_status": "PASS" if share >= 0.60 else "PROVISIONAL",
        "measured_entities": meas_pts,
        "quadrants": quads,
        "calibration": cut,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 0
    cmd = sys.argv[1]
    if cmd == "rebuild":
        return rebuild(
            measure="--measure" in sys.argv,
            bank="--no-bank" not in sys.argv,
            qa="--qa" in sys.argv,
        )
    if cmd == "metrics":
        m = publish_metrics()
        if "--json" in sys.argv:
            print(json.dumps(m, indent=2))
        else:
            print(f"universe: {m['entities']} entities from {m['records_source']}")
            print(f"L5 gate:  {m['gate_share']:.0%} → {m['gate_status']}")
            print(f"measured: {m['measured_entities']}/{m['entities']} entities with tier share > 0")
            print(f"quads:    {m['quadrants']}")
        return 0
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
