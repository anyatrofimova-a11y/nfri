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
from measure_utils import nf_exposure_key  # noqa: E402

L3_EXPOSURE_KEYS = SUB_KEYS + ("non_firm_compute_exposure",)


def _normalize_l3_patch(records: list, patch: dict) -> dict:
    """Map non_firm patches onto the layer-3 exposure key (compute vs intensity)."""
    eid = patch["entity_id"]
    rec = next((r for r in records if r["entity_id"] == eid), None)
    if not rec or rec.get("layer") != 3:
        return patch
    exp = dict(patch.get("exposure_inputs") or {})
    exp_in = rec.setdefault("exposure_inputs", {})
    nf_key = nf_exposure_key(exp_in)
    for src in ("non_firm_intensity", "non_firm_compute_exposure"):
        if src not in exp:
            continue
        nf = exp.pop(src)
        if src != nf_key and nf_key in exp_in and src in exp_in:
            _merge_sf(exp_in[nf_key], nf)
        else:
            if nf_key not in exp_in and src in exp_in and nf_key != src:
                exp_in[nf_key] = dict(exp_in.pop(src))
            _merge_sf(exp_in.setdefault(nf_key, {}), nf)
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
        paths = sorted(
            glob.glob(os.path.join(ROOT, "data", "l3_research", "batch*.json"))
            + glob.glob(os.path.join(ROOT, "data", "l3_research", "register_pull_batch*.json"))
            + glob.glob(os.path.join(ROOT, "data", "l3_research", "gate_*.json"))
        )
    if not paths:
        print("No l3 patch files.", file=sys.stderr)
        return 1
    records = json.load(open(RECORDS))
    applied = 0
    for path in paths:
        data = json.load(open(path))
        items = data if isinstance(data, list) else data.get("entities", data.get("patches", []))
        if not items and data.get("inputs"):
            items = []
            for eid, row in data["inputs"].items():
                nf = row.get("non_firm_intensity")
                if not nf:
                    continue
                rec = next((r for r in records if r["entity_id"] == eid), None)
                nf_key = nf_exposure_key(rec["exposure_inputs"]) if rec else "non_firm_intensity"
                patch = {"entity_id": eid, "exposure_inputs": {nf_key: nf}}
                if row.get("asset_link"):
                    patch["asset_link"] = row["asset_link"]
                items.append(patch)
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
