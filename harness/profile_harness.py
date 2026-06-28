#!/usr/bin/env python3
"""Profile depth harness — Ciridae-style entity analysis QA.

Checks research depth in records.scored.json, entity_copy overlay, and
profiles.json projection.

  python3 harness/profile_harness.py
  python3 harness/profile_harness.py --strict   # exit 1 on errors
  python3 harness/profile_harness.py --deploy   # print agent manifest
  python3 harness/profile_harness.py --build    # verify + rebuild site
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "records.scored.json")
COPY = os.path.join(ROOT, "contract", "entity_copy.json")
PROFILES = os.path.join(ROOT, "site", "data", "profiles.json")
PY = sys.executable


def _load(path: str):
    if not os.path.exists(path):
        return {}
    return json.load(open(path))


def check_records(records: list) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    l1 = [r for r in records if r.get("layer") == 1 and r.get("scores")]
    thin = 0
    for rec in records:
        if not rec.get("scores"):
            continue
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for k, sf in (rec.get(ax) or {}).items():
                rat = sf.get("rating_0_4", 0)
                rat_txt = (sf.get("rationale") or "").strip()
                if len(rat_txt) < 40:
                    thin += 1
                if rat >= 1 and not sf.get("sources"):
                    errors.append(f"{rec['entity_id']}.{k}: rating {rat} without source")
    if thin:
        warnings.append(f"{thin} sub-factor rationales under 40 chars (target: 2–4 sentences each)")
    copy = _load(COPY)
    entities = copy.get("entities", {}) if isinstance(copy, dict) else {}
    missing_exec = [
        r["entity_id"] for r in l1
        if not (entities.get(r["entity_id"]) or {}).get("executive_summary")
    ]
    missing_port = [
        r["entity_id"] for r in l1
        if not (entities.get(r["entity_id"]) or {}).get("portfolio_narrative")
    ]
    if missing_exec:
        warnings.append(f"L1 missing executive_summary in entity_copy: {len(missing_exec)}/{len(l1)}")
    if missing_port:
        warnings.append(f"L1 missing portfolio_narrative: {len(missing_port)}/{len(l1)}")
    return errors, warnings


def check_profiles(profiles: dict) -> list[str]:
    if not profiles:
        return ["site/data/profiles.json missing — run build_frontend.py"]
    errors = []
    for eid, p in profiles.items():
        if len(p.get("exposure") or []) < 5 or len(p.get("preparedness") or []) < 5:
            errors.append(f"profile {eid}: incomplete sub-factor rows")
    return errors


def verify(strict: bool) -> int:
    records = _load(DATA)
    if not records:
        print("FAIL — data/records.scored.json missing")
        return 1
    if not isinstance(records, list):
        records = []

    errors, warnings = check_records(records)
    errors.extend(check_profiles(_load(PROFILES)))

    print("PROFILE HARNESS — entity analysis depth")
    print("=" * 52)
    print(f"  scored entities: {sum(1 for r in records if r.get('scores'))}")
    if errors:
        for e in errors[:20]:
            print(f"  ✗ {e}")
        if len(errors) > 20:
            print(f"  … and {len(errors) - 20} more")
    else:
        print("  ✓ profiles projection + source discipline")
    for w in warnings:
        print(f"  · {w}")
    print("=" * 52)
    if errors:
        print(f"FAIL — {len(errors)} error(s)")
        return 1 if strict else 0
    print("PASS (warnings OK)" if warnings else "PASS")
    return 0


def main() -> int:
    if "--deploy" in sys.argv:
        return subprocess.run([PY, os.path.join(ROOT, "harness", "agent_deploy.py"), "--profiles"], cwd=ROOT).returncode

    strict = "--strict" in sys.argv
    code = verify(strict)
    if code and strict:
        return code

    if "--build" in sys.argv:
        b = subprocess.run([PY, os.path.join(ROOT, "harness", "build_frontend.py")], cwd=ROOT)
        if b.returncode:
            return b.returncode
        return verify(strict)

    if code == 0:
        print("\nnext: python3 harness/profile_harness.py --deploy")
        print("      fan out l1_research → score_and_validate → --build")
    return code


if __name__ == "__main__":
    sys.exit(main())
