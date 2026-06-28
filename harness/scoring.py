"""Hybrid latent × deterministic NFRI scoring — industry-anchored, fully reproducible.

Latent ratings come from research agents (qualitative anchors).
Deterministic ratings come from register measurements and disclosed filings.
Fusion weights follow contract/risk_model.json (tier × confidence).

Scoring is NEVER performed by an LLM — only the blend arithmetic runs here.
"""
from __future__ import annotations

import json
import os
import re
import statistics as st
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUBRIC_PATH = os.path.join(ROOT, "contract", "rubric.json")
RISK_MODEL_PATH = os.path.join(ROOT, "contract", "risk_model.json")

CONF_RANK = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}

DETERMINISTIC_TIERS = frozenset({"measured", "derived", "disclosed"})


def load_rubric(path: Optional[str] = None) -> dict:
    with open(path or RUBRIC_PATH) as f:
        return json.load(f)


def load_risk_model(path: Optional[str] = None) -> dict:
    with open(path or RISK_MODEL_PATH) as f:
        return json.load(f)


def _map_threshold(value: float, table: List[dict]) -> int:
    for row in table:
        if value <= row["max"]:
            return row["rating"]
    return 4


def _threshold_table(mapping: dict) -> List[dict]:
    if "thresholds" in mapping:
        return mapping["thresholds"]
    return mapping if isinstance(mapping, list) else []


def _lambda_tier_value(fusion: dict, tier: str) -> float:
    entry = fusion["lambda_by_tier"].get(tier, 0.0)
    if isinstance(entry, dict):
        return float(entry.get("value", 0.0))
    return float(entry)


def _float_measured(mv) -> Optional[float]:
    if mv is None:
        return None
    if isinstance(mv, (int, float)):
        return float(mv)
    if isinstance(mv, dict):
        if "share" in mv:
            return float(mv["share"])
        if "hhi" in mv:
            return float(mv["hhi"])
        if "interaction_index" in mv:
            return float(mv["interaction_index"])
    return None


def active_axis_config(rec: dict, axis_cfg: dict) -> dict:
    """Layer-aware exposure config: L3 uses non_firm_compute_exposure instead of non_firm_intensity."""
    layer = rec.get("layer")
    inputs = rec.get("exposure_inputs") if "non_firm_intensity" in axis_cfg else rec.get("preparedness_inputs")
    if inputs is None:
        return axis_cfg

    active = {}
    for key, cfg in axis_cfg.items():
        inc = cfg.get("include_layers")
        if inc and layer not in inc:
            continue
        if key == "non_firm_compute_exposure":
            comp = inputs.get("non_firm_compute_exposure", {})
            tier = comp.get("evidence_tier")
            if tier not in DETERMINISTIC_TIERS or comp.get("measured_value") is None:
                continue
        if key == "non_firm_intensity" and layer == 3:
            comp = inputs.get("non_firm_compute_exposure", {})
            tier = comp.get("evidence_tier")
            if tier in DETERMINISTIC_TIERS and comp.get("measured_value") is not None:
                continue
        active[key] = cfg

    if not active:
        return axis_cfg
    w_sum = sum(c["weight"] for c in active.values())
    if w_sum <= 0:
        return axis_cfg
    return {k: {**v, "weight": v["weight"] / w_sum} for k, v in active.items()}


def deterministic_rating_from_measured(sub_factor: str, sf: dict, model: dict) -> Optional[int]:
    """Derive a 0–4 rating from measured_value / disclosed fields when formula applies."""
    tier = sf.get("evidence_tier")
    if tier not in DETERMINISTIC_TIERS and tier != "FIXTURE_DEMO":
        return sf.get("deterministic_rating_0_4")

    if sf.get("deterministic_rating_0_4") is not None:
        return int(sf["deterministic_rating_0_4"])

    mappings = model["deterministic_mappings"]

    if sub_factor == "non_firm_intensity":
        val = _float_measured(sf.get("measured_value"))
        if val is not None:
            table_key = ("non_firm_compute_exposure_index"
                         if sf.get("source_type") == "propagated"
                         else "non_firm_intensity_from_share")
            return _map_threshold(val, _threshold_table(mappings[table_key]))

    if sub_factor == "non_firm_compute_exposure":
        val = _float_measured(sf.get("measured_value"))
        if val is not None:
            return _map_threshold(val, _threshold_table(mappings["non_firm_compute_exposure_index"]))

    if sub_factor == "aggregation_correlation" and sf.get("measured_value") is not None:
        val = _float_measured(sf.get("measured_value"))
        if val is not None:
            return _map_threshold(val, _threshold_table(mappings["hhi_to_aggregation_rating"]))

    if sub_factor == "capital_reinsurance":
        cap = mappings["fsr_scr_to_capital_rating"]
        fsr_map = cap.get("fsr_map", cap)
        scr_map = cap.get("scr_thresholds", cap)
        fsr = sf.get("disclosed_fsr") or sf.get("measured_value")
        if isinstance(fsr, str):
            r = (fsr or "").upper().replace("+", "").replace("-", "")
            if r in fsr_map:
                return fsr_map[r]
        scr = sf.get("scr_coverage_pct")
        if scr is not None:
            if scr >= 200:
                return scr_map["scr_coverage_gte_200"]["rating"]
            if scr >= 150:
                return scr_map["scr_coverage_gte_150"]["rating"]
            if scr >= 100:
                return scr_map["scr_coverage_gte_100"]["rating"]
            return scr_map["scr_coverage_lt_100"]["rating"]

    return None


def latent_rating(sf: dict) -> int:
    return int(sf.get("latent_rating_0_4", sf.get("rating_0_4", 0)))


def fusion_lambda(sf: dict, model: dict) -> float:
    fusion = model["fusion"]
    tier = sf.get("evidence_tier") or "assessed"
    if tier == "FIXTURE_DEMO":
        tier = "measured"
    base = _lambda_tier_value(fusion, tier)
    conf_adj = fusion["confidence_adjustment"].get(sf.get("confidence", "low"), -0.10)
    return max(0.0, min(1.0, base + conf_adj))


def fuse_subfactor(sub_factor: str, sf: dict, axis: str, model: Optional[dict] = None) -> dict:
    """Return effective rating plus latent/deterministic decomposition and citation IDs."""
    from citations import sub_factor_citation_ids

    model = model or load_risk_model()
    r_lat = latent_rating(sf)
    r_det = deterministic_rating_from_measured(sub_factor, sf, model)
    lam = fusion_lambda(sf, model) if r_det is not None else 0.0

    if r_det is not None and lam > 0:
        r_eff = round(max(0, min(4, lam * r_det + (1 - lam) * r_lat)), 2)
        mode = "hybrid"
    elif r_det is not None:
        r_eff = float(r_det)
        mode = "deterministic"
    else:
        r_eff = float(r_lat)
        mode = "latent"

    cids = list(dict.fromkeys(
        (sf.get("citation_ids") or []) + sub_factor_citation_ids(sub_factor, axis, model)
    ))
    if mode == "hybrid":
        cids = list(dict.fromkeys(cids + model["fusion"].get("citation_ids", [])))

    return {
        "rating_effective_0_4": r_eff,
        "latent_rating_0_4": r_lat,
        "deterministic_rating_0_4": r_det,
        "fusion_lambda": round(lam, 3),
        "score_mode": mode,
        "citation_ids": cids,
    }


def axis_score(inputs: dict, axis_cfg: dict, axis_name: str,
               model: Optional[dict] = None, rec: Optional[dict] = None) -> Tuple[float, dict]:
    """Weighted 0–100 axis score using fused sub-factor ratings."""
    model = model or load_risk_model()
    if rec is not None and axis_name == "exposure":
        axis_cfg = active_axis_config(rec, axis_cfg)
    total = 0.0
    blend: Dict[str, dict] = {}
    det_weight = 0.0

    for key, cfg in axis_cfg.items():
        sf = inputs.get(key)
        if sf is None:
            raise ValueError(f"missing sub-factor '{key}'")
        fused = fuse_subfactor(key, sf, axis_name, model)
        r_eff = fused["rating_effective_0_4"]
        total += cfg["weight"] * (r_eff / 4.0)
        blend[key] = {**fused, "weight": cfg["weight"]}
        if fused["score_mode"] in ("hybrid", "deterministic"):
            det_weight += cfg["weight"] * fused["fusion_lambda"]

    score = round(total * 100, 1)
    return score, {
        "sub_factors": blend,
        "deterministic_weight_share": round(det_weight, 3),
    }


def quadrant(exp: float, prep: float, cut_exp: float, cut_prep: float) -> str:
    if exp >= cut_exp and prep < cut_prep:
        return "exposed"
    if exp >= cut_exp and prep >= cut_prep:
        return "earning_it"
    if exp < cut_exp and prep >= cut_prep:
        return "whitespace"
    return "sidelined"


def overall_confidence(rec: dict) -> str:
    ranks = []
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for sf in rec[axis].values():
            ranks.append(CONF_RANK.get(sf.get("confidence", "low"), 1))
    avg = sum(ranks) / len(ranks)
    return CONF_NAME.get(round(avg), "low")


def median_cut_lines(records: List[dict], rubric: Optional[dict] = None,
                      model: Optional[dict] = None) -> Tuple[float, float]:
    rubric = rubric or load_rubric()
    exp = [axis_score(r["exposure_inputs"], rubric["exposure"], "exposure", model, r)[0] for r in records]
    prep = [axis_score(r["preparedness_inputs"], rubric["preparedness"], "preparedness", model)[0] for r in records]
    return round(st.median(exp), 1), round(st.median(prep), 1)


def parse_calibration(calibration: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not calibration:
        return None, None
    m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", calibration)
    if not m:
        return None, None
    return float(m.group(1)), float(m.group(2))


def score_record(rec: dict, cut_exp: float, cut_prep: float,
                 rubric: Optional[dict] = None, model: Optional[dict] = None) -> dict:
    rubric = rubric or load_rubric()
    model = model or load_risk_model()

    from citations import model_citation_ids

    exp, exp_blend = axis_score(rec["exposure_inputs"], rubric["exposure"], "exposure", model, rec)
    prep, prep_blend = axis_score(rec["preparedness_inputs"], rubric["preparedness"], "preparedness", model)

    exp_lat, _ = axis_score_latent_only(rec["exposure_inputs"], rubric["exposure"], rec)
    prep_lat, _ = axis_score_latent_only(rec["preparedness_inputs"], rubric["preparedness"])
    exp_det, _ = axis_score_deterministic_only(rec["exposure_inputs"], rubric["exposure"], model, rec)
    prep_det, _ = axis_score_deterministic_only(rec["preparedness_inputs"], rubric["preparedness"], model)

    return {
        "exposure_0_100": exp,
        "preparedness_0_100": prep,
        "exposure_latent_0_100": exp_lat,
        "preparedness_latent_0_100": prep_lat,
        "exposure_deterministic_0_100": exp_det,
        "preparedness_deterministic_0_100": prep_det,
        "margin_of_safety": round(prep - exp, 1),
        "quadrant": quadrant(exp, prep, cut_exp, cut_prep),
        "overall_confidence": overall_confidence(rec),
        "calibration": f"median exp>={cut_exp} prep>={cut_prep}",
        "blend": {
            "exposure_deterministic_weight_share": exp_blend["deterministic_weight_share"],
            "preparedness_deterministic_weight_share": prep_blend["deterministic_weight_share"],
            "exposure_sub_factors": exp_blend["sub_factors"],
            "preparedness_sub_factors": prep_blend["sub_factors"],
        },
        "model_version": model.get("version"),
        "model_spec": model.get("model_spec"),
        "citation_ids": model_citation_ids(model),
    }


def _axis_from_ratings(inputs: dict, axis_cfg: dict, rating_fn, rec: Optional[dict] = None) -> float:
    if rec is not None:
        axis_cfg = active_axis_config(rec, axis_cfg)
    total = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs[key]
        total += cfg["weight"] * (rating_fn(key, sf) / 4.0)
    return round(total * 100, 1)


def axis_score_latent_only(inputs: dict, axis_cfg: dict, rec: Optional[dict] = None) -> Tuple[float, None]:
    return _axis_from_ratings(inputs, axis_cfg, lambda _k, sf: latent_rating(sf), rec), None


def axis_score_deterministic_only(inputs: dict, axis_cfg: dict,
                                  model: Optional[dict] = None,
                                  rec: Optional[dict] = None) -> Tuple[Optional[float], None]:
    model = model or load_risk_model()
    if rec is not None:
        axis_cfg = active_axis_config(rec, axis_cfg)
    has_any = False
    total = 0.0
    weight = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs[key]
        r_det = deterministic_rating_from_measured(key, sf, model)
        if r_det is not None:
            has_any = True
            total += cfg["weight"] * (r_det / 4.0)
            weight += cfg["weight"]
    if not has_any or weight == 0:
        return None, None
    return round((total / weight) * 100, 1), None


def score_all(records: List[dict], cut_exp: Optional[float] = None, cut_prep: Optional[float] = None,
              rubric: Optional[dict] = None, model: Optional[dict] = None) -> Tuple[List[dict], float, float]:
    rubric = rubric or load_rubric()
    model = model or load_risk_model()
    if cut_exp is None or cut_prep is None:
        cut_exp, cut_prep = median_cut_lines(records, rubric, model)
    for rec in records:
        rec["scores"] = score_record(rec, cut_exp, cut_prep, rubric, model)
    return records, cut_exp, cut_prep
