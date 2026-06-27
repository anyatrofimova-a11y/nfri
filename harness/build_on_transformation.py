#!/usr/bin/env python3
"""Build site/on-non-firm-risk.html — long-form transformation thesis page."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import THESIS_CSS, ESSAY_CSS, collect_cite_order, load as load_contract, render_thesis  # noqa: E402
from compute_thesis_charts import compute_thesis_charts  # noqa: E402
from design_system import load_design_system  # noqa: E402
from findings_facts import compute_facts  # noqa: E402
from frontend.thesis_assemble import assemble_thesis_page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
SITE = os.path.join(ROOT, "site")
KNOW = os.path.join(ROOT, "contract", "knowledge")


def build_thesis_page(*, records=None, pts=None, share=None, payload_base=None) -> str:
    """Render thesis HTML. Accepts pre-built payload fragments from build_frontend."""
    from build_frontend import (  # noqa: WPS433 — avoid circular import at module load
        RAIL,
        authoritative_share,
        build_points,
        load_records,
        parse_calibration,
        parse_eval_report,
    )
    if records is None or pts is None:
        records, _ = load_records()
        pts = build_points(records)
    if share is None:
        _mp = os.path.join(ROOT, "data", "records.measured.json")
        tier_src = json.load(open(_mp)) if os.path.exists(_mp) else records
        share = authoritative_share(tier_src)
    cut_exp, cut_prep = parse_calibration((records[0].get("scores") or {}).get("calibration"))
    graph = json.load(open(os.path.join(KNOW, "graph.json"))) if os.path.exists(os.path.join(KNOW, "graph.json")) else {}
    cites_full = json.load(open(os.path.join(CT, "citations.json")))["references"]
    cites = {k: {"t": v.get("title", ""), "a": v.get("authors", ""), "y": v.get("year", ""),
                 "u": v.get("url", ""), "use": v.get("use", "")} for k, v in cites_full.items()}
    rail = [dict(r, url=cites.get(r["cite"], {}).get("u", "")) for r in RAIL]
    evals = parse_eval_report()
    thesis_charts = compute_thesis_charts(pts, graph)

    payload = payload_base or {}
    payload.update({
        "pts": pts,
        "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "share": share,
        "n": len(pts),
        "evals": evals,
        "rail": rail,
        "cites": cites,
        "thesisCharts": thesis_charts,
        "sfLabels": payload.get("sfLabels", {}),
    })

    contract = load_contract(os.path.join(CT, "on_transformation.json"))
    rubric = load_contract(os.path.join(CT, "rubric.json"))
    manifesto = load_contract(os.path.join(CT, "manifesto.json"))
    raw = json.dumps({k: v for k, v in contract.items() if not k.startswith("_")}, ensure_ascii=False)
    cite_num = collect_cite_order([raw])
    ctx = {
        "num": cite_num,
        "cites": cites_full,
        "facts": compute_facts(records, share),
        "rubric": rubric,
        "manifesto": manifesto,
        "meta": contract.get("meta", {}),
        "thesisCharts": thesis_charts,
        "charts": {"tiers": thesis_charts.get("tiers", {}), "quadrants": thesis_charts.get("quadrants", {})},
    }
    body = render_thesis(contract, ctx)
    ds = load_design_system(os.path.join(ROOT, "contract", "design_system.json"))
    return assemble_thesis_page(
        ds=ds,
        payload=payload,
        body_html=body,
        prose_css=ESSAY_CSS,
        thesis_css=THESIS_CSS,
        fonts_url=ds["fonts"]["google_url"],
    )


def main():
    html = build_thesis_page()
    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "on-non-firm-risk.html")
    open(out, "w").write(html)
    print(f"wrote {out}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
