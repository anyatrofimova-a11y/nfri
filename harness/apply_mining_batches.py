#!/usr/bin/env python3
"""Merge measurement mining batches into contract inputs.

  python3 harness/apply_mining_batches.py --apply
"""
from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_ROOT = os.path.join(ROOT, "data")


def _merge_book(batch_path: str, book: dict) -> int:
    doc = json.load(open(batch_path))
    rows = doc.get("inputs") or {}
    n = 0
    for eid, row in rows.items():
        if not row.get("total_gwp") or row.get("energy_power_gwp") is None:
            continue
        book.setdefault("inputs", {})[eid] = {**book.get("inputs", {}).get(eid, {}), **row}
        n += 1
    return n


def _merge_capital(batch_path: str, cap: dict) -> int:
    doc = json.load(open(batch_path))
    rows = doc.get("inputs") or {}
    n = 0
    for eid, row in rows.items():
        if not row:
            continue
        out = {
            "fsr_rating": row.get("fsr_rating") or row.get("fsr"),
            "fsr_scale": row.get("fsr_scale") or row.get("fsr_agency", "ambest"),
            "scr_coverage_pct": row.get("scr_coverage_pct"),
            "fsr_source": row.get("fsr_source") or row.get("source"),
            "scr_source": row.get("scr_source"),
            "as_of": row.get("as_of"),
        }
        if not out["fsr_rating"] and out["scr_coverage_pct"] is None:
            continue
        cap.setdefault("inputs", {})[eid] = {**cap.get("inputs", {}).get(eid, {}), **out}
        n += 1
    return n


def _merge_trigger(batch_path: str, tri: dict) -> int:
    doc = json.load(open(batch_path))
    rows = doc.get("inputs") or {}
    n = 0
    for eid, row in rows.items():
        if "n_nondamage_products" not in row:
            continue
        tri.setdefault("inputs", {})[eid] = {**tri.get("inputs", {}).get(eid, {}), **row}
        n += 1
    return n


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if not args.apply:
        print("dry-run — use --apply")
        return 0

    book_path = os.path.join(ROOT, "contract", "book_inputs.json")
    cap_path = os.path.join(ROOT, "contract", "capital_inputs.json")
    tri_path = os.path.join(ROOT, "contract", "trigger_inputs.json")
    book = json.load(open(book_path))
    cap = json.load(open(cap_path))
    tri = json.load(open(tri_path))
    total = 0

    for sub in ("book_mining", "sfcr_mining"):
        for path in sorted(glob.glob(os.path.join(BATCH_ROOT, sub, "batch*.json"))):
            total += _merge_book(path, book)
            print(f"book ← {os.path.basename(path)}")

    for path in sorted(glob.glob(os.path.join(BATCH_ROOT, "capital_mining", "batch*.json"))):
        total += _merge_capital(path, cap)
        print(f"capital ← {os.path.basename(path)}")

    for path in sorted(glob.glob(os.path.join(BATCH_ROOT, "trigger_mining", "batch*.json"))):
        total += _merge_trigger(path, tri)
        print(f"trigger ← {os.path.basename(path)}")

    json.dump(book, open(book_path, "w"), indent=2, ensure_ascii=False)
    json.dump(cap, open(cap_path, "w"), indent=2, ensure_ascii=False)
    json.dump(tri, open(tri_path, "w"), indent=2, ensure_ascii=False)
    print(f"merged {total} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
