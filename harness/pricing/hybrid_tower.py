#!/usr/bin/env python3
"""Pricing Stage 4 — hybrid tower (indemnity cap + parametric tail).

  python3 harness/pricing/hybrid_tower.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "pricing"))

from _common import (  # noqa: E402
    GBP_TO_USD,
    STAGE2,
    STAGE3,
    STAGE4,
    TRAD_CAP_FRACTION,
    load_json,
    write_json,
)


def main() -> int:
    for path in (STAGE2, STAGE3):
        if not path.exists():
            print(f"FAIL: missing {path} — run prior stages")
            return 1

    s2 = load_json(STAGE2)
    s3 = load_json(STAGE3)
    gamma = float(s3["gamma"])
    s3_by_id = {a["entity_id"]: a for a in s3.get("assets", [])}

    rows = []
    for asset in s2.get("assets", []):
        eid = asset["entity_id"]
        e_l = float(asset.get("E_L_gbp", 0))
        theta = float(s3_by_id.get(eid, {}).get("index_theta", 0))
        g_star = gamma * theta
        l_trad = round(e_l * TRAD_CAP_FRACTION, 0)
        parametric = round(max(0.0, g_star - l_trad), 0)
        tail_limit = round(max(parametric, e_l - l_trad), 0)
        rows.append({
            "entity_id": eid,
            "E_L_gbp": e_l,
            "L_trad_cap_gbp": l_trad,
            "parametric_tail_gbp": parametric,
            "parametric_tail_limit_gbp": tail_limit,
            "trigger_stack": {
                "indemnity_layer": "physical_damage_bi",
                "parametric_index": "mwh_shortfall",
                "attachment_mwh": round(theta * 0.5, 1) if theta > 0 else 0,
                "exhaustion_mwh": round(theta, 1) if theta > 0 else 0,
            },
            "trigger_gap_gbp": round(max(0.0, e_l - l_trad - parametric), 0),
            "citation_ids": ["ACAD-LOPEZ-HYBRID", "LMA-BI-GUIDE", "MGA-PARAMETRIX-SLA"],
        })

    payload = {
        "version": "0.1",
        "status": "provisional",
        "inputs_from": [
            str(STAGE2.relative_to(ROOT)),
            str(STAGE3.relative_to(ROOT)),
        ],
        "formula": "Cover = min(L, L_trad) + g_param(θ); L_trad = 60% × E[L]",
        "trad_cap_fraction": TRAD_CAP_FRACTION,
        "assets": rows,
    }
    write_json(STAGE4, payload)

    print("=== PRICING Stage 4: hybrid tower ===")
    positive = [r for r in rows if r["E_L_gbp"] > 0]
    if positive:
        sample = max(positive, key=lambda r: r["E_L_gbp"])
        print(f"  sample {sample['entity_id']}: L_trad=£{sample['L_trad_cap_gbp']:,.0f}  "
              f"tail=£{sample['parametric_tail_limit_gbp']:,.0f}")
    print(f"  assets: {len(rows)}")
    print(f"wrote: {STAGE4.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
