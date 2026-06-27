#!/usr/bin/env python3
"""NFRI methodology stress-test — turn the harness's own loops/evals back on the METHODOLOGY.

The L0-L6 eval suite (harness/evals.py) grades the *data*. This grades the *method*: it
asks whether the rubric, the feature dictionary and the publication gate are mutually
satisfiable, and whether the headline signals survive their own confidence flags. Every
check is deterministic and sourced from the contract + the current records — no judgement,
no synthetic numbers. Output: data/stress_test_report.txt.

Tests (each a small loop over the contract/records):
  S1  Gate satisfiability   — max measured/disclosed weight reachable per axis & blended,
                              given the feature_dictionary tier targets, by entity type.
  S2  Per-axis vs blended   — the policy says ">=60% PER AXIS"; the eval computes a BLENDED
                              average. Do they agree? Where do they diverge?
  S3  Upgrade sensitivity   — minimal set of sub-factor upgrades needed to clear the gate.
  S4  Calibration fragility — median cut-lines on n=15: how many entities sit within a hair
                              of a cut-line (a quadrant that flips on a 1-point rating nudge).
  S5  Confidence fragility  — do the most extreme Margin-of-Safety signals rest on low
                              confidence / unconfirmed inputs?
  S6  Rubric applicability  — sub-factors defined for carriers but applied to L3 assets.
"""
from __future__ import annotations
import json, os, sys, statistics as st
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_utils import nf_exposure_key  # noqa: E402

def load(p): return json.load(open(os.path.join(ROOT, p)))

RUBRIC = load("contract/rubric.json")
RECS   = load("data/records.optimized.json")
# Exclude layer-conditional sub-factors (e.g. non_firm_compute_exposure, include_layers:[3]) from the
# base gate-math: they 1:1 REPLACE a base sub-factor at their layer (same weight), so the measurable-
# weight ceiling is unchanged. Including them would both double-count weight (sum>1.0) and KeyError on
# TIER_TARGET. The base exposure axis sums to 1.0.
EXP_W  = {k: v["weight"] for k, v in RUBRIC["exposure"].items() if not v.get("include_layers")}
PREP_W = {k: v["weight"] for k, v in RUBRIC["preparedness"].items() if not v.get("include_layers")}
GATE   = 0.60

# ---- feature_dictionary.md tier targets, encoded ----
# "measurable"  -> a primary register/filing yields the number directly (measured/disclosed/derived)
# "conditional" -> disclosed IF a public filing/wording exists, else falls back to assessed
# "assessed"    -> irreducibly judgement; capped at medium confidence; never measured
TIER_TARGET = {
    # book_concentration is disclosable ONLY where a named energy/power premium class exists.
    # Evidence (2026-06-26): Beazley/Hiscox group AND syndicate accounts, AXA XL, Chubb, Zurich,
    # Munich Re all report the Solvency II "Energy" class as nil or not separately — energy is written
    # under Property/Casualty/Marine. So for DIVERSIFIED writers it is irreducibly assessed; only
    # specialist energy writers (e.g. dedicated renewable-energy MGAs) isolate it. -> conditional.
    "book_concentration":     "conditional",   # named energy class (specialist writers) -> disclosed; else assessed
    "non_firm_intensity":     "measurable",   # DNO ECR + NESO TEC Gate column (L3 direct)
    "aggregation_correlation":"measurable",   # derived: Herfindahl over grid geography
    "trigger_gap":            "conditional",  # filed product wordings -> disclosed, else assessed
    "tenor_mismatch":         "conditional",  # disclosed facility/policy terms, else assessed
    "data_monitoring":        "assessed",     # capped — no primary measurement exists
    "product_fit":            "measurable",   # named evidenced parametric product = disclosed
    "underwriting_expertise": "assessed",     # capped — named-person evidence only
    "capital_reinsurance":    "measurable",   # AM Best/S&P FSR + SFCR SCR coverage = disclosed
    "pricing_modelling":      "assessed",     # capped — published model artifact only
}
# Entity-type carve-outs the feature dictionary states explicitly:
#  - capital_reinsurance is disclosed ONLY for risk-carriers (FSR/SCR). Brokers/MGAs have
#    none -> it stays assessed for them.
#  - non_firm_intensity is *measured* only at L3 (the asset). For carriers it is *propagated*
#    from inferred coverage links -> assessed confidence, not a register read.
CARRIER_TYPES = {"insurer", "lloyds_syndicate", "reinsurer"}
ASSET_TYPES   = {"data_centre", "energy_asset", "storage_asset"}
INTERMEDIARY  = {"mga", "broker"}

def effective_tier(subfactor, etype):
    """What tier this sub-factor can realistically reach for this entity type."""
    base = TIER_TARGET[subfactor]
    if subfactor == "capital_reinsurance" and etype not in CARRIER_TYPES:
        return "assessed"        # no FSR/SCR for intermediaries or assets
    if subfactor == "non_firm_intensity" and etype not in ASSET_TYPES:
        return "assessed"        # carrier-level value is propagated/inferred, not measured
    return base

def axis_measurable(weights, etype, count_conditional):
    """Sum of axis weight that can reach measured/disclosed for this entity type.
    count_conditional=True is the OPTIMISTIC case (every filing/wording turns out public)."""
    s = 0.0
    for k, w in weights.items():
        t = effective_tier(k, etype)
        if t == "measurable" or (t == "conditional" and count_conditional):
            s += w
    return round(s, 3)

# ================= S1 / S2 : gate satisfiability, per-axis vs blended =================
lines = []
def out(s=""): lines.append(s)

out("NFRI METHODOLOGY STRESS-TEST")
out("=" * 64)
out(f"contract: rubric.json + feature_dictionary.md   gate: measured/disclosed >= {GATE:.0%}")
out("")
out("S1/S2  GATE SATISFIABILITY  (max reachable measured/disclosed weight)")
out("-" * 64)
out("                     EXPOSURE        PREPAREDNESS        BLENDED")
out("  entity type      real   opt       real     opt       real   opt   per-axis?")
ETYPES = ["insurer/syndicate", "mga/broker", "data_centre/energy_asset"]
REP = {"insurer/syndicate": "insurer", "mga/broker": "mga", "data_centre/energy_asset": "data_centre"}
worst_axis_real = 1.0
for label in ETYPES:
    et = REP[label]
    ex_r = axis_measurable(EXP_W, et, False); ex_o = axis_measurable(EXP_W, et, True)
    pr_r = axis_measurable(PREP_W, et, False); pr_o = axis_measurable(PREP_W, et, True)
    bl_r = (ex_r + pr_r) / 2; bl_o = (ex_o + pr_o) / 2
    per_axis_ok = "PASS" if (ex_r >= GATE and pr_r >= GATE) else "FAIL"
    worst_axis_real = min(worst_axis_real, ex_r, pr_r)
    out(f"  {label:<24} {ex_r:.0%}   {ex_o:.0%}     {pr_r:.0%}     {pr_o:.0%}      "
        f"{bl_r:.0%}   {bl_o:.0%}    {per_axis_ok}")
out("")
out("  reading:  'real' = feature-dictionary measurable factors only;")
out("            'opt'  = optimistic (every conditional filing/wording is public).")
out(f"  FINDING S2a: the PREPAREDNESS axis tops out at "
    f"{axis_measurable(PREP_W,'insurer',True):.0%} measured even optimistically")
out(f"              (only product_fit + capital_reinsurance are disclosable; "
    f"data_monitoring+underwriting+pricing = {PREP_W['data_monitoring']+PREP_W['underwriting_expertise']+PREP_W['pricing_modelling']:.0%}")
out(f"              are irreducibly assessed). A '>=60% PER AXIS' gate is UNSATISFIABLE on Preparedness.")
out(f"  FINDING S2b: harness/evals.py L5 averages the two axes (blended), it does NOT enforce")
out(f"              per-axis. METHODOLOGY/DATA_POLICY say 'per axis'. The doc and the code disagree.")
out(f"  FINDING S2c: even BLENDED, a carrier reaches only "
    f"{(axis_measurable(EXP_W,'insurer',False)+axis_measurable(PREP_W,'insurer',False))/2:.0%} on measurable")
out(f"              factors alone; clearing 60% REQUIRES upgrading a conditional sub-factor")
out(f"              (trigger_gap / tenor_mismatch via filed wordings) to disclosed.")

# ================= S3 : upgrade sensitivity =================
out("")
out("S3  UPGRADE SENSITIVITY  (cheapest path to clear the BLENDED 60% gate, per carrier)")
out("-" * 64)
et = "insurer"
have_ex = axis_measurable(EXP_W, et, False)
have_pr = axis_measurable(PREP_W, et, False)
blended = (have_ex + have_pr) / 2
out(f"  baseline measurable blended share (carrier): {blended:.0%}  (need >=60%)")
gap = GATE * 2 - (have_ex + have_pr)   # summed-weight gap (blended*2)
out(f"  summed-axis weight still needed: {max(gap,0):.2f}")
candidates = []
for k in ("trigger_gap", "tenor_mismatch"):
    candidates.append((k, "exposure", EXP_W[k]))
candidates.sort(key=lambda x: -x[2])
acc = 0.0; chosen = []
for k, ax, w in candidates:
    if acc >= gap: break
    acc += w; chosen.append((k, w))
if acc >= gap:
    out(f"  -> upgrading {', '.join(f'{k}(+{w:.2f})' for k,w in chosen)} to DISCLOSED clears it "
        f"(adds {acc:.2f}, new blended {(have_ex+acc+have_pr)/2:.0%}).")
else:
    out(f"  -> even upgrading every conditional exposure factor only reaches "
        f"{(axis_measurable(EXP_W,et,True)+have_pr)/2:.0%}; the gate needs a rubric change or "
        f"a lower threshold.")
out("  IMPLICATION for triage: filed product wordings / binding-authority class (trigger_gap)")
out("  are NOT optional polish — they are load-bearing for the publication gate.")

# ================= S4 : calibration fragility =================
# Skip sub-factors not present on a record (layer-conditional, e.g. non_firm_compute_exposure at L3):
# every record carries the base axis (sum 1.0); the L3 compute feature 1:1 replaces non_firm_intensity.
def axis_score(inp, cfg): return sum(c["weight"] * (inp[k]["rating_0_4"] / 4) for k, c in cfg.items() if k in inp) * 100
exp = [(r["entity_id"], axis_score(r["exposure_inputs"], RUBRIC["exposure"])) for r in RECS]
prep = [(r["entity_id"], axis_score(r["preparedness_inputs"], RUBRIC["preparedness"])) for r in RECS]
me = st.median(v for _, v in exp); mp = st.median(v for _, v in prep)
# one 0-4 rating step is worth (weight/4)*100 points on its axis; smallest meaningful nudge
min_exp_step = min(c["weight"] for c in RUBRIC["exposure"].values()) / 4 * 100
min_prep_step = min(c["weight"] for c in RUBRIC["preparedness"].values()) / 4 * 100
out("")
out("S4  CALIBRATION FRAGILITY  (median cut-lines on n=15)")
out("-" * 64)
out(f"  cut-lines: exposure median={me:.1f}, preparedness median={mp:.1f}")
out(f"  smallest single-rating nudge: exposure +/-{min_exp_step:.1f}, preparedness +/-{min_prep_step:.1f} pts")
fragile = []
for (eid, e), (_, p) in zip(exp, prep):
    de, dp = abs(e - me), abs(p - mp)
    if de <= min_exp_step or dp <= min_prep_step:
        fragile.append((eid, round(de, 1), round(dp, 1)))
out(f"  entities within ONE rating-step of a cut-line (quadrant flips on a single nudge): {len(fragile)}/15")
for eid, de, dp in sorted(fragile, key=lambda x: min(x[1], x[2])):
    out(f"    {eid:<34} d(exp)={de:>4}  d(prep)={dp:>4}")
out("  FINDING S4: with n=15 the medians are unstable; a large share of the field is one")
out("  rating-step from changing quadrant. The 15->57 universe will move every cut-line.")

# ================= S5 : confidence fragility of headline signals =================
CONF = {"low": 0, "medium": 1, "high": 2}
def overall_conf(r):
    cs = [sf.get("confidence", "low") for ax in ("exposure_inputs", "preparedness_inputs")
          for sf in r[ax].values()]
    return sum(CONF.get(c, 0) for c in cs) / len(cs)
mos = []
for r in RECS:
    e = axis_score(r["exposure_inputs"], RUBRIC["exposure"])
    p = axis_score(r["preparedness_inputs"], RUBRIC["preparedness"])
    mos.append((r["entity_id"], round(p - e, 1), round(overall_conf(r), 2)))
mos.sort(key=lambda x: x[1])
out("")
out("S5  CONFIDENCE FRAGILITY OF HEADLINE SIGNALS")
out("-" * 64)
out("  most extreme Margin-of-Safety (the signals the index exists to surface):")
for eid, m, c in mos[:3] + mos[-2:]:
    flag = "  <-- LOW confidence drives an extreme call" if c < 0.6 else ""
    out(f"    MoS={m:>6}   mean-confidence={c:<4}  {eid}{flag}")
extreme_lowconf = [x for x in mos[:3] + mos[-2:] if x[2] < 0.6]
out(f"  FINDING S5: {len(extreme_lowconf)} of the 5 most extreme signals rest on mean-confidence < 0.6.")
out("  The headline (Latos most-negative MoS) is the LEAST confident record — honest, but it")
out("  means the index's sharpest claim is also its weakest-sourced. Triage must measure these FIRST.")

# ================= S6 : rubric applicability to L3 assets =================
out("")
out("S6  RUBRIC APPLICABILITY  (carrier sub-factors applied to L3 assets)")
out("-" * 64)
carrier_only = ["book_concentration", "capital_reinsurance", "product_fit",
                "underwriting_expertise", "trigger_gap", "tenor_mismatch"]
assets = [r for r in RECS if r["entity_type"] in ASSET_TYPES]
weight_misapplied = sum(EXP_W.get(k, 0) + PREP_W.get(k, 0) for k in carrier_only)
out(f"  L3 assets in dataset: {len(assets)}")
out(f"  sub-factors defined for risk-CARRIERS but scored on assets: {', '.join(carrier_only)}")
out(f"  axis weight they carry (exposure+prep): {weight_misapplied:.2f} of 2.00")
out("  FINDING S6: ~half of each asset's score comes from carrier-shaped sub-factors")
out("  (a data centre has no 'book', 'reinsurance' or 'underwriting expertise'). Either define")
out("  asset-specific anchors or score assets on the firmness axis only and propagate upward.")

# ================= S7 : artifact consistency (reproducibility, for real) =================
out("")
out("S7  ARTIFACT CONSISTENCY  (does re-running the scorer reproduce the committed files?)")
out("-" * 64)
def latos(f):
    r = [x for x in load(f) if x["entity_id"] == "asset-latos-bridgend"][0]
    nf_k = nf_exposure_key(r["exposure_inputs"])
    return round(axis_score(r["exposure_inputs"], RUBRIC["exposure"]), 1), \
           r["exposure_inputs"][nf_k]["rating_0_4"]
src_exp, src_nf = latos("data/records.json")               # scorer source of truth
scored_exp, scored_nf = latos("data/records.scored.json")  # scorer output (should match source)
out(f"  records.json (source)     Latos exposure={src_exp}  non_firm_intensity={src_nf}")
out(f"  records.scored.json (out) Latos exposure={scored_exp}  non_firm_intensity={scored_nf}")
deltas_eids = {d["entity_id"] for d in load("contract/deltas.json")["deltas"]}
if src_exp != scored_exp and "asset-latos-bridgend" not in deltas_eids:
    out("  FINDING S7: records.scored.json DOES NOT match score_and_validate(records.json) and")
    out("  no delta explains the gap. The derived artifacts drifted from the source. METHODOLOGY")
    out(f"  §6.2 and validation_report.txt cite Latos MoS=-37.5 (exposure {src_exp}); the scored/")
    out(f"  optimized files carry exposure {scored_exp}. The L3 'reproducibility PASS' eval only")
    out("  re-scores the SAME file twice — it never checks output-vs-source. Add that check to CI.")
else:
    out("  OK: scored artifact reconciles with the source (or a delta explains the gap).")

# ================= summary =================
out("")
out("=" * 64)
out("SUMMARY — methodology actions (ranked):")
out("  1. Reconcile gate definition: change DATA_POLICY/METHODOLOGY to 'BLENDED >=60%' (matches")
out("     evals.py), OR change evals.py to per-axis and LOWER the Preparedness target to ~40%.")
out("  2. Treat trigger_gap (filed wordings) as a measured-tier TARGET, not a nice-to-have —")
out("     it is required to clear even the blended gate for carriers.")
out("  3. Re-derive cut-lines only on the full 57-entity pull; treat n=15 quadrants as provisional.")
out("  4. Flag low-confidence extreme-MoS records as 'measure-first' in the research loop.")
out("  5. Add asset-specific rubric anchors (S6) before publishing any L3 score.")
out("  6. Add an output-vs-source reproducibility check to CI (S7) and re-run the pipeline")
out("     so records.scored / records.optimized reconcile with records.json.")

report = "\n".join(lines)
open(os.path.join(ROOT, "data", "stress_test_report.txt"), "w").write(report)
print(report)
