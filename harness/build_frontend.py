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
import copy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import (ESSAY_CSS, collect_cite_order, load as load_contract,  # noqa: E402
                          render_act, render_foundations, render_section)
from design_system import load_design_system  # noqa: E402
from frontend.assemble import assemble_page  # noqa: E402
from frontend.viz_narrative import chart_narrative_ctx, resolve_tokens  # noqa: E402
from build_design_system_page import build as build_design_system_page  # noqa: E402
from build_methodology import build_methodology_page  # noqa: E402
from build_on_transformation import build_thesis_page  # noqa: E402
from build_entity_profiles import build_entity_profiles, write_profiles  # noqa: E402
from compute_thesis_charts import compute_thesis_charts  # noqa: E402
from scoring import active_axis_config, load_rubric, score_all  # noqa: E402

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
_RESEARCH_STUB = re.compile(
    r"^(?P<name>.+?): (?P<key>[\w]+) scored (?P<score>\d/4) from sourced research \((?P<date>[^)]+)\)\.?$"
)


def humanize_rationale(key: str, label: str, rationale: str) -> str:
    if not rationale:
        return ""
    m = _RESEARCH_STUB.match(rationale.strip())
    if m and m.group("key") == key:
        return (
            f"{m.group('name')}: {label.lower()} scored {m.group('score')} "
            f"from sourced research ({m.group('date')})."
        )
    return rationale

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


_SCORABLE = {"measured", "disclosed", "derived"}
_MEASURED_OVERLAY_FIELDS = (
    "evidence_tier", "measured_value", "deterministic_rating_0_4", "latent_rating_0_4",
    "rationale", "sources", "confidence", "citation_ids", "as_of", "unit", "source_type",
    "propagation_method",
)


def _axis_evidence_share(rec, axis_name: str) -> float:
    """Share of axis weight on measured/disclosed/derived tiers (L5 gate definition)."""
    rubric = load_rubric()
    cfg = rubric[axis_name]
    if axis_name == "exposure":
        cfg = active_axis_config(rec, cfg)
    inputs = rec.get(f"{axis_name}_inputs", {})
    covered = sum(
        c["weight"] for k, c in cfg.items()
        if k in inputs and (inputs[k].get("evidence_tier") or "assessed") in _SCORABLE
    )
    return round(covered, 3)


def authoritative_share(records):
    """Blended measured/disclosed share — mean entity average of E and P tier coverage."""
    if not records:
        return 0.0
    per = [(_axis_evidence_share(r, "exposure") + _axis_evidence_share(r, "preparedness")) / 2
           for r in records]
    return round(sum(per) / len(per), 3)


def merge_measured_overlay(records: list[dict]) -> list[dict]:
    """Overlay register/disclosure tiers from records.measured.json onto the build universe."""
    path = os.path.join(DATA_DIR, "records.measured.json")
    if not os.path.exists(path):
        return records
    measured = {r["entity_id"]: r for r in json.load(open(path))}
    out = []
    for rec in records:
        r = copy.deepcopy(rec)
        m = measured.get(r["entity_id"])
        if m:
            for ax in ("exposure_inputs", "preparedness_inputs"):
                for k, sf in (m.get(ax) or {}).items():
                    if k in r.get(ax, {}):
                        for field in _MEASURED_OVERLAY_FIELDS:
                            if field in sf:
                                r[ax][k][field] = sf[field]
        out.append(r)
    return out


def load_records():
    """Load universe for site build: records.json + measured overlay + full hybrid rescore.

    Avoids records.optimized.json (legacy median-only scorer without blend). Ensures scores,
    MoS, quadrants, and per-entity measured share match contract/MODEL_SPEC.md.
    """
    base = os.path.join(DATA_DIR, "records.json")
    if not os.path.exists(base):
        scored = os.path.join(DATA_DIR, "records.scored.json")
        base = scored if os.path.exists(scored) else os.path.join(DATA_DIR, "records.optimized.json")
    records = merge_measured_overlay(json.load(open(base)))
    records, _, _ = score_all(records)
    return records, base


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


from findings_facts import compute_facts  # noqa: E402


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
    rubric = load_rubric()
    axis_cfg = rubric["exposure" if axis == "exposure" else "preparedness"]
    if axis == "exposure":
        axis_cfg = active_axis_config(rec, axis_cfg)
    inputs = rec[f"{axis}_inputs"]
    blend = ((rec.get("scores") or {}).get("blend") or {}).get(f"{axis}_sub_factors", {})
    rows = []
    for k, sf in inputs.items():
        if k not in axis_cfg:
            continue
        bl = blend.get(k, {})
        wt = bl.get("weight")
        if wt is None:
            wt = axis_cfg[k]["weight"]
        rows.append({
            "key": k, "label": SF_LABEL.get(k, k), "axis": axis,
            "weight": wt,
            "lat": bl.get("latent_rating_0_4", sf.get("rating_0_4")),
            "det": bl.get("deterministic_rating_0_4"),
            "eff": bl.get("rating_effective_0_4", sf.get("rating_0_4")),
            "mode": bl.get("score_mode", "latent"),
            "lambda": bl.get("fusion_lambda", 0),
            "tier": sf.get("evidence_tier") or "assessed",
            "conf": sf.get("confidence", "low"),
            "rationale": humanize_rationale(k, SF_LABEL.get(k, k), (sf.get("rationale") or "")[:320]),
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
        det_exp = _axis_evidence_share(r, "exposure")
        det_prep = _axis_evidence_share(r, "preparedness")
        pts.append({
            "id": r["entity_id"], "name": r["name"], "layer": r["layer"],
            "type": r["entity_type"], "parent": r.get("parent_group", ""),
            "logo": f"assets/logos/{r['entity_id']}.png",
            "exp": s["exposure_0_100"], "prep": s["preparedness_0_100"],
            "mos": s["margin_of_safety"], "quad": s["quadrant"], "conf": s["overall_confidence"],
            "expLat": s.get("exposure_latent_0_100"), "expDet": s.get("exposure_deterministic_0_100"),
            "prepLat": s.get("preparedness_latent_0_100"), "prepDet": s.get("preparedness_deterministic_0_100"),
            "detExp": det_exp,
            "detPrep": det_prep,
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
    assets_src = os.path.join(ROOT, "assets")
    assets_dst = os.path.join(SITE_DIR, "assets")
    if os.path.isdir(assets_src):
        os.makedirs(assets_dst, exist_ok=True)
        for name in os.listdir(assets_src):
            src = os.path.join(assets_src, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(assets_dst, name))
        logos_src = os.path.join(assets_src, "logos")
        logos_dst = os.path.join(assets_dst, "logos")
        if os.path.isdir(logos_src):
            os.makedirs(logos_dst, exist_ok=True)
            for name in os.listdir(logos_src):
                src = os.path.join(logos_src, name)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(logos_dst, name))


def main():
    try:
        from fetch_logos import main as fetch_logos_main
        fetch_logos_main()
    except Exception:
        pass
    records, records_src = load_records()
    scored_path = os.path.join(DATA_DIR, "records.scored.json")
    if os.path.exists(scored_path):
        profiles, _ = build_entity_profiles(json.load(open(scored_path)))
        write_profiles(profiles)
    export_downloads(records_src)
    pts = build_points(records)
    cut_exp, cut_prep = parse_calibration((records[0].get("scores") or {}).get("calibration"))
    snapshot = records[0].get("provenance", {}).get("last_checked", "")
    evals = parse_eval_report()
    share = authoritative_share(records)
    graph = json.load(open(os.path.join(KNOW, "graph.json"))) if os.path.exists(os.path.join(KNOW, "graph.json")) else {"topics": [], "nodes": [], "edges": []}
    cites_full = json.load(open(os.path.join(ROOT, "contract", "citations.json")))["references"]
    cites = {k: {"t": v.get("title", ""), "a": v.get("authors", ""), "y": v.get("year", ""),
                 "u": v.get("url", ""), "use": v.get("use", "")} for k, v in cites_full.items()}
    rail = [dict(r, url=cites.get(r["cite"], {}).get("u", "")) for r in RAIL]
    _sm_path = os.path.join(ROOT, "contract", "scatter_methodology.json")
    _sm = json.load(open(_sm_path)) if os.path.exists(_sm_path) else {}
    scatter_method = {
        "quad": _sm.get("quadrant", {}),
        "layer": _sm.get("layer", {}),
    }

    index_charts = compute_thesis_charts(pts, graph)
    _cc_path = os.path.join(ROOT, "contract", "chart_copy.json")
    _cc_raw = json.load(open(_cc_path)).get("charts", {}) if os.path.exists(_cc_path) else {}
    _reg = (index_charts.get("mos_regression") or {}).get("stats") or {}
    _nar = chart_narrative_ctx(
        n=len(pts), cut_exp=cut_exp, cut_prep=cut_prep, share=share, pts=pts,
    )
    _nar.update({
        "slope": _reg.get("slope", "—"),
        "r2": _reg.get("r2", "—"),
        "nReg": _reg.get("n", len(pts)),
        "nL1": sum(1 for p in pts if p.get("layer") == 1),
    })
    _by = (index_charts.get("carrier_swarm") or {}).get("byCarrier") or {}
    _nar["nLinkedWriters"] = len(_by)
    _nar["nLinkedAssets"] = sum(len(v) for v in _by.values())

    def _resolved_copy(charts: dict) -> dict:
        out = {}
        for cid, block in charts.items():
            out[cid] = {
                k: resolve_tokens(v, _nar) if isinstance(v, str) else v
                for k, v in block.items()
            }
        return out

    _profiles_path = os.path.join(SITE_DATA, "profiles.json")
    profile_ids = list(json.load(open(_profiles_path)).keys()) if os.path.exists(_profiles_path) else []

    payload = {
        "pts": pts, "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "snapshot": snapshot, "evals": evals, "share": share,
        "graph": graph, "cites": cites, "rail": rail,
        "n": len(pts), "sfLabels": SF_LABEL, "scatterMethod": scatter_method,
        "indexCharts": index_charts,
        "chartCopy": _resolved_copy(_cc_raw),
        "profileIds": profile_ids,
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
    act_essays = {
        "industry": render_act(contracts["argument"], "industry", ctx),
        "landscape": render_act(contracts["argument"], "landscape", ctx),
        "mechanics": render_act(contracts["analysis"], "mechanics", ctx),
        "proposal": render_act(contracts["analysis"], "proposal", ctx),
    }
    foundations = render_foundations(ctx, intro=(
        "Every rating links to a primary source. The references cited across this index are "
        "listed below in citation order &mdash; academic, regulatory, actuarial and market "
        "sources, each with the role it plays in the model."))
    ds = load_design_system(os.path.join(ROOT, "contract", "design_system.json"))
    html = assemble_page(
        ds=ds,
        payload=payload,
        essays=essays,
        act_essays=act_essays,
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
    methodology_html = build_methodology_page(records=records, pts=pts, share=share, payload_base=payload)
    methodology_out = os.path.join(SITE_DIR, "methodology.html")
    open(methodology_out, "w").write(methodology_html)
    print(f"wrote {methodology_out}  ({len(methodology_html)//1024} KB, methodology tab)")

    thesis_html = build_thesis_page(records=records, pts=pts, share=share, payload_base=payload)
    thesis_out = os.path.join(SITE_DIR, "on-non-firm-risk.html")
    open(thesis_out, "w").write(thesis_html)
    print(f"wrote {thesis_out}  ({len(thesis_html)//1024} KB, transformation thesis)")



if __name__ == "__main__":
    main()
