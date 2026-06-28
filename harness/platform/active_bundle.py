#!/usr/bin/env python3
"""Phase 4 — Active Availability demo: alert → broker handoff → policy linkage.

Uses fixtures in data/fixtures/active_bundle_demo.json. Broker remains in chain (ADR-002).

  python3 harness/platform/active_bundle.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HARNESS_PLATFORM = os.path.join(ROOT, "harness", "platform")
if HARNESS_PLATFORM not in sys.path:
    sys.path.insert(0, HARNESS_PLATFORM)

from embed_api import policy_offer  # noqa: E402
from telemetry_ingest import alert_from_telemetry, ingest, validate_alert  # noqa: E402

DEMO_FIX = os.path.join(ROOT, "data", "fixtures", "active_bundle_demo.json")
TEL_FIX = os.path.join(ROOT, "data", "fixtures", "telemetry_sample.json")
REG_FIX = os.path.join(ROOT, "data", "fixtures", "register_snapshot.json")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _facility_for(demo: dict) -> dict | None:
    reg = _load(REG_FIX)
    for fac in reg.get("facilities", []):
        if fac["facility_id"] == demo["facility_id"]:
            return fac
    return None


def run_demo(*, verbose: bool = True) -> tuple[bool, dict]:
    demo = _load(DEMO_FIX)
    steps: dict[str, str] = {}
    broker_id = demo["broker_id"]
    policy = demo["policy"]

    # 1 — telemetry alert
    tel = _load(TEL_FIX)
    reading = next(
        (r for r in tel.get("readings", []) if r["facility_id"] == demo["facility_id"]),
        tel["readings"][0] if tel.get("readings") else None,
    )
    if not reading:
        steps["telemetry_alert"] = "FAIL: no telemetry reading"
        return False, steps

    fac = _facility_for(demo)
    alert = alert_from_telemetry(reading, fac, fixture_demo=bool(tel.get("FIXTURE_DEMO")))
    alert.pop("_fixture_demo", None)
    val_issues = validate_alert(alert)
    if val_issues:
        steps["telemetry_alert"] = f"FAIL: {val_issues}"
        return False, steps
    steps["telemetry_alert"] = f"PASS ({alert['event_type']}, {alert['severity']})"

    # 2 — embed policy offer (broker_id mandatory)
    req = {
        "facility_id": demo["facility_id"],
        "entity_id": demo["entity_id"],
        "broker_id": broker_id,
        "policy_id": policy["policy_id"],
        "cover_type": policy["cover_type"],
    }
    code, offer = policy_offer(req)
    if code != 200:
        steps["embed_policy_offer"] = f"FAIL: HTTP {code} {offer}"
        return False, steps
    if offer.get("broker_id") != broker_id:
        steps["embed_policy_offer"] = "FAIL: broker_id not preserved"
        return False, steps
    steps["embed_policy_offer"] = f"PASS (offer {offer['offer_id']})"

    # 3 — broker handoff (simulate acceptance)
    handoff_ok = (
        offer.get("broker_handoff", {}).get("broker_id") == broker_id
        and offer.get("value_chain_seat") == "csaas_embed"
        and "broker" in (offer.get("placement_chain") or [])
    )
    if not handoff_ok:
        steps["broker_handoff"] = "FAIL: placement chain bypass or missing broker"
        return False, steps
    steps["broker_handoff"] = f"PASS (broker {broker_id} in chain)"

    # 4 — policy linkage on alert
    alert["policy_linkage"] = {
        "policy_id": policy["policy_id"],
        "broker_id": broker_id,
        "trigger_eligible": policy.get("trigger_eligible", True),
    }
    link_issues = validate_alert(alert)
    if link_issues:
        steps["policy_linkage"] = f"FAIL: {link_issues}"
        return False, steps
    if not alert["policy_linkage"].get("broker_id"):
        steps["policy_linkage"] = "FAIL: ADR-002 broker_id missing on linkage"
        return False, steps
    steps["policy_linkage"] = f"PASS ({policy['policy_id']})"

    expected = demo.get("expected_flow", [])
    flow_ok = all(steps.get(k, "").startswith("PASS") for k in expected if k in steps)
    passed = flow_ok and demo.get("wedge") == "csaas_embed"

    if verbose:
        print("NFRI ACTIVE BUNDLE DEMO (Phase 4)")
        print("=" * 48)
        print(f"wedge: {demo.get('wedge')} · broker: {broker_id}")
        for key in expected:
            print(f"  [{steps.get(key, 'SKIP')}] {key}")
        print("=" * 48)
        print(f"DEMO: {'PASS' if passed else 'FAIL'}")

    return passed, steps


def main() -> int:
    passed, _ = run_demo(verbose=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
