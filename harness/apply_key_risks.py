#!/usr/bin/env python3
"""Merge key_risks batch patches → contract/key_risks.json.

  python3 harness/apply_key_risks.py --all
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_DIR = os.path.join(ROOT, "data", "key_risks")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.all:
        print("Use --all to merge batches then rebuild overlay")
        return 0
    n = len(glob.glob(os.path.join(BATCH_DIR, "batch*.json")))
    print(f"merging {n} key_risks batches…")
    rc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "harness", "build_key_risks.py"), "--merge"],
        cwd=ROOT,
    ).returncode
    if rc:
        return rc
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "harness", "build_frontend.py")],
        cwd=ROOT,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
