#!/usr/bin/env python3
"""Methodology orchestration harness — one command for all methodology surfaces.

Runs sync verification, optional style lint, and optional site build for:
  contract/methodology.json       → index #methodology
  contract/methodology_tab.json   → site/methodology.html
  contract/scatter_methodology.json → scatter drawer chips

Usage:
  python3 harness/methodology_harness.py              # verify only
  python3 harness/methodology_harness.py --check      # verify (alias)
  python3 harness/methodology_harness.py --strict    # verify, fail on sync errors
  python3 harness/methodology_harness.py --build       # verify + build methodology.html
  python3 harness/methodology_harness.py --full        # verify + build entire site
  python3 harness/methodology_harness.py --deploy      # print agent deploy manifest
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(ROOT, "harness")
PY = sys.executable


def _run(script: str, *args: str) -> int:
    path = os.path.join(HARNESS, script)
    return subprocess.run([PY, path, *args], cwd=ROOT).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Methodology orchestration harness")
    ap.add_argument("--check", action="store_true", help="verify sync only (default)")
    ap.add_argument("--strict", action="store_true", help="non-zero exit on sync failures")
    ap.add_argument("--build", action="store_true", help="build site/methodology.html")
    ap.add_argument("--full", action="store_true", help="run full build_frontend.py")
    ap.add_argument("--deploy", action="store_true", help="print agent deployment manifest")
    ap.add_argument("--lint", action="store_true", help="style_check methodology essay contracts")
    args = ap.parse_args()

    if args.deploy:
        return _run("agent_deploy.py", "--methodology")

    verify_args = ["--strict"] if args.strict else []
    code = _run("verify_methodology.py", *verify_args)
    if code != 0:
        return code

    if args.lint or args.full:
        lint_code = _run("style_check.py", *(["--strict"] if args.strict else []))
        if args.strict and lint_code != 0:
            return lint_code

    if args.build or args.full:
        if args.full:
            code = _run("build_frontend.py")
        else:
            code = _run("build_methodology.py")
        if code != 0:
            return code

    if not any((args.build, args.full, args.deploy, args.lint)):
        print("\nnext: python3 harness/methodology_harness.py --build")
        print("      python3 harness/agent_deploy.py --methodology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
