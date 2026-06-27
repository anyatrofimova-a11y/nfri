#!/usr/bin/env python3
"""Build site/methodology.html — scoring model + pipeline tab."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import THESIS_CSS, ESSAY_CSS, collect_cite_order, load as load_contract, render_thesis  # noqa: E402
from design_system import load_design_system  # noqa: E402
from findings_facts import compute_facts  # noqa: E402
from frontend.methodology_assemble import assemble_methodology_page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
SITE = os.path.join(ROOT, "site")


def build_methodology_page(*, records=None, pts=None, share=None, payload_base=None) -> str:
    """Render methodology tab HTML. Accepts pre-built payload fragments from build_frontend."""
    from build_frontend import (  # noqa: WPS433 — avoid circular import at module load
        RAIL,
        authoritative_share,
        build_points,
        compute_charts,
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
    cites_full = json.load(open(os.path.join(CT, "citations.json")))["references"]
    cites = {k: {"t": v.get("title", ""), "a": v.get("authors", ""), "y": v.get("year", ""),
                 "u": v.get("url", ""), "use": v.get("use", "")} for k, v in cites_full.items()}
    rail = [dict(r, url=cites.get(r["cite"], {}).get("u", "")) for r in RAIL]
    evals = parse_eval_report()
    charts = compute_charts(records)

    payload = dict(payload_base or {})
    payload.update({
        "pts": pts,
        "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "share": share,
        "n": len(pts),
        "evals": evals,
        "rail": rail,
        "cites": cites,
        "sfLabels": payload.get("sfLabels", {}),
    })

    contract = load_contract(os.path.join(CT, "methodology_tab.json"))
    rubric = load_contract(os.path.join(CT, "rubric.json"))
    raw = json.dumps({k: v for k, v in contract.items() if not k.startswith("_")}, ensure_ascii=False)
    cite_num = collect_cite_order([raw])
    ctx = {
        "num": cite_num,
        "cites": cites_full,
        "facts": compute_facts(records, share),
        "rubric": rubric,
        "meta": contract.get("meta", {}),
        "charts": charts,
    }
    body = render_thesis(contract, ctx)
    ds = load_design_system(os.path.join(ROOT, "contract", "design_system.json"))
    return assemble_methodology_page(
        ds=ds,
        payload=payload,
        body_html=body,
        prose_css=ESSAY_CSS,
        thesis_css=THESIS_CSS,
        fonts_url=ds["fonts"]["google_url"],
    )


def main():
    html = build_methodology_page()
    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "methodology.html")
    open(out, "w").write(html)
    print(f"wrote {out}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
