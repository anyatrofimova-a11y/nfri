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
)
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.section_tabs import SECTION_TABS_JS
from frontend.template import PAGE_TEMPLATE
from frontend.viz_narrative import (
    chart_narrative_ctx,
    render_term_panel,
    render_term_section_head,
    render_viz_block,
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTRACT = os.path.join(ROOT, "contract")


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _narrative_ctx(payload: dict) -> dict:
    cal = payload.get("cal") or {}
    pts = payload.get("pts") or []
    ctx = chart_narrative_ctx(
        n=payload.get("n", 0),
        cut_exp=cal.get("cutExp", 50),
        cut_prep=cal.get("cutPrep", 50),
        share=payload.get("share", 0),
        pts=pts,
    )
    reg = ((payload.get("indexCharts") or {}).get("mos_regression") or {}).get("stats") or {}
    ctx["slope"] = reg.get("slope", "—")
    ctx["r2"] = reg.get("r2", "—")
    ctx["nReg"] = reg.get("n", payload.get("n", 0))
    ctx["nL1"] = sum(1 for p in pts if p.get("layer") == 1)
    by_carrier = ((payload.get("indexCharts") or {}).get("carrier_swarm") or {}).get("byCarrier") or {}
    ctx["nLinkedWriters"] = len(by_carrier)
    ctx["nLinkedAssets"] = sum(len(v) for v in by_carrier.values())
    return ctx


def _viz_slots(payload: dict, charts: dict) -> dict[str, str]:
    ctx = _narrative_ctx(payload)
    ids = (
        "scatter_hero", "mos_by_layer", "table_rankings",
        "bench_mos",
    )
    out = {cid: render_viz_block(cid, charts, ctx) for cid in ids}
    scoreboard_controls = (
        '<div class="term-tabs" id="term-board-tabs">'
        '<button type="button" class="term-tab on" data-b="layer">By layer</button>'
        '<button type="button" class="term-tab" data-b="segment">By segment</button>'
        "</div>"
    )
    out["term_section"] = render_term_section_head(charts, ctx)
    out["term_regression"] = render_term_panel(
        "term_regression", charts, ctx, mount_id="term-regression", stats_id="term-reg-stats",
    )
    out["term_strategy"] = render_term_panel(
        "term_strategy", charts, ctx, mount_id="term-strategy",
    )
    out["term_scoreboard"] = render_term_panel(
        "term_scoreboard", charts, ctx, mount_id="term-scoreboard", controls=scoreboard_controls,
    )
    out["term_swarm"] = render_term_panel(
        "term_swarm", charts, ctx, mount_id="term-swarm",
    )
    out["term_quad_stack"] = render_term_panel(
        "term_quad_stack", charts, ctx, mount_id="term-quad-stack",
    )
    out["term_alpha"] = render_term_panel(
        "term_alpha", charts, ctx, mount_id="term-alpha", mount_class="term-table-wrap",
    )
    out["term_compare"] = render_term_panel(
        "term_compare", charts, ctx, mount_id="term-compare", mount_class="term-table-wrap",
        controls='<div class="term-compare-pick" id="term-compare-pick"></div>',
    )
    return out


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
    tri = (ds.get("brand") or {}).get("glyph") or (ds.get("brand") or {}).get(
        "triquetra", "assets/brand/princeps-glyph.png"
    )
    html = html.replace(
        "<!--__SPLASH_PRELOAD__-->",
        f'<link rel="preload" href="{tri}" as="image" fetchpriority="high">',
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
    acts_html = act_essays or {}
    html = html.replace("<!--__ACT_INDUSTRY__-->", acts_html.get("industry", essays.get("argument", "")))
    html = html.replace("<!--__ACT_LANDSCAPE__-->", acts_html.get("landscape", ""))
    html = html.replace("<!--__ACT_MECHANICS__-->", acts_html.get("mechanics", ""))
    html = html.replace("<!--__ACT_PROPOSAL__-->", acts_html.get("proposal", essays.get("analysis", "")))
    html = html.replace("<!--__VIZ_SCATTER__-->", viz.get("scatter_hero", ""))
    html = html.replace("<!--__VIZ_LAYER__-->", viz.get("mos_by_layer", ""))
    html = html.replace("<!--__VIZ_TABLE__-->", viz.get("table_rankings", ""))
    html = html.replace("<!--__VIZ_BENCH__-->", viz.get("bench_mos", ""))
    html = html.replace("<!--__TERM_SECTION__-->", viz.get("term_section", ""))
    html = html.replace("<!--__TERM_REGRESSION__-->", viz.get("term_regression", ""))
    html = html.replace("<!--__TERM_STRATEGY__-->", viz.get("term_strategy", ""))
    html = html.replace("<!--__TERM_SCOREBOARD__-->", viz.get("term_scoreboard", ""))
    html = html.replace("<!--__TERM_SWARM__-->", viz.get("term_swarm", ""))
    html = html.replace("<!--__TERM_QUAD__-->", viz.get("term_quad_stack", ""))
    html = html.replace("<!--__TERM_ALPHA__-->", viz.get("term_alpha", ""))
    html = html.replace("<!--__TERM_COMPARE__-->", viz.get("term_compare", ""))
    html = html.replace("<!--__TRUST_STRIP__-->", "")
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
