#!/usr/bin/env python3
"""NFRI data-optimization metrics: quantify dataset quality and quadrant-threshold
sensitivity so optimization loops have an objective target."""
import json, os, statistics as st
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, "data", "records.scored.json")))
CONF = {"high":3,"medium":2,"low":1}

# completeness, source density, confidence coverage
ratings=[]; sources=0; conf=[]
for r in R:
    for axis in ("exposure_inputs","preparedness_inputs"):
        for sf in r[axis].values():
            ratings.append(sf["rating_0_4"]); sources+=len(sf.get("sources",[])); conf.append(CONF[sf["confidence"]])
n=len(ratings)
exp=[r["scores"]["exposure_0_100"] for r in R]
prep=[r["scores"]["preparedness_0_100"] for r in R]
mos=[r["scores"]["margin_of_safety"] for r in R]

def quad(e,p,te,tp):
    if e>=te and p<tp: return "exposed"
    if e>=te and p>=tp: return "earning_it"
    if e<te and p>=tp: return "whitespace"
    return "sidelined"

print("=== DATASET QUALITY METRICS ===")
print(f"records: {len(R)} | sub-factor ratings: {n}")
print(f"source density: {sources/n:.2f} sources/rating (total {sources})")
print(f"mean confidence: {st.mean(conf):.2f}/3  | low-conf share: {sum(1 for c in conf if c==1)/n:.0%}")
print(f"exposure   mean={st.mean(exp):.1f} median={st.median(exp):.1f} sd={st.pstdev(exp):.1f} range={min(exp)}-{max(exp)}")
print(f"preparedness mean={st.mean(prep):.1f} median={st.median(prep):.1f} sd={st.pstdev(prep):.1f} range={min(prep)}-{max(prep)}")
print(f"margin_of_safety mean={st.mean(mos):.1f} median={st.median(mos):.1f} range={min(mos)}-{max(mos)}")

print("\n=== QUADRANT THRESHOLD SENSITIVITY ===")
me, mp = st.median(exp), st.median(prep)
for label,(te,tp) in {"fixed 50/50":(50,50), f"median {me:.0f}/{mp:.0f}":(me,mp), "55/65":(55,65)}.items():
    c=Counter(quad(e,p,te,tp) for e,p in zip(exp,prep))
    print(f"{label:>16}: " + ", ".join(f"{k}={v}" for k,v in sorted(c.items())))
print("\nNote: fixed 50/50 collapses the field into 'earning_it'; a median (relative) split spreads entities across all four quadrants, which is the more informative presentation for an outside-in index.")
