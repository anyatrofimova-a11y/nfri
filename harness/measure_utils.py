"""Shared helpers for measure_* harness scripts."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CARRIER_TYPES = {"insurer", "lloyds_syndicate", "reinsurer"}
PRODUCT_ENTITY_TYPES = CARRIER_TYPES | {"mga"}


def load_records(mode: str) -> tuple[list, str, str]:
    """Return (records, base_label, out_path). Live mode chains onto records.measured.json."""
    demo = os.path.join(ROOT, "data", "records.measured_demo.json")
    optimized = os.path.join(ROOT, "data", "records.optimized.json")
    measured = os.path.join(ROOT, "data", "records.measured.json")

    if mode == "fixture" and os.path.exists(demo):
        return json.load(open(demo)), "records.measured_demo.json", demo
    if mode == "live" and os.path.exists(measured):
        return json.load(open(measured)), "records.measured.json", measured
    return json.load(open(optimized)), "records.optimized.json", measured


def trigger_universe_from_optimized() -> list:
    """33 trigger_inputs entities + all L3 assets from records.optimized.json."""
    trigger_path = os.path.join(ROOT, "contract", "trigger_inputs.json")
    optimized = os.path.join(ROOT, "data", "records.optimized.json")
    trigger = set(json.load(open(trigger_path)).get("inputs", {}))
    recs = json.load(open(optimized))
    l3 = {r["entity_id"] for r in recs if r.get("layer") == 3}
    keep = trigger | l3
    return [r for r in recs if r["entity_id"] in keep]


def save_records(recs: list, mode: str, out_path: str) -> None:
    json.dump(recs, open(out_path, "w"), indent=2, ensure_ascii=False)
