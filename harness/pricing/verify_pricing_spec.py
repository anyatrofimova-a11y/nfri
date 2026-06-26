#!/usr/bin/env python3
"""NFRI pricing pipeline — scaffold verifier (P1–P5 gates)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRICING_MODEL = ROOT / "contract" / "products" / "pricing" / "pricing_model.json"
CITATIONS = ROOT / "contract" / "citations.json"
LOSS_PAIRS = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.json"
LOSS_SCHEMA = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.schema.json"


def main() -> int:
    checks: list[tuple[str, str, str]] = []
    model = json.loads(PRICING_MODEL.read_text())
    cites = json.loads(CITATIONS.read_text())["references"]

    # P1 — stages cite registry
    missing = []
    for stage in model["pipeline"]:
        for cid in stage.get("primary_citations", []):
            if cid not in cites:
                missing.append(f"{stage['id']}:{cid}")
    checks.append((
        "P1 stage citations resolve",
        "PASS" if not missing else "FAIL",
        "all resolve" if not missing else ", ".join(missing[:5]),
    ))

    # P2 — loss pairs file exists
    pairs_ok = LOSS_PAIRS.exists() and LOSS_SCHEMA.exists()
    pair_count = 0
    if pairs_ok:
        pair_count = len(json.loads(LOSS_PAIRS.read_text()).get("pairs", []))
    checks.append((
        "P2 loss_pairs scaffold",
        "PASS" if pairs_ok else "FAIL",
        f"{pair_count} pairs (calibration TBD)" if pairs_ok else "missing files",
    ))

    # P3–P5 — not implemented yet
    for gate in ("P3 payout coherence", "P4 premium vs EL", "P5 index traceability"):
        checks.append((gate, "WARN", "scaffold — implement when stages built"))

    print("NFRI PRICING SPEC VERIFICATION")
    print("=" * 64)
    fails = 0
    for name, status, detail in checks:
        print(f"  [{status:4}] {name}")
        print(f"         {detail}")
        if status == "FAIL":
            fails += 1
    print("=" * 64)
    print(f"SUMMARY: {sum(1 for _, s, _ in checks if s == 'PASS')} pass, "
          f"{sum(1 for _, s, _ in checks if s == 'WARN')} warn, {fails} fail")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
