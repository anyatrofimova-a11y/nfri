#!/usr/bin/env python3
"""Build site/on-compute-markets.html — CMUI manifesto / methodology page."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import ESSAY_CSS, THESIS_CSS, collect_cite_order, load as load_contract, render_foundations, render_thesis  # noqa: E402
from compute_facts import compute_cmui_facts, load_snapshot  # noqa: E402
from design_system import load_design_system  # noqa: E402
from frontend.compute_manifesto_assemble import assemble_compute_manifesto_page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data")


def _merge_citations() -> dict:
    nfri = json.load(open(os.path.join(CT, "citations.json")))["references"]
    cmui = json.load(open(os.path.join(CT, "compute_citations.json")))["references"]
    return {**nfri, **cmui}


def _load_records() -> list[dict]:
    for name in ("compute_records.scored.json", "compute_records.json"):
        path = os.path.join(DATA, name)
        if os.path.isfile(path):
            return json.load(open(path))
    return []


def _publish_compute_data():
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    for name in ("compute_dataset.csv", "compute_records.scored.json"):
        src = os.path.join(DATA, name)
        if os.path.isfile(src):
            dst = os.path.join(SITE, "data", name)
            with open(src) as fsrc, open(dst, "w") as fdst:
                fdst.write(fsrc.read())


def build_compute_manifesto_page() -> str:
    records = _load_records()
    snapshot = load_snapshot(ROOT)
    cites_full = _merge_citations()
    contract = load_contract(os.path.join(CT, "compute_manifesto.json"))
    rubric = load_contract(os.path.join(CT, "compute_rubric.json"))

    raw = json.dumps({k: v for k, v in contract.items() if not k.startswith("_")}, ensure_ascii=False)
    cite_num = collect_cite_order([raw])
    facts = compute_cmui_facts(records, snapshot)

    ctx = {
        "num": cite_num,
        "cites": cites_full,
        "facts": facts,
        "rubric": rubric,
        "manifesto": contract.get("manifesto", {}),
        "meta": contract.get("meta", {}),
    }
    body = render_thesis(contract, ctx)
    # Append bibliography if refs block did not render inline sections only
    if "fn-list" not in body:
        body += render_foundations(ctx)

    ds = load_design_system(os.path.join(CT, "design_system.json"))
    return assemble_compute_manifesto_page(
        ds=ds,
        entity_count=facts.get("total", len(records)),
        body_html=body,
        prose_css=ESSAY_CSS,
        thesis_css=THESIS_CSS,
        fonts_url=ds["fonts"]["google_url"],
    )


def main():
    html = build_compute_manifesto_page()
    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "on-compute-markets.html")
    open(out, "w").write(html)
    _publish_compute_data()
    print(f"wrote {out}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
