#!/usr/bin/env python3
"""NFRI Stages 3-5: linker (light) + deterministic scorer + validator.
Reads contract/rubric.json and data/records.json; writes data/records.scored.json,
data/dataset.csv and data/validation_report.txt. Scoring math is fully deterministic
(no LLM) so the index is reproducible."""
import json, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUBRIC = json.load(open(os.path.join(ROOT, "contract", "rubric.json")))
RECORDS = json.load(open(os.path.join(ROOT, "data", "records.json")))

CONF_RANK = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}

def axis_score(inputs, axis_cfg):
    """Weighted 0-100 score for one axis."""
    total = 0.0
    for key, cfg in axis_cfg.items():
        sf = inputs.get(key)
        if sf is None:
            raise ValueError(f"missing sub-factor '{key}'")
        total += cfg["weight"] * (sf["rating_0_4"] / 4.0)
    return round(total * 100, 1)

def quadrant(exp, prep):
    if exp >= 50 and prep < 50:  return "exposed"
    if exp >= 50 and prep >= 50: return "earning_it"
    if exp < 50 and prep >= 50:  return "whitespace"
    return "sidelined"

def overall_confidence(rec):
    ranks = []
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for sf in rec[axis].values():
            ranks.append(CONF_RANK.get(sf.get("confidence", "low"), 1))
    avg = sum(ranks) / len(ranks)
    return CONF_NAME[round(avg)] if round(avg) in CONF_NAME else "low"

# ---- Stage 3: linker (light) -- propagate asset firmness signal as a note ----
def linker_note(rec):
    al = rec.get("asset_link")
    if rec["layer"] == 3 and al:
        return f"firmness={al.get('gate_status')} curtailment={al.get('curtailment_exposure')} backup={al.get('backup_generation')}"
    return None

# ---- Stage 4: score ----
problems = []
for rec in RECORDS:
    rec["scores"] = None
    try:
        exp = axis_score(rec["exposure_inputs"], RUBRIC["exposure"])
        prep = axis_score(rec["preparedness_inputs"], RUBRIC["preparedness"])
    except ValueError as e:
        problems.append(f"[SCORE] {rec['entity_id']}: {e}")
        continue
    rec["scores"] = {
        "exposure_0_100": exp,
        "preparedness_0_100": prep,
        "margin_of_safety": round(prep - exp, 1),
        "quadrant": quadrant(exp, prep),
        "overall_confidence": overall_confidence(rec),
    }
    note = linker_note(rec)
    if note:
        rec["scores"]["asset_firmness"] = note

# ---- Stage 5: validate ----
seen = set()
for rec in RECORDS:
    eid = rec["entity_id"]
    if eid in seen:
        problems.append(f"[DEDUP] duplicate entity_id '{eid}'")
    seen.add(eid)
    # every rating >=1 must carry at least one source
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for key, sf in rec[axis].items():
            if sf["rating_0_4"] >= 1 and not sf.get("sources"):
                problems.append(f"[SOURCE] {eid}.{axis}.{key}: rating>=1 with no source")
            if not (0 <= sf["rating_0_4"] <= 4):
                problems.append(f"[RANGE] {eid}.{axis}.{key}: rating out of 0-4")

# ---- write outputs ----
DATA = os.path.join(ROOT, "data")
json.dump(RECORDS, open(os.path.join(DATA, "records.scored.json"), "w"), indent=2, ensure_ascii=False)

with open(os.path.join(DATA, "dataset.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["entity_id","name","layer","entity_type","exposure","preparedness","margin_of_safety","quadrant","confidence"])
    for r in RECORDS:
        s = r.get("scores") or {}
        w.writerow([r["entity_id"], r["name"], r["layer"], r["entity_type"],
                    s.get("exposure_0_100"), s.get("preparedness_0_100"),
                    s.get("margin_of_safety"), s.get("quadrant"), s.get("overall_confidence")])

# ---- report ----
lines = ["NFRI VALIDATION REPORT", "="*60, f"records: {len(RECORDS)}  unique ids: {len(seen)}", ""]
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
lines.append("QUADRANT COUNTS: " + ", ".join(f"{k}={v}" for k,v in q.items()))
report = "\n".join(lines)
open(os.path.join(DATA, "validation_report.txt"), "w").write(report)
print(report)
print("\nWROTE: records.scored.json, dataset.csv, validation_report.txt")
sys.exit(1 if problems else 0)
