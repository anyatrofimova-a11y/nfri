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
PUBLICATION_MANIFEST = os.path.join(ROOT, "contract", "publication_gate_manifest.json")


def trigger_universe_ids() -> set[str]:
    trigger = set(json.load(open(TRIGGER))["inputs"])
    opt = json.load(open(OPT))
    l3 = {r["entity_id"] for r in opt if r.get("layer") == 3}
    return trigger | l3


def all_l3_ids() -> set[str]:
    src = os.path.join(ROOT, "data", "records.json")
    if os.path.isfile(src):
        return {r["entity_id"] for r in json.load(open(src)) if r.get("layer") == 3}
    opt = json.load(open(OPT))
    return {r["entity_id"] for r in opt if r.get("layer") == 3}


def register_pull_ids() -> set[str]:
    """Full L3 universe for register measurement (all data centres + gate carriers)."""
    trigger = set(json.load(open(TRIGGER))["inputs"])
    cap = set(json.load(open(CAPITAL)).get("inputs", {}))
    return trigger | cap | all_l3_ids()


def broker_ids() -> set[str]:
    """L2 brokers for placement-chain structural invariants (Phase 2)."""
    src = os.path.join(ROOT, "data", "records.json")
    if not os.path.isfile(src):
        return set()
    return {r["entity_id"] for r in json.load(open(src)) if r.get("entity_type") == "broker"}


def stress_cohort_ids() -> set[str]:
    """Industry stress + graph universe: gate cohort plus L2 brokers (Phase 2 placement chain)."""
    return gate_cohort_ids() | broker_ids()


def publication_gate_cohort_ids() -> set[str]:
    """L5 publication gate cohort — pinned manifest when present.

    Excludes pure L2 brokers (not in manifest). Dynamic gate_cohort_ids() still grows with
    trigger/capital merges; the manifest prevents silent L5 dilution from batch3+ entities.
    """
    if os.path.isfile(PUBLICATION_MANIFEST):
        doc = json.load(open(PUBLICATION_MANIFEST))
        ids = doc.get("entity_ids") or doc.get("entities")
        if ids:
            return set(ids)
    return gate_cohort_ids()


def gate_cohort_ids() -> set[str]:
    """Measured gate cohort: trigger universe + capital carriers + mapped L3 assets.

    Excludes unmapped L3 assets (no ECR/boundary route yet) so they do not drag L5 down
    before live register measurement lands. See harness/publication_gate.py."""
    trigger = set(json.load(open(TRIGGER))["inputs"])
    cap = set(json.load(open(CAPITAL)).get("inputs", {}))
    mapped = set(json.load(open(BOUNDARY_MAP)).get("assets", {}))
    return trigger | cap | mapped


def main() -> int:
    force = "--force" in sys.argv
    gate = "--gate-cohort" in sys.argv
    register_pull = "--register-pull" in sys.argv
    stress = "--stress-cohort" in sys.argv
    if register_pull:
        ids_fn = register_pull_ids
        label = "register-pull (trigger+capital+all L3)"
    elif stress:
        ids_fn = stress_cohort_ids
        label = "stress cohort (gate+brokers)"
    elif gate:
        ids_fn = gate_cohort_ids
        label = "gate cohort (trigger+capital+mapped L3)"
    else:
        ids_fn = trigger_universe_ids
        label = "trigger+L3"

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
    src_path = os.path.join(ROOT, "data", "records.json")
    src = json.load(open(src_path)) if os.path.isfile(src_path) else json.load(open(OPT))
    by_id = {r["entity_id"]: r for r in src}
    recs = [by_id[eid] for eid in sorted(ids) if eid in by_id]
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
