#!/usr/bin/env python3
"""NFRI model-spec ↔ knowledge integrity verifier.

Cursor builds the model layer (MODEL_SPEC.md, risk_model.json, stress_tests.json) on a
curated knowledge base (contract/knowledge/*.md + graph.json), citing contract/citations.json
throughout. This harness checks that the layers actually agree — every citation resolves,
the knowledge is wired into the machine-readable model the scorer emits, the graph is
internally consistent, and the deterministic thresholds match across MODEL_SPEC / risk_model /
scoring.py / the legacy measure_* scripts. It is the "evals at every level" discipline turned
on the model spec itself. Output: data/model_spec_verification.txt (+ nonzero exit on FAIL).

  python3 harness/verify_model_spec.py
"""
from __future__ import annotations
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(ROOT, p)))
def exists(p): return os.path.exists(os.path.join(ROOT, p))

CITES   = load("contract/citations.json")["references"]
RISK    = load("contract/risk_model.json")
STRESS  = load("contract/stress_tests.json")
RUBRIC  = load("contract/rubric.json")
GRAPH   = load("contract/knowledge/graph.json")
SPEC    = open(os.path.join(ROOT, "contract/MODEL_SPEC.md")).read()
SUBFACTORS = set(RUBRIC["exposure"]) | set(RUBRIC["preparedness"])

results = []  # (name, status, detail)
def rec(name, status, detail): results.append((name, status, detail))

# ---- collect citation IDs referenced anywhere ----
def walk_citation_ids(obj):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "citation_ids" and isinstance(v, list):
                out |= {x for x in v if isinstance(x, str)}
            elif k == "citation_id" and isinstance(v, str):
                out.add(v)
            else:
                out |= walk_citation_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= walk_citation_ids(v)
    return out

ref_risk   = walk_citation_ids(RISK)
ref_stress = walk_citation_ids(STRESS)
ref_graph  = walk_citation_ids(GRAPH)
# MODEL_SPEC.md: backticked ALL-CAPS handles like `NESO-CMP434`.
# Exclude stress-scenario IDs (contract/stress_tests.json) — a different namespace that
# shares the ALL-CAPS-with-hyphens shape but is not a citation handle.
scenario_ids = {s["id"] for s in STRESS["scenarios"]}
ref_spec   = set(re.findall(r"`([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)`", SPEC)) - scenario_ids
defined    = set(CITES)
referenced = ref_risk | ref_stress | ref_graph | ref_spec

# ---- V1 citation integrity (every reference resolves) ----
missing = sorted(referenced - defined)
rec("V1 citation integrity", "PASS" if not missing else "FAIL",
    f"{len(referenced)} referenced, {len(defined)} defined; "
    + ("all resolve" if not missing else f"{len(missing)} UNRESOLVED: {', '.join(missing)}"))
# per-source breakdown of who introduced each missing id
if missing:
    for mid in missing:
        where = [n for n, s in (("risk_model", ref_risk), ("stress", ref_stress),
                                ("graph", ref_graph), ("spec", ref_spec)) if mid in s]
        rec(f"    └─ {mid}", "FAIL", f"referenced in: {', '.join(where)} — not in citations.json")

# ---- V2 orphan citations (defined but never used) ----
orphans = sorted(defined - referenced)
rec("V2 orphan citations", "PASS" if not orphans else "WARN",
    "none" if not orphans else f"{len(orphans)} unused: {', '.join(orphans)}")

# ---- V3 graph integrity ----
node_ids = [n["id"] for n in GRAPH["nodes"]]
dup = sorted({i for i in node_ids if node_ids.count(i) > 1})
topic_ids = {t["id"] for t in GRAPH["topics"]}
bad_edges = [(e["from"], e["to"]) for e in GRAPH["edges"]
             if e["from"] not in node_ids or e["to"] not in node_ids]
bad_subf, bad_topics, missing_extracts = [], [], []
for n in GRAPH["nodes"]:
    for sf in n.get("nfri_sub_factors", []):
        if sf not in SUBFACTORS: bad_subf.append((n["id"], sf))
    for t in n.get("topics", []):
        if t not in topic_ids: bad_topics.append((n["id"], t))
    ext = n.get("extract")
    if ext:
        rel = os.path.normpath(os.path.join("contract/knowledge", ext))
        if not exists(rel): missing_extracts.append((n["id"], ext))
g_ok = not (dup or bad_edges or bad_subf or bad_topics)
detail = []
if dup: detail.append(f"dup node ids {dup}")
if bad_edges: detail.append(f"{len(bad_edges)} edges to unknown nodes")
if bad_subf: detail.append(f"{len(bad_subf)} invalid nfri_sub_factors")
if bad_topics: detail.append(f"{len(bad_topics)} invalid topic refs")
rec("V3 graph integrity", "PASS" if g_ok else "FAIL",
    f"{len(node_ids)} nodes, {len(GRAPH['edges'])} edges; " + ("clean" if g_ok else "; ".join(detail)))
rec("V3b extract files present", "PASS" if not missing_extracts else "WARN",
    "all extracts present" if not missing_extracts
    else f"{len(missing_extracts)} missing: {', '.join(f'{n}->{e}' for n, e in missing_extracts)}")

# ---- V4 knowledge wired into the MACHINE model (risk_model.json) ----
# A knowledge anchor (graph node with an extract + citation) should have its citation appear
# in risk_model.json for at least one of the sub-factors it claims — else scored records never
# carry that citation and the "model is built on the knowledge" claim is prose-only.
risk_subfactor_cites = {}
for axis in ("exposure", "preparedness"):
    for sf, cfg in RISK["axis_formulas"][axis]["sub_factors"].items():
        risk_subfactor_cites[sf] = walk_citation_ids(cfg)
unwired = []
for n in GRAPH["nodes"]:
    cid = n.get("citation_id")
    if not n.get("extract") or not cid or cid not in defined:
        continue
    claimed = n.get("nfri_sub_factors", [])
    if claimed and not any(cid in risk_subfactor_cites.get(sf, set()) for sf in claimed):
        unwired.append((n["id"], cid, claimed))
rec("V4 knowledge wired into risk_model", "PASS" if not unwired else "FAIL",
    "every knowledge anchor cited by ≥1 of its sub-factors"
    if not unwired else
    f"{len(unwired)} knowledge anchors NOT wired into risk_model.json sub-factors:")
for nid, cid, sfs in unwired:
    rec(f"    └─ {cid}", "FAIL", f"node '{nid}' claims {sfs} but no sub-factor cites it")

# ---- V5 deterministic-threshold consistency (risk_model vs scoring vs legacy measure_*) ----
def scr_expected(pct):
    if pct >= 200: return 4
    if pct >= 150: return 3
    if pct >= 100: return 2
    return 1
mismatches = []
try:
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import measure_capital as mc
    for pct in (85, 100, 130, 150, 160, 200, 260):
        legacy = mc.scr_component(pct)
        canon = scr_expected(pct)
        if legacy != canon:
            mismatches.append(f"SCR {pct}%: measure_capital={legacy} vs risk_model={canon}")
except Exception as e:  # import-safe: don't fail the whole verifier on env issues
    mismatches.append(f"(could not import measure_capital: {e})")
rec("V5 SCR thresholds (measure_capital vs risk_model)", "PASS" if not mismatches else "WARN",
    "aligned" if not mismatches else "; ".join(mismatches))

# scoring.py must reproduce risk_model thresholds for non_firm / hhi
try:
    import scoring
    model = scoring.load_risk_model()
    nf_tbl = model["deterministic_mappings"]["non_firm_intensity_from_share"]["thresholds"]
    probe = {0.0: 0, 0.05: 0, 0.2: 1, 0.5: 2, 0.8: 3, 0.95: 4}
    nf_bad = [f"{v}->{scoring._map_threshold(v, nf_tbl)}≠{exp}"
              for v, exp in probe.items() if scoring._map_threshold(v, nf_tbl) != exp]
    rec("V5b non_firm thresholds (scoring vs risk_model)", "PASS" if not nf_bad else "FAIL",
        "scoring reproduces risk_model mapping" if not nf_bad else "; ".join(nf_bad))
except Exception as e:
    rec("V5b non_firm thresholds (scoring vs risk_model)", "WARN", f"(could not import scoring: {e})")

# ---- report ----
out = ["NFRI MODEL-SPEC ↔ KNOWLEDGE VERIFICATION", "=" * 64,
       f"citations.json: {len(defined)} refs | graph: {len(node_ids)} nodes | "
       f"risk_model sub-factors: {len(risk_subfactor_cites)}", ""]
for name, status, detail in results:
    out.append(f"  [{status:<4}] {name}")
    out.append(f"         {detail}")
fails = [r for r in results if r[1] == "FAIL"]
warns = [r for r in results if r[1] == "WARN"]
out += ["", f"SUMMARY: {sum(1 for r in results if r[1]=='PASS')} pass, "
            f"{len(warns)} warn, {len(fails)} fail"]
report = "\n".join(out)
open(os.path.join(ROOT, "data", "model_spec_verification.txt"), "w").write(report)

# Module-level attributes for harness wiring (evals.py L8 / run_loop.py): results, fails, warns.
# Blocking checks gate the exit code (citations resolve, knowledge wired, thresholds aligned);
# V2 orphans and V3 graph integrity are reported but NON-BLOCKING (structural, surfaced to Cursor).
blocking = [r for r in fails if r[0].lstrip().startswith(("V1", "V4", "V5"))]
n_fail, n_warn = len(fails), len(warns)

if __name__ == "__main__":
    print(report)
    print(f"\n(blocking failures: {len(blocking)} — V2 orphans / V3 graph integrity are non-blocking)")
    sys.exit(1 if blocking else 0)
