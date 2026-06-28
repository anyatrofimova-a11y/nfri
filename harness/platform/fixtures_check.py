#!/usr/bin/env python3
"""Validate parallel sprint fixtures against integration contracts (IC-02–IC-07).

Usage:
  python3 harness/platform/fixtures_check.py
  python3 harness/platform/fixtures_check.py --strict   # exit 1 on any issue
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = os.path.join(ROOT, "data", "fixtures")
CT = os.path.join(ROOT, "contract", "platform")


def _load(path: str) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_register_snapshot() -> list[str]:
    issues: list[str] = []
    path = os.path.join(FIX, "register_snapshot.json")
    if not os.path.isfile(path):
        return ["missing register_snapshot.json"]
    data = _load(path)
    if data.get("data_source") != "fixture":
        issues.append("register_snapshot.json: data_source must be 'fixture'")
    for fac in data.get("facilities", []):
        for key in ("facility_id", "entity_id", "value_chain_seat", "power_dependency"):
            if key not in fac:
                issues.append(f"facility {fac.get('entity_id', '?')}: missing {key}")
        ref = fac.get("power_dependency", {}).get("register_ref", {})
        if ref.get("evidence_tier") not in ("measured", "derived", "disclosed", "assessed"):
            issues.append(f"facility {fac.get('entity_id')}: invalid evidence_tier")
    return issues


def _check_graph_edges() -> list[str]:
    issues: list[str] = []
    path = os.path.join(FIX, "graph_edges.json")
    if not os.path.isfile(path):
        return ["missing graph_edges.json"]
    data = _load(path)
    if not data.get("edges"):
        issues.append("graph_edges.json: edges array empty")
    if not data.get("stress_scenarios"):
        issues.append("graph_edges.json: stress_scenarios required for Sprint 4")
    return issues


def _check_pricing_pair() -> list[str]:
    issues: list[str] = []
    req_path = os.path.join(FIX, "pricing_request.json")
    res_path = os.path.join(FIX, "pricing_response.json")
    if not os.path.isfile(req_path):
        return ["missing pricing_request.json"]
    if not os.path.isfile(res_path):
        return ["missing pricing_response.json"]
    req = _load(req_path)
    res = _load(res_path)
    if req.get("request_id") != res.get("request_id"):
        issues.append("pricing request/response request_id mismatch")
    if "audit" not in res:
        issues.append("pricing_response.json: missing audit block")
    for key in ("request_id", "facility_id", "entity_id", "pipeline_stages", "inputs"):
        if key not in req:
            issues.append(f"pricing_request.json: missing {key}")
    return issues


def _check_curtailment_alert() -> list[str]:
    issues: list[str] = []
    path = os.path.join(FIX, "curtailment_alert.json")
    if not os.path.isfile(path):
        return ["missing curtailment_alert.json"]
    data = _load(path)
    for key in ("alert_id", "facility_id", "entity_id", "event_type", "detected_at", "severity"):
        if key not in data:
            issues.append(f"curtailment_alert.json: missing {key}")
    linkage = data.get("policy_linkage")
    if linkage and not linkage.get("broker_id"):
        issues.append("curtailment_alert.json: policy_linkage should include broker_id (ADR-002)")
    return issues


def _check_extraction() -> list[str]:
    issues: list[str] = []
    path = os.path.join(FIX, "extraction_trigger_gap.json")
    if not os.path.isfile(path):
        return ["missing extraction_trigger_gap.json"]
    data = _load(path)
    if not data.get("source_text"):
        issues.append("extraction_trigger_gap.json: source_text required (ADR-003)")
    if data.get("confidence", 0) < 0.7 and not data.get("human_reviewed"):
        issues.append("extraction_trigger_gap.json: low confidence requires human_reviewed or review_required")
    return issues


def _check_integration_contracts() -> list[str]:
    issues: list[str] = []
    path = os.path.join(CT, "integration_contracts.json")
    if not os.path.isfile(path):
        return ["missing contract/platform/integration_contracts.json"]
    data = _load(path)
    ids = {c["id"] for c in data.get("contracts", [])}
    expected = {f"IC-{i:02d}" for i in range(1, 9)}
    missing = expected - ids
    if missing:
        issues.append(f"integration_contracts.json: missing {sorted(missing)}")
    return issues


def main() -> int:
    strict = "--strict" in sys.argv
    all_issues: list[str] = []
    checks = [
        ("IC registry", _check_integration_contracts),
        ("register snapshot", _check_register_snapshot),
        ("graph edges", _check_graph_edges),
        ("pricing I/O", _check_pricing_pair),
        ("curtailment alert", _check_curtailment_alert),
        ("extraction sample", _check_extraction),
    ]
    print("NFRI platform fixtures check")
    print("=" * 40)
    for name, fn in checks:
        issues = fn()
        status = "PASS" if not issues else "FAIL"
        print(f"[{status}] {name}")
        for i in issues:
            print(f"       · {i}")
        all_issues.extend(issues)
    print()
    if all_issues:
        print(f"Total issues: {len(all_issues)}")
        return 1 if strict else 0
    print("All fixture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
