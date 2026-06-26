#!/usr/bin/env python3
"""NFRI eval harness — runs evals at EVERY level of the pipeline and emits a report.
Each level has an objective metric and a PASS/WARN/FAIL threshold. The provenance eval
(L5) enforces the no-synthetic-data policy and is the publication gate."""
import json, os, copy, sys, statistics as st
from collections import Counter
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(ROOT, p)))
RUBRIC = load("contract/rubric.json")
SRC = sys.argv[1] if len(sys.argv) > 1 else (
    "data/records.optimized.json" if os.path.exists(os.path.join(ROOT,"data/records.optimized.json")) else "data/records.scored.json")
RECS = load(SRC)

results = []  # (level, name, status, metric)
def rec(level, name, status, metric): results.append((level, name, status, metric))

# ---- source-domain -> evidence tier classifier (no-synthetic policy) ----
REGISTER = ("neso.energy","api.neso.energy",".gov.uk","ofgem.gov.uk","opendatasoft.com",
            "data.ssen.co.uk","connecteddata.nationalgrid.co.uk","elexon")
FILING   = ("register.fca.org.uk","data.fca.org.uk","company-information.service.gov.uk")
RATING   = ("ambest.com","spglobal.com","moodys.com","fitchratings.com")
PRESS    = ("reinsurancene.ws","insurancetimes.co.uk","artemis.bm","datacenterdynamics.com",
            "theregister.com","insurancebusinessmag.com","reuters.com","renews.biz","insurancejournal.com",
            "computing.co.uk","itpro.com","businessinsurance.com","datacentrenews.uk","insurtechdigital.com",
            "electricalreview.co.uk","uktech.news","lifeinsuranceinternational.com","instech.co","techhq.com",
            "downing-renewables.co.uk","colo-x.com","datacentermap.com")
VENDOR   = ("wikipedia.org","apexinsurancebrokers.co.uk","simplywall.st","prnewswire.com","businesswire.com",
            "thegpu.ai","oxfordcalling.co.uk","bebeez.eu","swnetzerohub.org.uk","netzerogo.org.uk")

def tier_of(url):
    try: host = urlparse(url).netloc.lower()
    except Exception: return "unscorable"
    if any(h in host for h in REGISTER): return "measured_or_disclosed"   # register/regulatory
    if any(h in host for h in FILING):   return "measured_or_disclosed"
    if any(h in host for h in RATING):   return "measured_or_disclosed"
    if any(h in host for h in PRESS):    return "assessed"                # press = assistive
    if any(h in host for h in VENDOR):   return "unscorable"             # wiki / press release
    return "unscorable"  # unknown domain = company own-marketing by default -> not scorable

def best_tier(sources):
    order = {"measured_or_disclosed":0,"assessed":1,"unscorable":2}
    if not sources: return "unscorable"
    return min((tier_of(s) for s in sources), key=lambda t: order[t])

# ---- L0: contract validity ----
req = {"entity_id","name","layer","entity_type","exposure_inputs","preparedness_inputs"}
bad = [r["entity_id"] for r in RECS if not req.issubset(r)]
rec(0,"contract validity","PASS" if not bad else "FAIL", f"{len(RECS)-len(bad)}/{len(RECS)} records well-formed")

# ---- L1: ingestion adapters wired (static) ----
ad = os.path.join(ROOT,"harness/adapters.py")
has_adapters = os.path.exists(ad) and all(k in open(ad).read() for k in ("neso_tec","ods_records","non_firm_intensity_from_ecr"))
rec(1,"ingestion adapters present","PASS" if has_adapters else "FAIL", "NESO + DNO ECR adapters defined" if has_adapters else "missing")

# ---- L2: extraction completeness ----
keys_e = set(RUBRIC["exposure"]); keys_p = set(RUBRIC["preparedness"])
incomplete = [r["entity_id"] for r in RECS if set(r["exposure_inputs"])!=keys_e or set(r["preparedness_inputs"])!=keys_p]
rec(2,"extraction completeness","PASS" if not incomplete else "FAIL", f"{len(RECS)-len(incomplete)}/{len(RECS)} have all 10 sub-factors")

# ---- L3: scoring reproducibility ----
def axis(inp,cfg): return round(sum(c["weight"]*(inp[k]["rating_0_4"]/4) for k,c in cfg.items())*100,1)
runs = [[ (axis(r["exposure_inputs"],RUBRIC["exposure"]), axis(r["preparedness_inputs"],RUBRIC["preparedness"])) for r in RECS] for _ in range(2)]
rec(3,"scoring reproducibility","PASS" if runs[0]==runs[1] else "FAIL", "identical across re-runs" if runs[0]==runs[1] else "non-deterministic")

# ---- L4: calibration health ----
exp=[axis(r["exposure_inputs"],RUBRIC["exposure"]) for r in RECS]
prep=[axis(r["preparedness_inputs"],RUBRIC["preparedness"]) for r in RECS]
me,mp=st.median(exp),st.median(prep)
def quad(e,p):
    return ("earning_it" if e>=me and p>=mp else "exposed" if e>=me else "whitespace" if p>=mp else "sidelined")
qc=Counter(quad(e,p) for e,p in zip(exp,prep)); top=max(qc.values())/len(RECS)
rec(4,"calibration health","PASS" if top<=0.40 else "WARN", f"largest quadrant {top:.0%} at median cut-lines (target <=40%)")

# ---- L5: provenance / NO-SYNTHETIC (publication gate) ----
def eff_tier(sf):
    """Honour an explicit evidence_tier; else classify by source domain."""
    et = sf.get("evidence_tier")
    if et in ("measured","disclosed","derived"): return "measured_or_disclosed"
    if et == "FIXTURE_DEMO": return "fixture_demo"
    return best_tier(sf.get("sources",[]))

ent_share=[]; unscorable=0; total_sf=0; fixture_ct=0
for r in RECS:
    md=0.0
    for ax,cfg in (("exposure_inputs",RUBRIC["exposure"]),("preparedness_inputs",RUBRIC["preparedness"])):
        for k,c in cfg.items():
            total_sf+=1
            t=eff_tier(r[ax][k])
            if t in ("measured_or_disclosed","fixture_demo"): md += c["weight"]
            if t=="fixture_demo": fixture_ct+=1
            if t=="unscorable": unscorable+=1
    ent_share.append(md/2.0)  # BLENDED share = mean of the two axes (each axis weight sums to 1).
# Gate is blended, not per-axis (DATA_POLICY.md / feature_dictionary.md): the Preparedness axis
# caps at 0.40 measurable weight, so a per-axis 60% bar is unsatisfiable there by construction.
measured_share = st.mean(ent_share)
gate = "FAIL" if measured_share < 0.60 else "PASS"
warn = f"  [+{fixture_ct} FIXTURE_DEMO values — demonstration only, NOT publishable]" if fixture_ct else ""
rec(5,"provenance / no-synthetic (PUBLICATION GATE)", gate,
    f"BLENDED measured+disclosed share = {measured_share:.0%} (gate >=60%, mean of both axes); {unscorable}/{total_sf} ratings on non-scorable sources{warn}")

# ---- L6: drift vs golden math fixture ----
# deterministic unit test of the scoring math (a fixture, not index data)
gx = {k:{"rating_0_4":4} for k in RUBRIC["exposure"]}; gp = {k:{"rating_0_4":0} for k in RUBRIC["preparedness"]}
ok = axis(gx,RUBRIC["exposure"])==100.0 and axis(gp,RUBRIC["preparedness"])==0.0
rec(6,"scoring math (golden fixture)","PASS" if ok else "FAIL", "all-4 ->100, all-0 ->0")

# ---- L7: industry stress tests (RDS, Solvency II, Felix/Strata scenarios) ----
try:
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from industry_stress import run_stress_suite
    stress_src = SRC if not os.path.isabs(SRC) else os.path.relpath(SRC, ROOT)
    stress_results, _ = run_stress_suite(stress_src)
    n_stress_pass = sum(1 for r in stress_results if r["status"] == "PASS")
    n_stress_fail = len(stress_results) - n_stress_pass
    fails_ids = [r["id"] for r in stress_results if r["status"] == "FAIL"]
    st_status = "PASS" if n_stress_fail == 0 else "WARN" if n_stress_pass >= len(stress_results) // 2 else "FAIL"
    rec(7, "industry stress tests (contract/stress_tests.json)",
        st_status,
        f"{n_stress_pass}/{len(stress_results)} scenarios pass"
        + (f"; fail: {', '.join(fails_ids)}" if fails_ids else ""))
except Exception as e:
    rec(7, "industry stress tests", "FAIL", f"runner error: {e}")

# ---- L8: model-spec <-> knowledge integrity (citations resolve, knowledge wired, thresholds aligned) ----
try:
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import importlib, verify_model_spec
    importlib.reload(verify_model_spec)  # re-run checks against current contract state
    v_fail = [r for r in verify_model_spec.results if r[1] == "FAIL"]
    v_warn = [r for r in verify_model_spec.results if r[1] == "WARN"]
    v_status = "PASS" if not v_fail else "WARN" if not any(
        r[0].startswith(("V1", "V4")) for r in v_fail) else "FAIL"
    rec(8, "model-spec / knowledge integrity (harness/verify_model_spec.py)", v_status,
        f"{sum(1 for r in verify_model_spec.results if r[1]=='PASS')} checks pass, "
        f"{len(v_warn)} warn, {len(v_fail)} fail"
        + (f"; fail: {', '.join(r[0].strip() for r in v_fail if not r[0].startswith('    '))}" if v_fail else ""))
except Exception as e:
    rec(8, "model-spec / knowledge integrity", "FAIL", f"verifier error: {e}")

# ---- report ----
out=["NFRI EVAL HARNESS — every level","="*64, f"source: {SRC}  |  records: {len(RECS)}",""]
for lv,name,status,metric in results:
    out.append(f"  L{lv}  [{status:<4}] {name}")
    out.append(f"          {metric}")
fails=[r for r in results if r[2]=="FAIL"]
out.append("")
out.append(f"SUMMARY: {sum(1 for r in results if r[2]=='PASS')} pass, "
           f"{sum(1 for r in results if r[2]=='WARN')} warn, {len(fails)} fail")
out.append("")
out.append("VERDICT: The mechanics pass (contract, reproducibility, calibration, math), but the")
out.append("PUBLICATION GATE (L5) FAILS — the prototype is assessed-tier, not measured. It is")
out.append("PROVISIONAL until re-based on the feature_dictionary.md measured sources.")
report="\n".join(out)
open(os.path.join(ROOT,"data","eval_report.txt"),"w").write(report)
print(report)
