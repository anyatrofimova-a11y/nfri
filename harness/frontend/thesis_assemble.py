"""Assemble the on-transformation thesis page."""

from __future__ import annotations

import json
import re

from frontend.chrome import FAVICON_HEAD, render_arena_thesis_sidebar, render_site_foot, render_thesis_utility
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.thesis_template import THESIS_TEMPLATE

CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")


def _extract_toc(html: str) -> tuple[str, str]:
    m = re.search(
        r'(<div class="arena-sidebar-group">\s*<nav class="thesis-toc[^"]*"[^>]*>.*?</nav>\s*</div>)',
        html,
        re.DOTALL,
    )
    if not m:
        m = re.search(r'(<nav class="thesis-toc[^"]*"[^>]*>.*?</nav>)', html, re.DOTALL)
    if not m:
        return "", html
    toc = m.group(1)
    body = html.replace(toc, "", 1)
    return toc, body


def render_thesis_header(ds: dict, *, gate_pct: int = 0, entity_count: int = 0) -> str:
    return render_thesis_utility(ds, gate_pct=gate_pct, entity_count=entity_count, active="thesis")


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
    html = html.replace("<!--__FAVICON__-->", FAVICON_HEAD)
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
    html = html.replace("<!--__THESIS_SIDEBAR__-->", render_arena_thesis_sidebar(ds, toc))
    html = html.replace("<!--__THESIS_TOC__-->", "")
    html = html.replace("<!--__THESIS_BODY__-->", article_body)
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
