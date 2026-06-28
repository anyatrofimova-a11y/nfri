#!/usr/bin/env python3
"""IC-06 pricing quote service — deterministic premium from pipeline stages + audit log.

  python3 harness/pricing/quote.py --fixture
  python3 harness/pricing/quote.py --request data/fixtures/pricing_request.json
  python3 harness/pricing/quote.py --entity asset-kao-harlow --limit-usd 10000000
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "pricing"))

from _common import (  # noqa: E402
    AUDIT_DIR,
    GBP_TO_USD,
    MODEL_VERSION,
    STAGE1,
    STAGE2,
    STAGE3,
    STAGE4,
    STAGE5,
    inputs_hash,
    load_json,
    utc_now,
    write_json,
)

PY = sys.executable


def ensure_pipeline() -> None:
    for path in (STAGE1, STAGE2, STAGE3, STAGE4, STAGE5):
        if not path.exists():
            subprocess.run([PY, str(ROOT / "harness" / "pricing" / "run_pipeline.py")], cwd=str(ROOT), check=True)
            return


def portfolio_floor_rate(s5: dict, limit_usd: float) -> float:
    """Median pure/limit for assets with positive EL — basis-risk floor when EL=0."""
    rates = []
    for row in s5.get("assets", []):
        pure = float(row.get("pure_premium_usd", 0))
        if pure > 0 and limit_usd > 0:
            rates.append(pure / limit_usd)
    if not rates:
        return 0.0000568
    rates.sort()
    return rates[len(rates) // 2]


def quote_entity(request: dict) -> dict:
    ensure_pipeline()
    s1 = load_json(STAGE1)
    s2 = load_json(STAGE2)
    s3 = load_json(STAGE3)
    s4 = load_json(STAGE4)
    s5 = load_json(STAGE5)

    eid = request["entity_id"]
    limit_usd = float(request.get("inputs", {}).get("limit_usd") or 0)
    cover = request.get("inputs", {}).get("cover_type", "parametric")

    by1 = {a["entity_id"]: a for a in s1.get("assets", [])}
    by2 = {a["entity_id"]: a for a in s2.get("assets", [])}
    by3 = {a["entity_id"]: a for a in s3.get("assets", [])}
    by4 = {a["entity_id"]: a for a in s4.get("assets", [])}
    by5 = {a["entity_id"]: a for a in s5.get("assets", [])}

    a1 = by1.get(eid, {})
    a2 = by2.get(eid, {})
    a3 = by3.get(eid, {})
    a4 = by4.get(eid, {})
    a5 = by5.get(eid, {})

    pure_usd = float(a5.get("pure_premium_usd", 0))
    if pure_usd <= 0 and limit_usd > 0:
        fnr = float(s3.get("false_negative_rate", 0.1))
        floor = portfolio_floor_rate(s5, limit_usd) * (0.25 + fnr)
        pure_usd = round(limit_usd * floor, 0)

    load = float(a5.get("load_factor", 1.20))
    if cover == "hybrid":
        load += 0.03
    gross_usd = round(pure_usd * load, 0)
    capital_usd = round(gross_usd * 0.175, 0)

    gamma = float(s3.get("gamma", 0))
    theta = float(a3.get("index_theta", a1.get("curtailment_severity_mwh", 0)))
    fnr = float(s3.get("false_negative_rate", 0))

    response = {
        "request_id": request["request_id"],
        "premium_usd": gross_usd,
        "capital_load_usd": capital_usd,
        "payout_schedule": {
            "trigger_type": request.get("inputs", {}).get("trigger_spec", {}).get("trigger_type", "register_event"),
            "expectile_payout_g_star": gamma,
            "basis_risk_estimate": fnr,
            "cover_type": cover,
            "payout_at_theta_usd": round(gamma * theta * GBP_TO_USD, 0),
        },
        "stage_outputs": {
            "01_curtailment_intensity": {
                "curtailment_frequency": a1.get("curtailment_frequency_per_year"),
                "curtailment_severity_mwh": a1.get("curtailment_severity_mwh"),
                "curtailment_duration_hours": a1.get("curtailment_duration_hours"),
            },
            "02_compound_loss": {
                "E_N": a2.get("E_N"),
                "E_S": a2.get("E_S_gbp"),
                "E_L": a2.get("E_L_gbp"),
            },
            "03_expectile_payout": {
                "gamma": gamma,
                "basis_risk_mse": s3.get("basis_risk_mse"),
            },
            "04_hybrid_tower": {
                "L_trad_cap_gbp": a4.get("L_trad_cap_gbp"),
                "parametric_tail_limit_gbp": a4.get("parametric_tail_limit_gbp"),
            },
            "05_premium_capital": {
                "pure_premium_usd": pure_usd,
                "load_factor": load,
            },
        },
        "audit": {
            "inputs_hash": inputs_hash(request),
            "model_version": MODEL_VERSION,
            "citation_ids": request.get("inputs", {}).get("citation_ids", []),
            "timestamp": utc_now(),
        },
        "data_source": request.get("data_source", "fixture"),
    }
    return response


def write_audit(request: dict, response: dict) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    rid = request["request_id"]
    path = AUDIT_DIR / f"{rid}.json"
    write_json(path, {
        "request": request,
        "response": response,
        "audit": response["audit"],
    })
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="NFRI pricing quote (IC-06)")
    ap.add_argument("--fixture", action="store_true", help="Use data/fixtures/pricing_request.json")
    ap.add_argument("--request", type=str, help="Path to pricing request JSON")
    ap.add_argument("--entity", type=str, help="Quick quote entity_id")
    ap.add_argument("--limit-usd", type=float, default=10_000_000)
    args = ap.parse_args()

    if args.fixture:
        req_path = ROOT / "data" / "fixtures" / "pricing_request.json"
    elif args.request:
        req_path = ROOT / args.request
    elif args.entity:
        req_path = None
        request = {
            "request_id": f"pr-{args.entity}",
            "facility_id": f"fac-{args.entity}",
            "entity_id": args.entity,
            "pipeline_stages": [
                "01_curtailment_intensity", "02_compound_loss", "03_expectile_payout",
                "04_hybrid_tower", "05_premium_capital",
            ],
            "inputs": {
                "register_ref": "TEC-LIVE",
                "cover_type": "parametric",
                "limit_usd": args.limit_usd,
                "citation_ids": ["NESO-TEC", "ACAD-BASIS-RISK-EXPECTILES"],
            },
            "data_source": "live",
        }
    else:
        ap.print_help()
        return 1

    if req_path:
        request = load_json(req_path)

    response = quote_entity(request)
    audit_path = write_audit(request, response)

    print("=== NFRI PRICING QUOTE ===")
    print(f"  entity: {request['entity_id']}")
    print(f"  premium_usd: {response['premium_usd']:,.0f}")
    print(f"  capital_load_usd: {response['capital_load_usd']:,.0f}")
    print(f"  audit: {audit_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
