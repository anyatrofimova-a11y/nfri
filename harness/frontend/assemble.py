"""Assemble payload + essays into site/index.html."""

from __future__ import annotations

import json
import os

from frontend.chrome import (
    render_faq_band,
    render_hero_gate,
    render_index_thesis_toc,
    render_intro_pillars,
    render_mobile_dock,
    render_site_foot,
    render_splash,
    render_trust_strip,
)
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.section_tabs import SECTION_TABS_JS
from frontend.template import PAGE_TEMPLATE
from frontend.viz_narrative import chart_narrative_ctx, render_viz_block

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTRACT = os.path.join(ROOT, "contract")


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _viz_slots(payload: dict, charts: dict) -> dict[str, str]:
    cal = payload.get("cal") or {}
    ctx = chart_narrative_ctx(
        n=payload.get("n", 0),
        cut_exp=cal.get("cutExp", 50),
        cut_prep=cal.get("cutPrep", 50),
        share=payload.get("share", 0),
        pts=payload.get("pts") or [],
    )
    reg = ((payload.get("indexCharts") or {}).get("mos_regression") or {}).get("stats") or {}
    ctx["slope"] = reg.get("slope", "—")
    ctx["r2"] = reg.get("r2", "—")
    ctx["nReg"] = reg.get("n", payload.get("n", 0))
    ids = (
        "scatter_hero", "mos_by_layer", "table_rankings",
        "bench_mos", "term_regression", "term_scoreboard",
    )
    return {cid: render_viz_block(cid, charts, ctx) for cid in ids}


def assemble_page(
    *,
    ds: dict,
    payload: dict,
    essays: dict[str, str],
    act_essays: dict[str, str] | None = None,
    foundations: str,
    prose_css: str,
    fonts_url: str,
) -> str:
    charts = (_load_json(os.path.join(CONTRACT, "chart_copy.json")).get("charts") or {})
    thesis_pres = _load_json(os.path.join(CONTRACT, "thesis_presentation.json"))
    manifesto = _load_json(os.path.join(CONTRACT, "manifesto.json"))
    viz = _viz_slots(payload, charts)

    html = PAGE_TEMPLATE
    html = html.replace("/*__FONTS_URL__*/", fonts_url)
    logo = (ds.get("brand") or {}).get("logo_lockup") or (ds.get("brand") or {}).get("logo", "assets/princeps-logo-lockup.png")
    html = html.replace(
        "<!--__SPLASH_PRELOAD__-->",
        f'<link rel="preload" href="{logo}" as="image" fetchpriority="high">',
    )
    html = html.replace("/*__SITE_CSS__*/", render_site_css(ds, prose_css=prose_css))
    n = payload.get("n", 0)
    gate_pct = int(round(payload.get("share", 0) * 100))
    cite_count = len((payload.get("cites") or {}))
    html = html.replace("<!--__SPLASH__-->", render_splash(ds))
    html = html.replace(
        "<!--__HERO_GATE__-->",
        render_hero_gate(ds, entity_count=n, gate_pct=gate_pct),
    )
    html = html.replace(
        "<!--__THESIS_TOC__-->",
        render_index_thesis_toc(thesis_pres.get("toc_labels") or []),
    )
    acts = thesis_pres.get("acts") or []
    html = html.replace(
        "<!--__INTRO_PILLARS__-->",
        render_intro_pillars(acts=acts) if acts else render_intro_pillars(manifesto.get("pillars") or []),
    )
    acts_html = act_essays or {}
    html = html.replace("<!--__ACT_INDUSTRY__-->", acts_html.get("industry", essays.get("argument", "")))
    html = html.replace("<!--__ACT_LANDSCAPE__-->", acts_html.get("landscape", ""))
    html = html.replace("<!--__ACT_MECHANICS__-->", acts_html.get("mechanics", ""))
    html = html.replace("<!--__ACT_PROPOSAL__-->", acts_html.get("proposal", essays.get("analysis", "")))
    html = html.replace("<!--__VIZ_SCATTER__-->", viz.get("scatter_hero", ""))
    html = html.replace("<!--__VIZ_LAYER__-->", viz.get("mos_by_layer", ""))
    html = html.replace("<!--__VIZ_TABLE__-->", viz.get("table_rankings", ""))
    html = html.replace("<!--__VIZ_BENCH__-->", viz.get("bench_mos", ""))
    html = html.replace("<!--__VIZ_REGRESSION__-->", viz.get("term_regression", ""))
    html = html.replace("<!--__VIZ_SCOREBOARD__-->", viz.get("term_scoreboard", ""))
    html = html.replace(
        "<!--__TRUST_STRIP__-->",
        render_trust_strip(entity_count=n, gate_pct=gate_pct, cite_count=cite_count),
    )
    faq = ds.get("objection_faq") or []
    html = html.replace("<!--__FAQ_BAND__-->", render_faq_band(faq))
    html = html.replace("<!--__MOBILE_DOCK__-->", render_mobile_dock(ds))
    html = html.replace(
        "<!--__SITE_FOOT__-->",
        render_site_foot(ds, entity_count=n, gate_pct=gate_pct, index_page=True),
    )
    for key in ("findings", "methodology", "data"):
        html = html.replace(f"<!--__{key.upper()}__-->", essays.get(key, ""))
    html = html.replace("<!--__FOUNDATIONS__-->", foundations)
    client = CLIENT_JS.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False))
    client = client + "\n" + SECTION_TABS_JS
    html = html.replace("/*__CLIENT_JS__*/", client)
    return html
