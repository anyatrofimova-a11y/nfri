#!/usr/bin/env python3
"""Merge entity_analysis batch patches → contract/entity_analysis.json.

  python3 harness/apply_entity_analysis.py --all
  python3 harness/apply_entity_analysis.py data/entity_analysis/batch1.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "contract", "entity_analysis.json")
BATCH_DIR = os.path.join(ROOT, "data", "entity_analysis")


def _load_out() -> dict:
    if os.path.isfile(OUT):
        return json.load(open(OUT))
    return {
        "_doc": "Per-entity deep dive: grid posture, risk manifestation, cover stack.",
        "version": "0.1",
        "entities": {},
    }


def _extract_entities(doc) -> dict:
    if isinstance(doc, dict):
        if "entities" in doc and isinstance(doc["entities"], dict):
            return doc["entities"]
        if doc.get("entity_id"):
            eid = doc["entity_id"]
            body = {k: v for k, v in doc.items() if k != "entity_id"}
            return {eid: body}
        # bare entity map
        if all(isinstance(v, dict) for v in doc.values() if not str(list(doc.keys())[0]).startswith("_")):
            skip = {"_doc", "version", "as_of", "schema", "batch", "researched_by"}
            return {k: v for k, v in doc.items() if k not in skip and isinstance(v, dict)}
    if isinstance(doc, list):
        out = {}
        for item in doc:
            if isinstance(item, dict) and item.get("entity_id"):
                eid = item.pop("entity_id")
                out[eid] = item
        return out
    return {}


def merge_batch(path: str, entities: dict) -> int:
    raw = json.load(open(path))
    patch = _extract_entities(raw)
    n = 0
    for eid, block in patch.items():
        if not isinstance(block, dict):
            continue
        if "mining" not in block:
            block["mining"] = {
                "pass": "entity_analysis",
                "bots": ["cover_stack_analyst"],
                "last_checked": date.today().isoformat(),
                "method_note": f"Merged from {os.path.basename(path)}",
            }
        entities[eid] = {**entities.get(eid, {}), **block}
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    paths = list(args.files)
    if args.all:
        paths = sorted(glob.glob(os.path.join(BATCH_DIR, "batch*.json")))
    if not paths:
        print("No batch files.", file=sys.stderr)
        return 1

    doc = _load_out()
    entities = doc.setdefault("entities", {})
    total = 0
    for path in paths:
        n = merge_batch(path, entities)
        print(f"  {os.path.basename(path)}: +{n} entities")
        total += n
    doc["as_of"] = date.today().isoformat()
    print(f"Merged {total} entity blocks → {len(entities)} total in entity_analysis.json")
    if args.dry_run:
        return 0
    with open(OUT, "w") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
