#!/usr/bin/env python3
"""Phase 4 — telemetry ingest → curtailment alerts (IC-07).

Ingests fixture or register-derived constraint signals into curtailment_alert.schema.json
shape. No synthetic index scores — alerts use register refs and telemetry readings only.

  python3 harness/platform/telemetry_ingest.py --ingest
  python3 harness/platform/telemetry_ingest.py --ingest --register-only
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = os.path.join(ROOT, "data", "fixtures")
SCHEMA_PATH = os.path.join(ROOT, "contract", "platform", "schemas", "curtailment_alert.schema.json")
ALERTS_OUT = os.path.join(ROOT, "data", "alerts.json")

EVENT_TYPES = frozenset(
    {"curtailment_start", "curtailment_end", "constraint_warning", "gate_status_change", "sla_breach_risk"}
)
SEVERITIES = frozenset({"info", "warning", "critical"})
TELEMETRY_SOURCES = frozenset({"dcim", "bms", "epms", "cloud_monitor", "register", "stub"})
DATA_SOURCES = frozenset({"live", "fixture"})


def _load(path: str) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _facility_index() -> dict[str, dict]:
    reg = _load(os.path.join(FIX, "register_snapshot.json"))
    return {f["facility_id"]: f for f in reg.get("facilities", [])}


def validate_alert(alert: dict) -> list[str]:
    """Lightweight IC-07 validation (no external jsonschema dependency)."""
    issues: list[str] = []
    schema = _load(SCHEMA_PATH)
    for key in schema.get("required", []):
        if key not in alert:
            issues.append(f"missing required field: {key}")
    allowed = set(schema.get("properties", {}).keys())
    extra = set(alert.keys()) - allowed
    if extra:
        issues.append(f"additional properties not allowed: {sorted(extra)}")
    if alert.get("event_type") not in EVENT_TYPES:
        issues.append(f"invalid event_type: {alert.get('event_type')}")
    if alert.get("severity") not in SEVERITIES:
        issues.append(f"invalid severity: {alert.get('severity')}")
    if alert.get("telemetry_source") not in TELEMETRY_SOURCES:
        issues.append(f"invalid telemetry_source: {alert.get('telemetry_source')}")
    if alert.get("data_source") not in DATA_SOURCES:
        issues.append(f"invalid data_source: {alert.get('data_source')}")
    linkage = alert.get("policy_linkage")
    if linkage is not None:
        if not isinstance(linkage, dict):
            issues.append("policy_linkage must be object or null")
        elif "policy_id" not in linkage:
            issues.append("policy_linkage missing policy_id")
    return issues


def _severity_from_signals(gate_status: str, non_firm_share: float, mw_ratio: float | None) -> str:
    if gate_status in ("non_firm", "gate_1") and non_firm_share >= 0.9:
        return "critical"
    if mw_ratio is not None and mw_ratio < 0.85:
        return "critical"
    if gate_status in ("gate_1", "gate_2", "non_firm") or (mw_ratio is not None and mw_ratio < 0.95):
        return "warning"
    return "info"


def _event_from_gate(gate_status: str, prev: str | None = None) -> str:
    if prev and prev != gate_status:
        return "gate_status_change"
    if gate_status in ("gate_1", "non_firm"):
        return "constraint_warning"
    if gate_status == "gate_2":
        return "sla_breach_risk"
    return "constraint_warning"


def alert_from_register(facility: dict, *, detected_at: str | None = None) -> dict:
    """Register-derived constraint signal — no synthetic index scores."""
    dep = facility.get("power_dependency", {})
    gate = dep.get("gate_status", "firm")
    nfs = float(dep.get("non_firm_share", 0))
    severity = _severity_from_signals(gate, nfs, None)
    return {
        "alert_id": f"alert-reg-{facility['facility_id']}",
        "facility_id": facility["facility_id"],
        "entity_id": facility["entity_id"],
        "event_type": _event_from_gate(gate),
        "detected_at": detected_at or _now_iso(),
        "severity": severity,
        "mw_curtailed": None,
        "constraint_zone": dep.get("constraint_zone"),
        "telemetry_source": "register",
        "register_ref": (dep.get("register_ref") or {}).get("ref"),
        "policy_linkage": None,
        "data_source": "fixture",
    }


def alert_from_telemetry(reading: dict, facility: dict | None, *, fixture_demo: bool) -> dict:
    """Map DCIM/BMS reading to alert using register context for constraint zone/ref."""
    signals = reading.get("signals", {})
    import_mw = float(signals.get("import_mw", 0) or 0)
    available_mw = float(signals.get("available_mw", import_mw) or import_mw)
    mw_ratio = (available_mw / import_mw) if import_mw else None
    mw_curtailed = round(max(0.0, import_mw - available_mw), 2) if import_mw else None

    dep = (facility or {}).get("power_dependency", {})
    gate = signals.get("gate_status") or dep.get("gate_status", "firm")
    nfs = float(dep.get("non_firm_share", 0))
    severity = _severity_from_signals(gate, nfs, mw_ratio)

    event_type = "curtailment_start" if mw_curtailed and mw_curtailed > 0 else _event_from_gate(gate)
    source = reading.get("source", "stub")
    if source not in TELEMETRY_SOURCES:
        source = "stub"

    alert: dict[str, Any] = {
        "alert_id": f"alert-tel-{reading['facility_id']}-{reading.get('timestamp', '0')[:10]}",
        "facility_id": reading["facility_id"],
        "entity_id": reading["entity_id"],
        "event_type": event_type,
        "detected_at": reading.get("timestamp") or _now_iso(),
        "severity": severity,
        "mw_curtailed": mw_curtailed,
        "constraint_zone": signals.get("constraint_zone") or dep.get("constraint_zone"),
        "telemetry_source": source,
        "register_ref": (dep.get("register_ref") or {}).get("ref"),
        "policy_linkage": None,
        "data_source": "fixture",
    }
    if fixture_demo:
        alert["_fixture_demo"] = True  # stripped before validate/write
    return alert


def ingest(*, register_only: bool = False, telemetry_only: bool = False) -> tuple[list[dict], dict]:
    """Produce alerts from register and/or telemetry fixtures."""
    fac_idx = _facility_index()
    meta: dict[str, Any] = {"sources": [], "fixture_demo": False}
    alerts: list[dict] = []

    if not telemetry_only:
        for fac in fac_idx.values():
            alert = alert_from_register(fac)
            issues = validate_alert(alert)
            if issues:
                raise ValueError(f"register alert invalid for {fac['facility_id']}: {issues}")
            alerts.append(alert)
        meta["sources"].append("register_snapshot")

    if not register_only:
        tel_path = os.path.join(FIX, "telemetry_sample.json")
        if os.path.isfile(tel_path):
            tel = _load(tel_path)
            meta["fixture_demo"] = bool(tel.get("FIXTURE_DEMO"))
            for reading in tel.get("readings", []):
                fac = fac_idx.get(reading["facility_id"])
                raw = alert_from_telemetry(reading, fac, fixture_demo=meta["fixture_demo"])
                raw.pop("_fixture_demo", None)
                issues = validate_alert(raw)
                if issues:
                    raise ValueError(f"telemetry alert invalid: {issues}")
                alerts.append(raw)
            meta["sources"].append("telemetry_sample")

    return alerts, meta


def write_alerts(alerts: list[dict], meta: dict) -> str:
    payload = {
        "generated": _now_iso(),
        "ingest_meta": meta,
        "alerts": alerts,
    }
    os.makedirs(os.path.dirname(ALERTS_OUT), exist_ok=True)
    with open(ALERTS_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return ALERTS_OUT


def main() -> int:
    register_only = "--register-only" in sys.argv
    telemetry_only = "--telemetry-only" in sys.argv
    if "--ingest" not in sys.argv:
        print("Usage: telemetry_ingest.py --ingest [--register-only | --telemetry-only]")
        return 1

    alerts, meta = ingest(register_only=register_only, telemetry_only=telemetry_only)
    path = write_alerts(alerts, meta)
    demo_flag = " FIXTURE_DEMO" if meta.get("fixture_demo") else ""
    print(f"ingested {len(alerts)} alert(s) from {meta['sources']} → {path}{demo_flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
