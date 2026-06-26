"""Deterministic NFRI scoring — shared by score, optimize, and ingest pipelines."""
from typing import Optional, Tuple, List, Dict, Any
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUBRIC_PATH = os.path.join(ROOT, "contract", "rubric.json")

CONF_RANK = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}


def load_rubric(path: Optional[str] = None) -> dict:
    return json.load(open(path or RUBRIC_PATH))


def axis_score(inputs: dict, axis_cfg: dict) -> float:
    total = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs.get(key)
        if sf is None:
            raise ValueError(f"missing sub-factor '{key}'")
        total += cfg["weight"] * (sf["rating_0_4"] / 4.0)
    return round(total * 100, 1)


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


def median_cut_lines(records: list[dict], rubric: dict | None = None) -> tuple[float, float]:
    rubric = rubric or load_rubric()
    exp = [axis_score(r["exposure_inputs"], rubric["exposure"]) for r in records]
    prep = [axis_score(r["preparedness_inputs"], rubric["preparedness"]) for r in records]
    return round(st.median(exp), 1), round(st.median(prep), 1)


def parse_calibration(calibration: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not calibration:
        return None, None
    import re

    m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", calibration)
    if not m:
        return None, None
    return float(m.group(1)), float(m.group(2))


def score_record(rec: dict, cut_exp: float, cut_prep: float, rubric: Optional[dict] = None) -> dict:
    rubric = rubric or load_rubric()
    exp = axis_score(rec["exposure_inputs"], rubric["exposure"])
    prep = axis_score(rec["preparedness_inputs"], rubric["preparedness"])
    return {
        "exposure_0_100": exp,
        "preparedness_0_100": prep,
        "margin_of_safety": round(prep - exp, 1),
        "quadrant": quadrant(exp, prep, cut_exp, cut_prep),
        "overall_confidence": overall_confidence(rec),
        "calibration": f"median exp>={cut_exp} prep>={cut_prep}",
    }


def score_all(records: List[dict], cut_exp: Optional[float] = None, cut_prep: Optional[float] = None,
              rubric: Optional[dict] = None) -> Tuple[List[dict], float, float]:
    rubric = rubric or load_rubric()
    if cut_exp is None or cut_prep is None:
        cut_exp, cut_prep = median_cut_lines(records, rubric)
    for rec in records:
        rec["scores"] = score_record(rec, cut_exp, cut_prep, rubric)
    return records, cut_exp, cut_prep
