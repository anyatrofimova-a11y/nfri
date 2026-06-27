#!/usr/bin/env python3
"""Generate profile_editor synthesis from scored records (deterministic fallback).

Reads sub-factor rationales + scores; writes executive_summary and axis_rationale
without inventing facts beyond what's in records.scored.json.

Usage:
  python3 harness/generate_synthesis.py --batch batch1
  python3 harness/generate_synthesis.py --all
"
from __future__ import annotations

import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.scored.json")
MANIFEST = os.path.join(ROOT, "data", "synthesis", "manifest.json")
OUT_DIR = os.path.join(ROOT, "data", "synthesis")

SF_LABEL = {
    "book_concentration": "Book concentration",
    "non_firm_intensity": "Non-firm intensity",
    "aggregation_correlation": "Aggregation",
    "trigger_gap": "Trigger gap",
    "tenor_mismatch": "Tenor mismatch",
    "data_monitoring": "Data & monitoring",
    "product_fit": "Product fit",
    "underwriting_expertise": "Underwriting expertise",
    "capital_reinsurance": "Capital & reinsurance",
    "pricing_modelling": "Pricing & modelling",
}


def _first_sentence(text: str, max_len: int = 220) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return
    parts = re.split(r"(?<=[.!?])\s+", text)
    s = parts[0]
    if len(s) < 80 and len(parts) > 1:
        s = parts[0] + " " + parts[1]
    return s[:max_len].rstrip(" ,;") + ("…" if len(text) > max_len else "")


def _top_sf(rec: dict, axis: str, by: str = "eff") -> tuple[str, dict]:
    inputs = rec.get(f"{axis}_inputs") or {}
    blend = ((rec.get("scores") or {}).get("blend") or {}).get(f"{axis}_sub_factors", {})
    best_k, best_v, best_score = "", {}, -1
    for k, sf in inputs.items():
        bl = blend.get(k, {})
        score = bl.get("rating_effective_0_4", sf.get("rating_0_4", 0))
        tier = sf.get("evidence_tier") or "assessed"
        tier_bonus = {"measured": 0.5, "disclosed": 0.4, "derived": 0.3}.get(tier, 0)
        rank = score + tier_bonus
        if rank > best_score:
            best_score, best_k, best_v = rank, k, sf
    return best_k, best_v


def _measured_pct(rec: dict) -> int:
    s = rec.get("scores") or {}
    b = s.get("blend") or {}
    return round(((b.get("exposure_deterministic_weight_share", 0) + b.get("preparedness_deterministic_weight_share", 0)) / 2) * 100)


def synthesize(rec: dict) -> dict:
    s = rec.get("scores") or {}
    name = rec.get("name", rec["entity_id"])
    layer = rec.get("layer", 0)
    quad = s.get("quadrant", "")
    mos = s.get("margin_of_safety", 0)
    exp = s.get("exposure_0_100", 0)
    prep = s.get("preparedness_0_100", 0)
    meas = _measured_pct(rec)

    exp_k, exp_sf = _top_sf(rec, "exposure")
    prep_k, prep_sf = _top_sf(rec, "preparedness")
    exp_label = SF_LABEL.get(exp_k, exp_k)
    prep_label = SF_LABEL.get(prep_k, prep_k)

    quad_phrase = {
        "whitespace": "sits in whitespace — low book exposure but relatively strong preparedness",
        "earning_it": "sits in earning it — material exposure paired with credible preparedness",
        "exposed": "sits in exposed — meaningful exposure with preparedness lagging the cut",
        "sidelined": "sits sidelined — limited energy/non-firm book and thin preparedness on this slice",
    }.get(quad, f"maps to quadrant {quad}")

    prov = f" Index slice is heavily assessed ({meas}% measured share on this entity) — direction is defensible, magnitudes may move as registers populate." if meas < 35 else
    if layer == 3:
        al = rec.get("asset_link") or {}
        gate = al.get("gate_status") or "unknown gate"
        thesis = (
            f"{name} is a Layer-3 asset in the current universe with Margin of Safety {mos:+.1f} "
            f"(exposure {exp}, preparedness {prep}). Connection posture ({gate}) and curtailment exposure "
            f"drive the non-firm intensity score. {quad_phrase.capitalize()}."
        )
    elif layer == 4:
        thesis = (
            f"{name} is scored as tail capacity (L4) with MoS {mos:+.1f}. Reinsurance aggregation and "
            f"parametric preparedness are the main levers on this slice. {quad_phrase.capitalize()}."
        )
    elif layer == 2:
        thesis = (
            f"{name} is an intermediary (L2) in the placement stack with MoS {mos:+.1f}. Product and "
            f"monitoring fit dominate preparedness; exposure reflects how much non-firm risk is bound through "
            f"this channel. {quad_phrase.capitalize()}."
        )
    else:
        thesis = (
            f"{name} is a Layer-1 carrier in the scored universe with MoS {mos:+.1f} "
            f"(exposure {exp}, preparedness {prep}). {quad_phrase.capitalize()}. "
            f"The book mix and trigger structure on renewables, power and data-centre risks define the exposure shape."
        )
    thesis += prov

    exp_rat = _first_sentence(exp_sf.get("rationale", ""))
    prep_rat = _first_sentence(prep_sf.get("rationale", ""))
    tier_exp = exp_sf.get("evidence_tier") or "assessed"
    tier_prep = prep_sf.get("evidence_tier") or "assessed"

    axis_exp = (
        f"Exposure at {exp} reflects the weighted E1–E5 profile. The strongest line item is "
        f"{exp_label} (effective rating {exp_sf.get('rating_0_4', '—')}, tier {tier_exp}): {exp_rat}"
    )
    axis_prep = (
        f"Preparedness at {prep} is anchored on {prep_label} (effective rating {prep_sf.get('rating_0_4', '—')}, "
        f"tier {tier_prep}): {prep_rat}"
    )

    return {
        "executive_summary": thesis,
        "axis_rationale": {"exposure": axis_exp, "preparedness": axis_prep},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", action="append", help="batch key from manifest, e.g. batch1")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    manifest = json.load(open(MANIFEST))
    batches = manifest.get("batches", {})
    if args.all:
        batch_keys = sorted(batches.keys())
    elif args.batch:
        batch_keys = args.batch
    else:
        print("Specify --batch or --all", file=__import__("sys").stderr)
        return 1

    by_id = {r["entity_id"]: r for r in json.load(open(RECORDS)) if r.get("scores")}
    os.makedirs(OUT_DIR, exist_ok=True)

    for bk in batch_keys:
        ids = batches.get(bk, [])
        entities = {}
        for eid in ids:
            rec = by_id.get(eid)
            if not rec:
                continue
            entities[eid] = synthesize(rec)
        out = {"pass": "synthesis", "batch": bk, "entities": entities}
        path = os.path.join(OUT_DIR, f"{bk}.json")
        json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {path} ({len(entities)} entities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
