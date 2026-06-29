#!/usr/bin/env python3
"""NFRI — Essay engine (v2).

A single, general renderer for the long-form, narrative sections of the index
site (Argument, Industry analysis, Methodology, Data) plus an auto-numbered
academic / regulatory bibliography (Foundations). Content lives in versioned
contracts under contract/*.json; this module is a pure renderer.

Substantiation features:
  - Inline citation tokens {{cite:KEY}} or {{cite:KEY1,KEY2}} in any prose field
    resolve to numbered superscript footnotes linked to the Foundations list.
  - render_foundations(ctx) emits the numbered bibliography from the verified
    contract/citations.json registry — only the references actually cited.

Data-presentation features:
  - chart blocks render server-side inline SVG (no JS): evidence-tier coverage,
    quadrant distribution, sub-factor weights.

Block types:
  kicker, h, lead, p, pull, list, stat, framework, layers, table, sources,
  chart, refs

Context (ctx) threaded through render_section:
  { "num": {KEY: n}, "cites": {KEY: {...}}, "charts": {id: data} }

Usage:
  python3 harness/build_essays.py contract/analysis.json --check
  python3 harness/build_essays.py contract/methodology.json --preview
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QCLASS = {"whitespace": "whitespace", "earning_it": "earning", "sidelined": "sidelined", "exposed": "exposed"}


def _palette():
    """Quadrant and tier colors from contract/design_system.json."""
    try:
        from design_system import load_design_system
        c = load_design_system()["colors"]
    except Exception:
        c = {}
    return {
        "QCOL": {
            "exposed": c.get("exposed", "#CF4A45"),
            "earning_it": c.get("earning", "#34894B"),
            "whitespace": c.get("whitespace", "#3F7FB0"),
            "sidelined": c.get("sidelined", "#9AA7AD"),
        },
        "TIERCOL": {
            "measured": c.get("earning", "#2f9e54"),
            "disclosed": c.get("section_accent", "#3a6ea5"),
            "derived": c.get("measured", "#2E7D8A"),
            "assessed": c.get("sidelined", "#9aa7ad"),
        },
    }


try:
    from index_vocabulary import quadrant_labels, quadrant_taglines
    QLAB = quadrant_labels()
    QTAG = quadrant_taglines()
except Exception:
    QLAB = {"exposed": "Exposed", "earning_it": "Earning it", "whitespace": "Whitespace", "sidelined": "Sidelined"}
    QTAG = {"exposed": "Cleared on damage", "earning_it": "Carrying the bet", "whitespace": "Judgement surplus", "sidelined": "Off the bet"}
TIERCLASS = {"measured": "t-meas", "disclosed": "t-disc", "derived": "t-deriv", "assessed": "t-assess"}
VALID = {"kicker", "h", "lead", "p", "pull", "list", "stat", "framework", "layers",
         "table", "sources", "chart", "refs",
         "toc", "masthead", "section", "rubric_axis", "viz", "manifesto",
         "product_rail", "eval_gate", "breakdown_tabs", "act_band"}
CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")
FACT_RE = re.compile(r"\{\{fact:([a-z0-9_]+)\}\}")


def _chart_ink():
    try:
        from design_system import load_design_system
        c = load_design_system()["colors"]
        return c["content_emphasis"], c["content_default"], c["content_muted"]
    except Exception:
        return "#121210", "#3A3A38", "#6B6966"


def load(path):
    with open(path) as f:
        return json.load(f)


def apply_facts(html, ctx):
    """Replace {{fact:KEY}} tokens with live values computed from the scored
    universe (ctx['facts']). Keeps 'what the data shows' prose true to the data."""
    facts = (ctx or {}).get("facts", {})

    def repl(m):
        v = facts.get(m.group(1))
        return str(v) if v is not None else ""
    return FACT_RE.sub(repl, html)


# ---------- citation plumbing ----------

def collect_cite_order(raw_texts):
    """Scan contract source texts (in document order) for {{cite:KEY}} tokens;
    return {KEY: number} numbered by first appearance."""
    seen = []
    for t in raw_texts:
        for m in CITE_RE.finditer(t):
            for k in m.group(1).split(","):
                k = k.strip()
                if k and k not in seen:
                    seen.append(k)
    return {k: i + 1 for i, k in enumerate(seen)}


def apply_cites(html, ctx):
    if not ctx:
        return CITE_RE.sub("", html)
    num = ctx.get("num", {})

    def repl(m):
        out = []
        for k in m.group(1).split(","):
            k = k.strip()
            n = num.get(k)
            if n:
                out.append(f'<a href="#ref-{k}">{n}</a>')
        return f'<sup class="cref">{",".join(out)}</sup>' if out else ""
    return CITE_RE.sub(repl, html)


# ---------- block renderers (b, ctx) ----------

def _kicker(b, ctx):
    id_attr = f' id="{b["id"]}"' if b.get("id") else ""
    return f'<p class="arg-kicker"{id_attr}>{b["text"]}</p>'
def _h(b, ctx): return f'<h3 class="arg-h">{b["text"]}</h3>'
def _lead(b, ctx):
    return f'<p class="arg-lead{" dropcap" if b.get("dropcap") else ""}">{b["text"]}</p>'
def _p(b, ctx): return f'<p class="arg-p">{b["text"]}</p>'
def _pull(b, ctx): return f'<blockquote class="arg-pull">{b["text"]}</blockquote>'


def _act_band(b, ctx):
    rid = b.get("id", "")
    rid_attr = f' id="{rid}"' if rid else ""
    sub = b.get("subtitle", "")
    sub_html = (
        f'<p class="act-sub type-lead type-lead--muted">{sub}</p>' if sub else ""
    )
    lede = b.get("lede", "")
    lede_html = f'<p class="act-lede">{lede}</p>' if lede else ""
    title = b.get("title", "")
    accent = " act-title--accent" if title.startswith("Built for") else ""
    headline = (
        f'<div class="act-headline">'
        f'<h2 class="act-title type-title{accent}">{title}</h2>'
        f"{sub_html}</div>"
    )
    return (
        f'<div class="act-band"{rid_attr}>'
        f'<span class="act-n">{b.get("roman", "")}</span>'
        f"{headline}{lede_html}</div>"
    )
def _list(b, ctx):
    return '<ul class="arg-ul">' + "".join(f"<li>{i}</li>" for i in b.get("items", [])) + "</ul>"


def _stat(b, ctx):
    cells = "".join(
        f'<div class="st-cell"><span class="st-v">{i["value"]}</span>'
        f'<span class="st-l">{i["label"]}</span>'
        + (f'<span class="st-s">{i.get("sub")}</span>' if i.get("sub") else "") + "</div>"
        for i in b.get("items", [])
    )
    return f'<div class="st-row">{cells}</div>'


def _framework(b, ctx):
    cells = {c["quad"]: c for c in b.get("cells", [])}
    grid_pos = {"whitespace": "tl", "earning_it": "tr", "exposed": "br", "sidelined": "bl"}
    parts = []
    for q in ["whitespace", "earning_it", "exposed", "sidelined"]:
        c = cells.get(q)
        if not c:
            continue
        parts.append(f'<div class="arg-cell {QCLASS.get(q,q)} {grid_pos[q]}">'
                     f'<span class="arg-cell-tag">{c["label"]}</span><p>{c["note"]}</p></div>')
    axx = b.get("axes", {}).get("x", "Exposure →")
    axy = b.get("axes", {}).get("y", "Preparedness →")
    cap = f'<figcaption class="arg-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return ('<figure class="arg-fw"><div class="arg-fw-grid">'
            f'<span class="arg-ax arg-ax-y">{axy}</span><span class="arg-ax arg-ax-x">{axx}</span>'
            + "".join(parts) + "</div>" + cap + "</figure>")


def _layers(b, ctx):
    rows = "".join(
        f'<div class="ly-row"><div class="ly-tag">{i["tag"]}</div>'
        f'<div class="ly-body"><div class="ly-name">{i["name"]}</div>'
        f'<div class="ly-role">{i["role"]}</div>'
        + (f'<div class="ly-ex">{i.get("examples")}</div>' if i.get("examples") else "") + "</div></div>"
        for i in b.get("items", [])
    )
    cap = f'<figcaption class="arg-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return f'<div class="ly-wrap">{rows}</div>{cap}'


def _table(b, ctx):
    head = "".join(f"<th>{h}</th>" for h in b.get("head", []))
    rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b.get("rows", []))
    cap = f'<div class="tbl-cap">{b["caption"]}</div>' if b.get("caption") else ""
    note = f'<p class="tbl-note">{b["note"]}</p>' if b.get("note") else ""
    return (f'{cap}<div class="tbl-wrap"><table class="essay-tbl">'
            f'<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>{note}')


def _sources(b, ctx):
    cards = ""
    for s in b.get("items", []):
        tier = s.get("tier", "")
        ep = (f'<a class="src-ep" href="{s["endpoint"]}" target="_blank" rel="noopener">{s.get("endpoint_label","endpoint ↗")}</a>'
              if s.get("endpoint") else "")
        cards += (f'<div class="src-card"><div class="src-top">'
                  f'<span class="src-name">{s["name"]}</span>'
                  f'<span class="tier-pill {TIERCLASS.get(tier,"t-assess")}">{tier}</span></div>'
                  f'<div class="src-sub">{s.get("sub","")}</div>'
                  f'<p class="src-what">{s.get("what","")}</p>'
                  + (f'<div class="src-field">{s["field"]}</div>' if s.get("field") else "") + ep + "</div>")
    note = f'<p class="tbl-note">{b["note"]}</p>' if b.get("note") else ""
    return f'<div class="src-grid">{cards}</div>{note}'


# ---- charts (server-side inline SVG, no JS) ----

def _bar_h(label, value, pct, color, w=560, lw=190):
    """One horizontal bar row as SVG group fragment is built inline in _chart."""
    return label, value, pct, color


def _chart(b, ctx):
    kind = b.get("kind")
    if kind == "weights":
        return _chart_weights(b)
    data = (ctx or {}).get("charts", {}).get(kind, {})
    if kind == "flow":
        return _chart_flow(b, ctx)
    if kind == "boundaries":
        return _chart_boundaries(b)
    if kind == "tiers":
        return _chart_tiers(b, data)
    if kind == "quadrants":
        return _chart_quadrants(b, data)
    return ""


def _chart_caption(b, extra=""):
    cap = f'<figcaption class="ch-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return cap + extra


def _chart_tiers(b, data):
    ink, ink2, muted = _chart_ink()
    tiercol = _palette()["TIERCOL"]
    order = ["measured", "disclosed", "derived", "assessed"]
    total = sum(data.get(k, 0) for k in order) or 1
    W, H = 600, 64
    x = 0.0
    segs, leg = [], []
    for k in order:
        v = data.get(k, 0)
        frac = v / total
        wpx = frac * W
        if wpx > 0.6:
            segs.append(f'<rect x="{x:.1f}" y="22" width="{wpx:.1f}" height="26" fill="{tiercol[k]}"></rect>')
            if wpx > 46:
                segs.append(f'<text x="{x+wpx/2:.1f}" y="39" text-anchor="middle" font-size="11" '
                            f'fill="#fff" font-weight="600">{round(frac*100)}%</text>')
        x += wpx
        leg.append(f'<span class="ch-leg-i"><i style="background:{tiercol[k]}"></i>{k} · {v}</span>')
    svg = (f'<svg viewBox="0 0 {W} {H}" class="ch-svg" role="img" aria-label="Evidence-tier coverage">'
           f'<text x="0" y="14" font-size="11.5" fill="{muted}">Share of sub-factor ratings by evidence tier</text>'
           + "".join(segs) + "</svg>")
    return (f'<figure class="ch-fig">{svg}<div class="ch-leg">{"".join(leg)}</div>'
            + _chart_caption(b) + "</figure>")


def _chart_quadrants(b, data):
    ink, ink2, muted = _chart_ink()
    qcol = _palette()["QCOL"]
    order = ["earning_it", "whitespace", "sidelined", "exposed"]
    mx = max([data.get(k, 0) for k in order] + [1])
    W = 600
    bar_x = 138
    rowh = 42
    rows = []
    for i, k in enumerate(order):
        v = data.get(k, 0)
        y = 8 + i * rowh
        bw = (v / mx) * (W - bar_x - 60)
        tag = QTAG.get(k, "")
        rows.append(
            f'<text x="0" y="{y+14}" font-size="12" font-weight="600" fill="{ink}">{QLAB[k]}</text>'
            f'<text x="0" y="{y+28}" font-size="10" fill="{muted}">{tag}</text>'
            f'<rect x="{bar_x}" y="{y+8}" width="{max(bw,1):.1f}" height="16" rx="2" fill="{qcol[k]}"></rect>'
            f'<text x="{bar_x+max(bw,1)+6:.1f}" y="{y+22}" font-size="11.5" fill="{muted}" font-weight="600">{v}</text>'
        )
    svg = (f'<svg viewBox="0 0 {W} {8+len(order)*rowh+6}" class="ch-svg" role="img" '
           f'aria-label="Quadrant distribution">' + "".join(rows) + "</svg>")
    return f'<figure class="ch-fig">{svg}{_chart_caption(b)}</figure>'


def _chart_weights(b):
    """Static sub-factor weight bars; data embedded in the block as
    bars: [{group, name, weight}]."""
    bars = b.get("bars", [])
    groups = {}
    for it in bars:
        groups.setdefault(it["group"], []).append(it)
    out = []
    for g, items in groups.items():
        rows = []
        W = 560
        for it in items:
            w = it["weight"]
            bw = w * (W - 220)
            rows.append(f'<div class="wt-row"><span class="wt-name">{it["name"]}</span>'
                        f'<span class="wt-track"><span class="wt-bar" style="width:{w*100:.0f}%"></span></span>'
                        f'<span class="wt-val">{w:.2f}</span></div>')
        out.append(f'<div class="wt-group"><div class="wt-gh">{g}</div>{"".join(rows)}</div>')
    cap = f'<figcaption class="ch-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return f'<div class="wt-wrap">{"".join(out)}</div>{cap}'


def _lerp_hex(c1, c2, t):
    """Linear blend between two #rrggbb colours; t in [0,1]."""
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


def _chart_flow(b, ctx=None):
    """Stepped process flow (server-side HTML, no JS). steps: [{n, title, detail}].
    Cite tokens in detail resolve via apply_cites later."""
    steps = b.get("steps", [])
    rows = []
    for s in steps:
        rows.append(
            f'<li class="flow-step"><span class="flow-n">{s.get("n","")}</span>'
            f'<div class="flow-b"><div class="flow-t">{s.get("title","")}</div>'
            f'<p class="flow-d">{s.get("detail","")}</p></div></li>')
    return (f'<figure class="ch-fig"><ol class="flow">{"".join(rows)}</ol>'
            + _chart_caption(b) + "</figure>")


def _chart_boundaries(b):
    """Curtailment-probability heatmap bars (inline SVG). items: [{label, value(0-1), tier}].
    Bar length and colour scale with value (blue=low, red=high); dashed=derived."""
    items = list(b.get("items", []))
    items.sort(key=lambda i: i.get("value", 0), reverse=True)
    W, rowh, lw = 600, 30, 132
    rows = []
    for i, it in enumerate(items):
        v = float(it.get("value", 0))
        y = 8 + i * rowh
        bw = max(v * (W - lw - 54), 1.0)
        col = _lerp_hex("#3f7fb0", "#cf4a45", v)
        dash = ' stroke-dasharray="4 3"' if it.get("tier") == "derived" else ""
        rows.append(
            f'<text x="0" y="{y+15}" font-size="12" fill="#33474e">{it.get("label","")}</text>'
            f'<rect x="{lw}" y="{y+4}" width="{bw:.1f}" height="16" rx="3" fill="{col}"'
            f' stroke="#fff"{dash}></rect>'
            f'<text x="{lw+bw+6:.1f}" y="{y+16}" font-size="11.5" fill="#647077" '
            f'font-weight="600">{round(v*100)}%</text>')
    svg = (f'<svg viewBox="0 0 {W} {8+len(items)*rowh+6}" class="ch-svg" role="img" '
           f'aria-label="Curtailment probability by constraint boundary">' + "".join(rows) + "</svg>")
    leg = ('<div class="ch-leg"><span class="ch-leg-i"><i style="background:#3f7fb0"></i>lower</span>'
           '<span class="ch-leg-i"><i style="background:#cf4a45"></i>higher curtailment probability</span>'
           '<span class="ch-leg-i">dashed = derived</span></div>')
    return f'<figure class="ch-fig">{svg}{leg}{_chart_caption(b)}</figure>'


def _ref_link(r):
    if r.get("url"):
        return '<a href="' + r["url"] + '" target="_blank" rel="noopener">' + r["title"] + "</a>"
    return r["title"]


def _refs(b, ctx=None):
    items = "".join("<li>" + _ref_link(r) + ' <span class="arg-ref-a">' + r.get("authors", "") + "</span></li>"
                    for r in b.get("items", []))
    return f'<ul class="arg-refs">{items}</ul>'


# ---- thesis page blocks (on-transformation) ----

def _render_blocks(blocks, ctx):
    out = []
    for b in blocks or []:
        fn = _R.get(b.get("type"))
        if fn:
            out.append(fn(b, ctx))
    return "\n".join(out)


def _toc(b, ctx):
    items = "".join(
        f'<a class="thesis-toc-link" href="#{i["id"]}">{i["label"]}</a>'
        for i in b.get("items", [])
    )
    return (
        f'<div class="arena-sidebar-group">'
        f'<nav class="thesis-toc index-thesis-toc" aria-label="Contents">'
        f'<p class="arena-sidebar-label">Contents</p>{items}</nav></div>'
    )


def _masthead(b, ctx):
    meta = (ctx or {}).get("meta") or b
    if b.get("meta_key") and ctx:
        meta = ctx.get(b["meta_key"], meta)
    title = b.get("title") or meta.get("title", "")
    sub = meta.get("subtitle", "")
    authors = meta.get("authors", "")
    date = meta.get("date", "")
    date_bit = f'<span class="sep">·</span><span>{date}</span>' if date else ""
    headline = sub or title
    byline = f'<p class="arena-article-by">by <span>{authors}</span></p>' if authors else ""
    return (
        f'<header class="arena-article-head thesis-masthead">'
        f'<p class="arena-article-meta"><span>{title}</span>{date_bit}</p>'
        f'<h1 class="arena-article-title">{headline}</h1>'
        f"{byline}"
        f"</header>"
    )


def _section(b, ctx):
    kicker = b.get("kicker", "")
    inner = _render_blocks(b.get("blocks", []), ctx)
    return (
        f'<section class="thesis-section reveal" id="{b["id"]}">'
        f'<p class="arena-section-meta arg-kicker">{kicker}</p>{inner}</section>'
    )


def _rubric_axis(b, ctx):
    rubric = (ctx or {}).get("rubric", {})
    axis = rubric.get(b.get("axis", ""), {})
    if not axis:
        return ""
    rows = []
    for key, sf in axis.items():
        if key.startswith("_") or not isinstance(sf, dict):
            continue
        w = sf.get("weight", 0)
        q = sf.get("question", "")
        rows.append(
            f'<div class="rub-row"><div class="rub-head">'
            f'<span class="rub-id">{key.replace("_", " ")}</span>'
            f'<span class="rub-wt">w {w:.2f}</span></div>'
            f'<p class="rub-q">{q}</p>'
            f'<span class="wt-track"><span class="wt-bar" style="width:{w*100:.0f}%"></span></span></div>'
        )
    cap = f'<p class="arg-cap">{b["caption"]}</p>' if b.get("caption") else ""
    label = b.get("axis", "").upper()
    return f'<div class="rub-axis"><p class="rub-axis-label">{label}</p>{"".join(rows)}{cap}</div>'


def _viz(b, ctx):
    chart = b.get("chart", "")
    uid = b.get("id") or chart
    cap = f'<figcaption class="ch-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    stats_html = ""
    tc = ((ctx or {}).get("thesisCharts") or {}).get(chart, {})
    stats = tc.get("stats")
    if stats and chart == "mos_regression":
        slope_pct = stats["slope"] * 100
        stats_html = (
            f'<div class="viz-stats" data-stats="1">'
            f'<span>Slope: <b>{slope_pct:+.2f}%</b> per MoS point</span>'
            f'<span>95% CI: [{stats["ci_lo"]*100:+.2f}, {stats["ci_hi"]*100:+.2f}]</span>'
            f'<span>R²: <b>{stats["r2"]}</b></span>'
            f'<span>(n = {stats["n"]})</span></div>'
        )
    readonly = ' data-readonly="1"' if b.get("readonly") else ""
    wide = " thesis-wide" if chart in ("quadrant_scatter", "mos_regression", "carrier_swarm", "carrier_quad_stack") else ""
    return (
        f'<figure class="thesis-viz{wide}" id="viz-{uid}" data-chart="{chart}"{readonly}>'
        f'<div class="thesis-viz-mount" id="mount-{uid}"></div>{stats_html}{cap}</figure>'
    )


def _manifesto(b, ctx):
    src_key = b.get("source", "industrial_steps")
    block = ((ctx or {}).get("manifesto") or {}).get(src_key, {})
    if not block:
        return ""
    items = "".join(
        f'<div class="step-card"><span class="step-n">{i.get("n", "")}</span>'
        f'<div class="step-body"><div class="step-title">{i.get("title", "")}</div>'
        f'<p class="step-text">{i.get("text", "")}</p></div></div>'
        for i in block.get("items", [])
    )
    title = block.get("title", "")
    kicker = block.get("kicker", "")
    return (
        f'<div class="step-stack">'
        f'<p class="step-kicker type-kicker">{kicker}</p>'
        f'<h3 class="step-h">{title}</h3>{items}</div>'
    )


def _product_rail(b, ctx):
    products = ((ctx or {}).get("thesisCharts") or {}).get("products") or []
    filt = b.get("filter")
    if filt == "transformation":
        products = [p for p in products if p.get("topics")]
    cards = ""
    for p in products[:8]:
        url = p.get("url", "")
        link = f'<a href="{url}" target="_blank" rel="noopener">{p.get("citation_id", p["id"])} ↗</a>' if url else ""
        yr = f' · {p["year"]}' if p.get("year") else ""
        cards += (
            f'<div class="prod-card"><div class="prod-label">{p.get("label", "")}</div>'
            f'<div class="prod-meta">{link}{yr}</div></div>'
        )
    cap = f'<p class="ch-cap">{b["caption"]}</p>' if b.get("caption") else ""
    return f'<div class="prod-rail">{cards}</div>{cap}'


def _eval_gate(b, ctx):
    cap = f'<p class="ch-cap">{b["caption"]}</p>' if b.get("caption") else ""
    return f'<div class="thesis-eval-chips" id="thesis-eval"></div>{cap}'


def _breakdown_tabs(b, ctx):
    tabs = b.get("tabs", [])
    if not tabs:
        return ""
    seg = "".join(
        f'<button type="button" class="thesis-tab-btn{" on" if i == 0 else ""}" '
        f'data-tab="{t["id"]}">{t["label"]}</button>'
        for i, t in enumerate(tabs)
    )
    panels = "".join(
        f'<div class="thesis-tab-panel{" on" if i == 0 else ""}" data-panel="{t["id"]}">'
        f'{_render_blocks(t.get("blocks", []), ctx)}</div>'
        for i, t in enumerate(tabs)
    )
    return (
        f'<div class="thesis-tabs" data-thesis-tabs="1">'
        f'<div class="thesis-tab-seg">{seg}</div>{panels}</div>'
    )


_R = {"kicker": _kicker, "h": _h, "lead": _lead, "p": _p, "pull": _pull, "list": _list,
      "stat": _stat, "framework": _framework, "layers": _layers, "table": _table,
      "sources": _sources, "chart": _chart, "refs": _refs,
      "toc": _toc, "masthead": _masthead, "section": _section, "rubric_axis": _rubric_axis,
      "viz": _viz, "manifesto": _manifesto, "product_rail": _product_rail,
      "eval_gate": _eval_gate, "breakdown_tabs": _breakdown_tabs, "act_band": _act_band}


def _coalesce_act_bands(blocks):
    """Fold pull quotes immediately after act_band into the band lede."""
    out = []
    i = 0
    items = list(blocks or [])
    while i < len(items):
        b = items[i]
        if (
            b.get("type") == "act_band"
            and i + 1 < len(items)
            and items[i + 1].get("type") == "pull"
        ):
            merged = dict(b)
            merged["lede"] = items[i + 1].get("text", "")
            out.append(merged)
            i += 2
            continue
        out.append(b)
        i += 1
    return out


def render_blocks(blocks, ctx=None):
    out = []
    for b in _coalesce_act_bands(blocks):
        fn = _R.get(b.get("type"))
        if fn:
            out.append(fn(b, ctx))
    return apply_facts(apply_cites("\n".join(out), ctx), ctx)


def render_act(contract, act: str, ctx=None):
    blocks = [b for b in contract.get("blocks", []) if b.get("act") == act]
    return render_blocks(blocks, ctx)


def render_section(contract, ctx=None):
    html = render_blocks(contract.get("blocks", []), ctx)
    if contract.get("references"):
        html += "\n" + _refs({"items": contract["references"]}, ctx)
    return html


def render_thesis(contract, ctx=None):
    """Render long-form thesis page (on_transformation.json)."""
    ctx = dict(ctx or {})
    if contract.get("meta"):
        ctx["meta"] = contract["meta"]
    body = render_section(contract, ctx)
    return body


# ---------- the numbered bibliography ----------

TYPE_LABEL = {
    "textbook": "Textbook", "academic": "Academic", "regulatory": "Regulatory",
    "industry_research": "Industry research", "industry_standard": "Industry standard",
    "market_guidance": "Market guidance", "industry_practice": "Industry practice",
    "primary_data": "Primary data", "broker": "Broker", "carrier_research": "Carrier research",
    "mga": "MGA", "industry": "Industry", "model": "Model",
}


def render_foundations(ctx, intro=None):
    """Numbered bibliography of every reference actually cited, in citation order."""
    num = ctx.get("num", {})
    cites = ctx.get("cites", {})
    ordered = sorted(num.items(), key=lambda kv: kv[1])
    lis = []
    for key, n in ordered:
        c = cites.get(key)
        if not c:
            continue
        authors = c.get("authors", "")
        year = c.get("year", "")
        title = c.get("title", "")
        typ = TYPE_LABEL.get(c.get("type", ""), c.get("type", ""))
        url = c.get("url", "")
        use = c.get("use", "")
        title_html = (f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title)
        meta = f'{authors}{" (" + str(year) + ")" if year else ""}'
        lis.append(
            f'<li id="ref-{key}" class="fn-li"><span class="fn-n">{n}</span>'
            f'<div class="fn-body"><span class="fn-meta">{meta}</span> '
            f'<span class="fn-title">{title_html}</span> '
            f'<span class="fn-type">{typ}</span>'
            + (f'<div class="fn-use">{use}</div>' if use else "") + "</div></li>"
        )
    intro_html = f'<p class="arg-p">{intro}</p>' if intro else ""
    return intro_html + f'<ol class="fn-list">{"".join(lis)}</ol>'


def _collect_block_types(blocks, path=""):
    types = []
    for i, b in enumerate(blocks or []):
        t = b.get("type")
        types.append((f"{path}[{i}]", t))
        if t == "section":
            types.extend(_collect_block_types(b.get("blocks"), f"{path}[{i}].blocks"))
        if t == "breakdown_tabs":
            for j, tab in enumerate(b.get("tabs", [])):
                types.extend(_collect_block_types(tab.get("blocks"), f"{path}[{i}].tabs[{j}]"))
    return types


def check(contract):
    probs = []
    blocks = contract.get("blocks", [])
    if not blocks:
        probs.append("no blocks")
    for loc, t in _collect_block_types(blocks):
        if t not in VALID:
            probs.append(f"{loc}: unknown type {t!r}")
    raw = json.dumps({k: v for k, v in contract.items() if not k.startswith("_")})
    cited = set()
    for m in CITE_RE.finditer(raw):
        cited.update(k.strip() for k in m.group(1).split(","))
    from collections import Counter
    c = Counter(b.get("type") for b in blocks)
    print(f"{contract.get('section','?')} v{contract.get('version','?')} — {len(blocks)} blocks: "
          + ", ".join(f"{k}×{v}" for k, v in c.items()))
    if cited:
        print(f"inline citations: {len(cited)} → {', '.join(sorted(cited))}")
    if probs:
        print("PROBLEMS:\n  - " + "\n  - ".join(probs))
    else:
        print("OK — renderable.")
    return not probs


THESIS_CSS = r"""
  /* ===== thesis / methodology sibling pages (Arena shell) ===== */
  .site--thesis,.site--methodology{background:var(--bg-emphasis)}
  .site--thesis .thesis-section.reveal,
  .site--methodology .thesis-section.reveal,
  .site--thesis .thesis-masthead.reveal,
  .site--methodology .thesis-masthead.reveal{opacity:1;transform:none}
  .site--thesis .arena-article-head,
  .site--methodology .arena-article-head{
    padding:var(--space-lg) 0 var(--space-md);
    border-bottom:1px solid var(--line-subtle);margin:0 0 var(--space-sm);
  }
  .site--thesis .arena-article-title,
  .site--methodology .arena-article-title{max-width:none}
  .site--thesis .thesis-section,
  .site--methodology .thesis-section{
    padding-left:0;padding-right:0;
  }
  .thesis-toc-link{
    display:block;padding:3px 0;color:var(--ink2);text-decoration:none;
    font-family:var(--font-sans);font-size:0.8125rem;font-weight:400;line-height:1.35;
  }
  .thesis-toc-link:hover{color:var(--ink-headline)}
  .thesis-toc-link.on{color:var(--ink-headline);font-weight:500}
  .thesis-section{
    padding:36px 0 28px;border-bottom:1px solid var(--line-subtle);
    scroll-margin-top:calc(var(--header-h) + 12px);
  }
  .thesis-section:last-child{border-bottom:none}
  .thesis-wide{margin-left:calc(-1 * min(12vw, 8rem));margin-right:calc(-1 * min(12vw, 8rem));max-width:none}
  .thesis-viz{margin:22px 0 18px;padding:16px 18px;background:var(--bg-muted);border:1px solid var(--line-subtle);border-radius:var(--radius-sm)}
  .thesis-viz-mount{min-height:120px}
  .thesis-viz svg{width:100%;height:auto;display:block}
  .viz-stats{display:flex;flex-wrap:wrap;gap:12px 20px;margin:10px 0 4px;font-size:12.5px;color:var(--ink2);font-variant-numeric:tabular-nums}
  .viz-stats b{color:var(--ink)}
  .rub-axis{margin:16px 0 8px;padding:14px 16px;border:1px solid var(--line-subtle);border-radius:var(--radius-sm);background:var(--bg-default)}
  .rub-axis-label{font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;text-transform:uppercase;letter-spacing:var(--type-kicker-track);color:var(--accent);margin:0 0 12px}
  .rub-row{padding:10px 0;border-bottom:1px solid var(--line-subtle)}
  .rub-row:last-child{border-bottom:none}
  .rub-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
  .rub-id{font-size:13px;font-weight:600;color:var(--ink);text-transform:capitalize}
  .rub-wt{font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
  .rub-q{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);margin:0 0 8px;
  }
  .step-stack{margin:20px 0 8px}
  .step-kicker{margin:0 0 6px}
  .step-h{font-family:var(--font-essay);font-size:1.25rem;font-weight:500;margin:0 0 14px;color:var(--ink-headline)}
  .step-card{display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--line-subtle)}
  .step-card:last-child{border-bottom:none}
  .step-n{flex:0 0 2rem;font-family:var(--font-mono);font-size:13px;font-weight:600;color:var(--accent)}
  .step-title{font-family:var(--font-essay);font-weight:600;font-size:var(--type-essay-body);margin-bottom:4px}
  .step-text{
    margin:0;font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);
  }
  .prod-rail{display:flex;gap:1px;overflow-x:auto;margin:18px 0 8px;background:var(--line-subtle);border:1px solid var(--line-subtle);border-radius:var(--radius-sm)}
  .prod-card{flex:0 0 200px;padding:14px 16px;background:var(--bg-default)}
  .prod-label{font-family:var(--font-essay);font-size:var(--type-essay-body);font-weight:500;color:var(--ink-headline);line-height:1.35}
  .prod-meta{font-size:11.5px;color:var(--muted);margin-top:6px}
  .prod-meta a{color:var(--accent2);text-decoration:none}
  .thesis-tab-seg{display:flex;flex-wrap:wrap;gap:1px;margin:16px 0 18px;background:var(--line-subtle);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);padding:1px;width:fit-content;max-width:100%}
  .thesis-tab-btn{border:none;background:var(--bg-default);padding:8px 14px;font-size:12.5px;font-weight:600;color:var(--ink2);cursor:pointer;border-radius:calc(var(--radius-sm) - 1px)}
  .thesis-tab-btn.on{background:var(--bg-muted);color:var(--ink);box-shadow:inset 0 -2px 0 var(--section-accent)}
  .thesis-tab-panel{display:none}
  .thesis-tab-panel.on{display:block}
  .thesis-eval-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
  .thesis-rail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1px;margin:12px 0;background:var(--line-subtle);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);overflow:hidden}
  .thesis-gate-banner{margin:0 0 24px;padding:12px 16px;border-radius:var(--radius-sm);font-size:13px;line-height:1.45}
  .thesis-gate-banner.ok{background:var(--ok-bg);border:1px solid var(--ok-border)}
  .thesis-gate-banner.warn{background:var(--warn-bg);border:1px solid var(--warn-border)}
  @media(max-width:900px){.thesis-wide{margin-left:0;margin-right:0}}
"""


ESSAY_CSS = r"""
  /* Libre Caslon essay register — same face as Contents nav */
  .thesis-article,.thesis-section,.section.essay .prose,.section.essay .col{
    font-family:var(--font-essay);
    font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);
    color:var(--ink2);
  }
  /* process flow (mechanics / pipeline) */
  .flow{list-style:none;margin:18px 0 10px;padding:0 0 0 4px;position:relative}
  .flow:before{content:"";position:absolute;left:17px;top:14px;bottom:14px;width:2px;background:linear-gradient(var(--accent2),var(--whitespace))}
  .flow-step{display:flex;gap:14px;align-items:flex-start;padding:7px 0;position:relative}
  .flow-n{flex:0 0 28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;font-size:12.5px;font-weight:700;display:flex;align-items:center;justify-content:center;z-index:1;font-variant-numeric:tabular-nums}
  .flow-b{flex:1;border:1px solid var(--line);border-radius:12px;padding:10px 13px;background:#fff}
  .flow-t{font-weight:600;font-size:var(--type-essay-body);font-family:var(--font-essay);color:var(--ink-headline)}
  .flow-d{
    margin:4px 0 0;font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);
  }
  /* ===== essay prose — extends site type scale (.type-*) ===== */
  section.essay{padding:40px 0 38px}
  section.essay .col{max-width:none}
  .arg-kicker{
    font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;
    letter-spacing:var(--type-kicker-track);text-transform:uppercase;color:var(--accent);
    line-height:1.35;margin:32px 0 8px;
  }
  section.essay .col > .arg-kicker:first-child{margin-top:0}
  .arg-h{
    font-family:var(--font-essay);font-weight:500;
    font-size:clamp(var(--type-title-min),2.5vw,var(--type-title-max));
    line-height:var(--type-title-lead);letter-spacing:var(--type-title-track);
    margin:2px 0 14px;color:var(--ink-headline);
  }
  .arg-lead{
    font-family:var(--font-essay);font-size:var(--type-lead);line-height:var(--type-lead-lead);
    color:var(--ink2);margin:0 0 var(--essay-para-gap, 1.35em);
  }
  .arg-lead.dropcap::first-letter{
    float:left;font-family:var(--font-essay);font-size:3.75rem;line-height:.76;
    padding:4px 12px 0 0;color:var(--ink-headline);font-weight:500;
  }
  .arg-p{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);
    margin:0 0 var(--essay-para-gap, 1.35em);
  }
  .arg-p cite,.arg-p em{font-style:italic}
  .arg-pull{
    margin:22px 0;padding:4px 0 4px 16px;border-left:2px solid var(--line);
    font-family:var(--font-essay);font-size:var(--type-essay-pull);
    line-height:var(--type-essay-pull-lead);
    color:var(--ink-headline);font-style:italic;font-weight:400;
  }
  .arg-pull em{font-style:normal}
  .arg-ul{margin:6px 0 16px;padding-left:20px}
  .arg-ul li{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);margin-bottom:7px;
  }
  /* footnote markers */
  sup.cref{font-size:10px;line-height:0;font-weight:700;margin-left:1px}
  sup.cref a{color:var(--accent2);text-decoration:none;padding:0 1px}
  sup.cref a:hover{text-decoration:underline}
  /* stat row */
  .st-row{
    display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;
    margin:20px 0 22px;background:var(--line-subtle);border:1px solid var(--line-subtle);
    border-radius:var(--radius-sm);overflow:hidden;
  }
  .st-cell{padding:16px 18px;background:var(--bg-default);min-width:0}
  .st-l{font-size:14px}
  .st-s{font-size:13px;line-height:1.45}
  .st-v{display:block;font-family:var(--font-essay);font-size:26px;line-height:1;color:var(--accent);letter-spacing:-.01em;font-weight:600;font-variant-numeric:tabular-nums}
  .st-l{display:block;font-size:13px;font-weight:600;color:var(--ink);margin-top:7px}
  .st-s{display:block;font-size:12px;color:var(--muted);margin-top:3px;line-height:1.4}
  /* framework 2x2 */
  .arg-fw{margin:26px 0 22px}
  .arg-fw-grid{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:1px;padding:0;background:var(--line-subtle);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);overflow:hidden}
  .arg-cell{padding:13px 14px;background:var(--bg-default);min-height:104px}
  .arg-cell.tl,.arg-cell.tr{border-top:2px solid var(--line)}
  .arg-cell-tag{
    display:inline-block;font-family:var(--font-mono);font-size:var(--type-kicker);
    font-weight:500;text-transform:uppercase;letter-spacing:var(--type-kicker-track);
    color:var(--accent);margin-bottom:7px;
  }
  .arg-cell p{
    margin:0;font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);
  }
  .arg-cell.whitespace,.arg-cell.earning,.arg-cell.exposed,.arg-cell.sidelined{border-top:2px solid var(--line)}
  .arg-ax{position:absolute;font-size:11.5px;font-weight:600;color:var(--muted)}
  .arg-ax-x{bottom:0;left:50%;transform:translateX(-30%)}
  .arg-ax-y{top:42%;left:0;transform:rotate(-90deg) translateX(50%);transform-origin:left}
  .arg-cap{font-family:var(--font-essay);font-size:var(--type-meta);color:var(--muted);margin-top:4px}
  /* value-chain layers */
  .ly-wrap{margin:18px 0 8px;display:flex;flex-direction:column;gap:10px}
  .ly-row{display:flex;gap:13px;border-bottom:1px solid var(--line-subtle);padding:12px 0;background:transparent}
  .ly-row:last-child{border-bottom:none}
  .ly-tag{flex:0 0 54px;font-family:var(--font-mono);font-size:14px;font-weight:500;color:var(--accent);display:flex;align-items:center;justify-content:center}
  .ly-name{font-family:var(--font-essay);font-weight:600;font-size:var(--type-essay-body)}
  .ly-role{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    color:var(--ink2);margin-top:3px;line-height:var(--type-essay-lead);
  }
  .ly-ex{font-family:var(--font-essay);font-size:var(--type-meta);color:var(--muted);margin-top:5px}
  /* data tables */
  .tbl-cap{font-size:13px;font-weight:600;color:var(--ink);margin:14px 0 7px}
  .tbl-wrap{overflow-x:auto;border:1px solid var(--line-subtle);border-radius:var(--radius-sm);background:var(--bg-default)}
  table.essay-tbl{width:100%;border-collapse:collapse;font-size:13px;min-width:480px}
  table.essay-tbl th{text-align:left;font-weight:600;color:var(--muted);background:var(--bg-muted);padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
  table.essay-tbl td{padding:9px 12px;border-bottom:1px solid var(--line);color:var(--ink2);vertical-align:top;line-height:1.5}
  table.essay-tbl tr:last-child td{border-bottom:none}
  table.essay-tbl td b{color:var(--ink)}
  .tbl-note{font-size:12.5px;color:var(--muted);margin:8px 2px 0;line-height:1.5}
  /* source cards */
  .src-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:1px;margin:18px 0 6px;background:var(--line-subtle);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);overflow:hidden}
  .src-card{padding:13px 14px;background:var(--bg-default);display:flex;flex-direction:column}
  .src-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
  .src-name{font-weight:700;font-size:13.5px;color:var(--ink)}
  .tier-pill{
    font-family:var(--font-mono);font-size:var(--type-kicker);letter-spacing:var(--type-kicker-track);
    text-transform:uppercase;font-weight:500;white-space:nowrap;
  }
  .t-meas{color:var(--earning-s)}.t-disc{color:var(--section-accent)}
  .t-deriv{color:var(--accent2)}.t-assess{color:var(--muted)}
  .src-sub{font-size:var(--type-meta);color:var(--accent);font-weight:500;font-family:var(--font-mono);margin:6px 0 0}
  .src-what{font-size:12.5px;color:var(--ink2);line-height:1.5;margin:6px 0 0}
  .src-field{font-size:11.5px;color:var(--muted);font-family:var(--font-mono);background:var(--bg-muted);border-radius:var(--radius-sm);padding:5px 7px;margin-top:8px;line-height:1.4}
  .src-ep{font-size:11.5px;margin-top:8px;text-decoration:none}
  /* charts */
  .ch-fig{margin:18px 0 14px}
  .ch-svg{width:100%;height:auto;display:block}
  .ch-leg{display:flex;flex-wrap:wrap;gap:14px;margin:8px 2px 0;font-size:12px;color:var(--muted)}
  .ch-leg-i i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
  .ch-cap{font-family:var(--font-essay);font-size:var(--type-meta);color:var(--muted);margin-top:6px}
  .wt-wrap{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-md);margin:18px 0 8px}
  .wt-group{border:1px solid var(--line-subtle);border-radius:var(--radius-sm);padding:13px 14px;background:var(--bg-default)}
  .wt-gh{
    font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;
    text-transform:uppercase;letter-spacing:var(--type-kicker-track);color:var(--accent);
    margin-bottom:9px;
  }
  .wt-row{display:flex;align-items:center;gap:8px;margin-bottom:7px}
  .wt-name{flex:0 0 138px;font-size:12px;color:var(--ink2)}
  .wt-track{flex:1;height:9px;background:var(--bg-subtle);border-radius:var(--radius-sm);overflow:hidden}
  .wt-bar{display:block;height:100%;background:var(--accent2);border-radius:var(--radius-sm)}
  .wt-val{flex:0 0 34px;text-align:right;font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
  /* refs / foundations */
  .arg-refs{list-style:none;padding:14px 0 0;margin:24px 0 0;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:5px}
  .arg-refs li{font-size:13px}.arg-refs a{font-weight:600;text-decoration:none}.arg-refs a:hover{text-decoration:underline}
  .arg-ref-a{color:var(--muted)}
  .fn-list{list-style:none;counter-reset:none;padding:0;margin:14px 0 0}
  .fn-li{display:flex;gap:12px;padding:11px 0;border-bottom:1px solid var(--line);scroll-margin-top:70px}
  .ref-band .fn-list{margin-top:8px}
  .ref-band .fn-li{padding:8px 0;gap:10px}
  .fn-n{
    flex:0 0 2em;font-family:var(--font-mono);font-size:var(--type-meta);
    color:var(--muted);font-variant-numeric:tabular-nums;font-weight:500;
  }
  .ref-band .fn-n{font-size:10px}
  .fn-body{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--ink2);
  }
  .ref-band .fn-body{font-size:0.8125rem;line-height:1.5}
  .fn-meta{font-weight:600;color:var(--ink)}
  .fn-title{font-family:var(--font-essay);font-style:italic;font-weight:500}
  .fn-title a{text-decoration:none}.fn-title a:hover{text-decoration:underline}
  .fn-type{
    font-family:var(--font-mono);font-size:var(--type-kicker);text-transform:uppercase;
    letter-spacing:var(--type-kicker-track);color:var(--muted);margin-left:6px;
  }
  .fn-use{font-size:var(--type-meta);line-height:var(--type-meta-lead);color:var(--muted);margin-top:4px}
  .ref-band .fn-type{font-size:9px;letter-spacing:.06em}
  .ref-band .fn-use{font-size:11px;line-height:1.45;margin-top:3px}
  .fn-li:target{background:var(--accent-muted);padding-left:4px;padding-right:4px}
  @media(max-width:780px){.arg-lead{font-size:18px}.arg-fw-grid{grid-template-columns:1fr;padding-left:0}.arg-ax-y{display:none}.st-row{grid-template-columns:repeat(2,minmax(0,1fr))}.wt-wrap{grid-template-columns:1fr}.wt-name{flex-basis:120px}}
"""


def _preview(contract, path):
    body = render_section(contract, None)
    html = ('<!doctype html><meta charset="utf-8"><style>:root{--ink:#15282e;--ink2:#33474e;'
            '--muted:#647077;--line:#dde4e6;--bg:#fbfcfc;--accent:#1F4E5C;--accent2:#2E7D8A;'
            '--exposed:#cf4a45;--earning-s:#34894b;--whitespace:#3f7fb0;--sidelined:#9aa7ad}'
            'body{font-family:ui-sans-serif,system-ui,sans-serif;background:var(--bg);color:var(--ink);margin:0}'
            '.wrap{max-width:1120px;margin:0 auto;padding:0 22px}</style><style>' + ESSAY_CSS + '</style>'
            '<div class="wrap"><section class="essay"><div class="col">' + body + '</div></section></div>')
    out = os.path.join(ROOT, "site", os.path.basename(path).replace(".json", ".preview.html"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else os.path.join(ROOT, "contract", "argument.json")
    contract = load(path)
    if "--preview" in sys.argv:
        print("wrote", _preview(contract, path))
    else:
        sys.exit(0 if check(contract) else 1)
