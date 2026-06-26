#!/usr/bin/env python3
"""Basis-risk monitoring stub — reads commercial/basis_risk_monitoring.json and reports status.

Full implementation will compute Clarke monitoring ratio and FNR when loss_pairs populated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "contract" / "products" / "commercial" / "basis_risk_monitoring.json"
LOSS_PAIRS = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.json"


def main() -> int:
    if not CONFIG.exists():
        print("FAIL: missing basis_risk_monitoring.json")
        return 1
    cfg = json.loads(CONFIG.read_text())
    pairs = []
    if LOSS_PAIRS.exists():
        pairs = json.loads(LOSS_PAIRS.read_text()).get("pairs", [])

    print("=== BASIS RISK MONITORING ===")
    print(f"config: {CONFIG.relative_to(ROOT)}")
    print(f"downside_risk_r: {cfg.get('downside_risk_r')}")
    print(f"monitoring_ratio_threshold: {cfg.get('monitoring_ratio_threshold')}")
    print(f"review_cadence_days: {cfg.get('review_cadence_days')}")
    print(f"loss_pairs for calibration: {len(pairs)}")
    ready = all(cfg.get(k) is not None for k in (
        "downside_risk_r", "monitoring_ratio_threshold", "review_cadence_days"))
    print(f"programme_configured: {'yes' if ready else 'no (scaffold)'}")
    return 0 if ready else 0  # informational until commercial gate enforced


if __name__ == "__main__":
    raise SystemExit(main())
