#!/usr/bin/env python3
"""Full-fidelity entity profiles from records.scored.json → site/data/profiles.json."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DATA = os.path.join(ROOT, "site", "data")
TAGS_PATH = os.path.join(ROOT, "contract", "entity_tags.json")
COPY_PATH = os.path.join(ROOT, "contract", "entity_copy.json")
ANALYSIS_PATH = os.path.join(ROOT, "contract", "entity_analysis.json")
KEY_RISKS_PATH = os.path.join(ROOT, "contract", "key_risks.json")
RUBRIC_PATH = os.path.join(ROOT, "contract", "rubric.json")

SF_LABEL = {
    "book_concentration": "Book concentration", "non_firm_intensity": "Non-firm intensity",
    "aggregation_correlation": "Aggregation / correlation", "trigger_gap": "Trigger gap",
    "tenor_mismatch": "Tenor mismatch", "data_monitoring": "Data & monitoring",
    "product_fit": "Product fit", "underwriting_expertise": "Underwriting expertise",
    "capital_reinsurance": "Capital & reinsurance", "pricing_modelling": "Pricing & modelling",
}


def _load_tags():
    if os.path.isfile(TAGS_PATH):
        return json.load(open(TAGS_PATH)).get("entities", {})
    return {}


def _infer_segment(p: dict, tag_map: dict) -> str:
    eid = p.get("entity_id", "")
    if eid in tag_map:
        tags = tag_map[eid]
        if "data_centre" in tags:
            return "data_centre"
        if "parametric" in tags:
            return "parametric"
        if "energy" in tags:
            return "energy_asset"
    layer = p.get("layer")
    name = (p.get("name") or "").lower()
    if layer == 3:
        if "data" in name or "centre" in name:
            return "data_centre"
        return "energy_asset"
    return "other"


def _fmt_measured(val):
    if val is None:
        return None
    if isinstance(val, dict):
        if "share" in val and val.get("total_gwp") is not None:
            pct = round(float(val["share"]) * 100, 1)
            cur = val.get("currency", "")
            rel = val.get("relevant_gwp", "")
            tot = val.get("total_gwp", "")
            unit = val.get("unit") or "GWP share"
            return f"{pct}% {unit} ({rel}{cur} / {tot}{cur})"
        if "value" in val:
            return str(val["value"]) + (f" {val['unit']}" if val.get("unit") else "")
        return ", ".join(f"{k}: {v}" for k, v in val.items() if v is not None)
    return str(val)


def carrier_asset_links(records: list[dict]) -> dict[str, list[str]]:
    """Map L1 carrier id → linked L3 asset ids via segment tag overlap."""
    tag_map = _load_tags()
    carriers = [r for r in records if r.get("layer") == 1]
    assets = [r for r in records if r.get("layer") == 3]
    links: dict[str, list[str]] = {}
    for c in carriers:
        cid = c["entity_id"]
        ctags = set(tag_map.get(cid, []))
        if not ctags:
            ctags = {_infer_segment(c, tag_map)}
        matched = []
        for a in assets:
            aid = a["entity_id"]
            atags = set(tag_map.get(aid, []))
            seg = _infer_segment(a, tag_map)
            if atags & ctags or seg in ctags or "energy" in ctags and seg == "energy_asset":
                matched.append(aid)
        if not matched and assets:
            matched = [a["entity_id"] for a in assets[:8]]
        links[cid] = matched
    return links


def subfactor_rows_full(rec, axis, humanize=None, questions=None):
    inputs = rec[f"{axis}_inputs"]
    blend = ((rec.get("scores") or {}).get("blend") or {}).get(f"{axis}_sub_factors", {})
    rows = []
    for k, sf in inputs.items():
        bl = blend.get(k, {})
        rat = sf.get("rationale") or ""
        if humanize:
            rat = humanize(k, SF_LABEL.get(k, k), rat)
        mv = _fmt_measured(sf.get("measured_value"))
        qkey = k
        if k == "non_firm_intensity" and rec.get("layer") == 3:
            qkey = "non_firm_compute_exposure"
        rows.append({
            "key": k, "label": SF_LABEL.get(k, k), "axis": axis,
            "weight": bl.get("weight"),
            "lat": bl.get("latent_rating_0_4", sf.get("rating_0_4")),
            "det": bl.get("deterministic_rating_0_4"),
            "eff": bl.get("rating_effective_0_4", sf.get("rating_0_4")),
            "mode": bl.get("score_mode", "latent"),
            "lambda": bl.get("fusion_lambda", 0),
            "tier": sf.get("evidence_tier") or "assessed",
            "conf": sf.get("confidence", "low"),
            "rationale": rat,
            "question": (questions or {}).get(qkey),
            "measured_value": mv,
            "sources": sf.get("sources", []),
            "cites": bl.get("citation_ids", sf.get("citation_ids", [])),
        })
    return rows


def _load_entity_copy() -> dict:
    if not os.path.isfile(COPY_PATH):
        return {}
    raw = json.load(open(COPY_PATH))
    return raw.get("entities", {}) if isinstance(raw, dict) else {}


def _load_entity_analysis() -> dict:
    if not os.path.isfile(ANALYSIS_PATH):
        return {}
    raw = json.load(open(ANALYSIS_PATH))
    return raw.get("entities", {}) if isinstance(raw, dict) else {}


def _load_key_risks() -> dict:
    if not os.path.isfile(KEY_RISKS_PATH):
        return {}
    raw = json.load(open(KEY_RISKS_PATH))
    return raw.get("entities", {}) if isinstance(raw, dict) else {}


def _rubric_questions() -> dict[str, str]:
    if not os.path.isfile(RUBRIC_PATH):
        return {}
    rub = json.load(open(RUBRIC_PATH))
    out: dict[str, str] = {}
    for axis in ("exposure", "preparedness"):
        for k, cfg in (rub.get(axis) or {}).items():
            if cfg.get("question"):
                out[k] = cfg["question"]
    return out


def build_entity_profiles(records, humanize=None, logo_resolver=None):
    """Return {entity_id: profile_dict} from scored records (blend intact)."""
    copy = _load_entity_copy()
    analysis = _load_entity_analysis()
    key_risks_map = _load_key_risks()
    questions = _rubric_questions()
    links = carrier_asset_links(records)
    by_id = {r["entity_id"]: r for r in records}
    profiles = {}
    for rec in records:
        if not rec.get("scores"):
            continue
        eid = rec["entity_id"]
        s = rec["scores"]
        b = s.get("blend") or {}
        logo = f"assets/logos/{eid}.png"
        if logo_resolver:
            logo, _ = logo_resolver(eid)
        linked = links.get(eid, []) if rec.get("layer") == 1 else []
        linked_pts = []
        for aid in linked:
            ar = by_id.get(aid)
            if not ar or not ar.get("scores"):
                continue
            as_ = ar["scores"]
            linked_pts.append({
                "id": aid, "name": ar["name"],
                "mos": as_["margin_of_safety"], "quad": as_["quadrant"],
                "exp": as_["exposure_0_100"], "prep": as_["preparedness_0_100"],
            })
        mos_vals = [x["mos"] for x in linked_pts]
        portfolio = None
        if mos_vals:
            portfolio = {
                "n": len(mos_vals),
                "mosMin": min(mos_vals), "mosMax": max(mos_vals),
                "mosAvg": round(sum(mos_vals) / len(mos_vals), 1),
                "assets": linked_pts,
            }
        prov = rec.get("provenance") or {}
        profiles[eid] = {
            "id": eid, "name": rec["name"], "layer": rec["layer"],
            "type": rec.get("entity_type", ""), "parent": rec.get("parent_group") or "",
            "logo": logo,
            "exp": s["exposure_0_100"], "prep": s["preparedness_0_100"],
            "mos": s["margin_of_safety"], "quad": s["quadrant"],
            "conf": s.get("overall_confidence", "low"),
            "expLat": s.get("exposure_latent_0_100"), "expDet": s.get("exposure_deterministic_0_100"),
            "prepLat": s.get("preparedness_latent_0_100"), "prepDet": s.get("preparedness_deterministic_0_100"),
            "detExp": b.get("exposure_deterministic_weight_share", 0),
            "detPrep": b.get("preparedness_deterministic_weight_share", 0),
            "exposure": subfactor_rows_full(rec, "exposure", humanize, questions),
            "preparedness": subfactor_rows_full(rec, "preparedness", humanize, questions),
            "note": rec.get("notes") or "",
            "portfolio": portfolio,
            "provenance": {
                "last_checked": prov.get("last_checked", ""),
                "researched_by": prov.get("researched_by", ""),
                "method": prov.get("method", ""),
                "evidence": prov.get("evidence"),
            },
            "asset_link": rec.get("asset_link"),
        }
        overlay = copy.get(eid) or {}
        if overlay.get("executive_summary"):
            profiles[eid]["executive_summary"] = overlay["executive_summary"]
        if overlay.get("axis_rationale"):
            profiles[eid]["axis_rationale"] = overlay["axis_rationale"]
        if overlay.get("portfolio_narrative"):
            profiles[eid]["portfolio_narrative"] = overlay["portfolio_narrative"]
        if overlay.get("placements"):
            profiles[eid]["placements"] = overlay["placements"]
        if analysis.get(eid):
            profiles[eid]["entity_analysis"] = analysis[eid]
        kr = key_risks_map.get(eid) or {}
        if kr.get("key_risks"):
            profiles[eid]["key_risks"] = kr["key_risks"]
        if kr.get("researched_by"):
            profiles[eid]["key_risks_researched_by"] = kr["researched_by"]
        elif kr.get("source"):
            profiles[eid]["key_risks_source"] = kr["source"]
    return profiles, links


def write_profiles(profiles: dict, out_dir=SITE_DATA):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "profiles.json")
    with open(path, "w") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=0)
    return path
