#!/usr/bin/env python3
"""Run pricing pipeline stages 1–5.

  python3 harness/pricing/run_pipeline.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
STAGES = [
    "curtailment_intensity.py",
    "compound_loss.py",
    "expectile_payout.py",
    "hybrid_tower.py",
    "premium_capital.py",
]


def main() -> int:
    print("=== NFRI PRICING PIPELINE ===\n")
    for stage in STAGES:
        path = ROOT / "harness" / "pricing" / stage
        print(f"--- {stage} ---")
        p = subprocess.run([PY, str(path)], cwd=str(ROOT))
        if p.returncode != 0:
            return p.returncode
        print()
    print("=== PRICING PIPELINE complete (stages 1–5) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
