#!/usr/bin/env python3
"""Bootstrap records.measured.json from trigger universe (33 entities) + L3 assets.

  python3 harness/bootstrap_measured_universe.py
  python3 harness/bootstrap_measured_universe.py --force
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "records.measured.json")
OPT = os.path.join(ROOT, "data", "records.optimized.json")
TRIGGER = os.path.join(ROOT, "contract", "trigger_inputs.json")
CAPITAL = os.path.join(ROOT, "contract", "capital_inputs.json")
BOUNDARY_MAP = os.path.join(ROOT, "contract", "asset_boundary_map.json")


def trigger_universe_ids() -> set[str]:
    trigger = set(json.load(open(TRIGGER))["inputs"])
    opt = json.load(open(OPT))
    l3 = {r["entity_id"] for r in opt if r.get("layer") == 3}
    return trigger | l3


def gate_cohort_ids() -> set[str]:
    """Publication gate cohort: trigger universe + capital carriers + mapped L3 assets.

    Excludes unmapped L3 assets (no ECR/boundary route yet) so they do not drag L5 down
    before live register measurement lands. See harness/publication_gate.py."""
    trigger = set(json.load(open(TRIGGER))["inputs"])
    cap = set(json.load(open(CAPITAL)).get("inputs", {}))
    mapped = set(json.load(open(BOUNDARY_MAP)).get("assets", {}))
    return trigger | cap | mapped


def main() -> int:
    force = "--force" in sys.argv
    gate = "--gate-cohort" in sys.argv
    ids_fn = gate_cohort_ids if gate else trigger_universe_ids
    label = "gate cohort (trigger+capital+mapped L3)" if gate else "trigger+L3"

    if os.path.exists(OUT) and not force:
        existing = json.load(open(OUT))
        ids = ids_fn()
        have = {r["entity_id"] for r in existing}
        if ids == have:
            print(f"SKIP: records.measured.json already matches {label} ({len(have)} entities)")
            return 0
        if ids.issubset(have) and not gate:
            print(f"SKIP: records.measured.json already has {len(have)} entities (trigger+L3 covered)")
            return 0
        print(f"REBUILD: measured has {len(have)} entities; target {label} = {len(ids)}")

    ids = ids_fn()
    opt = json.load(open(OPT))
    recs = [r for r in opt if r["entity_id"] in ids]
    missing = ids - {r["entity_id"] for r in recs}
    if missing:
        print(f"WARN: missing from optimized: {sorted(missing)}")

    for r in recs:
        r.pop("scores", None)

    json.dump(recs, open(OUT, "w"), indent=2, ensure_ascii=False)
    layers = {}
    for r in recs:
        layers[r["layer"]] = layers.get(r["layer"], 0) + 1
    print("=== BOOTSTRAP measured universe ===")
    print(f"entities: {len(recs)}  ({label} target {len(ids)})")
    print(f"layers: {layers}")
    print(f"wrote: data/records.measured.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
