#!/usr/bin/env python3
"""Apply contract/asset_coverage_links.json to carrier asset_link.covered_assets.

  python3 harness/apply_coverage_links.py --live
"""
from __future__ import annotations

import json
import os
import sys

from measure_utils import ROOT, load_records, save_records

LINKS_PATH = os.path.join(ROOT, "contract", "asset_coverage_links.json")


def main() -> int:
    mode = "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    spec = json.load(open(LINKS_PATH))
    links = spec.get("links", {})
    by_id = {r["entity_id"]: r for r in recs}

    changed = []
    for eid, row in links.items():
        rec = by_id.get(eid)
        if not rec:
            continue
        assets = row.get("covered_assets") or []
        if not assets:
            continue
        al = rec.get("asset_link")
        if not isinstance(al, dict):
            al = {}
            rec["asset_link"] = al
        old = list(al.get("covered_assets") or [])
        al["covered_assets"] = assets
        al["coverage_confidence"] = row.get("confidence", "medium")
        al["coverage_sources"] = row.get("sources", [])
        al["coverage_rationale"] = row.get("rationale", "")
        al["coverage_as_of"] = row.get("as_of")
        changed.append((eid, old, assets, row.get("confidence")))

    save_records(recs, mode, out_path)

    print(f"=== APPLY asset_coverage_links ({mode}) ===")
    print(f"base: {base_label}  links file: {os.path.basename(LINKS_PATH)}\n")
    for eid, old, new, conf in changed:
        print(f"  {eid:<26} {len(old)} -> {len(new)} assets  conf={conf}")
        print(f"    {', '.join(new)}")
    print(f"\nentities updated: {len(changed)}")
    print(f"wrote: data/{os.path.basename(out_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
