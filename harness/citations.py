"""Citation registry helpers — every NFRI calculation resolves to contract/citations.json."""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CITATIONS_PATH = os.path.join(ROOT, "contract", "citations.json")
RISK_MODEL_PATH = os.path.join(ROOT, "contract", "risk_model.json")


def load_citations(path: Optional[str] = None) -> dict:
    with open(path or CITATIONS_PATH) as f:
        return json.load(f)


def load_risk_model(path: Optional[str] = None) -> dict:
    with open(path or RISK_MODEL_PATH) as f:
        return json.load(f)


def resolve(ids: List[str], registry: Optional[dict] = None) -> List[dict]:
    registry = registry or load_citations()
    refs = registry.get("references", {})
    out = []
    for cid in ids:
        if cid in refs:
            out.append({"id": cid, **refs[cid]})
    return out


def sub_factor_citation_ids(sub_factor: str, axis: str, model: Optional[dict] = None) -> List[str]:
    model = model or load_risk_model()
    sf = model["axis_formulas"][axis]["sub_factors"].get(sub_factor, {})
    return sf.get("citation_ids", [])


def model_citation_ids(model: Optional[dict] = None) -> List[str]:
    model = model or load_risk_model()
    ids = set(model.get("fusion", {}).get("citation_ids", []))
    for axis in ("exposure", "preparedness"):
        ids.update(model["axis_formulas"][axis].get("citation_ids", []))
    ids.update(model["axis_formulas"]["margin_of_safety"].get("citation_ids", []))
    return sorted(ids)
