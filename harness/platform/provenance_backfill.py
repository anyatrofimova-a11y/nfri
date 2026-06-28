#!/usr/bin/env python3
"""Honest evidence_tier backfill from source URLs (mirrors evals.py domains).

Only upgrades missing evidence_tier when sources resolve to register/filing/rating domains.
Never sets measured without register measured_value; never writes scores.

  python3 harness/platform/provenance_backfill.py
  python3 harness/platform/provenance_backfill.py --dry-run
"""
from __future__ import annotations

import json
import os
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEASURED = os.path.join(ROOT, "data", "records.measured.json")

REGISTER = (
    "neso.energy", "api.neso.energy", ".gov.uk", "ofgem.gov.uk", "opendatasoft.com",
    "data.ssen.co.uk", "connecteddata.nationalgrid.co.uk", "elexon",
)
FILING = (
    "register.fca.org.uk", "data.fca.org.uk", "company-information.service.gov.uk",
    "lloyds.com", "beazley.com", "chubb.com", "axaxl.com", "munichre.com", "zurich.com",
    "aviva.com", "hiscox.com", "allianz.com",
)
RATING = ("ambest.com", "spglobal.com", "moodys.com", "fitchratings.com")


def classify_url(url: str) -> str | None:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return None
    if any(h in host for h in REGISTER):
        return "measured" if "opendatasoft" in host or "neso" in host else "derived"
    if any(h in host for h in FILING):
        return "disclosed"
    if any(h in host for h in RATING):
        return "disclosed"
    return None


def best_tier(sources: list) -> str | None:
    order = {"disclosed": 0, "derived": 1, "measured": 2}
    tiers = [classify_url(s) for s in sources if classify_url(s)]
    if not tiers:
        return None
    # prefer disclosed over derived for filing pages
    if "disclosed" in tiers:
        return "disclosed"
    if "derived" in tiers:
        return "derived"
    return "measured"


def backfill(records: list, dry_run: bool = False) -> int:
    n = 0
    for rec in records:
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for sf in rec.get(ax, {}).values():
                if sf.get("evidence_tier") in ("measured", "disclosed", "derived"):
                    continue
                if sf.get("measured_value") is not None and sf.get("source_type") == "register":
                    if not sf.get("evidence_tier"):
                        sf["evidence_tier"] = "measured"
                        n += 1
                    continue
                srcs = sf.get("sources") or []
                tier = best_tier(srcs)
                if tier and not sf.get("evidence_tier"):
                    if not dry_run:
                        sf["evidence_tier"] = tier
                    n += 1
    return n


def main() -> int:
    dry = "--dry-run" in sys.argv
    if not os.path.isfile(MEASURED):
        print(f"missing {MEASURED}")
        return 1
    recs = json.load(open(MEASURED, encoding="utf-8"))
    n = backfill(recs, dry_run=dry)
    if not dry:
        json.dump(recs, open(MEASURED, "w"), indent=2, ensure_ascii=False)
    print(f"provenance_backfill: {n} sub-factors {'would be ' if dry else ''}tiered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
