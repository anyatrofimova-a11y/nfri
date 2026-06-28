#!/usr/bin/env python3
"""Backfill value_chain_seat on entity records from contract/platform/value_chain_seats.json.

Usage:
  python3 harness/platform/value_chain.py --backfill [records_path]
  python3 harness/platform/value_chain.py --derive beazley
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEATS_PATH = os.path.join(ROOT, "contract", "platform", "value_chain_seats.json")
DEFAULT_RECORDS = os.path.join(ROOT, "data", "records.json")


def load_seats() -> dict:
    with open(SEATS_PATH, encoding="utf-8") as f:
        return json.load(f)


def derive_seat(rec: dict, cfg: dict) -> str:
    if rec.get("value_chain_seat"):
        return rec["value_chain_seat"]
    et = rec.get("entity_type", "")
    by_type = cfg.get("defaults_by_entity_type", {})
    if et in by_type:
        return by_type[et]
    layer = str(rec.get("layer", ""))
    return cfg.get("defaults_by_layer", {}).get(layer, "asset")


def backfill(path: str) -> int:
    cfg = load_seats()
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    n = 0
    for rec in records:
        if rec.get("value_chain_seat"):
            continue
        rec["value_chain_seat"] = derive_seat(rec, cfg)
        n += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Backfilled value_chain_seat on {n}/{len(records)} records → {path}")
    return 0


def main() -> int:
    if "--backfill" in sys.argv:
        idx = sys.argv.index("--backfill")
        path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("-") else DEFAULT_RECORDS
        return backfill(path)
    if "--derive" in sys.argv:
        eid = sys.argv[sys.argv.index("--derive") + 1]
        with open(DEFAULT_RECORDS, encoding="utf-8") as f:
            records = json.load(f)
        rec = next(r for r in records if r["entity_id"] == eid)
        print(derive_seat(rec, load_seats()))
        return 0
    print("Usage: value_chain.py --backfill [path] | --derive <entity_id>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
