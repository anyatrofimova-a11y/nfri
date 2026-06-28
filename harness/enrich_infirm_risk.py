#!/usr/bin/env python3
"""Derive infirm_risk_profile[] on L3 entity_analysis from grid_posture + literature taxonomy.

  python3 harness/enrich_infirm_risk.py
  python3 harness/enrich_infirm_risk.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAXONOMY = os.path.join(ROOT, "contract", "infirm_connection_risk.json")
ANALYSIS = os.path.join(ROOT, "contract", "entity_analysis.json")
BOUNDARY = os.path.join(ROOT, "contract", "constraint_boundary.json")
TAGS = os.path.join(ROOT, "contract", "entity_tags.json")

CONNECTION_R = {"firm": 0, "unknown": 2, "queue": 3, "non_firm": 4}
GATE_R = {"firm": 0, "gate_2": 1, "unknown": 2, "gate_1": 3}

MANIFESTATION_TEMPLATES = {
    "capacity_derating": {
        "id": "capacity_derating",
        "headline": "Partial MW cap — not a full outage",
        "mechanism": "Infirm connection limits import or export below nameplate ({mw_phase1} MW contracted vs {mw_max} MW max) — revenue and utilisation loss without equipment failure.",
        "insured_today": "Property limits on TIV; no utilisation or availability shortfall cover evidenced.",
        "typical_gap": "non_firm_intensity + capacity headroom not priced as availability",
        "evidence_tier": "derived",
    },
    "utilisation_compute": {
        "id": "utilisation_compute",
        "headline": "Compute unreliability under grid stress",
        "mechanism": "Lawful curtailment or DOE limits defer batch/inference workload — SLA penalties and migration cost without physical damage to plant.",
        "insured_today": "Cyber outage covers vendor stack; grid-lawful curtailment typically excluded.",
        "typical_gap": "non_firm_compute_exposure — load × firmness × boundary coupling",
        "evidence_tier": "assessed",
    },
    "predictability": {
        "id": "predictability_gap",
        "headline": "Notice horizon shorter than SLA clock",
        "mechanism": "Predictability class {predictability_class} — parametric or DR planning needs forecast horizon; real-time ANM worst case.",
        "insured_today": "Standard BI waiting periods and occurrence limits mis-size chronic low-notice events.",
        "typical_gap": "trigger_gap + basis_mismatch on index design",
        "evidence_tier": "derived",
    },
}


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _boundary_prob(zone: str | None, boundaries: dict) -> float:
    if not zone:
        return 0.15
    z = zone.lower()
    best = 0.15
    for key, row in boundaries.items():
        if key.startswith("_"):
            continue
        label = (row.get("label") or key).lower()
        if any(tok in z for tok in label.split() if len(tok) > 3):
            best = max(best, float(row.get("curtailment_prob_norm") or 0))
        if key.replace("_", " ") in z or key.replace("_", "-") in z:
            best = max(best, float(row.get("curtailment_prob_norm") or 0))
    return min(1.0, best)


def _entity_tags(eid: str, tags: dict) -> list:
    if eid in tags:
        return tags[eid]
    short = eid.replace("asset-", "", 1)
    return tags.get(short, [])


def _is_dc(eid: str, gp: dict, tags: dict) -> bool:
    t = _entity_tags(eid, tags)
    if "data_centre" in t:
        return True
    blob = eid + " " + (gp.get("dno") or "") + " " + (gp.get("constraint_zone") or "")
    return bool(re.search(r"data.?cent|dc\b|hyperscale|colocation|cloud region", blob, re.I))


def _is_bess(eid: str) -> bool:
    return "bess" in eid or "battery" in eid


def _is_wind(eid: str) -> bool:
    return "wind" in eid or "offshore" in eid


def _predictability_class(gp: dict) -> str:
    conn = gp.get("connection") or "unknown"
    gate = gp.get("gate_status") or "unknown"
    if conn == "non_firm" and gate in ("gate_1", "unknown"):
        return "fully_flexible"
    if conn == "non_firm":
        return "dynamic_envelope"
    if conn == "queue":
        return "time_limited"
    if gate == "gate_1":
        return "dynamic_envelope"
    mw1, mwmax = gp.get("mw_phase1"), gp.get("mw_max")
    if mw1 and mwmax and float(mw1) < float(mwmax) * 0.95:
        return "capacity_limited"
    return "capacity_limited"


def _constraint_class(eid: str, gp: dict, tags: dict) -> str:
    if _is_dc(eid, gp, tags):
        return "distribution" if "distribution" in (gp.get("dno") or "").lower() else "transmission"
    if _is_wind(eid):
        return "transmission"
    if _is_bess(eid):
        return "transmission"
    return "transmission"


def _capacity_derating_r(gp: dict) -> int:
    mw1, mwmax = gp.get("mw_phase1"), gp.get("mw_max")
    if mw1 and mwmax and float(mwmax) > 0:
        ratio = float(mw1) / float(mwmax)
        if ratio <= 0.55:
            return 4
        if ratio <= 0.75:
            return 3
        if ratio <= 0.92:
            return 2
    conn = gp.get("connection") or "unknown"
    if conn == "non_firm":
        return 3
    if conn == "queue":
        return 2
    return 0 if conn == "firm" else 1


def _rate_dimension(dim_id: str, eid: str, gp: dict, tags: dict, bprob: float, pred: str, cclass: str) -> tuple[int, str, dict]:
    conn = gp.get("connection") or "unknown"
    gate = gp.get("gate_status") or "unknown"
    base_nf = max(CONNECTION_R.get(conn, 2), GATE_R.get(gate, 2))

    if dim_id == "interruption":
        r = min(4, base_nf + (2 if bprob >= 0.45 else 1 if bprob >= 0.25 else 0))
        note = f"connection={conn}, gate={gate}, boundary_p≈{bprob:.2f}"
        return r, note, {"connection": conn, "gate_status": gate, "curtailment_prob_norm": round(bprob, 3)}

    if dim_id == "capacity_derating":
        r = _capacity_derating_r(gp)
        mw1, mwmax = gp.get("mw_phase1"), gp.get("mw_max")
        note = f"MW ratio {mw1}/{mwmax}" if mw1 and mwmax else f"connection={conn}"
        return r, note, {"mw_phase1": mw1, "mw_max": mwmax}

    if dim_id == "utilisation_compute":
        if not _is_dc(eid, gp, tags):
            r = 2 if _is_wind(eid) or _is_bess(eid) else 1
            note = "Generation/storage — revenue utilisation not compute SLA"
        else:
            r = min(4, base_nf + (1 if bprob >= 0.3 else 0) + (1 if conn == "non_firm" else 0))
            note = "DC load — SLA/deferral channel active"
        return r, note, {"segment": "data_centre" if _is_dc(eid, gp, tags) else "energy"}

    if dim_id == "predictability":
        pmap = {"capacity_limited": 1, "time_limited": 2, "dynamic_envelope": 3, "fully_flexible": 4}
        r = pmap.get(pred, 2)
        return r, f"class={pred}", {"predictability_class": pred}

    if dim_id == "frequency_duration":
        r = min(4, int(round(bprob * 4)) + (1 if conn == "non_firm" else 0))
        return min(4, r), f"compound prior p≈{bprob:.2f}", {"curtailment_prob_norm": round(bprob, 3)}

    if dim_id == "constraint_class":
        r = 3 if cclass == "transmission" and bprob >= 0.35 else 2 if bprob >= 0.2 else 1
        return r, cclass, {"constraint_class": cclass}

    if dim_id == "connection_stage":
        if conn == "queue":
            return 4, "pre-energisation queue", {"connection": conn}
        if conn == "non_firm" and gate == "gate_1":
            return 3, "Gate 1 — pre-firm", {"gate_status": gate}
        if conn == "unknown":
            return 2, "connection unknown", {}
        return 0 if conn == "firm" and gate == "firm" else 1, f"{conn}/{gate}", {"connection": conn}

    if dim_id == "basis_mismatch":
        r = 2 + (1 if _is_dc(eid, gp, tags) else 0) + (1 if pred in ("dynamic_envelope", "fully_flexible") else 0)
        return min(4, r), "SLA vs register trigger gap", {"predictability_class": pred}

    return 1, "", {}


def _ensure_manifestations(entity: dict, gp: dict, pred: str, dims: list) -> None:
    existing = {m.get("id") for m in entity.get("risk_manifestation") or []}
    rmap = {d["id"]: d["rating_0_4"] for d in dims}
    added = []
    for key, tpl in MANIFESTATION_TEMPLATES.items():
        if rmap.get(key, 0) < 2 or key in existing or tpl["id"] in existing:
            continue
        m = dict(tpl)
        m["mechanism"] = m["mechanism"].format(
            mw_phase1=gp.get("mw_phase1", "?"),
            mw_max=gp.get("mw_max", "?"),
            predictability_class=pred.replace("_", " "),
        )
        m["sources"] = list(gp.get("sources") or [])[:2]
        added.append(m)
    if added:
        entity.setdefault("risk_manifestation", []).extend(added)


def build_profile(eid: str, entity: dict, taxonomy: dict, boundaries: dict, tags: dict) -> dict:
    gp = entity.get("grid_posture") or {}
    pred = _predictability_class(gp)
    bprob = _boundary_prob(gp.get("constraint_zone"), boundaries)
    cclass = _constraint_class(eid, gp, tags)

    dims_out = []
    weights = []
    for dim in taxonomy.get("dimensions", []):
        did = dim["id"]
        r, note, inputs = _rate_dimension(did, eid, gp, tags, bprob, pred, cclass)
        w = float(dim.get("weight") or 0.1)
        weights.append(w)
        dims_out.append({
            "id": did,
            "label": dim["label"],
            "rating_0_4": r,
            "weight": w,
            "loss_channel": dim.get("loss_channel", ""),
            "insurance_gap": dim.get("insurance_gap", ""),
            "maps_to_subfactor": dim.get("maps_to_subfactor"),
            "assessment_note": note,
            "measured_inputs": inputs,
            "evidence_tier": "derived" if inputs else "assessed",
            "citation_ids": dim.get("citation_ids", [])[:3],
        })

    wsum = sum(weights) or 1.0
    composite = sum(d["rating_0_4"] * d["weight"] for d in dims_out) / (4.0 * wsum)
    dominant = max(dims_out, key=lambda d: d["rating_0_4"] * d["weight"])

    profile = {
        "as_of": date.today().isoformat(),
        "predictability_class": pred,
        "constraint_class": cclass,
        "infirm_severity_index": round(composite, 3),
        "dominant_channel": dominant["id"],
        "dominant_label": dominant["label"],
        "literature_anchor": "Monterde four-class access + Princeton transmission vs generation distinction",
        "dimensions": dims_out,
    }
    _ensure_manifestations(entity, gp, pred, dims_out)
    return profile


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    taxonomy = _load_json(TAXONOMY)
    analysis_doc = _load_json(ANALYSIS)
    boundaries = _load_json(BOUNDARY) if os.path.isfile(BOUNDARY) else {}
    boundaries = {k: v for k, v in boundaries.items() if not k.startswith("_") and isinstance(v, dict)}
    tags = _load_json(TAGS).get("entities", {}) if os.path.isfile(TAGS) else {}

    entities = analysis_doc.get("entities", {})
    n = 0
    for eid, ent in entities.items():
        if not eid.startswith("asset-"):
            continue
        ent["infirm_risk_profile"] = build_profile(eid, ent, taxonomy, boundaries, tags)
        n += 1

    analysis_doc.setdefault("schema", {})
    analysis_doc["schema"]["infirm_risk_profile"] = {
        "predictability_class": "capacity_limited | time_limited | dynamic_envelope | fully_flexible",
        "constraint_class": "transmission | generation | distribution",
        "infirm_severity_index": "0–1 weighted severity",
        "dimensions": "8-channel assessment — see contract/infirm_connection_risk.json",
    }

    if args.dry_run:
        print(f"Would enrich {n} L3 entities")
        return

    with open(ANALYSIS, "w") as f:
        json.dump(analysis_doc, f, indent=2)
        f.write("\n")
    print(f"enriched infirm_risk_profile on {n} L3 entities → {ANALYSIS}")


if __name__ == "__main__":
    main()
