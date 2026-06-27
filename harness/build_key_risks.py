#!/usr/bin/env python3
"""Build rich key_risks[] per entity from scored records + entity_analysis + gaps.

  python3 harness/build_key_risks.py
  python3 harness/build_key_risks.py --write   # contract/key_risks.json (deterministic only)
  python3 harness/build_key_risks.py --merge   # merge agent batches then write overlay
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORED = os.path.join(ROOT, "data", "records.scored.json")
ANALYSIS = os.path.join(ROOT, "contract", "entity_analysis.json")
FRAME = os.path.join(ROOT, "contract", "key_risks_framework.json")
OUT = os.path.join(ROOT, "contract", "key_risks.json")
BATCH_DIR = os.path.join(ROOT, "data", "key_risks")

SF_LABEL = {
    "book_concentration": "Book concentration",
    "non_firm_intensity": "Non-firm intensity",
    "non_firm_compute_exposure": "Non-firm compute exposure",
    "aggregation_correlation": "Aggregation / correlation",
    "trigger_gap": "Trigger gap",
    "tenor_mismatch": "Tenor mismatch",
    "data_monitoring": "Data & monitoring",
    "product_fit": "Product fit",
    "underwriting_expertise": "Underwriting expertise",
    "capital_reinsurance": "Capital & reinsurance",
    "pricing_modelling": "Pricing & modelling",
}

TIER_ORDER = {"assessed": 0, "derived": 1, "disclosed": 2, "measured": 3, "FIXTURE_DEMO": 3}


def _load_analysis() -> dict:
    if not os.path.isfile(ANALYSIS):
        return {}
    return json.load(open(ANALYSIS)).get("entities", {})


def _det_share(rec: dict) -> tuple[float, float]:
    s = rec.get("scores") or {}
    b = s.get("blend") or {}
    return (
        float(b.get("exposure_deterministic_weight_share") or 0),
        float(b.get("preparedness_deterministic_weight_share") or 0),
    )


def _subfactors(rec: dict, axis: str) -> list[dict]:
    blend = ((rec.get("scores") or {}).get("blend") or {}).get(f"{axis}_sub_factors", {})
    rows = []
    for k, sf in (rec.get(f"{axis}_inputs") or {}).items():
        bl = blend.get(k, {})
        wt = bl.get("weight") or 0
        rows.append({
            "key": k,
            "label": SF_LABEL.get(k, k),
            "weight": wt,
            "eff": bl.get("rating_effective_0_4", sf.get("rating_0_4")),
            "tier": sf.get("evidence_tier") or "assessed",
            "rationale": (sf.get("rationale") or "")[:280],
            "sources": sf.get("sources") or [],
        })
    return sorted(rows, key=lambda r: -(r["weight"] or 0))


def _provisional_card(rec: dict, det_exp: float, det_prep: float) -> dict | None:
    share = (det_exp + det_prep) / 2
    if share >= 0.2:
        return None
    assessed = []
    for axis in ("exposure", "preparedness"):
        for sf in _subfactors(rec, axis):
            if sf["tier"] in ("assessed",) and (sf["weight"] or 0) > 0:
                assessed.append(sf)
    assessed.sort(key=lambda x: -(x["weight"] or 0))
    top = assessed[:3]
    if not top:
        return None
    names = ", ".join(f"{t['label']} ({t['tier']}, w={t['weight']:.2f})" for t in top)
    gaps = []
    if any(t["key"] == "book_concentration" for t in top):
        gaps.append("book_mining / sfcr_mining")
    if any(t["key"] in ("non_firm_intensity", "non_firm_compute_exposure") for t in top):
        gaps.append("register_pull")
    if any(t["key"] == "trigger_gap" for t in top):
        gaps.append("trigger_mining")
    if any(t["key"] == "aggregation_correlation" for t in top):
        gaps.append("l4_research")
    mining = " · ".join(dict.fromkeys(gaps)) or "l1_research / thin_rationales"
    return {
        "title": "Provisional evidence base",
        "body": (
            f"Only {round(share * 100)}% of sub-factor weight rests on registers or filings. "
            f"Exposure axis {round(det_exp * 100)}% measured · preparedness {round(det_prep * 100)}%. "
            f"Largest assessed lines: {names}. Close via {mining}."
        ),
        "severity": "high" if share < 0.1 else "medium",
        "sub_factors": [t["key"] for t in top],
        "mining_gap": mining,
        "sources": [u for t in top for u in t["sources"][:1]][:3],
        "citation_ids": ["PRA-PPP"],
    }


def _trigger_card(rec: dict, analysis: dict) -> dict | None:
    exp = _subfactors(rec, "exposure")
    tg = next((s for s in exp if s["key"] == "trigger_gap"), None)
    if not tg or (tg["eff"] or 0) < 2:
        return None
    eid = rec["entity_id"]
    ea = analysis.get(eid) or {}
    absent = (ea.get("cover_stack") or {}).get("absent") or []
    manifest = ea.get("risk_manifestation") or []
    detail = ""
    src = tg["sources"][:2]
    if absent:
        detail = f" Absent today: {absent[0].get('cover', '')} — {absent[0].get('note', '')[:120]}."
    elif manifest:
        m0 = manifest[0]
        detail = f" {m0.get('headline', '')}: {m0.get('typical_gap', m0.get('mechanism', ''))[:140]}."
    else:
        detail = " Curtailment and availability losses may not match physical-damage wordings on the binder."
    disclosed = tg["tier"] == "disclosed"
    return {
        "title": "Trigger gap — non-damage losses",
        "body": (
            f"{tg['label']} scores {tg['eff']}/4 ({tg['tier']})."
            + (" Filing-backed product count only — wording detail still thin." if disclosed else "")
            + detail
        ),
        "severity": "high" if (tg["eff"] or 0) >= 3 else "medium",
        "sub_factors": ["trigger_gap"],
        "mining_gap": "trigger_mining",
        "sources": src,
        "citation_ids": ["LMA-BI-GUIDE", "ACAD-BASIS-RISK-EXPECTILES"],
    }


def _aggregation_card(rec: dict) -> dict | None:
    if rec.get("layer") not in (1, 4):
        return None
    exp = _subfactors(rec, "exposure")
    ag = next((s for s in exp if s["key"] == "aggregation_correlation"), None)
    if not ag or (ag["eff"] or 0) < 2:
        return None
    layer_note = (
        "Reinsurer tail sits on correlated UK power / DC cedant stacks — HHI rises when boundaries align."
        if rec.get("layer") == 4
        else "Book stacks on the same constraint boundaries as linked assets; losses move together under curtailment."
    )
    return {
        "title": "Aggregation / correlation concentration",
        "body": (
            f"{ag['label']} at {ag['eff']}/4 ({ag['tier']}). {layer_note} "
            f"{(ag['rationale'] or '')[:160]}"
        ).strip(),
        "severity": "high" if (ag["eff"] or 0) >= 3 else "medium",
        "sub_factors": ["aggregation_correlation"],
        "mining_gap": "register_pull · entity_analysis",
        "sources": ag["sources"][:2],
        "citation_ids": ["ACT-HHI-EIOPA", "LLOYDS-RDS"],
    }


def _non_firm_card(rec: dict, analysis: dict) -> dict | None:
    if rec.get("layer") != 3:
        return None
    exp = _subfactors(rec, "exposure")
    nf = next(
        (s for s in exp if s["key"] in ("non_firm_intensity", "non_firm_compute_exposure")),
        None,
    )
    if not nf:
        return None
    if nf["tier"] == "measured":
        mv = (rec.get("exposure_inputs") or {}).get(nf["key"], {}).get("measured_value")
        if isinstance(mv, dict) and mv.get("share") is not None:
            pct = round(float(mv["share"]) * 100)
            if pct < 15:
                return None
            return {
                "title": "Non-firm grid connection",
                "body": (
                    f"Register pull: {pct}% MW on flexible/non-firm connections "
                    f"({mv.get('mw_nonfirm', '?')}/{mv.get('mw_total', '?')} MW). "
                    "Curtailment probability maps via constraint boundary."
                ),
                "severity": "high" if pct >= 50 else "medium",
                "sub_factors": [nf["key"]],
                "mining_gap": "register_pull",
                "sources": nf["sources"][:2],
                "citation_ids": ["DCUSA-ECR", "NESO-CONSTRAINT-COSTS"],
            }
    if nf["tier"] != "assessed" or (nf["eff"] or 0) < 2:
        return None
    gp = (analysis.get(rec["entity_id"]) or {}).get("grid_posture") or {}
    conn = gp.get("connection") or "unknown"
    return {
        "title": "Non-firm intensity unmeasured",
        "body": (
            f"Grid posture {conn}; register tier still assessed. "
            f"Exposure axis leans on research judgement until ECR/TEC row lands for this site."
        ),
        "severity": "medium",
        "sub_factors": [nf["key"]],
        "mining_gap": "register_pull",
        "sources": (gp.get("sources") or nf["sources"])[:2],
        "citation_ids": ["DCUSA-ECR"],
    }


def _mos_card(rec: dict) -> dict | None:
    s = rec.get("scores") or {}
    quad = s.get("quadrant")
    if quad != "exposed":
        return None
    mos = s.get("margin_of_safety", 0)
    return {
        "title": "Exposure ahead of preparedness",
        "body": (
            f"Margin of safety {mos:+.1f} — exposure {s.get('exposure_0_100')} vs "
            f"preparedness {s.get('preparedness_0_100')}. "
            "Non-firm and trigger gaps weigh before capital and product depth catch up."
        ),
        "severity": "high" if mos < -40 else "medium",
        "sub_factors": [],
        "mining_gap": "capital_mining · trigger_mining",
        "sources": [],
        "citation_ids": [],
    }


def build_for_record(rec: dict, analysis: dict) -> list[dict]:
    det_exp, det_prep = _det_share(rec)
    cards = []
    for fn in (_mos_card, _provisional_card, _trigger_card, _aggregation_card, _non_firm_card):
        if fn is _provisional_card:
            c = fn(rec, det_exp, det_prep)
        elif fn in (_trigger_card, _non_firm_card):
            c = fn(rec, analysis)
        else:
            c = fn(rec)
        if c:
            cards.append(c)
    # dedupe titles
    seen: set[str] = set()
    out = []
    for c in cards:
        if c["title"] in seen:
            continue
        seen.add(c["title"])
        out.append(c)
    return out[:3]


def merge_batches(entities: dict) -> int:
    n = 0
    for path in sorted(glob.glob(os.path.join(BATCH_DIR, "batch*.json"))):
        doc = json.load(open(path))
        patch = doc.get("entities") or doc.get("inputs") or {}
        if not isinstance(patch, dict):
            continue
        for eid, block in patch.items():
            if not isinstance(block, dict):
                continue
            risks = block.get("key_risks") or block.get("risks")
            if risks:
                entities[eid] = {"key_risks": risks, "researched_by": doc.get("researched_by", "risk_analyst")}
                n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()

    records = json.load(open(SCORED))
    analysis = _load_analysis()
    agent_overlay: dict = {}
    if os.path.isfile(OUT):
        agent_overlay = json.load(open(OUT)).get("entities", {})

    if args.merge:
        merge_batches(agent_overlay)

    built = {}
    for rec in records:
        if not rec.get("scores"):
            continue
        eid = rec["entity_id"]
        if eid in agent_overlay and agent_overlay[eid].get("key_risks"):
            built[eid] = agent_overlay[eid]
        else:
            risks = build_for_record(rec, analysis)
            if risks:
                built[eid] = {"key_risks": risks, "source": "build_key_risks.py"}

    doc = {
        "_doc": json.load(open(FRAME)).get("_doc", "") if os.path.isfile(FRAME) else "",
        "version": "0.1",
        "as_of": date.today().isoformat(),
        "entities": built,
    }

    if args.write or args.merge:
        json.dump(doc, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {OUT} ({len(built)} entities with key_risks)")
    else:
        sample = next(iter(built.values()), {})
        print(json.dumps(sample.get("key_risks", [])[:2], indent=2))
        print(f"… {len(built)} entities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
