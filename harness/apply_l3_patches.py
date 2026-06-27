#!/usr/bin/env python3
"""Merge l3_research batch patches into data/records.json."""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.json")

sys.path.insert(0, os.path.join(ROOT, "harness"))
from apply_l1_patches import SUB_KEYS, PATCH_FIELDS, apply_patch, _merge_sf  # noqa: E402

L3_EXPOSURE_KEYS = SUB_KEYS + ("non_firm_compute_exposure",)


def _normalize_l3_patch(records: list, patch: dict) -> dict:
    """Map non_firm_compute_exposure patch onto record keys (L3 schema migration)."""
    eid = patch["entity_id"]
    rec = next((r for r in records if r["entity_id"] == eid), None)
    if not rec or rec.get("layer") != 3:
        return patch
    exp = dict(patch.get("exposure_inputs") or {})
    if "non_firm_compute_exposure" in exp:
        nf = exp.pop("non_firm_compute_exposure")
        exp_in = rec.setdefault("exposure_inputs", {})
        if "non_firm_compute_exposure" not in exp_in and "non_firm_intensity" in exp_in:
            exp_in["non_firm_compute_exposure"] = dict(exp_in.pop("non_firm_intensity"))
        if "non_firm_compute_exposure" not in exp_in:
            exp_in["non_firm_compute_exposure"] = {}
        _merge_sf(exp_in["non_firm_compute_exposure"], nf)
    patch = dict(patch)
    patch["exposure_inputs"] = exp
    return patch


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    paths = args.files
    if args.all:
        paths = sorted(glob.glob(os.path.join(ROOT, "data", "l3_research", "batch*.json")))
    if not paths:
        print("No l3 patch files.", file=sys.stderr)
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
            patch = _normalize_l3_patch(records, patch)
            if apply_patch(records, patch):
                applied += 1
                al = patch.get("asset_link")
                if al:
                    idx = next(i for i, r in enumerate(records) if r["entity_id"] == patch["entity_id"])
                    records[idx]["asset_link"] = {**(records[idx].get("asset_link") or {}), **al}
    if args.dry_run:
        print(f"dry-run: would patch {applied} entities")
        return 0
    json.dump(records, open(RECORDS, "w"), indent=2, ensure_ascii=False)
    print(f"Patched {applied} entities → {RECORDS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
