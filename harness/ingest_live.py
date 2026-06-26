#!/usr/bin/env python3
"""Live register ingestion + re-score for the NFRI prototype slice.

Pulls NESO TEC (Gate/firmness) and DNO ECR rows (NGED CKAN + NPG national combine),
updates Layer-3 measured fields where register evidence exists, applies audited deltas,
re-scores with median cut-lines, exports dataset + frontend.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))

from adapters import ecr_search, gate_from_tec, neso_tec  # noqa: E402
from scoring import load_rubric, score_all  # noqa: E402

TODAY = date.today().isoformat()
DATA = os.path.join(ROOT, "data")
DELTAS = os.path.join(ROOT, "contract", "deltas.json")

# entity_id -> register search config
ASSET_INGEST = {
    "asset-kao-harlow": {
        "terms": ["Harlow", "Kao Data", "Edinburgh Way Harlow"],
        "tec_terms": ["Harlow", "Kao"],
        "min_import_mw": 1.0,
    },
    "asset-ark": {
        "terms": ["Corsham", "Spring Park Corsham", "Ark Data"],
        "tec_terms": ["Corsham", "Spring Park"],
        "min_import_mw": 1.0,
    },
    "asset-latos-bridgend": {
        "terms": ["Bridgend", "Latos", "Cardiff Rover"],
        "tec_terms": ["Bridgend", "Latos", "Cardiff"],
        "min_import_mw": 1.0,
    },
    "asset-culham-aigz": {
        "terms": ["Culham", "UKAEA Culham"],
        "tec_terms": ["Culham"],
        "min_import_mw": 5.0,
    },
}


def set_path(rec: dict, path: str, val) -> None:
    parts = path.split(".")
    obj = rec
    for part in parts[:-1]:
        obj = obj[part]
    obj[parts[-1]] = val


def apply_deltas(records: list[dict]) -> int:
    spec = json.load(open(DELTAS))
    by_id = {r["entity_id"]: r for r in records}
    applied = 0
    for d in spec["deltas"]:
        rec = by_id.get(d["entity_id"])
        if not rec:
            continue
        set_path(rec, d["field"], d["to"])
        applied += 1
    return applied


def share_to_rating(share: float) -> int:
    return 0 if share < 0.05 else 1 if share < 0.25 else 2 if share < 0.55 else 3 if share < 0.85 else 4


def conf_from_n(n: int) -> str:
    return "high" if n >= 5 else "medium" if n >= 2 else "low"


def ingest_ecr(entity_id: str, cfg: dict) -> dict | None:
    rows = []
    seen = set()
    for term in cfg["terms"]:
        for row in ecr_search(term, limit=50):
            key = json.dumps(row, sort_keys=True, default=str)
            if key not in seen:
                seen.add(key)
                rows.append(row)

    min_mw = cfg.get("min_import_mw", 1.0)
    filtered = [r for r in rows if (r.get("import_mw") or 0) >= min_mw or (r.get("export_mw") or 0) >= min_mw]
    if not filtered and rows:
        filtered = rows[:10]

    if not filtered:
        return None

    tot = nf = 0.0
    sources = set()
    for row in filtered:
        mw = row.get("import_mw") or row.get("export_mw") or 0
        if mw <= 0:
            continue
        tot += mw
        if row.get("non_firm"):
            nf += mw
        sources.add(row.get("source_url", ""))

    if tot <= 0:
        return None

    share = nf / tot
    source_url = next((s for s in sources if s), "https://northernpowergrid.opendatasoft.com/explore/dataset/ecr_manual_combine_test/")
    return {
        "rating_0_4": share_to_rating(share),
        "measured_value": round(share, 3),
        "unit": "MW-share-non-firm",
        "as_of": TODAY,
        "evidence_tier": "measured",
        "source_type": "register",
        "rationale": (
            f"Live ECR pull: MW-weighted non-firm share = {nf:.1f}/{tot:.1f} MW ({share:.0%}) "
            f"across {len(filtered)} register rows matching {cfg['terms']}."
        ),
        "sources": [source_url],
        "confidence": conf_from_n(len(filtered)),
        "register_rows_matched": len(filtered),
    }


def ingest_tec(entity_id: str, cfg: dict) -> dict | None:
    rows = []
    seen = set()
    for term in cfg.get("tec_terms", cfg["terms"]):
        for row in neso_tec(limit=10, q=term):
            pid = row.get("Project ID") or row.get("Project Name")
            if pid in seen:
                continue
            seen.add(pid)
            rows.append(row)
    if not rows:
        return None

    best = max(rows, key=lambda r: float(r.get("Cumulative Total Capacity (MW)") or 0))
    gate_status, note = gate_from_tec(best)
    url = "https://www.neso.energy/data-portal/transmission-entry-capacity-register"
    return {
        "gate_status": gate_status,
        "tec_project": best.get("Project Name"),
        "tec_mw": best.get("Cumulative Total Capacity (MW)"),
        "tec_status": best.get("Project Status"),
        "note": note,
        "sources": [url],
    }


def main() -> None:
    records = json.load(open(os.path.join(DATA, "records.json")))
    applied = apply_deltas(records)

    ingest_log = []
    for rec in records:
        if rec["layer"] != 3:
            continue
        eid = rec["entity_id"]
        cfg = ASSET_INGEST.get(eid)
        if not cfg:
            continue

        ecr = ingest_ecr(eid, cfg)
        tec = ingest_tec(eid, cfg)
        entry = {"entity_id": eid, "ecr": bool(ecr), "tec": bool(tec)}

        if ecr:
            old = rec["exposure_inputs"]["non_firm_intensity"]["rating_0_4"]
            rec["exposure_inputs"]["non_firm_intensity"] = ecr
            entry["non_firm_rating"] = f"{old} -> {ecr['rating_0_4']}"
            rec.setdefault("provenance", {})["method"] = "mixed"
            rec["provenance"]["last_checked"] = TODAY

        al = rec.setdefault("asset_link", {"covered_assets": []})
        if tec:
            al["gate_status"] = tec["gate_status"]
            al["tec_project"] = tec["tec_project"]
            al["tec_mw"] = tec["tec_mw"]
            al["tec_status"] = tec["tec_status"]
            entry["gate_status"] = tec["gate_status"]
            if tec.get("note"):
                rec["notes"] = (rec.get("notes") or "") + f" TEC: {tec['note']}"

        ingest_log.append(entry)

    records, cut_exp, cut_prep = score_all(records)

    opt_path = os.path.join(DATA, "records.optimized.json")
    json.dump(records, open(opt_path, "w"), indent=2, ensure_ascii=False)
    json.dump(records, open(os.path.join(DATA, "records.scored.json"), "w"), indent=2, ensure_ascii=False)

    csv_path = os.path.join(DATA, "dataset.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "name", "layer", "entity_type", "exposure", "preparedness",
                    "margin_of_safety", "quadrant", "confidence", "calibration"])
        for r in records:
            s = r.get("scores") or {}
            w.writerow([r["entity_id"], r["name"], r["layer"], r["entity_type"],
                        s.get("exposure_0_100"), s.get("preparedness_0_100"),
                        s.get("margin_of_safety"), s.get("quadrant"),
                        s.get("overall_confidence"), s.get("calibration")])

    report_path = os.path.join(DATA, "ingest_report.txt")
    lines = [
        "NFRI LIVE INGEST REPORT",
        "=" * 60,
        f"snapshot: {TODAY}",
        f"deltas applied: {applied}",
        f"median cut-lines: exposure>={cut_exp}  preparedness>={cut_prep}",
        "",
    ]
    for entry in ingest_log:
        lines.append(f"  {entry['entity_id']}: ecr={entry['ecr']} tec={entry['tec']} "
                     f"{entry.get('non_firm_rating', '')} {entry.get('gate_status', '')}".strip())
    lines.append("")
    lines.append("RANKED BY MARGIN OF SAFETY:")
    for r in sorted(records, key=lambda x: x["scores"]["margin_of_safety"], reverse=True):
        s = r["scores"]
        lines.append(f"  {s['margin_of_safety']:>6}  [{s['quadrant']:<10}] L{r['layer']} {r['name']}")
    open(report_path, "w").write("\n".join(lines))

    print("\n".join(lines))
    print(f"\nWROTE: {opt_path}, {csv_path}, {report_path}")

    import build_frontend
    build_frontend.main()


if __name__ == "__main__":
    main()
