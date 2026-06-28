#!/usr/bin/env python3
"""NFRI data-optimization loop: apply audited deltas to the source records, re-score
with relative (median) quadrant cut-lines, and report before/after. This is the loop
that 'perfects' the data each pass — deltas are versioned in contract/deltas.json."""
import json, os, statistics as st, copy
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUBRIC = json.load(open(os.path.join(ROOT,"contract","rubric.json")))
BASE   = json.load(open(os.path.join(ROOT,"data","records.json")))
DSPEC  = json.load(open(os.path.join(ROOT,"contract","deltas.json")))

def axis(inp,cfg):
    # Renormalise over the sub-factors actually present (mirrors scoring.py.active_axis_config):
    # layer-conditional keys (non_firm_compute_exposure replaces non_firm_intensity at L3) keep each axis 0-100.
    a={k:c for k,c in cfg.items() if k in inp}; w=sum(c["weight"] for c in a.values()) or 1.0
    return round(sum(c["weight"]*(inp[k]["rating_0_4"]/4) for k,c in a.items())/w*100,1)

def quad(e,p,te,tp):
    if e>=te and p<tp: return "exposed"
    if e>=te and p>=tp: return "earning_it"
    if e<te and p>=tp: return "whitespace"
    return "sidelined"

def score_all(recs, te, tp):
    for r in recs:
        e=axis(r["exposure_inputs"],RUBRIC["exposure"]); p=axis(r["preparedness_inputs"],RUBRIC["preparedness"])
        r["scores"]={"exposure_0_100":e,"preparedness_0_100":p,"margin_of_safety":round(p-e,1),"quadrant":quad(e,p,te,tp)}
    return recs

def set_path(rec, path, val):
    parts = path.split(".")
    o = rec
    for p in parts[:-1]:
        if p not in o:
            print(f"  skip delta {rec.get('entity_id')}: missing {p} in {path}")
            return False
        o = o[p]
    o[parts[-1]] = val
    return True

# --- BEFORE (fixed 50/50 on untouched data) ---
before=score_all(copy.deepcopy(BASE),50,50)
qb=Counter(r["scores"]["quadrant"] for r in before)

# --- apply deltas ---
opt=copy.deepcopy(BASE)
byid={r["entity_id"]:r for r in opt}
applied=0; missed=[]
for d in DSPEC["deltas"]:
    r=byid.get(d["entity_id"])
    if not r:
        missed.append(d["entity_id"])
        continue
    if set_path(r, d["field"], d["to"]):
        applied += 1
    else:
        missed.append(f"{d['entity_id']}:{d['field']}")

# --- recalibrate with median cut-lines on the optimized data ---
tmp=score_all(copy.deepcopy(opt),50,50)
me=st.median([r["scores"]["exposure_0_100"] for r in tmp])
mp=st.median([r["scores"]["preparedness_0_100"] for r in tmp])
after=score_all(opt,me,mp)
qa=Counter(r["scores"]["quadrant"] for r in after)
for r in after:  # record the calibration used
    r["scores"]["calibration"]=f"median exp>={me} prep>={mp}"

json.dump(after, open(os.path.join(ROOT,"data","records.optimized.json"),"w"), indent=2, ensure_ascii=False)

print("=== DATA-OPTIMIZATION LOOP ===")
print(f"deltas applied: {applied}/{len(DSPEC['deltas'])}  missed: {missed or 'none'}")
print(f"median cut-lines: exposure>={me}  preparedness>={mp}\n")
print("quadrant distribution  BEFORE (fixed 50/50, raw):")
print("  " + ", ".join(f"{k}={v}" for k,v in sorted(qb.items())))
print("quadrant distribution  AFTER (deltas + median cut-lines):")
print("  " + ", ".join(f"{k}={v}" for k,v in sorted(qa.items())))
print("\nmovers:")
bb={r['entity_id']:r['scores']['quadrant'] for r in before}
for r in after:
    if bb[r['entity_id']]!=r['scores']['quadrant']:
        print(f"  {r['name']:<28} {bb[r['entity_id']]:>11} -> {r['scores']['quadrant']}")
print("\nfinal ranking by margin of safety:")
for r in sorted(after,key=lambda r:r['scores']['margin_of_safety'],reverse=True):
    s=r['scores']; print(f"  {s['margin_of_safety']:>6}  exp={s['exposure_0_100']:>5} prep={s['preparedness_0_100']:>5} [{s['quadrant']:<10}] {r['name']}")
print("\nWROTE: data/records.optimized.json")
