"""Brand, navigation, hero masthead, mobile bar."""

from __future__ import annotations


def render_brand(ds: dict, *, href: str | None = None, compact: bool = False) -> str:
    b = ds.get("brand") or {}
    pub, prod = b.get("publisher", "Princeps"), b.get("product", "NFRI")
    cls = "brand" + (" brand--compact" if compact else "")
    inner = (
        f'<span class="brand-mark" aria-hidden="true"></span>'
        f'<span class="brand-lockup">'
        f'<span class="brand-pub">{pub}</span>'
        f'<span class="brand-index">{prod}</span>'
        f'</span>'
    )
    label = f"{pub} {prod}"
    if href:
        return f'<a class="{cls}" href="{href}" aria-label="{label}">{inner}</a>'
    return f'<span class="{cls}" aria-label="{label}">{inner}</span>'


def render_main_nav() -> str:
    return (
        '<nav aria-label="Sections">'
        '<a href="#argument">Manifesto</a>'
        '<a href="#index">Scatter</a>'
        '<a href="#table">Entities</a>'
        '<a href="#foundations">References</a>'
        '<a href="#knowledge">Evidence</a>'
        '</nav>'
    )


def render_hero_gate(ds: dict, *, entity_count: int = 0, gate_pct: int = 0) -> str:
    c = ds.get("site_hero") or {}
    kicker = c.get("kicker", "")
    title = c.get("title", "")
    lede = c.get("lede", "")
    stats = (
        f'<span class="gate-stats type-meta"><b>{entity_count}</b> entities · '
        f'<b>{gate_pct}%</b> measured gate</span>'
    )
    return (
        f'<header class="gate-shell">'
        f'<div class="gate-bar"><div class="wrap">{render_brand(ds, href="#index")}{render_main_nav()}</div></div>'
        f'<section class="hero-gate" aria-label="Introduction"><div class="wrap"><div class="gate-grid">'
        f'<div class="gate-main">'
        f'<p class="hero-kicker type-kicker">{kicker}</p>'
        f'<h1 class="hero-title type-display">{title}</h1>'
        f'<p class="hero-lede type-lead">{lede}</p>'
        f'<div class="gate-foot">'
        f'<a class="hero-cta-btn" href="#index">Explore the index →</a>{stats}'
        f'</div></div>'
        f'</div></div></section></header>'
    )


def render_mobile_dock(ds: dict) -> str:
    return (
        f'<div class="site-dock" role="navigation" aria-label="Quick actions">'
        f'{render_brand(ds, href="#index", compact=True)}'
        f'<a class="dock-cta" href="#index">Explore index</a></div>'
    )
