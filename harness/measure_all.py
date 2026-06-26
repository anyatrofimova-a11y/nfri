#!/usr/bin/env python3
"""Run all live measure passes in sequence (chains onto records.measured.json).

  python3 harness/measure_all.py --live
  python3 harness/measure_all.py --fixture
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

SCRIPTS = [
    "measure_capital.py",
    "measure_trigger.py",
    "measure_product.py",
    "measure_book.py",
    "measure_non_firm.py",
]


def main() -> int:
    mode = "--live" if "--live" in sys.argv else "--fixture"
    print(f"=== MEASURE ALL ({mode}) ===\n")
    for script in SCRIPTS:
        path = f"{ROOT}/harness/{script}"
        print(f"--- {script} ---")
        p = subprocess.run([PY, path, mode], cwd=ROOT)
        if p.returncode != 0:
            print(f"FAIL: {script}")
            return p.returncode
        print()
    print("=== MEASURE ALL complete ===")
    print("Output: data/records.measured.json (or records.measured_demo.json in fixture mode)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
