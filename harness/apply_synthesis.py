#!/usr/bin/env python3
"""Merge synthesis batch patches into contract/entity_copy.json.

Usage:
  python3 harness/apply_synthesis.py data/synthesis/batch1.json ...
  python3 harness/apply_synthesis.py --all
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = os.path.join(ROOT, "contract", "entity_copy.json")


def _load_copy() -> dict:
    if os.path.isfile(COPY):
        raw = json.load(open(COPY))
        if isinstance(raw, dict) and "entities" in raw:
            return raw
    return {
        "_doc": "Entity-level synthesis overlay merged into profiles.json at build. "
        "Keys = entity_id. Written by profile_editor, portfolio_analyst, placement_mapper bots — never axis scores.",
        "entities": {},
    }


def _items(data) -> dict:
    if isinstance(data, list):
        return {x["entity_id"]: x for x in data if "entity_id" in x}
    if isinstance(data, dict):
        if "entities" in data:
            ent = data["entities"]
            return ent if isinstance(ent, dict) else {x["entity_id"]: x for x in ent}
        if "entity_id" in data:
            return {data["entity_id"]: data}
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--all-portfolio", action="store_true", help="merge data/portfolio/batch*.json only")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = args.files
    if args.all_portfolio:
        paths = sorted(glob.glob(os.path.join(ROOT, "data", "portfolio", "batch*.json")))
        paths += sorted(glob.glob(os.path.join(ROOT, "data", "placements", "*.json")))
    elif args.all:
        paths = sorted(glob.glob(os.path.join(ROOT, "data", "synthesis", "batch*.json")))

    if not paths:
        print("No synthesis patch files.", file=sys.stderr)
        return 1

    doc = _load_copy()
    entities = doc.setdefault("entities", {})
    merged = 0
    for path in paths:
        patch = _items(json.load(open(path)))
        print(f"Applying {path} ({len(patch)} entities)")
        for eid, block in patch.items():
            cur = entities.setdefault(eid, {})
            for key in ("executive_summary", "portfolio_narrative", "placements"):
                if block.get(key):
                    cur[key] = block[key]
            if block.get("axis_rationale"):
                cur["axis_rationale"] = {
                    **(cur.get("axis_rationale") or {}),
                    **block["axis_rationale"],
                }
            merged += 1

    if args.dry_run:
        print(f"dry-run: would merge {merged} entity blocks")
        return 0

    json.dump(doc, open(COPY, "w"), indent=2, ensure_ascii=False)
    print(f"Merged {merged} blocks → {COPY} ({len(entities)} total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
