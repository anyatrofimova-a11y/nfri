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
QCOL = {"exposed": "#cf4a45", "earning_it": "#34894b", "whitespace": "#3f7fb0", "sidelined": "#9aa7ad"}
QLAB = {"exposed": "Exposed", "earning_it": "Earning it", "whitespace": "Whitespace", "sidelined": "Sidelined"}
TIERCLASS = {"measured": "t-meas", "disclosed": "t-disc", "derived": "t-deriv", "assessed": "t-assess"}
TIERCOL = {"measured": "#2f9e54", "disclosed": "#3a6ea5", "derived": "#2E7D8A", "assessed": "#9aa7ad"}
VALID = {"kicker", "h", "lead", "p", "pull", "list", "stat", "framework", "layers",
         "table", "sources", "chart", "refs"}
CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")
FACT_RE = re.compile(r"\{\{fact:([a-z0-9_]+)\}\}")


def slugify(text: str) -> str:
    """URL-safe anchor from a heading string (strip inline HTML first)."""
    s = re.sub(r"<[^>]+>", "", str(text))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "section"


def collect_headings(contract) -> list[dict]:
    """Extract h-block titles (with preceding kickers) for section TOC."""
    out = []
    pending_kicker = ""
    for b in contract.get("blocks", []):
        if b.get("type") == "kicker" and b.get("text"):
            pending_kicker = b["text"]
        elif b.get("type") == "h" and b.get("text"):
            out.append({
                "id": b.get("id") or slugify(b["text"]),
                "text": b["text"],
                "kicker": pending_kicker,
            })
            pending_kicker = ""
    return out


def render_toc(headings, label="In this section") -> str:
    if not headings:
        return ""
    items = []
    for i, h in enumerate(headings, 1):
        kicker = h.get("kicker") or ""
        kicker_html = f'<span class="toc-kicker">{kicker}</span>' if kicker else ""
        items.append(
            f'<li><a class="toc-link" href="#{h["id"]}">'
            f'<span class="toc-n">{i}</span>'
            f'<span class="toc-body">{kicker_html}'
            f'<span class="toc-title">{h["text"]}</span></span></a></li>'
        )
    return (
        f'<div class="essay-toc-wrap">'
        f'<nav class="essay-toc" aria-label="{label}">'
        f'<p class="essay-toc-label">{label}</p>'
        f'<ol class="essay-toc-list">{"".join(items)}</ol>'
        f'</nav></div>'
    )


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

def _kicker(b, ctx): return f'<p class="arg-kicker">{b["text"]}</p>'
def _h(b, ctx):
    sid = b.get("id") or slugify(b["text"])
    return f'<h3 class="arg-h" id="{sid}">{b["text"]}</h3>'
def _lead(b, ctx):
    return f'<p class="arg-lead{" dropcap" if b.get("dropcap") else ""}">{b["text"]}</p>'
def _p(b, ctx): return f'<p class="arg-p">{b["text"]}</p>'
def _pull(b, ctx): return f'<blockquote class="arg-pull">{b["text"]}</blockquote>'
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
    if kind == "tiers":
        return _chart_tiers(b, data)
    if kind == "quadrants":
        return _chart_quadrants(b, data)
    return ""


def _chart_caption(b, extra=""):
    cap = f'<figcaption class="ch-cap">{b["caption"]}</figcaption>' if b.get("caption") else ""
    return cap + extra


def _chart_tiers(b, data):
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
            segs.append(f'<rect x="{x:.1f}" y="22" width="{wpx:.1f}" height="26" fill="{TIERCOL[k]}"></rect>')
            if wpx > 46:
                segs.append(f'<text x="{x+wpx/2:.1f}" y="39" text-anchor="middle" font-size="11" '
                            f'fill="#fff" font-weight="600">{round(frac*100)}%</text>')
        x += wpx
        leg.append(f'<span class="ch-leg-i"><i style="background:{TIERCOL[k]}"></i>{k} · {v}</span>')
    svg = (f'<svg viewBox="0 0 {W} {H}" class="ch-svg" role="img" aria-label="Evidence-tier coverage">'
           '<text x="0" y="14" font-size="11.5" fill="#647077">Share of sub-factor ratings by evidence tier</text>'
           + "".join(segs) + "</svg>")
    return (f'<figure class="ch-fig">{svg}<div class="ch-leg">{"".join(leg)}</div>'
            + _chart_caption(b) + "</figure>")


def _chart_quadrants(b, data):
    order = ["earning_it", "whitespace", "sidelined", "exposed"]
    mx = max([data.get(k, 0) for k in order] + [1])
    W = 600
    rowh = 30
    rows = []
    for i, k in enumerate(order):
        v = data.get(k, 0)
        y = 8 + i * rowh
        bw = (v / mx) * (W - 150)
        rows.append(f'<text x="0" y="{y+15}" font-size="12" fill="#33474e">{QLAB[k]}</text>'
                    f'<rect x="120" y="{y+4}" width="{max(bw,1):.1f}" height="16" rx="3" fill="{QCOL[k]}"></rect>'
                    f'<text x="{120+max(bw,1)+6:.1f}" y="{y+16}" font-size="11.5" fill="#647077" font-weight="600">{v}</text>')
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


def _ref_link(r):
    if r.get("url"):
        return '<a href="' + r["url"] + '" target="_blank" rel="noopener">' + r["title"] + "</a>"
    return r["title"]


def _refs(b, ctx=None):
    items = "".join("<li>" + _ref_link(r) + ' <span class="arg-ref-a">' + r.get("authors", "") + "</span></li>"
                    for r in b.get("items", []))
    return f'<ul class="arg-refs">{items}</ul>'


_R = {"kicker": _kicker, "h": _h, "lead": _lead, "p": _p, "pull": _pull, "list": _list,
      "stat": _stat, "framework": _framework, "layers": _layers, "table": _table,
      "sources": _sources, "chart": _chart, "refs": _refs}


def render_section(contract, ctx=None):
    out = []
    for b in contract.get("blocks", []):
        fn = _R.get(b.get("type"))
        if fn:
            out.append(fn(b, ctx))
    if contract.get("references"):
        out.append(_refs({"items": contract["references"]}, ctx))
    return apply_facts(apply_cites("\n".join(out), ctx), ctx)


# ---------- the numbered bibliography ----------


def _format_use(use: str) -> str:
    parts = []
    for p in (use or "").split(";"):
        p = p.strip()
        if not p:
            continue
        if not p.endswith("."):
            p += "."
        parts.append(p)
    return " ".join(parts)


def _format_citation_entry(c: dict) -> str:
    authors = c.get("authors", "")
    year = c.get("year", "")
    title = c.get("title", "")
    url = c.get("url", "")
    pub = c.get("publisher") or c.get("journal") or ""
    meta = f'{authors}{" (" + str(year) + ")" if year else ""}.'
    title_html = (
        f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title
    )
    pub_html = f' <span class="fn-pub">{pub}</span>' if pub else ""
    return f'<div class="fn-cite"><span class="fn-meta">{meta}</span> <span class="fn-title">{title_html}</span>{pub_html}</div>'


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
        use = _format_use(c.get("use", ""))
        lis.append(
            f'<li id="ref-{key}" class="fn-li"><span class="fn-n">{n}</span>'
            f'<div class="fn-body">{_format_citation_entry(c)}'
            + (f'<div class="fn-use">{use}</div>' if use else "") + "</div></li>"
        )
    intro_html = f'<p class="arg-p">{intro}</p>' if intro else ""
    return intro_html + f'<ol class="fn-list">{"".join(lis)}</ol>'


def check(contract):
    probs = []
    blocks = contract.get("blocks", [])
    if not blocks:
        probs.append("no blocks")
    for i, b in enumerate(blocks):
        if b.get("type") not in VALID:
            probs.append(f"block {i}: unknown type {b.get('type')!r}")
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


ESSAY_CSS = r"""
  section.essay{padding:0}
  section.essay .col{max-width:42rem}
  .arg-kicker{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:500;margin:var(--space-md) 0 var(--space-xs)}
  section.essay .col > .arg-kicker:first-child{margin-top:0}
  .arg-h{font-family:var(--font-display);font-size:clamp(20px,2.5vw,24px);font-weight:500;line-height:1.2;letter-spacing:-.02em;margin:0 0 var(--space-sm);color:var(--ink)}
  .arg-lead{font-size:18px;line-height:1.55;color:var(--ink);margin:0 0 var(--space-sm)}
  .arg-lead.dropcap::first-letter{float:left;font-family:var(--font-display);font-size:3.2em;line-height:.85;padding:4px 10px 0 0;color:var(--section-accent)}
  .arg-p{font-size:15px;line-height:1.62;color:var(--ink2);margin:0 0 var(--space-sm)}
  .arg-pull{margin:var(--space-md) 0;padding:0 0 0 var(--space-sm);border-left:2px solid var(--section-accent);font-family:var(--font-display);font-size:19px;line-height:1.38;color:var(--ink);font-style:italic}
  .arg-ul{margin:0 0 var(--space-sm);padding-left:18px}.arg-ul li{font-size:15px;line-height:1.55;color:var(--ink2);margin-bottom:6px}
  sup.cref{font-size:10px;line-height:0;font-weight:600;margin-left:1px}
  sup.cref a{color:var(--accent2);text-decoration:none}
  .st-row{display:flex;flex-wrap:wrap;gap:var(--space-sm);margin:var(--space-md) 0}
  .st-cell{flex:1 1 140px;border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default)}
  .st-v{display:block;font-family:var(--font-display);font-size:26px;line-height:1;color:var(--section-accent)}
  .st-l{display:block;font-size:13px;font-weight:600;color:var(--ink);margin-top:6px}
  .st-s{display:block;font-size:12px;color:var(--muted);margin-top:2px;line-height:1.4}
  .arg-fw{margin:var(--space-md) 0}
  .arg-fw-grid{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:var(--space-sm);padding:0 0 var(--space-sm) 22px}
  .arg-cell{border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default);min-height:96px}
  .arg-cell-tag{display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;padding:2px 8px;border-radius:var(--radius-pill);color:#fff;margin-bottom:6px}
  .arg-cell p{margin:0;font-size:13px;line-height:1.5;color:var(--ink2)}
  .arg-cell.whitespace .arg-cell-tag{background:var(--whitespace)}
  .arg-cell.earning .arg-cell-tag{background:var(--earning-s)}
  .arg-cell.exposed .arg-cell-tag{background:var(--exposed)}
  .arg-cell.sidelined .arg-cell-tag{background:var(--sidelined)}
  .arg-ax{position:absolute;font-size:11px;font-weight:500;color:var(--muted)}
  .arg-ax-x{bottom:0;left:50%;transform:translateX(-30%)}
  .arg-ax-y{top:42%;left:0;transform:rotate(-90deg) translateX(50%);transform-origin:left}
  .arg-cap{font-size:13px;color:var(--muted);margin-top:4px}
  .ly-wrap{margin:var(--space-sm) 0;display:flex;flex-direction:column;gap:var(--space-xs)}
  .ly-row{display:flex;gap:var(--space-sm);border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default)}
  .ly-tag{flex:0 0 48px;font-family:var(--font-display);font-size:18px;font-weight:500;color:var(--section-accent);border-right:1px solid var(--line-subtle);display:flex;align-items:center;justify-content:center}
  .ly-name{font-weight:600;font-size:14px}
  .ly-role{font-size:13px;color:var(--ink2);margin-top:2px;line-height:1.5}
  .ly-ex{font-size:12px;color:var(--muted);margin-top:4px}
  .tbl-wrap{overflow-x:auto;border:1px solid var(--line-subtle);border-radius:var(--radius-lg);background:var(--bg-default)}
  table.essay-tbl{width:100%;border-collapse:collapse;font-size:13px;min-width:480px}
  table.essay-tbl th{text-align:left;font-weight:500;color:var(--muted);background:var(--bg-muted);padding:9px 12px;border-bottom:1px solid var(--line-subtle)}
  table.essay-tbl td{padding:9px 12px;border-bottom:1px solid var(--line-subtle);color:var(--ink2);vertical-align:top;line-height:1.5}
  .src-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:var(--space-sm);margin:var(--space-sm) 0}
  .src-card{border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default)}
  .src-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
  .src-name{font-weight:600;font-size:14px;color:var(--ink)}
  .tier-pill{font-size:10px;font-weight:600;text-transform:uppercase;padding:2px 7px;border-radius:var(--radius-md)}
  .t-meas{background:var(--ok-bg);color:var(--earning-s)}.t-disc{background:#e8f0f8;color:var(--section-accent)}
  .t-deriv{background:var(--bg-muted);color:var(--measured)}.t-assess{background:var(--bg-subtle);color:var(--muted)}
  .src-sub{font-size:12px;color:var(--muted);margin-top:4px}
  .src-what{font-size:13px;color:var(--ink2);line-height:1.5;margin:6px 0 0}
  .src-field{font-size:12px;color:var(--muted);font-family:var(--font-mono);margin-top:6px}
  .tbl-cap{font-size:13px;font-weight:600;color:var(--ink);margin:var(--space-sm) 0 var(--space-xs)}
  .tbl-note{font-size:13px;color:var(--muted);margin:var(--space-xs) 0 0}
  .ch-leg{display:flex;flex-wrap:wrap;gap:var(--space-sm);margin-top:var(--space-xs);font-size:12px;color:var(--muted)}
  .wt-wrap{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-md);margin:var(--space-sm) 0}
  .wt-group{border:1px solid var(--line-subtle);border-radius:var(--radius-lg);padding:var(--space-sm);background:var(--bg-default)}
  .wt-gh{font-size:11px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:var(--space-xs)}
  .wt-row{display:flex;align-items:center;gap:8px;margin-bottom:6px}
  .wt-name{flex:0 0 120px;font-size:12px;color:var(--ink2)}
  .wt-track{flex:1;height:8px;background:var(--bg-subtle);border-radius:var(--radius-sm);overflow:hidden}
  .wt-bar{display:block;height:100%;background:var(--section-accent);border-radius:var(--radius-sm)}
  .wt-val{flex:0 0 32px;text-align:right;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
  .fn-cite{margin:0 0 4px}
  .fn-meta{font-weight:600;color:var(--ink)}
  .fn-title{font-style:italic}
  .fn-pub{color:var(--muted);font-style:normal;font-size:12px}
  .fn-use{font-size:13px;color:var(--muted);margin-top:4px;line-height:1.5}
  @media(max-width:780px){.wt-wrap{grid-template-columns:1fr}}
  .ch-fig{margin:var(--space-sm) 0}
  .ch-cap{font-size:13px;color:var(--muted);margin-top:4px}
  .arg-refs{list-style:none;padding:var(--space-md) 0 0;margin:var(--space-md) 0 0;border-top:1px solid var(--line-subtle)}
  .arg-refs li{font-size:13px;margin-bottom:4px}
  .fn-list{list-style:none;padding:0;margin:var(--space-sm) 0 0}
  .fn-li{display:flex;gap:var(--space-sm);padding:var(--space-sm) 0;border-bottom:1px solid var(--line-subtle)}
  .fn-n{flex:0 0 24px;height:24px;border-radius:50%;background:var(--bg-muted);color:var(--section-accent);font-size:11px;font-weight:600;display:flex;align-items:center;justify-content:center}
  .fn-body{font-size:13px;line-height:1.5;color:var(--ink2)}
  .essay-toc-wrap{margin-bottom:var(--space-lg)}
  .essay-toc-label{
    font-size:11px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;
    color:var(--accent);margin:0 0 var(--space-sm);
  }
  .essay-toc-list{
    list-style:none;padding:0;margin:0;
    display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,280px),1fr));
    gap:var(--space-xs);
  }
  .toc-link{
    display:flex;gap:var(--space-sm);align-items:flex-start;height:100%;
    padding:var(--space-sm);border:1px solid var(--line-subtle);border-radius:var(--radius-md);
    background:var(--bg-default);text-decoration:none;
    transition:border-color .15s,background .15s,box-shadow .15s;
  }
  .toc-link:hover,.toc-link:focus-visible{
    border-color:var(--section-accent);background:var(--bg-muted);
    outline:none;box-shadow:0 2px 8px rgba(0,0,0,.04);
  }
  .toc-n{
    flex:0 0 28px;width:28px;height:28px;border-radius:50%;
    background:var(--bg-muted);color:var(--section-accent);
    font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;
    font-variant-numeric:tabular-nums;margin-top:1px;
  }
  .toc-body{min-width:0;flex:1}
  .toc-kicker{
    display:block;font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);margin-bottom:4px;
  }
  .toc-title{
    display:block;font-family:var(--font-display);font-size:15px;font-weight:500;
    color:var(--ink);line-height:1.35;letter-spacing:-.01em;
  }
  @media(max-width:780px){.arg-fw-grid{grid-template-columns:1fr;padding-left:0}.arg-ax-y{display:none}}
"""

MANIFESTO_CSS = r"""
  /* part-band + section shells live in design_system.py */
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
