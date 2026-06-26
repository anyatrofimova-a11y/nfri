#!/usr/bin/env python3
"""Pricing Stage 2 — compound loss E[L] = E[N]·E[S] from Stage 1 calibration.

  python3 harness/pricing/compound_loss.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE1 = ROOT / "contract/products/pricing/stages/01_curtailment_intensity/calibration.json"
OUT = ROOT / "contract/products/pricing/stages/02_compound_loss/output.json"
DEFAULT_VOLL_GBP_MWH = 500.0


def main() -> int:
    if not STAGE1.exists():
        print(f"FAIL: run curtailment_intensity.py first — missing {STAGE1}")
        return 1

    cal = json.loads(STAGE1.read_text())
    rows = []
    for asset in cal.get("assets", []):
        e_n = asset["curtailment_frequency_per_year"]
        e_s_mwh = asset["curtailment_severity_mwh"]
        e_s_gbp = e_s_mwh * DEFAULT_VOLL_GBP_MWH
        e_l = e_n * e_s_gbp
        rows.append({
            "entity_id": asset["entity_id"],
            "E_N": e_n,
            "E_S_mwh": e_s_mwh,
            "E_S_gbp": round(e_s_gbp, 0),
            "VoLL_gbp_mwh": DEFAULT_VOLL_GBP_MWH,
            "E_L_gbp": round(e_l, 0),
            "citation_ids": ["ACT-COMP-LOSS", "ACAD-EXPONENTIAL-PARETO-SLA-PREMIUM"],
        })

    payload = {
        "version": "0.1",
        "status": "provisional",
        "inputs_from": str(STAGE1.relative_to(ROOT)),
        "formula": "E[L] = E[N] · E[S]; S = MWh_shortfall × VoLL",
        "assets": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print("=== PRICING Stage 2: compound loss ===")
    for r in rows:
        print(f"  {r['entity_id']:<22} E[L]=£{r['E_L_gbp']:,.0f}  (N={r['E_N']}, S=£{r['E_S_gbp']:,.0f})")
    print(f"wrote: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
