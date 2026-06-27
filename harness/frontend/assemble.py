"""Assemble payload + essays into site/index.html."""

from __future__ import annotations

import json

from frontend.chrome import render_hero_gate, render_mobile_dock
from frontend.client import CLIENT_JS
from frontend.css import render_site_css
from frontend.template import PAGE_TEMPLATE


def assemble_page(
    *,
    ds: dict,
    payload: dict,
    essays: dict[str, str],
    foundations: str,
    prose_css: str,
    fonts_url: str,
) -> str:
    html = PAGE_TEMPLATE
    html = html.replace("/*__FONTS_URL__*/", fonts_url)
    html = html.replace("/*__SITE_CSS__*/", render_site_css(ds, prose_css=prose_css))
    html = html.replace("<!--__HERO_GATE__-->", render_hero_gate(
        ds, entity_count=payload.get("n", 0), gate_pct=int(round(payload.get("share", 0) * 100)),
    ))
    html = html.replace("<!--__MOBILE_DOCK__-->", render_mobile_dock(ds))
    for key in ("argument", "analysis", "findings", "methodology", "data"):
        html = html.replace(f"<!--__{key.upper()}__-->", essays.get(key, ""))
    html = html.replace("<!--__FOUNDATIONS__-->", foundations)
    html = html.replace("/*__CLIENT_JS__*/", CLIENT_JS.replace("/*__PAYLOAD__*/null", json.dumps(payload, ensure_ascii=False)))
    return html
