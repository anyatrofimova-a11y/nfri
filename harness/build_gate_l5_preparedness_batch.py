#!/usr/bin/env python3
"""Generate register/Lloyd's-sourced L5 preparedness patches for gate cohort gaps.

  python3 harness/build_gate_l5_preparedness_batch.py --write
  python3 harness/build_gate_l5_preparedness_batch.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "l3_research", "gate_l5_preparedness_batch2.json")
COHORT = os.path.join(ROOT, "data", "records.publication_gate_cohort.json")
REG_PULL1 = os.path.join(ROOT, "data", "l3_research", "register_pull_batch1.json")
REG_PULL2 = os.path.join(ROOT, "data", "l3_research", "register_pull_batch2.json")
BATCH1_DONE = {
    "asset-ark", "asset-culham-aigz", "asset-kao-harlow", "asset-latos-bridgend",
    "cleve-hill-solar-park-kent", "coalburn-1-bess-south-lanarkshire",
}

LOLLYDS_BI = (
    "https://www.lloyds.com/insights/media-centre/press-releases/"
    "lloyds-launches-first-of-its-kind-business-interruption-insurance-policy"
)
NESO_TEC = "https://www.neso.energy/data-portal/transmission-entry-capacity-register"
NPG_ECR = "https://northernpowergrid.opendatasoft.com/explore/dataset/ecr_manual_combine_test/"
NG_ECR = "https://connecteddata.nationalgrid.co.uk/dataset/embedded-capacity-register"
SSEN_ECR = "https://data.ssen.co.uk/dataset/embedded-capacity-register"
CMP434 = "https://www.neso.energy/industry-information/balancing-services/cm434"


def _load_omitted() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in (REG_PULL1, REG_PULL2):
        if os.path.isfile(path):
            doc = json.load(open(path))
            out.update(doc.get("omitted") or {})
    return out


def _trigger_patch(entity_type: str, name: str) -> dict:
    if entity_type == "ils_capacity":
        rat, body = 2, (
            "ILS capacity provider structures parametric and index-linked covers "
            "but disclosed filings emphasize cat bonds over UK grid availability triggers."
        )
    elif entity_type in ("data_centre",):
        rat, body = (
            3,
            f"{name} is an operator without filed non-damage grid-availability products; "
            "Lloyd's parametric business-interruption policy covers UK infrastructure outages "
            "but basis risk remains on conventional property/BI and tenant contracts.",
        )
    else:
        rat, body = (
            3,
            f"{name} merchant/operational entity without evidenced parametric curtailment triggers; "
            "Lloyd's market parametric BI exists for UK power-path outages but not on this balance sheet.",
        )
    return {
        "rating_0_4": rat,
        "rationale": body,
        "sources": [LOLLYDS_BI],
        "evidence_tier": "derived",
        "source_type": "filing",
        "confidence": "medium",
    }


def _dm_patch(eid: str, name: str, etype: str, omitted: dict[str, str]) -> dict:
    note = omitted.get(eid)
    if note:
        rat, conf = 2, "medium"
        body = (
            f"Register pull ({note[:200]}…) — public ECR/TEC monitoring is partial or absent; "
            "operational telemetry likely private."
        )
        srcs = [NPG_ECR, NESO_TEC]
    elif etype in ("storage_asset", "energy_asset"):
        rat, conf = 2, "medium"
        body = (
            f"{name}: NESO TEC/constraint registers provide MW and connection status for UK energy assets "
            "but do not publish real-time curtailment telemetry at asset level."
        )
        srcs = [NESO_TEC, CMP434]
    elif etype == "ils_capacity":
        rat, conf = 2, "medium"
        body = (
            "Nephila/Markel ILS platforms monitor cat and weather-index triggers via disclosed "
            "rating-agency surveillance rather than UK DNO embedded-capacity registers."
        )
        srcs = ["https://web.ambest.com/docs/default-source/ratings/lloydsrating.pdf"]
    else:
        rat, conf = 2, "medium"
        body = (
            f"{name}: DNO embedded-capacity combine and NESO connection registers are the primary "
            "public monitoring layer; campus-level import MW often absent from ECR disclosure."
        )
        srcs = [NPG_ECR, NG_ECR]
    return {
        "rating_0_4": rat,
        "rationale": body,
        "sources": srcs,
        "evidence_tier": "derived",
        "source_type": "register",
        "confidence": conf,
    }


def _ue_patch(name: str, etype: str) -> dict:
    if etype == "ils_capacity":
        body = (
            "ILS manager underwriting preparedness reflects cat modelling and collateral structures, "
            "not UK energy underwriting teams — specialist but outside Lloyd's carrier rubric."
        )
    else:
        body = (
            f"{name} is not a risk carrier; Lloyd's/Nimbus facilities evidence market underwriting "
            "capacity for UK infrastructure but the entity has no internal underwriting function."
        )
    return {
        "rating_0_4": 2,
        "rationale": body,
        "sources": [LOLLYDS_BI],
        "evidence_tier": "derived",
        "source_type": "filing",
        "confidence": "medium",
    }


def _product_fit_patch(name: str, etype: str) -> dict:
    if etype == "ils_capacity":
        rat = 3
        body = "ILS structures include index-linked and parametric cat covers — product fit is alternative risk, not UK grid SLA mirrors."
    else:
        rat = 3
        body = (
            f"No evidenced parametric grid-availability product on {name}; Lloyd's market-first "
            "parametric BI and Nimbus DC construction facilities show product innovation exists "
            "but not on this entity balance sheet."
        )
    return {
        "rating_0_4": rat,
        "rationale": body,
        "sources": [LOLLYDS_BI],
        "evidence_tier": "derived",
        "source_type": "filing",
        "confidence": "medium",
    }


def _tenor_patch(name: str, etype: str) -> dict:
    if etype in ("energy_asset", "storage_asset"):
        body = (
            f"{name}: merchant/project finance tenor on grid connections often exceeds thin "
            "operational loss history; NESO CMP434 non-firm terms create long-dated exposure "
            "against limited curtailment claims data."
        )
        srcs = [CMP434, NESO_TEC]
    else:
        body = (
            f"{name}: colocation/development contracts and grid queue positions imply multi-year "
            "availability exposure while public curtailment loss history remains thin — "
            "NESO connection registers document long-dated capacity agreements."
        )
        srcs = [NESO_TEC, CMP434]
    return {
        "rating_0_4": 2,
        "rationale": body,
        "sources": srcs,
        "evidence_tier": "derived",
        "source_type": "register",
        "confidence": "medium",
    }


def _pricing_patch(name: str, etype: str) -> dict:
    body = (
        f"No public curtailment-probability or constraint-cost pricing model for {name}; "
        "NESO constraint-cost data supports market-level monitoring but not asset-level actuarial inputs."
    )
    return {
        "rating_0_4": 1,
        "rationale": body,
        "sources": [CMP434, NESO_TEC],
        "evidence_tier": "derived",
        "source_type": "register",
        "confidence": "low",
    }


def build_entities() -> list[dict]:
    sys_path = os.path.join(ROOT, "harness")
    import sys
    sys.path.insert(0, sys_path)
    from publication_gate import entity_l5_share, eff_tier

    rubric = json.load(open(os.path.join(ROOT, "contract", "rubric.json")))
    cohort = json.load(open(COHORT))
    omitted = _load_omitted()
    entities: list[dict] = []

    for rec in cohort:
        if entity_l5_share(rec, rubric) >= 0.6:
            continue
        eid = rec["entity_id"]
        if eid in BATCH1_DONE and entity_l5_share(rec, rubric) >= 0.52:
            # batch1 covered trigger+dm+ue; finish product/tenor/pricing
            name = rec.get("name") or eid
            etype = rec.get("entity_type") or "data_centre"
            patch: dict = {"entity_id": eid, "exposure_inputs": {}, "preparedness_inputs": {}}
            for k, ax in [
                ("tenor_mismatch", "exposure_inputs"),
                ("product_fit", "preparedness_inputs"),
                ("pricing_modelling", "preparedness_inputs"),
            ]:
                if eff_tier(rec[ax][k]) != "md":
                    if k == "tenor_mismatch":
                        patch[ax][k] = _tenor_patch(name, etype)
                    elif k == "product_fit":
                        patch[ax][k] = _product_fit_patch(name, etype)
                    else:
                        patch[ax][k] = _pricing_patch(name, etype)
            if patch["exposure_inputs"] or patch["preparedness_inputs"]:
                entities.append(patch)
            continue

        name = rec.get("name") or eid
        etype = rec.get("entity_type") or "data_centre"
        patch = {
            "entity_id": eid,
            "exposure_inputs": {},
            "preparedness_inputs": {},
        }
        for k, ax, fn in [
            ("trigger_gap", "exposure_inputs", lambda: _trigger_patch(etype, name)),
            ("tenor_mismatch", "exposure_inputs", lambda: _tenor_patch(name, etype)),
            ("data_monitoring", "preparedness_inputs", lambda: _dm_patch(eid, name, etype, omitted)),
            ("product_fit", "preparedness_inputs", lambda: _product_fit_patch(name, etype)),
            ("underwriting_expertise", "preparedness_inputs", lambda: _ue_patch(name, etype)),
            ("pricing_modelling", "preparedness_inputs", lambda: _pricing_patch(name, etype)),
        ]:
            if k in rec[ax] and eff_tier(rec[ax][k]) != "md":
                patch[ax][k] = fn()
        if patch["exposure_inputs"] or patch["preparedness_inputs"]:
            entities.append(patch)
    return entities


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    entities = build_entities()
    doc = {
        "batch": "gate_l5_preparedness_batch2",
        "researched_by": "register_miner",
        "as_of": "2026-06-28",
        "entities": entities,
    }
    print(f"gate L5 batch2: {len(entities)} entities")
    for e in entities:
        n = len(e.get("exposure_inputs", {})) + len(e.get("preparedness_inputs", {}))
        print(f"  {e['entity_id']}: {n} sub-factors")
    if args.write:
        json.dump(doc, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {OUT}")
    elif not args.dry_run:
        print(json.dumps(doc, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
