#!/usr/bin/env python3
"""Disclosed trigger_gap from evidenced non-damage product count (inverse map).

n=0→4, 1→3, 2→2, 3→1, ≥4→0. Reads contract/trigger_inputs.json with measure_product.py.
"""
from __future__ import annotations

import json
import os
import sys

from measure_utils import PRODUCT_ENTITY_TYPES, ROOT, load_records, save_records

CITATION_IDS = ["LLOYDS-PARAMETRIC-CYBER", "LMA-BI-GUIDE", "MGA-PARAMETRIX-SLA", "DESCARTES-DC-PARAMETRIC"]


def count_to_trigger_gap(n: int) -> int:
    n = max(0, int(n))
    return {0: 4, 1: 3, 2: 2, 3: 1}.get(n, 0)


def build_subfactor(row: dict, mode: str) -> dict:
    n = int(row.get("n_nondamage_products", 0))
    rating = count_to_trigger_gap(n)
    products = row.get("products") or []
    srcs = row.get("sources") or []
    return {
        "rating_0_4": rating,
        "measured_value": {"n_nondamage_products": n, "products": products},
        "unit": "evidenced product count (inverse)",
        "as_of": row.get("as_of", "2026-06-26"),
        "evidence_tier": "disclosed" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "filing",
        "rationale": (
            f"Disclosed non-damage/parametric product count n={n} → trigger_gap={rating} "
            f"(0 products = max basis risk / legacy physical-damage gap)."
        ),
        "sources": srcs or ["(fixture placeholder)"],
        "confidence": "high" if n >= 2 and srcs else "medium" if srcs else "low",
        "citation_ids": CITATION_IDS,
    }


def main() -> None:
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    inputs_path = (
        os.path.join(ROOT, "harness", "fixtures", "trigger_fixture.json")
        if mode == "fixture"
        else os.path.join(ROOT, "contract", "trigger_inputs.json")
    )
    inputs = json.load(open(inputs_path)).get("inputs", {})

    changed = []
    for r in recs:
        if r["entity_type"] not in PRODUCT_ENTITY_TYPES:
            continue
        row = inputs.get(r["entity_id"])
        if not row:
            continue
        old = r["exposure_inputs"]["trigger_gap"]["rating_0_4"]
        r["exposure_inputs"]["trigger_gap"] = build_subfactor(row, mode)
        changed.append((r["entity_id"], old, r["exposure_inputs"]["trigger_gap"]["rating_0_4"], row))

    save_records(recs, mode, out_path if mode == "live" else out_path)

    print(f"=== MEASURE trigger_gap ({mode}) ===")
    print(f"base: {base_label}  inputs: {os.path.basename(inputs_path)}\n")
    for eid, old, new, row in changed:
        print(f"  {eid:<22} rating {old} -> {new}   n={row.get('n_nondamage_products')}")
    targets = [r for r in recs if r["entity_type"] in PRODUCT_ENTITY_TYPES]
    print(f"\nentities updated: {len(changed)}/{len(targets)}")
    print(f"wrote: data/{os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
