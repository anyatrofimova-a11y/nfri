#!/usr/bin/env python3
"""Validate audit batch output and print steward summary.

Audit pass documents QA findings only — it does not patch records.scored.json.
Use findings to drive manual fixes or downstream mining passes.

  python3 harness/apply_audit.py --all
  python3 harness/apply_audit.py data/audit/batch1.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DIR = os.path.join(ROOT, "data", "audit")


def validate_batch(path: str) -> tuple[bool, dict]:
    doc = json.load(open(path))
    ok = True
    if doc.get("pass") != "audit":
        print(f"  ✗ {os.path.basename(path)}: pass != audit", file=sys.stderr)
        ok = False
    if not doc.get("researched_by"):
        print(f"  ✗ {os.path.basename(path)}: missing researched_by", file=sys.stderr)
        ok = False
    entities = doc.get("entities") or {}
    if not entities:
        print(f"  ✗ {os.path.basename(path)}: empty entities", file=sys.stderr)
        ok = False
    for eid, ent in entities.items():
        if "findings" not in ent:
            print(f"  ✗ {eid}: missing findings", file=sys.stderr)
            ok = False
    return ok, doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    paths = list(args.files)
    if args.all:
        paths = sorted(glob.glob(os.path.join(AUDIT_DIR, "batch*.json")))
    if not paths:
        print("No audit batch files.", file=sys.stderr)
        return 1

    total_entities = 0
    total_findings = 0
    errors = 0
    for path in paths:
        ok, doc = validate_batch(path)
        if not ok:
            errors += 1
            continue
        s = doc.get("summary", {})
        total_entities += s.get("entities", len(doc.get("entities", {})))
        total_findings += s.get("findings_total", 0)
        print(f"  ✓ {os.path.basename(path)} — {s.get('entities', '?')} entities, "
              f"{s.get('findings_total', '?')} findings")

    print(f"\nValidated {len(paths) - errors}/{len(paths)} batches — "
          f"{total_entities} entities, {total_findings} findings")
    print("Note: audit batches are read-only QA; no record patches applied.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
