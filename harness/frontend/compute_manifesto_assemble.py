"""Assemble the CMUI manifesto page (static prose, no scatter client)."""

from __future__ import annotations

import re

from frontend.chrome import FAVICON_HEAD, render_arena_methodology_sidebar, render_site_foot, render_thesis_utility
from frontend.compute_manifesto_template import COMPUTE_MANIFESTO_TEMPLATE
from frontend.css import render_site_css


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


def assemble_compute_manifesto_page(
    *,
    ds: dict,
    entity_count: int,
    body_html: str,
    prose_css: str,
    thesis_css: str,
    fonts_url: str,
) -> str:
    toc, article_body = _extract_toc(body_html)
    html = COMPUTE_MANIFESTO_TEMPLATE
    html = html.replace("<!--__FAVICON__-->", FAVICON_HEAD)
    html = html.replace("/*__FONTS_URL__*/", fonts_url)
    html = html.replace("/*__SITE_CSS__*/", render_site_css(ds, prose_css=prose_css + thesis_css))
    html = html.replace(
        "<!--__COMPUTE_HEADER__-->",
        render_thesis_utility(ds, entity_count=entity_count, active="compute"),
    )
    html = html.replace("<!--__COMPUTE_SIDEBAR__-->", render_arena_methodology_sidebar(ds, toc))
    html = html.replace("<!--__COMPUTE_BODY__-->", article_body)
    html = html.replace(
        "<!--__SITE_FOOT__-->",
        render_site_foot(ds, entity_count=entity_count, gate_pct=0, index_page=False),
    )
    return html
