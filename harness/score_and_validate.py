#!/usr/bin/env python3
"""NFRI Stages 3-5: linker (light) + hybrid scorer + validator.
Uses harness/scoring.py (latent × deterministic fusion per contract/MODEL_SPEC.md)."""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))

from scoring import load_rubric, score_all  # noqa: E402

RUBRIC = load_rubric()
RECORDS = json.load(open(os.path.join(ROOT, "data", "records.json")))


def linker_note(rec):
    al = rec.get("asset_link")
    if rec["layer"] == 3 and al:
        return (f"firmness={al.get('gate_status')} curtailment={al.get('curtailment_exposure')} "
                f"backup={al.get('backup_generation')}")
    return None


problems = []
records, cut_exp, cut_prep = score_all(RECORDS)

for rec in RECORDS:
    note = linker_note(rec)
    if note and rec.get("scores"):
        rec["scores"]["asset_firmness"] = note

seen = set()
for rec in RECORDS:
    eid = rec["entity_id"]
    if eid in seen:
        problems.append(f"[DEDUP] duplicate entity_id '{eid}'")
    seen.add(eid)
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for key, sf in rec[axis].items():
            if sf["rating_0_4"] >= 1 and not sf.get("sources"):
                problems.append(f"[SOURCE] {eid}.{axis}.{key}: rating>=1 with no source")
            if not (0 <= sf["rating_0_4"] <= 4):
                problems.append(f"[RANGE] {eid}.{axis}.{key}: rating out of 0-4")

DATA = os.path.join(ROOT, "data")
json.dump(RECORDS, open(os.path.join(DATA, "records.scored.json"), "w"), indent=2, ensure_ascii=False)

with open(os.path.join(DATA, "dataset.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["entity_id", "name", "layer", "entity_type", "exposure", "preparedness",
                "margin_of_safety", "quadrant", "confidence", "calibration",
                "exposure_latent", "exposure_det", "prep_latent", "prep_det"])
    for r in RECORDS:
        s = r.get("scores") or {}
        w.writerow([r["entity_id"], r["name"], r["layer"], r["entity_type"],
                    s.get("exposure_0_100"), s.get("preparedness_0_100"),
                    s.get("margin_of_safety"), s.get("quadrant"), s.get("overall_confidence"),
                    s.get("calibration"), s.get("exposure_latent_0_100"),
                    s.get("exposure_deterministic_0_100"), s.get("preparedness_latent_0_100"),
                    s.get("preparedness_deterministic_0_100")])

lines = ["NFRI VALIDATION REPORT", "=" * 60,
         f"records: {len(RECORDS)}  unique ids: {len(seen)}",
         f"model: contract/MODEL_SPEC.md v0.2 (hybrid latent×deterministic)",
         f"median cut-lines: exposure>={cut_exp} prep>={cut_prep}", ""]
scored = [r for r in RECORDS if r.get("scores")]
lines.append(f"scored OK: {len(scored)}/{len(RECORDS)}")
lines.append(f"validation problems: {len(problems)}")
for p in problems:
    lines.append("  - " + p)
lines.append("")
lines.append("RANKED BY MARGIN OF SAFETY (preparedness - exposure):")
for r in sorted(scored, key=lambda r: r["scores"]["margin_of_safety"], reverse=True):
    s = r["scores"]
    lines.append(f"  {s['margin_of_safety']:>6}  exp={s['exposure_0_100']:>5} prep={s['preparedness_0_100']:>5}  "
                 f"[{s['quadrant']:<10}] L{r['layer']} {r['name']}  ({s['overall_confidence']})")
lines.append("")
from collections import Counter
q = Counter(r["scores"]["quadrant"] for r in scored)
lines.append("QUADRANT COUNTS: " + ", ".join(f"{k}={v}" for k, v in q.items()))
report = "\n".join(lines)
open(os.path.join(DATA, "validation_report.txt"), "w").write(report)
print(report)
print("\nWROTE: records.scored.json, dataset.csv, validation_report.txt")
sys.exit(1 if problems else 0)
