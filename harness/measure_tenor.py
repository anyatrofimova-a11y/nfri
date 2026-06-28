#!/usr/bin/env python3
"""Disclosed tenor_mismatch from max cover tenor vs claims history (risk_model).

m = max(0, T_policy − H_claims) / 15 → anchor_0_4(m) (same thresholds as measure_book share_to_rating).
Reads contract/tenor_inputs.json with measure_book.py / measure_trigger.py.
"""
from __future__ import annotations

import json
import os
import sys

from measure_utils import PRODUCT_ENTITY_TYPES, ROOT, load_records, save_records

CITATION_IDS = ["ACT-COMP-LOSS", "UK-GOV-SII-REFORM"]


def m_to_rating(m: float) -> int:
    """anchor_0_4 — identical breakpoints to measure_book.share_to_rating."""
    return 0 if m < 0.02 else 1 if m < 0.06 else 2 if m < 0.15 else 3 if m < 0.30 else 4


def compute_m(t: float, h: float) -> float:
    return max(0.0, float(t) - float(h)) / 15.0


def build_subfactor(row: dict, mode: str) -> dict:
    t = float(row["max_cover_tenor_years"])
    h = float(row["claims_history_years"])
    m = compute_m(t, h)
    rating = m_to_rating(m)
    srcs = row.get("sources") or []
    if row.get("source") and row["source"] not in srcs:
        srcs = [row["source"], *srcs]
    return {
        "rating_0_4": rating,
        "measured_value": {
            "max_cover_tenor_years": t,
            "claims_history_years": h,
            "m": round(m, 4),
        },
        "unit": "tenor mismatch index m",
        "as_of": row.get("as_of", "2026-06-27"),
        "evidence_tier": "disclosed" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "filing",
        "rationale": (
            f"Disclosed max cover tenor T={t}y vs claims history H={h}y → "
            f"m=max(0,T−H)/15={m:.3f} → tenor_mismatch={rating}."
        ),
        "sources": srcs or ["(fixture placeholder)"],
        "confidence": "high" if srcs and row.get("tenor_basis") else "medium" if srcs else "low",
        "citation_ids": CITATION_IDS,
    }


def main() -> None:
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    inputs_path = (
        os.path.join(ROOT, "harness", "fixtures", "tenor_fixture.json")
        if mode == "fixture"
        else os.path.join(ROOT, "contract", "tenor_inputs.json")
    )
    inputs = json.load(open(inputs_path)).get("inputs", {})

    changed = []
    for r in recs:
        if r["entity_type"] not in PRODUCT_ENTITY_TYPES:
            continue
        row = inputs.get(r["entity_id"])
        if not row or row.get("max_cover_tenor_years") is None or row.get("claims_history_years") is None:
            continue
        old = r["exposure_inputs"]["tenor_mismatch"]["rating_0_4"]
        r["exposure_inputs"]["tenor_mismatch"] = build_subfactor(row, mode)
        changed.append((r["entity_id"], old, r["exposure_inputs"]["tenor_mismatch"]["rating_0_4"], row))

    save_records(recs, mode, out_path)

    print(f"=== MEASURE tenor_mismatch ({mode}) ===")
    print(f"base: {base_label}  inputs: {os.path.basename(inputs_path)}\n")
    for eid, old, new, row in changed:
        m = compute_m(row["max_cover_tenor_years"], row["claims_history_years"])
        print(
            f"  {eid:<24} rating {old} -> {new}   "
            f"T={row['max_cover_tenor_years']}y H={row['claims_history_years']}y m={m:.3f}"
        )
    targets = [r for r in recs if r["entity_type"] in PRODUCT_ENTITY_TYPES]
    print(f"\nentities updated: {len(changed)}/{len(targets)}")
    print(f"wrote: data/{os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
