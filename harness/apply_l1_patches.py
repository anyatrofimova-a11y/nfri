#!/usr/bin/env python3
"""Merge l1_research batch patches into data/records.json.

Usage:
  python3 harness/apply_l1_patches.py data/l1_research/batch1.json ...
  python3 harness/apply_l1_patches.py --all   # all batch*.json in data/l1_research/
  python3 harness/apply_l1_patches.py --all-l4  # data/l4_research/batch*.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.json")
SUB_KEYS = (
    "book_concentration",
    "non_firm_intensity",
    "aggregation_correlation",
    "trigger_gap",
    "tenor_mismatch",
    "data_monitoring",
    "product_fit",
    "underwriting_expertise",
    "capital_reinsurance",
    "pricing_modelling",
)
PATCH_FIELDS = (
    "rating_0_4",
    "latent_rating_0_4",
    "rationale",
    "sources",
    "citation_ids",
    "confidence",
    "evidence_tier",
    "measured_value",
    "unit",
    "as_of",
    "source_type",
)


def _merge_sf(target: dict, patch: dict) -> None:
    for k in PATCH_FIELDS:
        if k in patch and patch[k] is not None:
            target[k] = patch[k]


def apply_patch(records: list, patch: dict) -> bool:
    eid = patch["entity_id"]
    idx = next((i for i, r in enumerate(records) if r["entity_id"] == eid), None)
    if idx is None:
        print(f"  skip unknown entity_id: {eid}", file=sys.stderr)
        return False
    rec = records[idx]
    for axis in ("exposure_inputs", "preparedness_inputs"):
        axis_patch = patch.get(axis) or {}
        for key, sf_patch in axis_patch.items():
            if key not in SUB_KEYS and key != "non_firm_compute_exposure":
                print(f"  warn {eid}: unknown sub-factor {key}", file=sys.stderr)
                continue
            if key not in rec.get(axis, {}):
                print(f"  warn {eid}: missing {axis}.{key} on record", file=sys.stderr)
                continue
            _merge_sf(rec[axis][key], sf_patch)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="patch JSON files")
    ap.add_argument("--all", action="store_true", help="merge all data/l1_research/batch*.json")
    ap.add_argument("--all-l4", action="store_true", help="merge all data/l4_research/batch*.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = args.files
    if args.all:
        paths = sorted(glob.glob(os.path.join(ROOT, "data", "l1_research", "batch*.json")))
    elif args.all_l4:
        paths = sorted(glob.glob(os.path.join(ROOT, "data", "l4_research", "batch*.json")))

    if not paths:
        print("No patch files.", file=sys.stderr)
        return 1

    records = json.load(open(RECORDS))
    applied = 0
    for path in paths:
        data = json.load(open(path))
        items = data if isinstance(data, list) else data.get("entities", data.get("patches", []))
        if isinstance(items, dict):
            items = [{"entity_id": k, **v} for k, v in items.items()]
        print(f"Applying {path} ({len(items)} entities)")
        for patch in items:
            if apply_patch(records, patch):
                applied += 1

    if args.dry_run:
        print(f"dry-run: would patch {applied} entities")
        return 0

    json.dump(records, open(RECORDS, "w"), indent=2, ensure_ascii=False)
    print(f"Patched {applied} entities → {RECORDS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
