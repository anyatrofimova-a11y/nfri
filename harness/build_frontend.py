#!/usr/bin/env python3
"""NFRI Stage 6 — build the static index site (the product) from the scored dataset,
the eval reports, the knowledge graph and the citation registry.

A narrative-led public index: an unscored population reduced to a two-axis tension
(Exposure × Preparedness → Margin of Safety), shipped clean, free and downloadable, with
doloop-style provenance honesty (publication gate + PROVISIONAL banner).

Sections rendered (PRODUCT_MODEL.md §5):
  1. Thesis hero + publication-status banner (eval L5 blended measured share)
  2. The 2×2 hero scatter — size = confidence, opacity = deterministic (measured) weight share
  3. Ranked Margin-of-Safety table (sortable / filterable)
  4. Entity drill-down — latent × deterministic decomposition + per-sub-factor citations
  5. In-force regulatory rail (CMP434/448, GC0166, demand CFI) → what each re-prices
  6. Knowledge-graph explorer (contract/knowledge/graph.json)
  7. Method / eval L0–L8 status + downloads

Self-contained: all data embedded inline, no external dependencies, no build step.
Output: site/index.html + site/data/* (downloads).
"""
import csv
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import (ESSAY_CSS, collect_cite_order, load as load_contract,  # noqa: E402
                          render_foundations, render_section)
from design_system import load_design_system  # noqa: E402
from frontend.assemble import assemble_page  # noqa: E402
from build_design_system_page import build as build_design_system_page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_DIR = os.path.join(ROOT, "site")
SITE_DATA = os.path.join(SITE_DIR, "data")
KNOW = os.path.join(ROOT, "contract", "knowledge")

CONF = {"high": 3, "medium": 2, "low": 1}
CONF_NAME = {3: "high", 2: "medium", 1: "low"}
SF_LABEL = {
    "book_concentration": "Book concentration", "non_firm_intensity": "Non-firm intensity",
    "aggregation_correlation": "Aggregation / correlation", "trigger_gap": "Trigger gap",
    "tenor_mismatch": "Tenor mismatch", "data_monitoring": "Data & monitoring",
    "product_fit": "Product fit", "underwriting_expertise": "Underwriting expertise",
    "capital_reinsurance": "Capital & reinsurance", "pricing_modelling": "Pricing & modelling",
}

# In-force regulatory rail — curated; each entry links to a citation that must resolve.
RAIL = [
    {"id": "CMP434/435", "title": "Implementing Connections Reform (Gate 1 / Gate 2)",
     "inforce": "10 Jun 2025", "cite": "NESO-CMP434",
     "reprices": "Every L3 firmness — Gate status becomes an objective register fact.",
     "sub": "non_firm_intensity"},
    {"id": "CMP448", "title": "Progression Commitment Fee to the Gate-2 queue",
     "inforce": "2 Jan 2026", "cite": "NESO-CMP448",
     "reprices": "Cost of holding a Gate-2 queue place — Gate-2 assets.",
     "sub": "tenor_mismatch"},
    {"id": "GC0166", "title": "BM Parameters for Limited Duration Assets",
     "inforce": "5 Dec 2025", "cite": "NESO-GC0166",
     "reprices": "How flexible / battery assets are dispatched.",
     "sub": "pricing_modelling"},
    {"id": "Demand CFI", "title": "Ofgem / NESO demand connections reform",
     "inforce": "2026 (consulting)", "cite": "OFGEM-DEMAND-REFORM",
     "reprices": "Right to curtail very large users — DC demand queue (~125 GW).",
     "sub": "non_firm_intensity"},
]


WEIGHTS = {
    "exposure_inputs": {"book_concentration": 0.30, "non_firm_intensity": 0.25,
                        "aggregation_correlation": 0.20, "trigger_gap": 0.15, "tenor_mismatch": 0.10},
    "preparedness_inputs": {"data_monitoring": 0.25, "product_fit": 0.20, "underwriting_expertise": 0.20,
                            "capital_reinsurance": 0.20, "pricing_modelling": 0.15},
}
_SCORABLE = {"measured", "disclosed", "derived"}


def authoritative_share(records):
    """Blended measured/disclosed share = mean over entities of the average of the two axes'
    weight of sub-factors on a measured/disclosed/derived tier. Computed on the rendered set."""
    per = []
    for r in records:
        axis_shares = []
        for ax, w in WEIGHTS.items():
            covered = sum(wt for k, wt in w.items()
                          if (r.get(ax, {}).get(k, {}).get("evidence_tier") or "assessed") in _SCORABLE)
            axis_shares.append(covered)  # weights sum to 1.0, so covered is already a share
        per.append(sum(axis_shares) / len(axis_shares))
    return round(sum(per) / len(per), 3) if per else 0.0


def compute_charts(records):
    """Aggregate the scored universe into chart-ready data for the essay engine:
    evidence-tier coverage (substantiation) and quadrant distribution."""
    from collections import Counter
    tiers, quads = Counter(), Counter()
    for r in records:
        s = r.get("scores") or {}
        if s.get("quadrant"):
            quads[s["quadrant"]] += 1
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for sf in r.get(ax, {}).values():
                tiers[(sf.get("evidence_tier") or "assessed")] += 1
    return {"tiers": dict(tiers), "quadrants": dict(quads)}


def _name_list(names, limit=4):
    names = list(names)
    if len(names) <= limit:
        if len(names) <= 1:
            return names[0] if names else ""
        return ", ".join(names[:-1]) + " and " + names[-1]
    return ", ".join(names[:limit]) + f" and {len(names) - limit} others"


def compute_facts(records, share):
    """Live numeric/text facts for the 'what the data shows' prose ({{fact:KEY}})."""
    from collections import Counter
    scored = [r for r in records if r.get("scores")]
    quad = Counter((r["scores"] or {}).get("quadrant") for r in scored)
    layers = Counter(r["layer"] for r in scored)
    by_mos = sorted(scored, key=lambda r: r["scores"]["margin_of_safety"])
    names = {q: [r["name"] for r in scored if r["scores"].get("quadrant") == q]
             for q in ("exposed", "earning_it", "whitespace", "sidelined")}
    f = {
        "total": len(scored),
        "exposed_count": quad.get("exposed", 0),
        "earning_count": quad.get("earning_it", 0),
        "whitespace_count": quad.get("whitespace", 0),
        "sidelined_count": quad.get("sidelined", 0),
        "exposed_names": _name_list(names["exposed"]) or "none yet",
        "whitespace_names": _name_list(names["whitespace"]) or "none yet",
        "earning_names": _name_list(names["earning_it"]) or "none yet",
        "measured_pct": f"{round(share * 100)}%",
        "n_layers": len([k for k in layers if k]),
        "l1": layers.get(1, 0), "l2": layers.get(2, 0), "l3": layers.get(3, 0), "l4": layers.get(4, 0),
    }
    if by_mos:
        f["low_mos_name"] = by_mos[0]["name"]
        f["low_mos_val"] = by_mos[0]["scores"]["margin_of_safety"]
        f["top_mos_name"] = by_mos[-1]["name"]
        f["top_mos_val"] = f"+{by_mos[-1]['scores']['margin_of_safety']}"
    return f


def overall_conf(rec):
    ranks = [CONF[sf["confidence"]] for ax in ("exposure_inputs", "preparedness_inputs")
             for sf in rec[ax].values()]
    return CONF_NAME.get(round(sum(ranks) / len(ranks)), "low")


def parse_calibration(cal):
    if cal:
        m = re.search(r"exp>=([\d.]+)\s+prep>=([\d.]+)", cal)
        if m:
            return float(m.group(1)), float(m.group(2))
    return 50.0, 50.0


def load_records():
    opt = os.path.join(DATA_DIR, "records.optimized.json")
    src = opt if os.path.exists(opt) else os.path.join(DATA_DIR, "records.scored.json")
    return json.load(open(src)), src


def parse_eval_report():
    """Return [{level,status,name,metric}] from data/eval_report.txt (the L0–L8 chips)."""
    path = os.path.join(DATA_DIR, "eval_report.txt")
    out = []
    if not os.path.exists(path):
        return out
    lines = open(path).read().splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r"\s*L(\d)\s+\[(\w+)\]\s+(.*)", ln)
        if m:
            metric = lines[i + 1].strip() if i + 1 < len(lines) else ""
            out.append({"level": int(m.group(1)), "status": m.group(2),
                        "name": m.group(3).strip(), "metric": metric})
    return out


def blended_measured_share(records):
    """Mirror evals.py L5: mean over entities of the avg of the two axes' deterministic share."""
    shares = []
    for r in records:
        b = (r.get("scores") or {}).get("blend") or {}
        e = b.get("exposure_deterministic_weight_share")
        p = b.get("preparedness_deterministic_weight_share")
        if e is not None and p is not None:
            shares.append((e + p) / 2)
    return round(sum(shares) / len(shares), 3) if shares else 0.0


def subfactor_rows(rec, axis):
    """Combine raw input (rationale/sources/confidence/tier) with the fusion blend."""
    inputs = rec[f"{axis}_inputs"]
    blend = ((rec.get("scores") or {}).get("blend") or {}).get(f"{axis}_sub_factors", {})
    rows = []
    for k, sf in inputs.items():
        bl = blend.get(k, {})
        rows.append({
            "key": k, "label": SF_LABEL.get(k, k), "axis": axis,
            "weight": bl.get("weight"),
            "lat": bl.get("latent_rating_0_4", sf.get("rating_0_4")),
            "det": bl.get("deterministic_rating_0_4"),
            "eff": bl.get("rating_effective_0_4", sf.get("rating_0_4")),
            "mode": bl.get("score_mode", "latent"),
            "lambda": bl.get("fusion_lambda", 0),
            "tier": sf.get("evidence_tier") or "assessed",
            "conf": sf.get("confidence", "low"),
            "rationale": (sf.get("rationale") or "")[:320],
            "sources": sf.get("sources", [])[:3],
            "cites": bl.get("citation_ids", [])[:6],
        })
    return rows


def build_points(records):
    pts = []
    for r in records:
        s = r.get("scores") or {}
        if not s:
            continue
        if "overall_confidence" not in s:
            s["overall_confidence"] = overall_conf(r)
        b = s.get("blend") or {}
        pts.append({
            "id": r["entity_id"], "name": r["name"], "layer": r["layer"],
            "type": r["entity_type"], "parent": r.get("parent_group", ""),
            "exp": s["exposure_0_100"], "prep": s["preparedness_0_100"],
            "mos": s["margin_of_safety"], "quad": s["quadrant"], "conf": s["overall_confidence"],
            "expLat": s.get("exposure_latent_0_100"), "expDet": s.get("exposure_deterministic_0_100"),
            "prepLat": s.get("preparedness_latent_0_100"), "prepDet": s.get("preparedness_deterministic_0_100"),
            "detExp": b.get("exposure_deterministic_weight_share", 0),
            "detPrep": b.get("preparedness_deterministic_weight_share", 0),
            "exposure": subfactor_rows(r, "exposure"),
            "preparedness": subfactor_rows(r, "preparedness"),
            "note": (r.get("notes") or "")[:240],
        })
    return pts


def export_downloads(records_src):
    os.makedirs(SITE_DATA, exist_ok=True)
    for name in ("records.optimized.json", "records.scored.json", "dataset.csv"):
        src = os.path.join(DATA_DIR, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SITE_DATA, name))
    for src in (os.path.join(KNOW, "graph.json"), os.path.join(ROOT, "contract", "citations.json")):
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SITE_DATA, os.path.basename(src)))


def main():
    records, records_src = load_records()
    export_downloads(records_src)
    pts = build_points(records)
    cut_exp, cut_prep = parse_calibration((records[0].get("scores") or {}).get("calibration"))
    snapshot = records[0].get("provenance", {}).get("last_checked", "")
    evals = parse_eval_report()
    # Headline gate share = weight-adjusted measured/disclosed share computed on the evidence
    # overlay (records.measured.json carries the true tiers; optimize.py currently re-derives
    # from latent and drops them). Authoritative for THIS universe, never a stale eval report.
    _mp = os.path.join(DATA_DIR, "records.measured.json")
    tier_src = json.load(open(_mp)) if os.path.exists(_mp) else records
    share = authoritative_share(tier_src)
    graph = json.load(open(os.path.join(KNOW, "graph.json"))) if os.path.exists(os.path.join(KNOW, "graph.json")) else {"topics": [], "nodes": [], "edges": []}
    cites_full = json.load(open(os.path.join(ROOT, "contract", "citations.json")))["references"]
    cites = {k: {"t": v.get("title", ""), "a": v.get("authors", ""), "y": v.get("year", ""),
                 "u": v.get("url", ""), "use": v.get("use", "")} for k, v in cites_full.items()}
    rail = [dict(r, url=cites.get(r["cite"], {}).get("u", "")) for r in RAIL]

    payload = {
        "pts": pts, "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "snapshot": snapshot, "evals": evals, "share": share,
        "graph": graph, "cites": cites, "rail": rail,
        "n": len(pts), "sfLabels": SF_LABEL,
    }

    CT = os.path.join(ROOT, "contract")
    order = ("argument", "analysis", "findings", "methodology", "data")
    contracts = {n: load_contract(os.path.join(CT, f"{n}.json")) for n in order}
    # Citation numbering by first appearance across the sections, in reading order.
    # Exclude underscore metadata (e.g. _doc) so example tokens don't pollute numbering.
    def _content(c):
        return json.dumps({k: v for k, v in c.items() if not k.startswith("_")}, ensure_ascii=False)
    cite_num = collect_cite_order([_content(contracts[n]) for n in order])
    ctx = {"num": cite_num, "cites": cites_full, "charts": compute_charts(records),
           "facts": compute_facts(records, share)}
    essays = {n: render_section(contracts[n], ctx) for n in order}
    foundations = render_foundations(ctx, intro=(
        "Every rating links to a primary source. The references cited across this index are "
        "listed below in citation order &mdash; academic, regulatory, actuarial and market "
        "sources, each with the role it plays in the model."))
    ds = load_design_system(os.path.join(ROOT, "contract", "design_system.json"))
    html = assemble_page(
        ds=ds,
        payload=payload,
        essays=essays,
        foundations=foundations,
        prose_css=ESSAY_CSS,
        fonts_url=ds["fonts"]["google_url"],
    )
    os.makedirs(SITE_DIR, exist_ok=True)
    out = os.path.join(SITE_DIR, "index.html")
    open(out, "w").write(html)
    gate = "PASS" if share >= 0.60 else "PROVISIONAL"
    print(f"wrote {out}  ({len(html)//1024} KB, {len(pts)} entities, "
          f"{len(graph.get('nodes', []))} graph nodes, blended measured share {share:.0%} → {gate})")
    ds_html = build_design_system_page()
    ds_out = os.path.join(SITE_DIR, "design-system.html")
    open(ds_out, "w").write(ds_html)
    print(f"wrote {ds_out}  (design system gallery)")



if __name__ == "__main__":
    main()
