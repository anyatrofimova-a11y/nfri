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
from build_essays import (ESSAY_CSS, MANIFESTO_CSS, collect_cite_order, collect_headings,
                          load as load_contract, render_foundations, render_section,
                          render_toc)
from design_system import load_design_system, render_design_css

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


def render_site_hero(mf: dict, ds: dict) -> str:
    h = mf.get("hero") or {}
    c = ds.get("site_hero") or {}
    kicker = h.get("eyebrow") or c.get("kicker", "")
    title = h.get("title") or c.get("title", "")
    lede = h.get("lede") or c.get("lede", "")
    return (
        f'<section class="site-hero" aria-label="Introduction">'
        f'<div class="wrap">'
        f'<p class="hero-kicker">{kicker}</p>'
        f'<h1 class="hero-title">{title}</h1>'
        f'<p class="hero-lede">{lede}</p>'
        f'<a class="hero-cta" href="#cards">Explore the index</a>'
        f'</div></section>'
    )


def render_industrial_steps(mf: dict) -> str:
    block = mf.get("industrial_steps") or {}
    items = block.get("items") or []
    if not items:
        return ""
    lis = "".join(
        f'<li><b>{i["title"]}.</b> {i["text"]}</li>'
        for i in items
    )
    return f'<ul class="steps-compact" aria-label="{block.get("title", "Stack")}">{lis}</ul>'


def render_manifesto_deck(mf: dict) -> str:
    """Pillars + stack — placed after thesis, not above the index."""
    pillars = "".join(
        f'<div class="mf-pillar"><span class="mf-n">{p["n"]}</span>'
        f'<span class="mf-t">{p["title"]}</span>'
        f'<p class="mf-p">{p["text"]}</p></div>'
        for p in mf.get("pillars", [])
    )
    body = (f'<div class="manifesto-grid">{pillars}</div>' if pillars else "") + render_industrial_steps(mf)
    if not body.strip():
        return ""
    return (
        '<section class="section manifesto-deck" id="about">'
        '<div class="section-head"><p class="section-kicker">About the index</p>'
        '<h2 class="section-title">What we measure and why</h2></div>'
        + body
        + "</section>"
    )


def render_manifesto_hero(mf: dict) -> str:
    return render_manifesto_deck(mf)


def render_part_band(part: dict) -> str:
    return (
        f'<div class="part-band" id="{part.get("id", "")}">'
        f'<span class="part-n">{part.get("roman", "")}</span>'
        f'<h2 class="part-t">{part.get("title", "")}</h2>'
        f'</div>'
    )


def render_welcome_modal(ds: dict) -> str:
    w = ds.get("welcome_modal", {})
    return f'''<div id="welcome-scrim" role="dialog" aria-labelledby="welcome-title">
  <div class="welcome-box">
    <h2 id="welcome-title">{w.get("title", "")}</h2>
    <p class="welcome-sub">{w.get("subtitle", "")}</p>
    <p class="welcome-body">{w.get("body", "")}</p>
    <p class="welcome-foot">{w.get("footnote", "")}</p>
    <p class="welcome-tip">{w.get("tip", "")}</p>
    <div class="welcome-actions">
      <button type="button" class="btn-ghost" id="welcome-close">Close</button>
      <button type="button" class="btn-primary" id="welcome-go">{w.get("cta", "Start exploring")}</button>
    </div>
  </div>
</div>'''


def part_bands_html(mf: dict) -> dict[str, str]:
    return {p["id"]: render_part_band(p) for p in mf.get("parts", []) if p.get("id")}


def main():
    records, records_src = load_records()
    export_downloads(records_src)
    pts = build_points(records)
    cut_exp, cut_prep = parse_calibration((records[0].get("scores") or {}).get("calibration"))
    snapshot = records[0].get("provenance", {}).get("last_checked", "")
    evals = parse_eval_report()
    # Headline gate share = the canonical eval L5 number (tier-based, matches DATA_POLICY); fall back
    # to the fusion λ-weighted share if the report is absent.
    l5 = next((e for e in evals if e["level"] == 5), None)
    m = re.search(r"share\s*=\s*(\d+)%", l5["metric"]) if l5 else None
    share = (int(m.group(1)) / 100) if m else blended_measured_share(records)
    graph = json.load(open(os.path.join(KNOW, "graph.json"))) if os.path.exists(os.path.join(KNOW, "graph.json")) else {"topics": [], "nodes": [], "edges": []}
    cites_full = json.load(open(os.path.join(ROOT, "contract", "citations.json")))["references"]
    cites = {k: {"t": v.get("title", ""), "a": v.get("authors", ""), "y": v.get("year", ""),
                 "u": v.get("url", ""), "use": v.get("use", "")} for k, v in cites_full.items()}
    rail = [dict(r, url=cites.get(r["cite"], {}).get("u", "")) for r in RAIL]

    payload = {
        "pts": pts, "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "snapshot": snapshot, "evals": evals, "share": share,
        "graph": graph, "cites": cites, "rail": rail,
        "n": len(pts),
    }

    CT = os.path.join(ROOT, "contract")
    ds = load_design_system(os.path.join(CT, "design_system.json"))
    manifesto = load_contract(os.path.join(CT, "manifesto.json"))
    order = ("argument", "analysis", "findings", "methodology", "data")
    contracts = {n: load_contract(os.path.join(CT, f"{n}.json")) for n in order}
    parts = part_bands_html(manifesto)
    analysis_toc = render_toc(collect_headings(contracts["analysis"]))
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
    html = TEMPLATE.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False))
    html = html.replace("/*__DESIGN_CSS__*/", render_design_css(ds))
    html = html.replace("/*__FONTS_URL__*/", ds["fonts"]["google_url"])
    html = html.replace("/*__ARGUMENT_CSS__*/", ESSAY_CSS + MANIFESTO_CSS)
    html = html.replace("<!--__WELCOME_MODAL__-->", render_welcome_modal(ds))
    html = html.replace("<!--__SITE_HERO__-->", render_site_hero(manifesto, ds))
    html = html.replace("<!--__MANIFESTO_HERO__-->", render_manifesto_hero(manifesto))
    html = html.replace("<!--__PART_THESIS__-->", parts.get("part-thesis", ""))
    html = html.replace("<!--__PART_EVIDENCE__-->", parts.get("part-evidence", ""))
    html = html.replace("<!--__ANALYSIS_TOC__-->", analysis_toc)
    html = html.replace("<!--__ARGUMENT__-->", essays["argument"])
    html = html.replace("<!--__ANALYSIS__-->", essays["analysis"])
    html = html.replace("<!--__FINDINGS__-->", essays["findings"])
    html = html.replace("<!--__METHODOLOGY__-->", essays["methodology"])
    html = html.replace("<!--__DATA__-->", essays["data"])
    html = html.replace("<!--__FOUNDATIONS__-->", foundations)
    os.makedirs(SITE_DIR, exist_ok=True)
    out = os.path.join(SITE_DIR, "index.html")
    open(out, "w").write(html)
    gate = "PASS" if share >= 0.60 else "PROVISIONAL"
    print(f"wrote {out}  ({len(html)//1024} KB, {len(pts)} entities, "
          f"{len(graph.get('nodes', []))} graph nodes, blended measured share {share:.0%} → {gate})")


# ============================ TEMPLATE ============================
TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Non-Firm Power Risk Index</title>
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<style>
  *{box-sizing:border-box}
  /*__DESIGN_CSS__*/
  section{padding:var(--section-y) 0;border-bottom:1px solid var(--line-subtle)}
  h2{font-family:var(--font-display);font-size:clamp(20px,2.5vw,26px);font-weight:500;margin:0 0 var(--space-xs);letter-spacing:-.02em;color:var(--ink)}
  .sec-sub{color:var(--muted);font-size:15px;margin:0 0 var(--space-md);max-width:52ch;line-height:1.55}
  .controls{display:none}
  .card,.panel{background:var(--card);border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm)}
  svg{width:100%;height:auto;display:block}
  .legend{display:flex;gap:var(--space-sm);flex-wrap:wrap;font-size:13px;color:var(--muted);margin:var(--space-xs) 0;align-items:center}
  .legend i{display:inline-block;width:10px;height:10px;border-radius:var(--radius-sm);margin-right:4px;vertical-align:-1px}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line-subtle)}
  th{color:var(--muted);font-weight:500;cursor:pointer;user-select:none;white-space:nowrap;font-size:13px}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  tr.row{cursor:pointer} tr.row:hover{background:var(--bg-muted)}
  .pill{font-size:11px;padding:2px 8px;border-radius:var(--radius-pill);color:#fff;white-space:nowrap}
  .mbar{display:inline-block;height:6px;border-radius:var(--radius-sm);background:var(--measured);vertical-align:middle}
  .mtrack{display:inline-block;width:48px;height:6px;border-radius:var(--radius-sm);background:var(--bg-subtle);vertical-align:middle;overflow:hidden}
  .conf{font-size:12px;color:var(--muted)}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-md)}
  @media(max-width:780px){.grid2{grid-template-columns:1fr}}
  .rail{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:var(--space-sm)}
  .rcard{border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default)}
  .rcard .id{font-weight:600;font-size:14px}.rcard .if{font-size:12px;color:var(--earning-s);font-weight:500}
  .rcard p{margin:6px 0 0;font-size:13px;color:var(--ink2);line-height:1.5}
  .chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:var(--space-xs)}
  .chip{font-size:11px;border:1px solid var(--line);border-radius:var(--radius-md);padding:2px 8px;color:var(--ink2);background:var(--bg-default)}
  #scrim{position:fixed;inset:0;background:rgba(17,17,17,.25);opacity:0;pointer-events:none;transition:.18s;z-index:40}
  #scrim.on{opacity:1;pointer-events:auto}
  #drawer{position:fixed;top:0;right:0;height:100%;width:min(520px,94vw);background:var(--bg-default);
          box-shadow:-8px 0 32px rgba(0,0,0,.1);transform:translateX(100%);transition:.22s cubic-bezier(.4,0,.2,1);
          z-index:41;overflow:auto}
  #drawer.on{transform:none}
  .dh{padding:var(--space-sm) var(--space-md);border-bottom:1px solid var(--line-subtle);position:sticky;top:0;background:var(--bg-default);z-index:2}
  .dh h3{margin:0;font-size:20px;font-family:var(--font-display);font-weight:500;color:var(--ink)}
  .dh .x{position:absolute;top:14px;right:16px;cursor:pointer;font-size:20px;color:var(--muted);border:none;background:none}
  .db{padding:var(--space-sm) var(--space-md) var(--space-lg)}
  .scorerow{display:flex;gap:var(--space-md);flex-wrap:wrap;margin:0 0 var(--space-sm)}
  .scorerow .s{font-size:12px;color:var(--muted)}.scorerow .s b{display:block;font-size:20px;color:var(--ink);font-variant-numeric:tabular-nums;font-weight:600}
  .decomp{font-size:13px;color:var(--muted);margin:0 0 var(--space-sm)}
  .axh{font-weight:600;font-size:13px;margin:var(--space-sm) 0 6px;display:flex;justify-content:space-between}
  .sf{border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:10px 12px;margin-bottom:var(--space-xs)}
  .sf .top{display:flex;align-items:center;gap:8px;font-size:13px}
  .sf .nm{font-weight:600}.sf .w{color:var(--muted);font-size:11px;margin-left:auto}
  .mode{font-size:10px;text-transform:uppercase;letter-spacing:.04em;padding:1px 6px;border-radius:var(--radius-md);font-weight:600}
  .mode.latent{background:var(--bg-subtle);color:var(--muted)}.mode.hybrid{background:#e8f0f2;color:var(--section-accent)}.mode.deterministic{background:var(--ok-bg);color:var(--earning-s)}
  .sf .r{font-size:13px;color:var(--ink2);margin:6px 0 0;line-height:1.5}
  .sf .ev{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px;align-items:center}
  .sf .ev a{font-size:11px}.tier{font-size:10px;padding:1px 6px;border-radius:var(--radius-md);background:var(--bg-muted);color:var(--muted)}
  .ratbar{display:inline-flex;gap:2px;margin-left:2px}.ratbar i{width:6px;height:10px;border-radius:1px;background:var(--bg-subtle)}.ratbar i.on{background:var(--accent2)}
  #kg{width:100%;height:480px;border:1px solid var(--line-subtle);border-radius:var(--radius-lg);background:var(--bg-default);overflow:hidden}
  .kgnode{cursor:pointer}.kgnode text{font-size:9px;fill:var(--ink2);pointer-events:none}
  #kgdetail{font-size:14px;color:var(--ink2);min-height:48px;line-height:1.5}
  #kgdetail h4{margin:0 0 4px;font-size:15px;font-weight:600;color:var(--ink)}
  .foot{color:var(--muted);font-size:13px;line-height:1.6;padding:var(--space-md) 0 var(--space-lg)}
  .evchips{display:flex;gap:6px;flex-wrap:wrap;margin:var(--space-xs) 0 var(--space-sm)}
  .ev-l{font-size:12px;border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:4px 10px;display:flex;gap:6px;align-items:center;background:var(--bg-default)}
  .ev-l b{font-variant-numeric:tabular-nums;font-weight:600}
  .dot{width:7px;height:7px;border-radius:50%}.PASS .dot{background:var(--earning-s)}.FAIL .dot{background:var(--exposed)}.WARN .dot{background:var(--accent)}
  .banner{display:flex;gap:var(--space-sm);align-items:flex-start;border-radius:var(--radius-md);padding:12px 14px;font-size:14px;line-height:1.5}
  .banner.ok{background:var(--ok-bg);border:1px solid var(--ok-border)}
  .banner:not(.ok){background:var(--warn-bg);border:1px solid var(--warn-border)}
  .banner b{font-weight:600}
  .meta{display:flex;gap:var(--space-md);flex-wrap:wrap;color:var(--muted);font-size:13px}
  .dl{display:flex;gap:var(--space-xs);flex-wrap:wrap}
  .dl a{font-size:13px;text-decoration:none;border:1px solid var(--line);border-radius:var(--radius-md);padding:6px 12px;background:var(--bg-default);color:var(--ink2)}
  .dl a:hover{border-color:var(--section-accent);text-decoration:none}
/*__ARGUMENT_CSS__*/
</style></head>
<body>
<!--__WELCOME_MODAL__-->
<!--__SITE_HERO__-->
<div class="zone-analytical">
<header class="top"><div class="wrap">
  <div class="brand"><span class="brand-mark">NF</span>NFRI</div>
  <nav aria-label="Sections">
    <a href="#cards">Explore</a>
    <a href="#index">Scatter</a>
    <a href="#argument">Thesis</a>
    <span class="nav-sep"></span>
    <a href="#methodology">Method</a>
    <a href="#foundations">Sources</a>
  </nav>
</div></header>

<div class="wrap">
  <div class="status-strip">
    <div id="banner" class="banner"></div>
    <div class="status-meta" id="meta"></div>
    <div class="status-dl">
      <a href="data/dataset.csv" download>CSV</a>
      <a href="data/records.optimized.json" download>JSON</a>
    </div>
  </div>

  <section id="cards" class="section">
    <div class="section-head">
      <p class="section-kicker">I · Index</p>
      <h2 class="section-title">Explore the universe</h2>
      <p class="section-lede">Search carriers, MGAs, brokers, assets and reinsurers. Click any row for the full score decomposition.</p>
    </div>
    <div class="idx-toolbar" id="idx-toolbar">
      <input type="search" class="idx-search" id="idx-search" placeholder="Search…" aria-label="Search entities">
      <button type="button" class="idx-btn on" data-t="layer" data-v="all">All</button>
      <button type="button" class="idx-btn" data-t="layer" data-v="1">L1</button>
      <button type="button" class="idx-btn" data-t="layer" data-v="2">L2</button>
      <button type="button" class="idx-btn" data-t="layer" data-v="3">L3</button>
      <button type="button" class="idx-btn" data-t="quad" data-v="all">All quads</button>
      <button type="button" class="idx-btn" data-t="sort" data-v="mos">By margin</button>
      <span class="idx-meta" id="idx-count"></span>
    </div>
    <div class="card-list" id="card-list"></div>
  </section>

  <section id="index" class="section">
    <div class="section-head">
      <h2 class="section-title">Exposure × Preparedness</h2>
      <p class="section-lede">Median cut-lines define quadrants. Dot size reflects confidence; fill reflects measured evidence share.</p>
    </div>
    <div class="panel">
      <svg id="plot" viewBox="0 0 960 580" role="img" aria-label="Exposure vs Preparedness"></svg>
      <div class="legend">
        <span><i style="background:var(--earning-s)"></i>Earning it</span>
        <span><i style="background:var(--exposed)"></i>Exposed</span>
        <span><i style="background:var(--whitespace)"></i>Whitespace</span>
        <span><i style="background:var(--sidelined)"></i>Sidelined</span>
      </div>
    </div>
    <div class="controls" id="filters" hidden></div>
  </section>

  <section id="table" class="section">
    <div class="section-head">
      <h2 class="section-title">Ranked by margin of safety</h2>
    </div>
    <div class="panel"><table id="tbl"><thead><tr>
      <th data-k="name">Entity</th><th data-k="layer" class="num">L</th>
      <th data-k="exp" class="num">Exposure</th><th data-k="prep" class="num">Prepared</th>
      <th data-k="mos" class="num">Margin</th><th data-k="quad">Quadrant</th>
      <th data-k="meas" class="num">Measured</th><th data-k="conf">Conf.</th>
    </tr></thead><tbody></tbody></table></div>
  </section>

  <!--__PART_THESIS__-->
  <section id="argument" class="section essay"><div class="col"><!--__ARGUMENT__--></div></section>

  <section id="analysis" class="section essay essay-with-toc">
    <!--__ANALYSIS_TOC__-->
    <div class="col"><!--__ANALYSIS__--></div>
  </section>

  <!--__MANIFESTO_HERO__-->

  <!--__PART_EVIDENCE__-->
  <section id="findings" class="essay"><div class="col"><!--__FINDINGS__--></div></section>

  <section id="rail">
    <h2>In force — the rules that re-price firmness</h2>
    <p class="sec-sub">doloop discipline: not what's proposed, what actually landed. Each modification flags the
      records it re-scores when Gate or curtailment terms change.</p>
    <div class="rail" id="railcards"></div>
  </section>

  <section id="methodology" class="essay"><div class="col"><!--__METHODOLOGY__--></div></section>

  <section id="data" class="essay"><div class="col"><!--__DATA__--></div></section>

  <section id="foundations" class="essay"><div class="col">
    <p class="arg-kicker">Foundations</p>
    <h3 class="arg-h">Academic, regulatory & actuarial references</h3>
    <!--__FOUNDATIONS__--></div></section>

  <section id="knowledge">
    <h2>Knowledge graph</h2>
    <p class="sec-sub">The evidence spine: industry and academic sources, the sub-factors they inform, and how
      they connect. Filter by topic; click a node for the citation and findings.</p>
    <div class="controls" id="kgfilters"></div>
    <div class="grid2">
      <svg id="kg" viewBox="0 0 600 520"></svg>
      <div class="card"><div id="kgdetail"><h4>Select a node</h4>
        <p class="conf">The graph triangulates the thesis: interruption ≠ damage (Che-Castaldo),
          basis risk (expectiles), compound loss (Klugman), credibility fusion (Bühlmann).</p></div></div>
    </div>
  </section>

  <section id="method">
    <h2>Method & evals</h2>
    <p class="sec-sub">Scoring is arithmetic in code, never an LLM opinion (<code>harness/scoring.py</code>);
      no value is synthetic (<code>contract/DATA_POLICY.md</code>). The harness grades itself L0–L8 —
      L5 is the publication gate.</p>
    <div class="evchips" id="evchips"></div>
    <p class="foot">
      Ratings fuse <b>latent</b> (sourced research judgement) and <b>deterministic</b> (register/filing)
      inputs by credibility weighting, <code>r_eff = clamp(λ·r_det + (1−λ)·r_lat)</code>
      (<code>contract/MODEL_SPEC.md</code>). Quadrants use in-sample <b>median</b> cut-lines.
      Every rating links to its source; assessed values are marked; anything below the publication gate is
      <b>PROVISIONAL</b>. This is an outside-in research aid — not audited positions, not investment advice.
    </p>
  </section>
  <footer class="site-foot">
    <span>NFRI research index · scores fuse register data with cited research</span>
    <a href="data/dataset.csv" download>Download CSV</a>
    <a href="data/records.optimized.json" download>Download JSON</a>
    <a href="#method">Method & evals</a>
    <a href="#foundations">References</a>
  </footer>
</div><!-- /.zone-analytical -->

<div id="scrim" onclick="closeDrawer()"></div>
<aside id="drawer"><div class="dh"><button class="x" onclick="closeDrawer()">✕</button><h3 id="dName"></h3>
  <div class="conf" id="dMeta"></div></div><div class="db" id="dBody"></div></aside>

<script>
const D = /*__PAYLOAD__*/null;
const QCOL={exposed:'#cf4a45',earning_it:'#34894b',whitespace:'#3f7fb0',sidelined:'#9aa7ad'};
const QLAB={exposed:'Exposed',earning_it:'Earning it',whitespace:'Whitespace',sidelined:'Sidelined'};
const CSIZE={high:10,medium:7.5,low:5.5};
const LAYER={1:'Carriers & syndicates',2:'MGAs & brokers',3:'Assets',4:'Capacity & reins.'};
let layerF='all', quadF='all', sortK='mos', sortDir=-1, kgTopic='all', searchQ='';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)], NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function initials(n){return (n||'?').split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();}

/* ---------- welcome modal ---------- */
(function(){
  const scrim=$('#welcome-scrim'); if(!scrim)return;
  const hide=()=>{scrim.classList.add('hidden');localStorage.setItem('nfri-welcome-seen','1');};
  if(localStorage.getItem('nfri-welcome-seen')) hide();
  $('#welcome-go')?.addEventListener('click',()=>{hide();location.hash='#cards';});
  $('#welcome-close')?.addEventListener('click',hide);
  scrim.addEventListener('click',e=>{if(e.target===scrim)hide();});
})();

/* ---------- banner + meta ---------- */
(function(){
  const pct=Math.round(D.share*100), ok=D.share>=0.60;
  $('#banner').className='banner'+(ok?' ok':'');
  $('#banner').innerHTML=`<div>${ok?'✓':'⚠'}</div><div>${ok
    ? `<b>Publishable.</b> Blended measured/disclosed share ${pct}% ≥ 60% gate.`
    : `<b>PROVISIONAL — assessed-tier prototype.</b> Blended measured/disclosed share is ${pct}%; the publication
       gate (≥60%) is not yet met, so scores are an honest research estimate, not a measurement. Direction is
       defensible; magnitudes move as live registers and filings land.`}</div>`;
  $('#meta').innerHTML=`<span><b>${D.n}</b> entities scored</span>
    <span>snapshot ${esc(D.snapshot)}</span>
    <span>median cut · exposure ≥ ${D.cal.cutExp} · prep ≥ ${D.cal.cutPrep}</span>
    <span>${D.graph.nodes.length} knowledge nodes</span>`;
})();

/* ---------- unified filter ---------- */
function filtered(){
  const q=searchQ.trim().toLowerCase();
  return D.pts.filter(p=>(layerF==='all'||p.layer==+layerF)&&(quadF==='all'||p.quad===quadF)
    &&(!q||p.name.toLowerCase().includes(q)||p.id.toLowerCase().includes(q)||(p.type||'').toLowerCase().includes(q)));
}
function sorted(list){
  const key=p=>sortK==='meas'?(p.detExp+p.detPrep)/2:p[sortK];
  return [...list].sort((a,b)=>{const x=key(a),y=key(b);return (x>y?1:x<y?-1:0)*sortDir;});
}

/* ---------- index toolbar ---------- */
(function(){
  const tb=$('#idx-toolbar'); if(!tb)return;
  tb.querySelector('#idx-search')?.addEventListener('input',e=>{searchQ=e.target.value;refreshIndex();});
  tb.querySelectorAll('.idx-btn').forEach(b=>b.onclick=()=>{
    const t=b.dataset.t,v=b.dataset.v;
    if(t==='sort'){sortK=v==='mos'?'mos':v;sortDir=-1;refreshIndex();return;}
    tb.querySelectorAll(`.idx-btn[data-t="${t}"]`).forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    if(t==='layer')layerF=v; else if(t==='quad')quadF=v;
    refreshIndex();
  });
})();

function rangeBar(p){
  const lo=Math.min(p.exp,p.prep), hi=Math.max(p.exp,p.prep), mid=(p.exp+p.prep)/2;
  return `<div class="range-wrap"><div class="range-label">Exposure · Preparedness spread</div>
    <div class="range-track" style="position:relative">
      <span class="range-tick" style="left:${p.exp}%" title="Exposure ${p.exp}"></span>
      <span class="range-tick avg" style="left:${mid.toFixed(1)}%" title="Mid ${mid.toFixed(0)}"></span>
      <span class="range-tick" style="left:${p.prep}%" title="Preparedness ${p.prep}"></span>
    </div>
    <div class="range-nums"><span>0</span><span>min ${lo.toFixed(0)} · max ${hi.toFixed(0)} · MoS ${p.mos>0?'+':''}${p.mos}</span><span>100</span></div></div>`;
}

function renderCards(){
  const list=$('#card-list'); if(!list)return; list.innerHTML='';
  const rows=sorted(filtered());
  $('#idx-count').textContent=`${rows.length} of ${D.n}`;
  rows.forEach(p=>{
    const mosCls=p.mos>=0?'pos':'neg';
    const div=document.createElement('div'); div.className='ent-card';
    div.innerHTML=`<div class="ent-id"><div class="ent-avatar">${initials(p.name)}</div>
      <div><div class="ent-name">${esc(p.name)}<span class="quad-tag" style="background:${QCOL[p.quad]}">${QLAB[p.quad]}</span></div>
      <div class="ent-meta">L${p.layer} · ${esc(LAYER[p.layer]||p.type)}</div></div></div>
      <div class="ent-scores"><div class="ent-mos ${mosCls}">${p.mos>0?'+':''}${p.mos}</div>
      <div class="ent-pair">Exp ${p.exp} · Prep ${p.prep}</div></div>`;
    div.onclick=()=>openDrawer(p.id); list.appendChild(div);
  });
}

function refreshIndex(){renderCards();draw();table();}

const shown=()=>sorted(filtered());

/* ---------- scatter ---------- */
const W=960,H=580,PAD={l:68,r:28,t:26,b:58};
const X=v=>PAD.l+(v/100)*(W-PAD.l-PAD.r), Y=v=>H-PAD.b-(v/100)*(H-PAD.t-PAD.b);
function draw(){
  const svg=$('#plot'); svg.innerHTML='';
  const mx=X(D.cal.cutExp), my=Y(D.cal.cutPrep);
  [['whitespace',PAD.l,PAD.t,mx-PAD.l,my-PAD.t],['earning_it',mx,PAD.t,X(100)-mx,my-PAD.t],
   ['sidelined',PAD.l,my,mx-PAD.l,Y(0)-my],['exposed',mx,my,X(100)-mx,Y(0)-my]]
   .forEach(([q,x,y,w,h])=>svg.appendChild(el('rect',{x,y,width:Math.max(0,w),height:Math.max(0,h),fill:QCOL[q],opacity:.06})));
  svg.appendChild(el('line',{x1:mx,y1:PAD.t,x2:mx,y2:Y(0),stroke:'#DCDCDC','stroke-dasharray':'4 4'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:my,x2:X(100),y2:my,stroke:'#DCDCDC','stroke-dasharray':'4 4'}));
  [['whitespace',PAD.l+10,PAD.t+18,'start'],['earning_it',X(100)-10,PAD.t+18,'end'],
   ['sidelined',PAD.l+10,Y(0)-12,'start'],['exposed',X(100)-10,Y(0)-12,'end']].forEach(([q,x,y,a])=>{
    const t=el('text',{x,y,'text-anchor':a,'font-size':12,'font-weight':700,fill:QCOL[q],opacity:.85});t.textContent=QLAB[q];svg.appendChild(t);});
  svg.appendChild(el('line',{x1:PAD.l,y1:Y(0),x2:X(100),y2:Y(0),stroke:'#737373'}));
  svg.appendChild(el('line',{x1:PAD.l,y1:PAD.t,x2:PAD.l,y2:Y(0),stroke:'#737373'}));
  for(let v=0;v<=100;v+=25){
    let t=el('text',{x:X(v),y:Y(0)+20,'text-anchor':'middle','font-size':11,fill:'#737373'});t.textContent=v;svg.appendChild(t);
    let u=el('text',{x:PAD.l-10,y:Y(v)+4,'text-anchor':'end','font-size':11,fill:'#737373'});u.textContent=v;svg.appendChild(u);
  }
  let ax=el('text',{x:(PAD.l+X(100))/2,y:H-14,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#141414'});ax.textContent='Exposure →';svg.appendChild(ax);
  let ay=el('text',{x:18,y:(PAD.t+Y(0))/2,'text-anchor':'middle','font-size':12.5,'font-weight':600,fill:'#141414',transform:`rotate(-90 18 ${(PAD.t+Y(0))/2})`});ay.textContent='Preparedness →';svg.appendChild(ay);
  shown().forEach(p=>{
    const g=el('g',{class:'kgnode'}), r=CSIZE[p.conf]||5.5, meas=(p.detExp+p.detPrep)/2;
    const c=el('circle',{cx:X(p.exp),cy:Y(p.prep),r,fill:QCOL[p.quad],stroke:QCOL[p.quad],'stroke-width':1.6,
      'fill-opacity':(0.18+0.82*meas).toFixed(2)});
    const t=el('text',{x:X(p.exp)+r+3,y:Y(p.prep)+3.5,'font-size':10.5,fill:'#3C3C3C'});t.textContent=shortName(p.name);
    g.appendChild(c);g.appendChild(t);
    g.style.cursor='pointer'; g.onmousemove=e=>tip(e,p); g.onmouseleave=hideTip; g.onclick=()=>openDrawer(p.id);
    svg.appendChild(g);
  });
}
function shortName(n){return n.replace(' — ',' ').replace(' (Willis Towers Watson)','').replace('Data Centres','DC').slice(0,22);}

/* ---------- tooltip ---------- */
let tipEl;
function tip(e,p){
  if(!tipEl){tipEl=document.createElement('div');tipEl.id='tip';
    tipEl.style.cssText='position:fixed;pointer-events:none;background:#fff;border:1px solid var(--line);box-shadow:0 6px 24px rgba(0,0,0,.14);border-radius:10px;padding:9px 11px;max-width:280px;font-size:12.5px;z-index:50;transition:opacity .1s';
    document.body.appendChild(tipEl);}
  tipEl.innerHTML=`<div style="font-weight:700;font-size:11px;text-transform:uppercase;color:${QCOL[p.quad]}">${QLAB[p.quad]}</div>
    <div style="font-weight:600">${esc(p.name)}</div>
    <div style="color:#647077">L${p.layer} · ${esc(p.type)} · conf ${p.conf}</div>
    <div style="margin-top:4px">Exp <b>${p.exp}</b> · Prep <b>${p.prep}</b> · MoS <b>${p.mos>0?'+':''}${p.mos}</b></div>
    <div style="color:#647077;margin-top:3px">measured ${Math.round((p.detExp+p.detPrep)/2*100)}% · click for detail</div>`;
  tipEl.style.left=Math.min(e.clientX+14,innerWidth-300)+'px';tipEl.style.top=(e.clientY+14)+'px';tipEl.style.opacity=1;
}
function hideTip(){if(tipEl)tipEl.style.opacity=0;}

/* ---------- table ---------- */
function meas(p){return (p.detExp+p.detPrep)/2;}
function table(){
  const tb=$('#tbl tbody'); tb.innerHTML='';
  shown().forEach(p=>{
    const tr=document.createElement('tr'); tr.className='row'; tr.onclick=()=>openDrawer(p.id);
    const m=Math.round(meas(p)*100);
    tr.innerHTML=`<td>${esc(p.name)}</td><td class="num">${p.layer}</td>
      <td class="num">${p.exp}</td><td class="num">${p.prep}</td>
      <td class="num"><b>${p.mos>0?'+':''}${p.mos}</b></td>
      <td><span class="pill" style="background:${QCOL[p.quad]}">${QLAB[p.quad]}</span></td>
      <td class="num"><span class="mtrack"><span class="mbar" style="width:${m}%"></span></span> ${m}%</td>
      <td class="conf">${p.conf}</td>`;
    tb.appendChild(tr);
  });
}
document.querySelectorAll('#tbl th').forEach(th=>th.onclick=()=>{
  const k=th.dataset.k; sortDir=(sortK===k)?-sortDir:(['name','quad','conf'].includes(k)?1:-1); sortK=k; table();
});

/* ---------- entity drawer ---------- */
function ratbar(v){let s='<span class="ratbar">';for(let i=0;i<4;i++)s+=`<i class="${v>i?'on':''}"></i>`;return s+'</span>';}
function sfBlock(s){
  const cites=s.cites.map(c=>`<a href="#" onclick="citePop('${c}');return false">${c}</a>`).join(' ');
  const srcs=s.sources.map(u=>`<a href="${u}" target="_blank" rel="noopener">source ↗</a>`).join(' ');
  return `<div class="sf"><div class="top"><span class="nm">${s.label}</span>
    <span class="mode ${s.mode}">${s.mode}</span><span class="w">w ${s.weight}</span></div>
    <div class="r">${esc(s.rationale)}</div>
    <div class="ev"><span class="conf">lat ${ratbar(s.lat)} · det ${s.det==null?'—':ratbar(s.det)} · <b>eff ${s.eff}</b>${s.lambda?` · λ ${s.lambda}`:''}</span>
      <span class="tier">${s.tier}</span> ${srcs} ${cites}</div></div>`;
}
function openDrawer(id){
  const p=D.pts.find(x=>x.id===id); if(!p)return;
  $('#dName').textContent=p.name;
  $('#dMeta').innerHTML=`${LAYER[p.layer]||'L'+p.layer} · ${esc(p.type)}${p.parent?' · '+esc(p.parent):''} · confidence ${p.conf}`;
  const dec=(lat,det,eff,lbl)=>`<div class="decomp"><b>${lbl}</b> latent ${lat??'—'} · deterministic ${det??'—'} → <b>${eff}</b></div>`;
  $('#dBody').innerHTML=`
    <div class="scorerow">
      <div class="s">Exposure<b>${p.exp}</b></div><div class="s">Preparedness<b>${p.prep}</b></div>
      <div class="s">Margin of Safety<b style="color:${QCOL[p.quad]}">${p.mos>0?'+':''}${p.mos}</b></div>
      <div class="s">Quadrant<b style="font-size:15px;color:${QCOL[p.quad]}">${QLAB[p.quad]}</b></div></div>
    ${dec(p.expLat,p.expDet,p.exp,'Exposure axis:')}${dec(p.prepLat,p.prepDet,p.prep,'Preparedness axis:')}
    <div class="axh"><span>Exposure sub-factors</span><span class="conf">measured ${Math.round(p.detExp*100)}%</span></div>
    ${p.exposure.map(sfBlock).join('')}
    <div class="axh"><span>Preparedness sub-factors</span><span class="conf">measured ${Math.round(p.detPrep*100)}%</span></div>
    ${p.preparedness.map(sfBlock).join('')}`;
  $('#drawer').classList.add('on'); $('#scrim').classList.add('on');
}
function closeDrawer(){$('#drawer').classList.remove('on');$('#scrim').classList.remove('on');}
function citePop(id){const c=D.cites[id];if(!c){alert(id);return;}
  alert(`${id}\n\n${c.t}\n${c.a} (${c.y})\n\n${c.use}\n\n${c.u}`);}
addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});

/* ---------- in-force rail ---------- */
$('#railcards').innerHTML=D.rail.map(r=>`<div class="rcard">
  <div style="display:flex;justify-content:space-between;align-items:baseline"><span class="id">${r.id}</span><span class="if">● in force ${r.inforce}</span></div>
  <div style="font-size:12.5px;font-weight:600;margin-top:3px">${esc(r.title)}</div>
  <p>${esc(r.reprices)}</p>
  <div class="chips"><span class="chip">re-prices · ${r.sub}</span>${r.url?`<a class="chip" href="${r.url}" target="_blank" rel="noopener">${r.cite} ↗</a>`:''}</div>
</div>`).join('');

/* ---------- knowledge graph ---------- */
(function(){
  const f=$('#kgfilters'), topics=[['all','All topics'],...D.graph.topics.map(t=>[t.id,t.label])];
  f.innerHTML=topics.map(([v,l],i)=>`<button data-v="${v}" class="${i==0?'on':''}">${l}</button>`).join('');
  f.querySelectorAll('button').forEach(b=>b.onclick=()=>{f.querySelectorAll('button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');kgTopic=b.dataset.v;drawKG();});
})();
const KTYPE={academic:'#5b6fa6',model:'#2E7D8A',register:'#3a945e',regulatory:'#b07b2e',broker:'#a05a8f',
  product:'#c2715a',industry_practice:'#7a8a93',carrier:'#9a6a12',market_guidance:'#7a8a93',cri:'#3f7fb0'};
function hash(s){let h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;return h;}
function drawKG(){
  const svg=$('#kg'); svg.innerHTML=''; const w=600,h=520,cx=w/2,cy=h/2;
  const T=D.graph.topics, ti={}; T.forEach((t,i)=>{const a=i/T.length*2*Math.PI;ti[t.id]={x:cx+Math.cos(a)*195,y:cy+Math.sin(a)*150};});
  const vis=n=>kgTopic==='all'||(n.topics||[]).includes(kgTopic);
  const pos={}, deg={};
  D.graph.edges.forEach(e=>{deg[e.from]=(deg[e.from]||0)+1;deg[e.to]=(deg[e.to]||0)+1;});
  D.graph.nodes.forEach(n=>{
    const ts=(n.topics||[]).filter(t=>ti[t]); let bx=cx,by=cy;
    if(ts.length){bx=ts.reduce((s,t)=>s+ti[t].x,0)/ts.length;by=ts.reduce((s,t)=>s+ti[t].y,0)/ts.length;}
    const hx=(hash(n.id)%100)/100-.5, hy=(hash(n.id+'y')%100)/100-.5;
    pos[n.id]={x:bx+hx*86,y:by+hy*80};
  });
  D.graph.edges.forEach(e=>{const a=pos[e.from],b=pos[e.to];if(!a||!b)return;
    if(!vis(D.graph.nodes.find(n=>n.id===e.from))&&!vis(D.graph.nodes.find(n=>n.id===e.to)))return;
    svg.appendChild(el('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:'#d3dbdd','stroke-width':1,opacity:.7}));});
  D.graph.nodes.forEach(n=>{const p=pos[n.id];if(!p)return;const on=vis(n);
    const g=el('g',{class:'kgnode',opacity:on?1:.16});
    const r=Math.min(11,4+(deg[n.id]||0)*0.9);
    g.appendChild(el('circle',{cx:p.x,cy:p.y,r,fill:KTYPE[n.type]||'#7a8a93',stroke:'#fff','stroke-width':1.4}));
    if(on&&r>=6){const t=el('text',{x:p.x+r+2,y:p.y+3});t.textContent=(n.label||n.id).slice(0,22);g.appendChild(t);}
    g.onclick=()=>kgPick(n); svg.appendChild(g);
  });
}
function kgPick(n){
  const c=n.citation_id?D.cites[n.citation_id]:null;
  $('#kgdetail').innerHTML=`<h4>${esc(n.label)}</h4>
    <div class="conf">${n.type}${n.citation_id?` · <a href="#" onclick="citePop('${n.citation_id}');return false">${n.citation_id}</a>`:''}${n.year?' · '+n.year:''}</div>
    ${c&&c.u?`<div style="margin:4px 0"><a href="${c.u}" target="_blank" rel="noopener">${esc(c.t||'source')} ↗</a></div>`:''}
    ${(n.nfri_sub_factors||[]).length?`<div class="chips" style="margin:8px 0">${n.nfri_sub_factors.map(s=>`<span class="chip">${s}</span>`).join('')}</div>`:''}
    ${(n.juice||[]).length?`<ul style="margin:8px 0 0;padding-left:18px">${n.juice.map(j=>`<li>${esc(j)}</li>`).join('')}</ul>`:''}`;
}

/* ---------- eval chips ---------- */
$('#evchips').innerHTML=D.evals.map(e=>`<span class="ev-l ${e.status}" title="${esc(e.metric)}">
  <span class="dot"></span><b>L${e.level}</b> ${e.status} · ${esc(e.name.replace(/\s*\(.*\)/,''))}</span>`).join('');

draw(); table(); renderCards(); drawKG();
</script>
</body></html>"""

if __name__ == "__main__":
    main()
