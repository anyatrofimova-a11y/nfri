#!/usr/bin/env python3
"""Pricing Stage 1 — curtailment intensity from measured L3 non_firm_intensity.

Derives provisional frequency/severity proxies from register-measured MW share.
Writes contract/products/pricing/stages/01_curtailment_intensity/calibration.json

  python3 harness/pricing/curtailment_intensity.py
  python3 harness/pricing/curtailment_intensity.py --records data/records.measured.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "contract/products/pricing/stages/01_curtailment_intensity/calibration.json"
DEFAULT_VOLL = 500.0  # GBP/MWh provisional VoLL anchor


def extract_non_firm(nf: dict) -> tuple[float, float] | None:
    """Return (share, mw_total) from measured or legacy scalar measured_value."""
    if nf.get("evidence_tier") != "measured":
        return None
    mv = nf.get("measured_value")
    if mv is None:
        return None
    share = mw_total = None
    if isinstance(mv, dict):
        share = mv.get("share")
        mw_total = mv.get("mw_total") or mv.get("import_mw")
    elif isinstance(mv, (int, float)):
        share = float(mv)
    if share is None:
        return None
    if mw_total is None:
        rat = nf.get("rationale") or ""
        m = re.search(r"=\s*[\d.]+/([\d.]+)\s*MW", rat)
        if m:
            mw_total = float(m.group(1))
        else:
            mw_total = max(1.0, share * 100)  # provisional when MW not stored
    return float(share), float(mw_total)


def share_to_frequency(share: float) -> float:
    """Heuristic: 0.5–12 events/year scaled by non-firm MW share (provisional)."""
    return round(0.5 + float(share) * 11.5, 3)


def severity_mwh(mw_total: float, share: float, hours: float = 24.0) -> float:
    """One event at non-firm capacity for `hours` at full import."""
    return round(float(mw_total) * float(share) * hours, 1)


def main() -> int:
    records_path = ROOT / "data/records.measured.json"
    if len(sys.argv) > 2 and sys.argv[1] == "--records":
        records_path = ROOT / sys.argv[2]

    if not records_path.exists():
        print(f"FAIL: missing {records_path}")
        return 1

    records = json.loads(records_path.read_text())
    assets = []
    for rec in records:
        if rec.get("layer") != 3:
            continue
        nf = rec.get("exposure_inputs", {}).get("non_firm_intensity", {})
        parsed = extract_non_firm(nf)
        if parsed is None:
            continue
        share, mw_total = parsed
        freq = share_to_frequency(share)
        sev = severity_mwh(mw_total, share)
        assets.append({
            "entity_id": rec["entity_id"],
            "name": rec.get("name"),
            "non_firm_share": share,
            "mw_total": mw_total,
            "curtailment_frequency_per_year": freq,
            "curtailment_severity_mwh": sev,
            "curtailment_duration_hours": 24,
            "evidence_tier": nf.get("evidence_tier"),
            "citation_ids": ["NESO-TEC", "DCUSA-ECR", "ACAD-BOEHME-NONFIRM"],
        })

    payload = {
        "version": "0.1",
        "status": "provisional",
        "source_records": str(records_path.relative_to(ROOT)),
        "method": "Register-measured non_firm share → heuristic frequency/severity (replace with OPF/time-series when available)",
        "assets": assets,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print("=== PRICING Stage 1: curtailment intensity ===")
    print(f"assets calibrated: {len(assets)}")
    for a in assets:
        print(f"  {a['entity_id']:<22} share={a['non_firm_share']:.2f}  "
              f"λ={a['curtailment_frequency_per_year']}/yr  severity={a['curtailment_severity_mwh']} MWh")
    print(f"wrote: {OUT.relative_to(ROOT)}")
    return 0 if assets else 1


if __name__ == "__main__":
    raise SystemExit(main())
