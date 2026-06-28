#!/usr/bin/env python3
"""Pricing Stage 3 — expectile-optimal payout g*(θ) from register-measured calibration.

Derives (index_theta, true_loss_s) pairs from Stages 1–2 (no synthetic loss history).
Writes calibration.json and updates loss_pairs.json from register sources.

  python3 harness/pricing/expectile_payout.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness" / "pricing"))

from _common import (  # noqa: E402
    EXPECTILE_TAU,
    LOSS_PAIRS,
    STAGE1,
    STAGE2,
    STAGE3,
    load_json,
    write_json,
)


def fit_expectile_gamma(pairs: list[tuple[float, float]], tau: float = EXPECTILE_TAU) -> float:
    """Linear expectile slope γ via reweighted least squares on (θ, S) pairs."""
    positive = [(t, s) for t, s in pairs if t > 0 and s >= 0]
    if not positive:
        return 500.0  # VoLL anchor when no severity signal

    gamma = sum(s / t for t, s in positive) / len(positive)
    for _ in range(60):
        weights = []
        targets = []
        for t, s in positive:
            resid = s - gamma * t
            w = tau if resid >= 0 else (1.0 - tau)
            weights.append(w * t * t)
            targets.append(w * t * s)
        denom = sum(weights)
        if denom <= 0:
            break
        gamma = sum(targets) / denom
    return round(gamma, 4)


def basis_risk_mse(pairs: list[tuple[float, float]], gamma: float) -> float:
    positive = [(t, s) for t, s in pairs if t > 0]
    if not positive:
        return 0.0
    err = [(s - gamma * t) ** 2 for t, s in positive]
    return round(sum(err) / len(err), 2)


def false_negative_rate(pairs: list[tuple[float, float]], gamma: float, trigger: float = 0.0) -> float:
    """P(S > 0 ∧ g(θ) ≤ trigger) — downside basis risk proxy."""
    events = [(t, s) for t, s in pairs if s > 0]
    if not events:
        return 0.0
    fn = sum(1 for t, s in events if gamma * t <= trigger)
    return round(fn / len(events), 4)


def main() -> int:
    if not STAGE1.exists() or not STAGE2.exists():
        print("FAIL: run stages 1–2 first")
        return 1

    s1 = load_json(STAGE1)
    s2 = load_json(STAGE2)
    s2_by_id = {a["entity_id"]: a for a in s2.get("assets", [])}

    pairs: list[tuple[float, float]] = []
    loss_rows = []
    per_asset = []

    for asset in s1.get("assets", []):
        eid = asset["entity_id"]
        theta = float(asset["curtailment_severity_mwh"])
        row2 = s2_by_id.get(eid, {})
        loss_gbp = float(row2.get("E_S_gbp", 0))
        pairs.append((theta, loss_gbp))
        loss_rows.append({
            "asset_id": eid,
            "as_of": "2026-06-27",
            "index_type": "mwh_shortfall",
            "index_theta": theta,
            "true_loss_s": loss_gbp,
            "citation_ids": asset.get("citation_ids", []) + ["ACAD-BASIS-RISK-EXPECTILES"],
            "source": "register_measured_stage12",
        })
        payout_at_theta = 0.0  # filled after gamma fit
        per_asset.append({"entity_id": eid, "index_theta": theta, "E_S_gbp": loss_gbp})

    gamma = fit_expectile_gamma(pairs)
    mse = basis_risk_mse(pairs, gamma)
    fnr = false_negative_rate(pairs, gamma)

    for row in per_asset:
        row["payout_g_star_gbp"] = round(gamma * row["index_theta"], 2)

    payload = {
        "version": "0.1",
        "status": "provisional",
        "inputs_from": [
            str(STAGE1.relative_to(ROOT)),
            str(STAGE2.relative_to(ROOT)),
        ],
        "method": "Linear expectile g*(θ)=γ·θ calibrated on register-derived (MWh, VoLL×MWh) pairs",
        "gamma": gamma,
        "expectile_tau": EXPECTILE_TAU,
        "payout_function": {
            "type": "linear_expectile",
            "formula": "g*(theta) = gamma * theta",
            "gamma": gamma,
            "tau": EXPECTILE_TAU,
            "index_type": "mwh_shortfall",
            "unit": "GBP",
        },
        "basis_risk_mse": mse,
        "false_negative_rate": fnr,
        "calibration_pairs": len([p for p in pairs if p[0] > 0]),
        "assets": per_asset,
        "citation_ids": [
            "ACAD-BASIS-RISK-EXPECTILES",
            "ACAD-TEH-WOOLNOUGH-TRIGGER",
            "ACAD-CLARKE-INDEX-DEMAND",
        ],
    }
    write_json(STAGE3, payload)

    write_json(LOSS_PAIRS, {
        "version": "0.1",
        "note": "Register-measured (θ,S) pairs from Stages 1–2 — no synthetic loss history.",
        "pairs": loss_rows,
    })

    print("=== PRICING Stage 3: expectile payout ===")
    print(f"  γ={gamma}  MSE={mse:,.0f}  FNR={fnr:.2%}  pairs={len(loss_rows)}")
    print(f"wrote: {STAGE3.relative_to(ROOT)}")
    print(f"wrote: {LOSS_PAIRS.relative_to(ROOT)}")
    return 0 if loss_rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
