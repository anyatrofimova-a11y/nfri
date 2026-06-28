#!/usr/bin/env python3
"""Derived L3 interaction: non_firm_compute_exposure = load_norm × share × curtailment_prob.

  python3 harness/measure_interaction.py --live
  python3 harness/measure_interaction.py --fixture
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

from measure_utils import ROOT, load_records, save_records

TODAY = date.today().isoformat()
LOAD_CAP_MW = 500.0
CITATION_IDS = [
    "ACAD-CCM-NF-LOAD",
    "NESO-CONSTRAINT-COSTS",
    "INDUSTRY-DC-COMPUTE-DEMAND",
    "NESO-TEC",
    "DCUSA-ECR",
]


def parse_non_firm(nf: dict) -> tuple[float, float] | None:
    mv = nf.get("measured_value")
    if mv is None:
        return None
    if isinstance(mv, dict):
        share = mv.get("share")
        mw = mv.get("mw_total") or mv.get("import_mw")
        if share is not None and mw is not None:
            return float(share), float(mw)
    if isinstance(mv, (int, float)):
        rat = nf.get("rationale") or ""
        import re
        m = re.search(r"=\s*[\d.]+/([\d.]+)\s*MW", rat)
        mw = float(m.group(1)) if m else None
        if mw is not None:
            return float(mv), mw
    return None


def load_boundary_maps(mode: str) -> tuple[dict, dict, str]:
    if mode == "fixture":
        fx = json.load(open(os.path.join(ROOT, "harness", "fixtures", "interaction_fixture.json")))
        return fx["boundaries"], fx["assets"], fx["source_note"]
    boundaries = json.load(open(os.path.join(ROOT, "contract", "constraint_boundary.json")))["boundaries"]
    assets = json.load(open(os.path.join(ROOT, "contract", "asset_boundary_map.json")))["assets"]
    src = "contract/constraint_boundary.json + contract/asset_boundary_map.json"
    return boundaries, assets, src


def compute_interaction(import_mw: float, share: float, curtailment_prob: float) -> dict:
    load_norm = min(1.0, max(0.0, import_mw) / LOAD_CAP_MW)
    share = max(0.0, min(1.0, share))
    p = max(0.0, min(1.0, curtailment_prob))
    index = round(load_norm * share * p, 4)
    return {
        "interaction_index": index,
        "load_norm": round(load_norm, 4),
        "non_firm_share": round(share, 4),
        "curtailment_prob": round(p, 4),
        "import_mw": round(import_mw, 1),
    }


def index_to_rating(index: float) -> int:
    thresholds = [
        (0.01, 0),
        (0.05, 1),
        (0.15, 2),
        (0.35, 3),
        (1.01, 4),
    ]
    for mx, rating in thresholds:
        if index <= mx:
            return rating
    return 4


def build_subfactor(
    parts: dict,
    boundary_key: str,
    boundary_label: str,
    source: str,
    mode: str,
    curtailment_source: str,
) -> dict:
    idx = parts["interaction_index"]
    rating = index_to_rating(idx)
    return {
        "rating_0_4": rating,
        "latent_rating_0_4": rating,
        "deterministic_rating_0_4": rating,
        "measured_value": parts,
        "unit": "interaction_index (0-1)",
        "as_of": TODAY,
        "evidence_tier": "derived" if mode == "live" else "FIXTURE_DEMO",
        "source_type": "register_derived",
        "rationale": (
            f"I = load_norm×s_NF×p_curtail = {parts['load_norm']:.3f}×{parts['non_firm_share']:.3f}"
            f"×{parts['curtailment_prob']:.3f} = {idx:.4f} → rating {rating} "
            f"({boundary_label}, {parts['import_mw']} MW import)."
        ),
        "sources": [
            "https://northernpowergrid.opendatasoft.com/explore/dataset/ecr_manual_combine_test/",
            "https://www.neso.energy/industry-information/constraint-costs",
        ],
        "confidence": "high" if parts["import_mw"] >= 10 and parts["non_firm_share"] > 0 else "medium",
        "citation_ids": CITATION_IDS,
        "boundary_key": boundary_key,
        "inputs_from": source,
        "curtailment_source": curtailment_source,
    }


def main() -> int:
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs, base_label, out_path = load_records(mode)
    boundaries, asset_map, src = load_boundary_maps(mode)
    fallback = boundaries.get("unknown", {"curtailment_prob_norm": 0.5, "label": "unknown"})

    changed = []
    targets = [r for r in recs if r.get("layer") == 3]
    for rec in targets:
        eid = rec["entity_id"]
        exp = rec["exposure_inputs"]
        nf_comp = exp.get("non_firm_compute_exposure", {})
        if nf_comp.get("evidence_tier") == "measured":
            continue
        if rec.get("entity_type") in ("energy_asset", "storage_asset") and parse_non_firm(nf_comp):
            continue
        parsed = parse_non_firm(exp.get("non_firm_intensity", {}))
        if not parsed:
            continue
        share, import_mw = parsed
        bkey = asset_map.get(eid, "unknown")
        bmeta = boundaries.get(bkey, fallback)
        p = float(bmeta.get("curtailment_prob_norm", fallback["curtailment_prob_norm"]))
        parts = compute_interaction(import_mw, share, p)
        old = rec["exposure_inputs"].get("non_firm_compute_exposure", {}).get("rating_0_4")
        rec["exposure_inputs"]["non_firm_compute_exposure"] = build_subfactor(
            parts,
            bkey,
            bmeta.get("label", bkey),
            src,
            mode,
            bmeta.get("method", "constraint_boundary.json"),
        )
        changed.append((eid, old, rec["exposure_inputs"]["non_firm_compute_exposure"]["rating_0_4"], parts))

    save_records(recs, mode, out_path)

    print(f"=== MEASURE non_firm_compute_exposure ({mode}) ===")
    print(f"base: {base_label}  boundaries: {src}\n")
    for eid, old, new, parts in changed:
        print(f"  {eid:<26} rating {old} -> {new}   I={parts['interaction_index']:.4f}  "
              f"MW={parts['import_mw']} share={parts['non_firm_share']:.3f} p={parts['curtailment_prob']:.2f}")
    print(f"\nassets with interaction: {len(changed)}/{len(targets)}")
    print(f"wrote: data/{os.path.basename(out_path)}")
    return 0 if changed or mode == "fixture" else 0


if __name__ == "__main__":
    raise SystemExit(main())
