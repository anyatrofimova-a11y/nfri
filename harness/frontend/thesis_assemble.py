"""Assemble the on-transformation thesis page."""

from __future__ import annotations

import json
import re

from frontend.chrome import render_brand
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.thesis_template import THESIS_TEMPLATE

CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")


def _extract_toc(html: str) -> tuple[str, str]:
    m = re.search(r'(<nav class="thesis-toc"[^>]*>.*?</nav>)', html, re.DOTALL)
    if not m:
        return "", html
    toc = m.group(1)
    body = html.replace(toc, "", 1)
    return toc, body


def render_thesis_header(ds: dict, *, gate_pct: int, entity_count: int) -> str:
    ok = gate_pct >= 60
    banner_cls = "ok" if ok else "warn"
    banner = (
        f'<div class="thesis-gate-banner {banner_cls}">'
        f'<b>{"Measured" if ok else "Provisional"}.</b> '
        f'{gate_pct}% blended measured/disclosed share · {entity_count} entities scored.'
        f"</div>"
    )
    return (
        f'<header class="gate-bar"><div class="wrap thesis-top-bar">'
        f'{render_brand(ds, href="index.html")}'
        f'<nav aria-label="Site"><a href="index.html">Live index</a></nav>'
        f"</div></header>"
        f'<div class="wrap">{banner}</div>'
    )


def assemble_thesis_page(
    *,
    ds: dict,
    payload: dict,
    body_html: str,
    prose_css: str,
    thesis_css: str,
    fonts_url: str,
) -> str:
    toc, article_body = _extract_toc(body_html)
    html = THESIS_TEMPLATE
    html = html.replace("/*__FONTS_URL__*/", fonts_url)
    html = html.replace("/*__SITE_CSS__*/", render_site_css(ds, prose_css=prose_css + thesis_css))
    html = html.replace(
        "<!--__THESIS_HEADER__-->",
        render_thesis_header(
            ds,
            gate_pct=int(round(payload.get("share", 0) * 100)),
            entity_count=payload.get("n", 0),
        ),
    )
    html = html.replace("<!--__THESIS_TOC__-->", toc)
    html = html.replace("<!--__THESIS_BODY__-->", article_body)
    html = html.replace(
        "/*__CLIENT_JS__*/",
        CLIENT_JS.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False)),
    )
    return html
