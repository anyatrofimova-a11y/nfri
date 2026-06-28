"""Assemble the methodology tab page."""

from __future__ import annotations

import json
import re

from frontend.chrome import render_brand, render_site_foot, render_site_nav
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.methodology_template import METHODOLOGY_TEMPLATE

CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")


def _extract_toc(html: str) -> tuple[str, str]:
    m = re.search(r'(<nav class="thesis-toc"[^>]*>.*?</nav>)', html, re.DOTALL)
    if not m:
        return "", html
    toc = m.group(1)
    body = html.replace(toc, "", 1)
    return toc, body


def render_methodology_header(ds: dict, *, gate_pct: int = 0, entity_count: int = 0) -> str:
    return (
        f'<header class="gate-bar"><div class="wrap thesis-top-bar">'
        f'{render_brand(ds, product_href="index.html")}'
        f'{render_site_nav(active="methodology")}'
        f"</div></header>"
    )


def assemble_methodology_page(
    *,
    ds: dict,
    payload: dict,
    body_html: str,
    prose_css: str,
    thesis_css: str,
    fonts_url: str,
) -> str:
    toc, article_body = _extract_toc(body_html)
    html = METHODOLOGY_TEMPLATE
    html = html.replace("/*__FONTS_URL__*/", fonts_url)
    html = html.replace("/*__SITE_CSS__*/", render_site_css(ds, prose_css=prose_css + thesis_css))
    html = html.replace(
        "<!--__METHODOLOGY_HEADER__-->",
        render_methodology_header(
            ds,
            gate_pct=int(round(payload.get("share", 0) * 100)),
            entity_count=payload.get("n", 0),
        ),
    )
    html = html.replace("<!--__METHODOLOGY_TOC__-->", toc)
    html = html.replace("<!--__METHODOLOGY_BODY__-->", article_body)
    n = payload.get("n", 0)
    gate_pct = int(round(payload.get("share", 0) * 100))
    html = html.replace(
        "<!--__SITE_FOOT__-->",
        render_site_foot(ds, entity_count=n, gate_pct=gate_pct, index_page=False),
    )
    html = html.replace(
        "/*__CLIENT_JS__*/",
        CLIENT_JS.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False)),
    )
    return html
