"""Hybrid latent × deterministic CMUI scoring — compute markets underwriting index.

Latent ratings come from research agents (qualitative anchors).
Deterministic ratings come from market indices, filings, and NFRI links.
Fusion weights follow contract/compute_risk_model.json.

Scoring is NEVER performed by an LLM — only blend arithmetic runs here.
"""
from __future__ import annotations

import json
import os
import re
import statistics as st
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPUTE_MODEL_PATH = os.path.join(ROOT, "contract", "compute_risk_model.json")
COMPUTE_RUBRIC_PATH = os.path.join(ROOT, "contract", "compute_rubric.json")
COMPUTE_CITATIONS_PATH = os.path.join(ROOT, "contract", "compute_citations.json")
NFRI_MODEL_PATH = os.path.join(ROOT, "contract", "risk_model.json")

CONF_RANK = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}

DETERMINISTIC_TIERS = frozenset({"measured", "derived", "disclosed"})
L1_L2_L4 = frozenset({1, 2, 4})


def load_compute_model(path: Optional[str] = None) -> dict:
    with open(path or COMPUTE_MODEL_PATH) as f:
        return json.load(f)


def load_nfri_model(path: Optional[str] = None) -> dict:
    with open(path or NFRI_MODEL_PATH) as f:
        return json.load(f)


def load_compute_citations(path: Optional[str] = None) -> dict:
    with open(path or COMPUTE_CITATIONS_PATH) as f:
        return json.load(f)


def load_compute_rubric(path: Optional[str] = None) -> dict:
    rubric_path = path or COMPUTE_RUBRIC_PATH
    if os.path.exists(rubric_path):
        with open(rubric_path) as f:
            return json.load(f)
    return rubric_from_model()


def rubric_from_model(model: Optional[dict] = None) -> dict:
    """Build weight-only rubric axes from compute_risk_model.json (fallback)."""
    model = model or load_compute_model()
    rubric: Dict[str, dict] = {"exposure": {}, "preparedness": {}}
    for axis in ("exposure", "preparedness"):
        for key, cfg in model["axis_formulas"][axis]["sub_factors"].items():
            rubric[axis][key] = {
                "weight": cfg["weight"],
                "citation_ids": cfg.get("citation_ids", []),
            }
            if "include_layers" in cfg:
                rubric[axis][key]["include_layers"] = cfg["include_layers"]
    return rubric


def sub_factor_citation_ids(sub_factor: str, axis: str, model: Optional[dict] = None) -> List[str]:
    model = model or load_compute_model()
    sf = model["axis_formulas"][axis]["sub_factors"].get(sub_factor, {})
    return sf.get("citation_ids", [])


def model_citation_ids(model: Optional[dict] = None) -> List[str]:
    model = model or load_compute_model()
    ids = set(model.get("fusion", {}).get("citation_ids", []))
    for axis in ("exposure", "preparedness"):
        ids.update(model["axis_formulas"][axis].get("citation_ids", []))
    ids.update(model["axis_formulas"]["margin_of_safety"].get("citation_ids", []))
    return sorted(ids)


def _map_threshold_max(value: float, table: List[dict]) -> int:
    for row in table:
        if value <= row["max"]:
            return row["rating"]
    return 4


def _map_threshold_min(value: float, table: List[dict]) -> int:
    for row in table:
        if value >= row.get("min", 0):
            return row["rating"]
    return 0


def _threshold_table(mapping: dict) -> List[dict]:
    if "thresholds" in mapping:
        return mapping["thresholds"]
    return mapping if isinstance(mapping, list) else []


def _lambda_tier_value(fusion: dict, tier: str) -> float:
    entry = fusion["lambda_by_tier"].get(tier, 0.0)
    if isinstance(entry, dict):
        return float(entry.get("value", 0.0))
    return float(entry)


def _float_val(mv: Any) -> Optional[float]:
    if mv is None:
        return None
    if isinstance(mv, (int, float)):
        return float(mv)
    if isinstance(mv, dict):
        for key in (
            "value", "beta_t", "g_basis", "v", "s_ow", "m_tenor",
            "interaction_index", "n_norm", "c_book", "h", "share",
        ):
            if key in mv:
                return float(mv[key])
    return None


def _dict_measured(sf: dict) -> dict:
    mv = sf.get("measured_value")
    return mv if isinstance(mv, dict) else {}


def _capital_rating(sf: dict, cap_mapping: dict) -> Optional[int]:
    fsr_map = cap_mapping.get("fsr_map", {})
    scr_map = cap_mapping.get("scr_thresholds", {})
    fsr = sf.get("disclosed_fsr") or sf.get("measured_value")
    base: Optional[int] = None
    if isinstance(fsr, str):
        r = (fsr or "").upper().replace("+", "").replace("-", "")
        if r in fsr_map:
            base = fsr_map[r]
    scr = sf.get("scr_coverage_pct")
    if scr is not None:
        if scr >= 200:
            base = scr_map["scr_coverage_gte_200"]["rating"]
        elif scr >= 150:
            base = scr_map["scr_coverage_gte_150"]["rating"]
        elif scr >= 100:
            base = scr_map["scr_coverage_gte_100"]["rating"]
        else:
            base = scr_map["scr_coverage_lt_100"]["rating"]
    if base is None:
        return sf.get("deterministic_rating_0_4")
    if sf.get("gpu_abs_disclosed"):
        bump = cap_mapping.get("gpu_abs_bump", 1)
        cap = cap_mapping.get("gpu_abs_bump_cap", 4)
        return min(cap, base + bump)
    return base


def _data_monitoring_rating(sf: dict, mapping: dict) -> Optional[int]:
    d = _dict_measured(sf)
    if not d and sf.get("deterministic_rating_0_4") is not None:
        return int(sf["deterministic_rating_0_4"])
    n_idx = int(d.get("index_count", d.get("min_indices", 0)))
    has_util = bool(d.get("has_utilization", False))
    spot_scrape = bool(d.get("spot_scraping", False))
    for tier in mapping.get("tiers", []):
        if tier.get("has_v0_model"):
            continue
        need_idx = tier.get("min_indices", 0)
        if n_idx < need_idx:
            continue
        if "has_utilization" in tier and tier["has_utilization"] != has_util:
            continue
        if tier.get("spot_scraping") is not None and tier["spot_scraping"] != spot_scrape:
            continue
        return tier["rating"]
    return 0


def _pricing_modelling_rating(sf: dict, mapping: dict) -> Optional[int]:
    d = _dict_measured(sf)
    if not d and sf.get("deterministic_rating_0_4") is not None:
        return int(sf["deterministic_rating_0_4"])
    for tier in mapping.get("tiers", []):
        if tier.get("has_v0_model") and d.get("has_v0_model"):
            return tier["rating"]
        if tier.get("has_forward_and_eloss") and d.get("has_forward_and_eloss"):
            return tier["rating"]
        if tier.get("has_spot_var_only") and d.get("has_spot_var_only"):
            return tier["rating"]
        if tier.get("has_vendor_unverified") and d.get("has_vendor_unverified"):
            return tier["rating"]
        if tier.get("rating") == 0 and not any(
            tier.get(k) for k in (
                "has_v0_model", "has_forward_and_eloss",
                "has_spot_var_only", "has_vendor_unverified",
            )
        ):
            return 0
    return None


def _capacity_at_risk_value(rec: dict, sf: dict, model: dict) -> Optional[float]:
    layer = rec.get("layer")
    d = _dict_measured(sf)
    if layer in L1_L2_L4:
        if "c_book" in d:
            return float(d["c_book"])
        if "gwp_compute_share" in d:
            return float(d["gwp_compute_share"])
        return _float_val(sf.get("measured_value"))
    hours_annual = d.get("hours_annual")
    hours_hedged = d.get("hours_hedged", 0)
    if hours_annual and float(hours_annual) > 0:
        unhedged = float(hours_annual) * (1.0 - float(hours_hedged) / float(hours_annual))
        n_ref = model["deterministic_mappings"]["capacity_at_risk_reference_hours"]["value"]
        return min(1.0, unhedged / n_ref)
    return _float_val(sf.get("measured_value"))


def _tightness_beta(sf: dict) -> Optional[float]:
    d = _dict_measured(sf)
    if "beta_t" in d:
        return float(d["beta_t"])
    sigma = d.get("tightness_sigma_30")
    f_short = d.get("f_short")
    if sigma is not None and f_short is not None:
        return float(sigma) * float(f_short)
    return _float_val(sf.get("measured_value"))


def _price_volatility_v(sf: dict) -> Optional[float]:
    d = _dict_measured(sf)
    if "v" in d:
        return float(d["v"])
    p_unhedged = d.get("p_unhedged")
    cv = d.get("cv_90")
    if p_unhedged is not None and cv is not None:
        return float(p_unhedged) * float(cv)
    return _float_val(sf.get("measured_value"))


def _depreciation_m_tenor(sf: dict, mapping: dict) -> Optional[float]:
    d = _dict_measured(sf)
    if "m_tenor" in d:
        return float(d["m_tenor"])
    if "delta_t_years" in d:
        return max(0.0, float(d["delta_t_years"]) / 6.0)
    f0 = d.get("forward_spot_ratio_f12m_f0")
    theta = mapping.get("obsolescence_ratio_threshold", 0.50)
    t_account = d.get("t_account_years", mapping.get("accounting_life_years_default", 6))
    if f0 is not None and float(f0) < theta:
        # Implied shorter economic life when 12m forward collapses vs spot
        implied_shortfall = (1.0 - float(f0)) * t_account
        return max(0.0, implied_shortfall / 6.0)
    return _float_val(sf.get("measured_value"))


def deterministic_rating_from_measured(
    sub_factor: str,
    sf: dict,
    model: dict,
    rec: Optional[dict] = None,
) -> Optional[int]:
    tier = sf.get("evidence_tier")
    if tier not in DETERMINISTIC_TIERS and tier != "FIXTURE_DEMO":
        return sf.get("deterministic_rating_0_4")

    if sf.get("deterministic_rating_0_4") is not None:
        return int(sf["deterministic_rating_0_4"])

    mappings = model["deterministic_mappings"]

    if sub_factor == "capacity_at_risk" and rec is not None:
        val = _capacity_at_risk_value(rec, sf, model)
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["capacity_at_risk_thresholds"]))

    if sub_factor == "tightness_sensitivity":
        val = _tightness_beta(sf)
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["tightness_sensitivity_thresholds"]))

    if sub_factor == "price_basis_gap":
        val = _float_val(sf.get("measured_value"))
        if val is None:
            d = _dict_measured(sf)
            rc, ri = d.get("r_contract"), d.get("r_index")
            if rc and ri and float(rc) > 0 and float(ri) > 0:
                import math
                val = abs(math.log(float(rc) / float(ri)))
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["price_basis_gap_thresholds"]))

    if sub_factor == "price_volatility_exposure":
        val = _price_volatility_v(sf)
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["price_volatility_exposure_thresholds"]))

    if sub_factor == "shock_calendar_exposure":
        val = _float_val(sf.get("measured_value"))
        if val is None:
            d = _dict_measured(sf)
            val = (
                float(d.get("w_finetune", 0))
                + float(d.get("w_post_train", 0))
                + (1.0 if d.get("open_weights_in_prod") else 0.0)
            )
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["shock_calendar_exposure_thresholds"]))

    if sub_factor == "depreciation_tenor_mismatch":
        val = _depreciation_m_tenor(sf, mappings["depreciation_tenor_mismatch_thresholds"])
        if val is not None:
            return _map_threshold_max(val, _threshold_table(mappings["depreciation_tenor_mismatch_thresholds"]))

    if sub_factor == "grid_compute_coupling":
        val = _float_val(sf.get("measured_value"))
        if val is None:
            d = _dict_measured(sf)
            val = d.get("interaction_index")
        if val is not None:
            return _map_threshold_max(float(val), _threshold_table(mappings["grid_compute_coupling_index"]))

    if sub_factor == "index_hedge_coverage":
        d = _dict_measured(sf)
        h = d.get("h")
        if h is None:
            ha, hh = d.get("hours_annual"), d.get("hours_hedged")
            if ha and float(ha) > 0:
                h = float(hh or 0) / float(ha)
        if h is None:
            h = _float_val(sf.get("measured_value"))
        if h is not None:
            return _map_threshold_min(float(h), _threshold_table(mappings["index_hedge_coverage_thresholds"]))

    if sub_factor == "data_monitoring":
        r = _data_monitoring_rating(sf, mappings["data_monitoring_tier_map"])
        if r is not None:
            return r

    if sub_factor == "product_fit":
        d = _dict_measured(sf)
        n = d.get("product_count", sf.get("measured_value"))
        if n is not None:
            return min(4, int(n))

    if sub_factor == "pricing_modelling":
        r = _pricing_modelling_rating(sf, mappings["pricing_modelling_tier_map"])
        if r is not None:
            return r

    if sub_factor == "capital_reinsurance":
        return _capital_rating(sf, mappings["fsr_scr_to_capital_rating"])

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


def fuse_subfactor(
    sub_factor: str,
    sf: dict,
    axis: str,
    model: Optional[dict] = None,
    rec: Optional[dict] = None,
) -> dict:
    model = model or load_compute_model()
    r_lat = latent_rating(sf)
    r_det = deterministic_rating_from_measured(sub_factor, sf, model, rec)
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


def axis_score(
    inputs: dict,
    axis_cfg: dict,
    axis_name: str,
    model: Optional[dict] = None,
    rec: Optional[dict] = None,
) -> Tuple[float, dict]:
    model = model or load_compute_model()
    total = 0.0
    blend: Dict[str, dict] = {}
    det_weight = 0.0

    for key, cfg in axis_cfg.items():
        sf = inputs.get(key)
        if sf is None:
            raise ValueError(f"missing sub-factor '{key}' on axis '{axis_name}'")
        fused = fuse_subfactor(key, sf, axis_name, model, rec)
        r_eff = fused["rating_effective_0_4"]
        total += cfg["weight"] * (r_eff / 4.0)
        blend[key] = {**fused, "weight": cfg["weight"]}
        if fused["score_mode"] in ("hybrid", "deterministic"):
            det_weight += cfg["weight"] * fused["fusion_lambda"]

    return round(total * 100, 1), {
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
    avg = sum(ranks) / len(ranks) if ranks else 1
    return CONF_NAME.get(round(avg), "low")


def customer_hhi(rec: dict) -> Optional[float]:
    agg = rec.get("aggregation") or {}
    if "customer_hhi" in agg:
        return float(agg["customer_hhi"])
    rev = agg.get("customer_revenue_shares")
    if isinstance(rev, list) and rev:
        return sum(float(x) ** 2 for x in rev)
    return None


def median_cut_lines(
    records: List[dict],
    rubric: Optional[dict] = None,
    model: Optional[dict] = None,
) -> Tuple[float, float]:
    rubric = rubric or load_compute_rubric()
    model = model or load_compute_model()
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


def _axis_from_ratings(
    inputs: dict,
    axis_cfg: dict,
    rating_fn,
    rec: Optional[dict] = None,
) -> float:
    total = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs[key]
        total += cfg["weight"] * (rating_fn(key, sf) / 4.0)
    return round(total * 100, 1)


def axis_score_latent_only(
    inputs: dict,
    axis_cfg: dict,
    rec: Optional[dict] = None,
) -> Tuple[float, None]:
    return _axis_from_ratings(inputs, axis_cfg, lambda _k, sf: latent_rating(sf), rec), None


def axis_score_deterministic_only(
    inputs: dict,
    axis_cfg: dict,
    model: Optional[dict] = None,
    rec: Optional[dict] = None,
) -> Tuple[Optional[float], None]:
    model = model or load_compute_model()
    has_any = False
    total = 0.0
    weight = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs[key]
        r_det = deterministic_rating_from_measured(key, sf, model, rec)
        if r_det is not None:
            has_any = True
            total += cfg["weight"] * (r_det / 4.0)
            weight += cfg["weight"]
    if not has_any or weight == 0:
        return None, None
    return round((total / weight) * 100, 1), None


def propagate_nfri_grid_coupling(rec: dict, nfri_scores: Optional[dict] = None) -> None:
    """Fill grid_compute_coupling from NFRI linked asset scores when present."""
    link = rec.get("nfri_link") or {}
    asset_id = link.get("asset_id")
    if not asset_id or nfri_scores is None:
        return
    asset = nfri_scores.get(asset_id)
    if not asset:
        return
    idx = asset.get("interaction_index")
    if idx is None:
        return
    sf = rec.setdefault("exposure_inputs", {}).setdefault("grid_compute_coupling", {})
    sf.setdefault("measured_value", {"interaction_index": idx})
    sf.setdefault("evidence_tier", "derived")
    sf.setdefault("confidence", "high")
    sf.setdefault("citation_ids", ["CMUI-NFRI-BRIDGE"])


def score_record(
    rec: dict,
    cut_exp: float,
    cut_prep: float,
    rubric: Optional[dict] = None,
    model: Optional[dict] = None,
) -> dict:
    rubric = rubric or load_compute_rubric()
    model = model or load_compute_model()

    exp, exp_blend = axis_score(rec["exposure_inputs"], rubric["exposure"], "exposure", model, rec)
    prep, prep_blend = axis_score(rec["preparedness_inputs"], rubric["preparedness"], "preparedness", model)

    exp_lat, _ = axis_score_latent_only(rec["exposure_inputs"], rubric["exposure"], rec)
    prep_lat, _ = axis_score_latent_only(rec["preparedness_inputs"], rubric["preparedness"])
    exp_det, _ = axis_score_deterministic_only(rec["exposure_inputs"], rubric["exposure"], model, rec)
    prep_det, _ = axis_score_deterministic_only(rec["preparedness_inputs"], rubric["preparedness"], model)

    hhi = customer_hhi(rec)
    agg_out: Dict[str, Any] = {}
    if hhi is not None:
        agg_out["customer_hhi"] = round(hhi, 4)
        thresh = model["aggregation"]["customer_hhi"]["stress_uplift_threshold"]
        if hhi > thresh:
            agg_out["concentration_flag"] = "whale_risk"

    out: Dict[str, Any] = {
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
    if agg_out:
        out["aggregation"] = agg_out
    if rec.get("nfri_link"):
        out["nfri_link"] = rec["nfri_link"]
    return out


def score_all(
    records: List[dict],
    cut_exp: Optional[float] = None,
    cut_prep: Optional[float] = None,
    rubric: Optional[dict] = None,
    model: Optional[dict] = None,
    nfri_scores: Optional[dict] = None,
) -> Tuple[List[dict], float, float]:
    rubric = rubric or load_compute_rubric()
    model = model or load_compute_model()
    for rec in records:
        propagate_nfri_grid_coupling(rec, nfri_scores)
    if cut_exp is None or cut_prep is None:
        cut_exp, cut_prep = median_cut_lines(records, rubric, model)
    for rec in records:
        rec["scores"] = score_record(rec, cut_exp, cut_prep, rubric, model)
    return records, cut_exp, cut_prep


def _demo_records() -> List[dict]:
    """Minimal fixture for CLI smoke test."""
    return [
        {
            "id": "demo-neocloud",
            "name": "Demo Neocloud",
            "layer": 3,
            "stratum": "S2",
            "exposure_inputs": {
                "capacity_at_risk": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                    "measured_value": {"hours_annual": 5_000_000, "hours_hedged": 1_000_000},
                },
                "tightness_sensitivity": {
                    "evidence_tier": "derived",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                    "measured_value": {"beta_t": 0.52},
                },
                "price_basis_gap": {
                    "evidence_tier": "measured",
                    "confidence": "high",
                    "latent_rating_0_4": 2,
                    "measured_value": {"g_basis": 0.22},
                },
                "price_volatility_exposure": {
                    "evidence_tier": "derived",
                    "confidence": "medium",
                    "latent_rating_0_4": 3,
                    "measured_value": {"v": 0.28},
                },
                "shock_calendar_exposure": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 3,
                },
                "depreciation_tenor_mismatch": {
                    "evidence_tier": "derived",
                    "confidence": "medium",
                    "latent_rating_0_4": 2,
                    "measured_value": {"forward_spot_ratio_f12m_f0": 0.72},
                },
                "grid_compute_coupling": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 1,
                },
            },
            "preparedness_inputs": {
                "index_hedge_coverage": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 1,
                    "measured_value": {"h": 0.20},
                },
                "data_monitoring": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 2,
                    "measured_value": {"index_count": 1, "has_utilization": True},
                },
                "product_fit": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 1,
                },
                "pricing_modelling": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 1,
                },
                "underwriting_expertise": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 0,
                },
                "capital_reinsurance": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 1,
                },
            },
        },
        {
            "id": "demo-mga",
            "name": "Demo Compute MGA",
            "layer": 2,
            "exposure_inputs": {
                "capacity_at_risk": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 2,
                    "measured_value": {"c_book": 0.45},
                },
                "tightness_sensitivity": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 2,
                },
                "price_basis_gap": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 1,
                },
                "price_volatility_exposure": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 2,
                },
                "shock_calendar_exposure": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 2,
                },
                "depreciation_tenor_mismatch": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 1,
                },
                "grid_compute_coupling": {
                    "evidence_tier": "assessed",
                    "confidence": "low",
                    "latent_rating_0_4": 0,
                },
            },
            "preparedness_inputs": {
                "index_hedge_coverage": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 1,
                },
                "data_monitoring": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                    "measured_value": {"index_count": 2, "has_utilization": False},
                },
                "product_fit": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                    "measured_value": {"product_count": 3},
                },
                "pricing_modelling": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                    "measured_value": {"has_forward_and_eloss": True},
                },
                "underwriting_expertise": {
                    "evidence_tier": "disclosed",
                    "confidence": "high",
                    "latent_rating_0_4": 3,
                },
                "capital_reinsurance": {
                    "evidence_tier": "assessed",
                    "confidence": "medium",
                    "latent_rating_0_4": 2,
                },
            },
        },
    ]


def main() -> None:
    records = _demo_records()
    scored, cut_e, cut_p = score_all(records)
    print(f"CMUI demo — median cuts: exposure>={cut_e}, preparedness>={cut_p}")
    for rec in scored:
        s = rec["scores"]
        print(
            f"  {rec['id']}: E={s['exposure_0_100']} P={s['preparedness_0_100']} "
            f"MoS={s['margin_of_safety']} quad={s['quadrant']}"
        )


if __name__ == "__main__":
    main()
