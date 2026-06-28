#!/usr/bin/env python3
"""Pricing Stage 5 — premium + capital load from compound loss and hybrid tower.

  python3 harness/pricing/premium_capital.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "pricing"))

from _common import (  # noqa: E402
    EXPENSE_LOAD,
    GBP_TO_USD,
    RISK_MARGIN_BASE,
    SCR_RATE,
    STAGE2,
    STAGE3,
    STAGE4,
    STAGE5,
    load_json,
    write_json,
)


def tail_factor(e_l: float, tail_limit: float) -> float:
    if e_l <= 0:
        return 0.0
    return min(0.25, tail_limit / e_l * 0.15)


def main() -> int:
    for path in (STAGE2, STAGE3, STAGE4):
        if not path.exists():
            print(f"FAIL: missing {path} — run prior stages")
            return 1

    s2 = load_json(STAGE2)
    s3 = load_json(STAGE3)
    s4 = load_json(STAGE4)
    s4_by_id = {a["entity_id"]: a for a in s4.get("assets", [])}
    fnr = float(s3.get("false_negative_rate", 0))

    rows = []
    total_pure = 0.0
    total_gross = 0.0
    total_scr = 0.0

    for asset in s2.get("assets", []):
        eid = asset["entity_id"]
        e_l_gbp = float(asset.get("E_L_gbp", 0))
        tower = s4_by_id.get(eid, {})
        tail = float(tower.get("parametric_tail_limit_gbp", 0))
        tf = tail_factor(e_l_gbp, tail)
        risk_margin = RISK_MARGIN_BASE + tf + fnr * 0.05
        load_factor = 1.0 + EXPENSE_LOAD + risk_margin

        pure_gbp = e_l_gbp
        pure_usd = round(pure_gbp * GBP_TO_USD, 0)
        gross_usd = round(pure_usd * load_factor, 0)
        scr_usd = round(gross_usd * SCR_RATE, 0)
        reins_gap = round(scr_usd * 0.35, 0)  # provisional reinsurance need

        rows.append({
            "entity_id": eid,
            "pure_premium_gbp": round(pure_gbp, 0),
            "pure_premium_usd": pure_usd,
            "gross_premium_usd": gross_usd,
            "load_factor": round(load_factor, 4),
            "capital_charge_usd": scr_usd,
            "reinsurance_gap_usd": reins_gap,
            "citation_ids": ["ACT-CREDIBILITY", "PRA-SII-SCR", "ACAD-EXPONENTIAL-PARETO-SLA-PREMIUM"],
        })
        total_pure += pure_usd
        total_gross += gross_usd
        total_scr += scr_usd

    payload = {
        "version": "0.1",
        "status": "provisional",
        "inputs_from": [
            str(STAGE2.relative_to(ROOT)),
            str(STAGE3.relative_to(ROOT)),
            str(STAGE4.relative_to(ROOT)),
        ],
        "formula": "gross = pure × (1 + expense + risk_margin); SCR = gross × SCR_rate",
        "gbp_to_usd": GBP_TO_USD,
        "expense_load": EXPENSE_LOAD,
        "scr_rate": SCR_RATE,
        "portfolio": {
            "pure_premium_usd": round(total_pure, 0),
            "gross_premium_usd": round(total_gross, 0),
            "capital_charge_usd": round(total_scr, 0),
            "asset_count": len(rows),
        },
        "assets": rows,
    }
    write_json(STAGE5, payload)

    print("=== PRICING Stage 5: premium + capital ===")
    print(f"  portfolio pure=USD {payload['portfolio']['pure_premium_usd']:,.0f}  "
          f"gross=USD {payload['portfolio']['gross_premium_usd']:,.0f}")
    print(f"wrote: {STAGE5.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
