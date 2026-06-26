#!/usr/bin/env python3
"""Bank NESO constraint / congestion time series → boundary curtailment_prob anchors.

Pulls:
  - Constraint Breakdown (thermal cost + volume, daily national)
  - Operational Transparency congestion (boundary actual vs forecast limits)

Writes:
  - contract/constraint_boundary.json (measured anchors)
  - contract/data/constraint_timeseries.json (banked series summary)

  python3 harness/bank_constraint_costs.py
  python3 harness/bank_constraint_costs.py --days 180
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from statistics import mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_BOUNDARY = os.path.join(ROOT, "contract", "constraint_boundary.json")
OUT_SERIES = os.path.join(ROOT, "contract", "data", "constraint_timeseries.json")

CONSTRAINT_RESOURCE = "6afe1c2b-6d70-4e76-8e74-0952b0a2beab"  # 2025-26 breakdown
CONGESTION_RESOURCE = "aa9d4303-b7ec-4881-be07-16bad8824ab6"
NESO_API = "https://api.neso.energy/api/3/action/datastore_search"

# NFRI boundary → NESO congestion column pairs (actual MW / forecast limit MW)
BOUNDARY_COLUMNS = {
    "east_england": [
        ("LE1 - Actual", "LE1 - Forecast"),
        ("B9 - Actual", "B9 - Forecast"),
        ("B7 - Actual", "B7 - Forecast"),
    ],
    "south_wales": [
        ("B6- Actual", "B6- Forecast"),
        ("B6a - Actual", "B6a - Forecast"),
    ],
    "south_west": [
        ("GMSNOW - Actual", "GMSNOW - Forecast"),
        ("Min of B4 B5 - Actual", "Min of B4 B5 - Forecast"),
    ],
    "southern": [
        ("B15 -Actual", "B15 -Forecast"),
        ("DRESHEX - Actual", "DRESHEX - Forecast"),
        ("EC5 - Actual", "EC5 - Forecast"),
    ],
    "scotland": [
        ("SC -Actual", "SC -Forecast"),
    ],
}


def _get(url: str, params: dict) -> dict:
    import requests
    time.sleep(0.6)
    r = requests.get(url, params=params, timeout=60, headers={"User-Agent": "NFRI-harness/0.4"})
    r.raise_for_status()
    return r.json()


def fetch_all(resource_id: str, limit: int = 32000) -> list[dict]:
    rows = []
    offset = 0
    page = 1000
    while offset < limit:
        data = _get(NESO_API, {"resource_id": resource_id, "limit": page, "offset": offset})
        batch = data["result"]["records"]
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < page:
            break
        offset += page
    return rows


def _float(val) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",", ""))
    except ValueError:
        return None


def boundary_utilization(rows: list[dict], pairs: list[tuple[str, str]]) -> list[float]:
    utils = []
    for row in rows:
        for act_col, lim_col in pairs:
            act = _float(row.get(act_col))
            lim = _float(row.get(lim_col))
            if act is None or lim is None or lim <= 0:
                continue
            utils.append(min(2.0, act / lim))
    return utils


def normalize_probs(raw: dict[str, float]) -> dict[str, float]:
    vals = list(raw.values())
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        return {k: 0.5 for k in raw}
    return {k: round(0.15 + 0.75 * (v - lo) / (hi - lo), 4) for k, v in raw.items()}


def thermal_stats(rows: list[dict]) -> dict:
    costs, vols = [], []
    for row in rows:
        c = _float(row.get("Thermal constraints cost"))
        v = abs(_float(row.get("Thermal constraints volume")) or 0)
        if c is not None:
            costs.append(c)
        if v:
            vols.append(v)
    if not costs:
        return {}
    return {
        "days": len(costs),
        "thermal_cost_gbp_mean": round(mean(costs), 0),
        "thermal_cost_gbp_p90": round(sorted(costs)[int(0.9 * len(costs)) - 1], 0),
        "thermal_volume_mwh_mean": round(mean(vols), 0) if vols else None,
    }


def main() -> int:
    print("=== BANK NESO constraint / congestion time series ===\n")
    try:
        import requests  # noqa: F401
    except ImportError:
        print("FAIL: pip install requests")
        return 1

    cong_rows = fetch_all(CONGESTION_RESOURCE)
    constraint_rows = fetch_all(CONSTRAINT_RESOURCE)
    print(f"congestion rows: {len(cong_rows)}  constraint breakdown rows: {len(constraint_rows)}")

    raw_util = {}
    boundary_detail = {}
    for bkey, pairs in BOUNDARY_COLUMNS.items():
        utils = boundary_utilization(cong_rows, pairs)
        if not utils:
            continue
        avg = mean(utils)
        raw_util[bkey] = avg
        boundary_detail[bkey] = {
            "congestion_util_mean": round(avg, 4),
            "congestion_util_p90": round(sorted(utils)[int(0.9 * len(utils)) - 1], 4),
            "neso_column_pairs": pairs,
            "n_observations": len(utils),
        }

    probs = normalize_probs(raw_util)
    national = thermal_stats(constraint_rows)

    boundaries = {}
    for bkey in BOUNDARY_COLUMNS:
        if bkey not in probs:
            continue
        meta = boundary_detail[bkey]
        boundaries[bkey] = {
            "label": bkey.replace("_", " ").title(),
            "curtailment_prob_norm": probs[bkey],
            "evidence_tier": "measured",
            "method": "Mean NESO boundary congestion utilization (actual/limit) from Operational Transparency series",
            "congestion_util_mean": meta["congestion_util_mean"],
            "neso_columns": [p[0] for p in meta["neso_column_pairs"]],
            "as_of": date.today().isoformat(),
            "citation_ids": ["NESO-CONSTRAINT-COSTS"],
        }

    boundaries["unknown"] = {
        "label": "Unmapped boundary (national mean)",
        "curtailment_prob_norm": round(mean(probs.values()), 4) if probs else 0.5,
        "evidence_tier": "derived",
        "method": "Mean of mapped boundaries",
        "as_of": date.today().isoformat(),
        "citation_ids": ["NESO-CONSTRAINT-COSTS"],
    }

    payload = {
        "__LIVE__": True,
        "purpose": "Boundary-level curtailment probability from banked NESO congestion + constraint time series.",
        "source": "https://www.neso.energy/data-portal/constraint-breakdown",
        "congestion_source": "https://www.neso.energy/data-portal/operational-transparency-forum-network-congestion-data",
        "citation_ids": ["NESO-CONSTRAINT-COSTS", "NESO-CMP448"],
        "banked_at": date.today().isoformat(),
        "national_thermal": national,
        "boundaries": boundaries,
    }
    os.makedirs(os.path.dirname(OUT_SERIES), exist_ok=True)
    json.dump(payload, open(OUT_BOUNDARY, "w"), indent=2, ensure_ascii=False)
    json.dump(
        {
            "banked_at": payload["banked_at"],
            "congestion_rows": len(cong_rows),
            "constraint_rows": len(constraint_rows),
            "national_thermal": national,
            "boundary_utilization": boundary_detail,
            "curtailment_prob_norm": probs,
        },
        open(OUT_SERIES, "w"),
        indent=2,
    )

    print("\nBoundary curtailment_prob_norm (from NESO congestion utilization):")
    for k, v in sorted(probs.items()):
        print(f"  {k:<16} util={boundary_detail[k]['congestion_util_mean']:.3f}  p={v:.3f}")
    if national:
        print(f"\nNational thermal (last {national['days']} days): "
              f"mean cost £{national['thermal_cost_gbp_mean']:,.0f}/day, "
              f"p90 £{national['thermal_cost_gbp_p90']:,.0f}/day")
    print(f"\nwrote: {os.path.relpath(OUT_BOUNDARY, ROOT)}")
    print(f"wrote: {os.path.relpath(OUT_SERIES, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
