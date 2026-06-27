#!/usr/bin/env python3
"""Merge thesis enrichment batches into contract inputs.

  python3 harness/apply_thesis_batches.py           # dry-run
  python3 harness/apply_thesis_batches.py --apply
"""
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = os.path.join(ROOT, "data", "thesis", "batches")

PATHS = {
    "T1": (os.path.join(BATCH, "T1_book_mining.json"), os.path.join(ROOT, "contract", "book_inputs.json"), "inputs"),
    "T2": (os.path.join(BATCH, "T2_trigger_research.json"), os.path.join(ROOT, "contract", "trigger_inputs.json"), "inputs"),
    "T3": (os.path.join(BATCH, "T3_geo_tags.json"), os.path.join(ROOT, "contract", "asset_geo_tags.json"), "entities"),
    "T4": (os.path.join(BATCH, "T4_entity_links.json"), os.path.join(ROOT, "contract", "entity_links.json"), "links"),
}


def _merge_file(batch_path: str, target_path: str, key: str, apply: bool) -> list[str]:
    if not os.path.isfile(batch_path):
        return []
    batch = json.load(open(batch_path))
    doc = json.load(open(target_path))
    incoming = batch.get(key, {})
    added = []
    for eid, row in incoming.items():
        if eid.startswith("_") or eid.startswith("__"):
            continue
        if eid not in doc.get(key, {}):
            added.append(eid)
        doc.setdefault(key, {})[eid] = {**doc.get(key, {}).get(eid, {}), **row}
    if apply:
        json.dump(doc, open(target_path, "w"), indent=2, ensure_ascii=False)
    return added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    total = 0
    for track, (batch_path, target_path, key) in PATHS.items():
        if not os.path.isfile(batch_path):
            print(f"{track}: skip (no batch)")
            continue
        added = _merge_file(batch_path, target_path, key, args.apply)
        total += len(added)
        print(f"{track}: +{len(added)} keys {'applied' if args.apply else '(dry-run)'}")
        if added[:5]:
            print(f"  e.g. {', '.join(added[:5])}")
    print(f"total new keys: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
