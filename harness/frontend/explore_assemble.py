"""Assemble site/explore.html — card grid universe browser."""

from __future__ import annotations

import json

from frontend.chrome import FAVICON_HEAD, render_explore_hero, render_site_foot, render_splash
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.explore_template import EXPLORE_TEMPLATE


def assemble_explore_page(
    *,
    ds: dict,
    payload: dict,
    prose_css: str,
    fonts_url: str,
) -> str:
    html = EXPLORE_TEMPLATE
    html = html.replace("<!--__FAVICON__-->", FAVICON_HEAD)
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
    html = html.replace("<!--__SPLASH__-->", render_splash(ds))
    html = html.replace(
        "<!--__EXPLORE_HERO__-->",
        render_explore_hero(ds, entity_count=n, gate_pct=gate_pct),
    )
    html = html.replace(
        "<!--__SITE_FOOT__-->",
        render_site_foot(ds, entity_count=n, gate_pct=gate_pct, index_page=False),
    )
    client = CLIENT_JS.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False))
    html = html.replace("/*__CLIENT_JS__*/", client)
    return html
