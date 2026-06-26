#!/usr/bin/env python3
"""Disclosed product_fit from evidenced non-damage product count (direct map).

product_fit = min(n, 4). Reads contract/trigger_inputs.json with measure_trigger.py.
"""
from __future__ import annotations

import json
import os
import sys

from measure_utils import PRODUCT_ENTITY_TYPES, ROOT, load_records, save_records

CITATION_IDS = ["LLOYDS-PARAMETRIC-CYBER", "MGA-PARAMETRIX-SLA", "DESCARTES-DC-PARAMETRIC", "INSTECH-NDBI-PARAMETRIC"]


def count_to_product_fit(n: int) -> int:
    return min(max(0, int(n)), 4)


def build_subfactor(row: dict, mode: str) -> dict:
    n = int(row.get("n_nondamage_products", 0))
    rating = count_to_product_fit(n)
    products = row.get("products") or []
    srcs = row.get("sources") or []
    return {
        "rating_0_4": rating,
        "measured_value": {"n_nondamage_products": n, "products": products},
        "unit": "evidenced product count (direct)",
        "as_of": row.get("as_of", "2026-06-26"),
        "evidence_tier": "disclosed" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "filing",
        "rationale": (
            f"Disclosed non-damage/parametric product count n={n} → product_fit={rating}."
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
        old = r["preparedness_inputs"]["product_fit"]["rating_0_4"]
        r["preparedness_inputs"]["product_fit"] = build_subfactor(row, mode)
        changed.append((r["entity_id"], old, r["preparedness_inputs"]["product_fit"]["rating_0_4"], row))

    save_records(recs, mode, out_path)

    print(f"=== MEASURE product_fit ({mode}) ===")
    print(f"base: {base_label}  inputs: {os.path.basename(inputs_path)}\n")
    for eid, old, new, row in changed:
        print(f"  {eid:<22} rating {old} -> {new}   n={row.get('n_nondamage_products')}")
    targets = [r for r in recs if r["entity_type"] in PRODUCT_ENTITY_TYPES]
    print(f"\nentities updated: {len(changed)}/{len(targets)}")
    print(f"wrote: data/{os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
