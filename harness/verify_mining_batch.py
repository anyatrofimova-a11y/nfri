#!/usr/bin/env python3
"""Validate book_mining / sfcr_mining batch output before merge.

Rejects hallucinated or schema-invalid rows. Subagents MUST pass this before finishing.

  python3 harness/verify_mining_batch.py data/sfcr_mining/batch1.json
  python3 harness/verify_mining_batch.py --pass sfcr_mining --all
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED = ("total_gwp", "energy_power_gwp", "currency", "lines_counted", "source", "as_of")
BANNED_LINE_PATTERNS = (
    r"^fire and other damage",
    r"^property damage",
    r"^miscellaneous financial loss",
    r"^other$",
)
URL_RE = re.compile(r"^https?://", re.I)
AS_OF_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _errors_for_row(eid: str, row: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(row, dict):
        return [f"{eid}: row is not an object"]
    for k in REQUIRED:
        if k not in row or row[k] in (None, "", []):
            errs.append(f"{eid}: missing {k}")
    src = row.get("source")
    if src and not URL_RE.match(str(src)):
        errs.append(f"{eid}: source must be http(s) URL, got {src!r}")
    as_of = row.get("as_of")
    if as_of and not AS_OF_RE.match(str(as_of)):
        errs.append(f"{eid}: as_of must be YYYY-MM-DD")
    try:
        total = float(row.get("total_gwp", 0))
        energy = float(row.get("energy_power_gwp", -1))
    except (TypeError, ValueError):
        errs.append(f"{eid}: total_gwp / energy_power_gwp must be numbers")
        return errs
    if total <= 0:
        errs.append(f"{eid}: total_gwp must be > 0")
    if energy < 0:
        errs.append(f"{eid}: energy_power_gwp must be >= 0")
    if energy > total:
        errs.append(f"{eid}: energy_power_gwp ({energy}) > total_gwp ({total})")
    share = energy / total if total else 0
    if share > 0.5:
        errs.append(f"{eid}: energy share {share:.0%} > 50% — likely broad LoB, omit or narrow class")
    lines = row.get("lines_counted") or []
    if not isinstance(lines, list) or not lines:
        errs.append(f"{eid}: lines_counted must be non-empty array")
    else:
        for ln in lines:
            low = str(ln).lower().strip()
            for pat in BANNED_LINE_PATTERNS:
                if re.search(pat, low):
                    errs.append(f"{eid}: banned broad line {ln!r}")
    cur = row.get("currency")
    if cur and str(cur) not in ("GBP", "USD", "EUR"):
        errs.append(f"{eid}: currency must be GBP|USD|EUR")
    return errs


def verify_batch(path: str, allowed_entities: set[str] | None = None) -> tuple[list[str], int]:
    doc = json.load(open(path))
    if not isinstance(doc, dict):
        return [f"{path}: root must be object"], 0
    inputs = doc.get("inputs")
    if not isinstance(inputs, dict):
        return [f"{path}: inputs must be object (use {{}} if all omitted)"], 0
    errs: list[str] = []
    for eid, row in inputs.items():
        if allowed_entities and eid not in allowed_entities:
            errs.append(f"{eid}: not in batch manifest")
        errs.extend(_errors_for_row(eid, row))
    return errs, len(inputs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="batch JSON path")
    ap.add_argument("--pass", dest="pass_id", help="book_mining|sfcr_mining")
    ap.add_argument("--all", action="store_true", help="verify all batches for pass")
    args = ap.parse_args()

    paths: list[str] = []
    allowed: dict[str, set[str]] = {}

    if args.all and args.pass_id:
        batch_dir = os.path.join(ROOT, "data", args.pass_id)
        manifest_path = os.path.join(batch_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            batches = json.load(open(manifest_path)).get("batches", {})
            for bk, ids in batches.items():
                p = os.path.join(batch_dir, f"{bk}.json")
                if os.path.isfile(p):
                    paths.append(p)
                    allowed[p] = set(ids)
        else:
            paths = sorted(glob.glob(os.path.join(batch_dir, "batch*.json")))
    elif args.path:
        paths = [args.path if os.path.isabs(args.path) else os.path.join(ROOT, args.path)]
    else:
        ap.print_help()
        return 1

    rc = 0
    total_rows = 0
    for path in paths:
        allow = allowed.get(path)
        if allow is None and args.pass_id:
            bk = os.path.splitext(os.path.basename(path))[0]
            mp = os.path.join(os.path.dirname(path), "manifest.json")
            if os.path.isfile(mp):
                allow = set(json.load(open(mp)).get("batches", {}).get(bk, []))
        errs, n = verify_batch(path, allow)
        total_rows += n
        if errs:
            rc = 1
            print(f"FAIL {path} ({n} rows)")
            for e in errs:
                print(f"  · {e}")
        else:
            print(f"PASS {path} ({n} rows)")
    if rc:
        print("\nFix or omit invalid rows — no synthetic values.", file=sys.stderr)
    else:
        print(f"\nOK — {total_rows} rows validated")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
