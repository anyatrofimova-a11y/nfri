"""Brand, navigation, hero masthead, mobile bar."""

from __future__ import annotations


def render_splash(ds: dict) -> str:
    b = ds.get("brand") or {}
    logo = b.get("logo", "assets/princeps-logo.png")
    tag = b.get("product_label", "Non-Firm Power Risk Index")
    return (
        f'<div id="splash" class="splash" role="dialog" aria-label="Welcome">'
        f'<div class="splash-inner">'
        f'<img class="splash-logo" src="{logo}" alt="Princeps" width="320" height="64">'
        f'<p class="splash-tag type-kicker">{tag}</p>'
        f"</div></div>"
    )


def render_brand(
    ds: dict,
    *,
    href: str | None = None,
    compact: bool = False,
    size: str = "md",
) -> str:
    b = ds.get("brand") or {}
    pub, prod = b.get("publisher", "Princeps"), b.get("product", "NFRI")
    cls = "brand" + (" brand--compact" if compact else "")
    mark_cls = "brand-mark"
    if size == "lg":
        mark_cls += " lg"
    elif size == "sm":
        mark_cls += " sm"
    inner = (
        f'<span class="{mark_cls}" aria-hidden="true"></span>'
        f'<span class="brand-lockup">'
        f'<span class="brand-pub">{pub}</span>'
        f'<span class="brand-index">{prod}</span>'
        f'</span>'
    )
    label = f"{pub} {prod}"
    if href:
        return f'<a class="{cls}" href="{href}" aria-label="{label}">{inner}</a>'
    return f'<span class="{cls}" aria-label="{label}">{inner}</span>'


def render_foot_brand(ds: dict, *, entity_count: int = 0, gate_pct: int = 0) -> str:
    b = ds.get("brand") or {}
    pub = b.get("publisher", "Princeps")
    prod_label = b.get("product_label", "Non-Firm Power Risk Index")
    tag = b.get("tagline", "A Princeps research index")
    url = b.get("publisher_url", "https://princeps.dev")
    stats = ""
    if entity_count:
        stats = f" · {entity_count} entities · {gate_pct}% measured gate"
    return (
        f'<span class="foot-brand">'
        f'<span class="brand-mark sm" aria-hidden="true"></span>'
        f'<span class="foot-brand-text">'
        f'<a class="foot-pub" href="{url}" rel="noopener">{pub}</a>'
        f'<span class="foot-product">{prod_label}</span>'
        f'<span class="foot-tagline type-meta">{tag}{stats}</span>'
        f"</span></span>"
    )


def render_site_foot(
    ds: dict,
    *,
    entity_count: int = 0,
    gate_pct: int = 0,
    index_page: bool = True,
) -> str:
    brand = render_foot_brand(ds, entity_count=entity_count, gate_pct=gate_pct)
    if index_page:
        links = (
            '<a href="data/dataset.csv" download>Dataset CSV</a>'
            '<a href="data/records.optimized.json" download>Full JSON</a>'
            '<a href="methodology.html">Methodology</a>'
            '<a href="#foundations">References</a>'
        )
    else:
        links = (
            '<a href="index.html">Live index</a>'
            '<a href="methodology.html">Methodology</a>'
            '<a href="on-non-firm-risk.html">On transformation</a>'
        )
    return (
        f'<div class="site-foot-inner">{brand}'
        f'<nav class="site-foot-links" aria-label="Footer">{links}</nav></div>'
    )


def render_welcome_modal(ds: dict) -> str:
    w = ds.get("welcome_modal") or {}
    b = ds.get("brand") or {}
    title = w.get("title") or b.get("product_label", "Non-Firm Power Risk Index")
    brand = render_brand(ds, size="lg")
    return (
        f'<div id="welcome-scrim" role="dialog" aria-labelledby="welcome-title">'
        f'<div class="welcome-box">'
        f'<div class="welcome-brand">{brand}</div>'
        f'<h2 id="welcome-title">{title}</h2>'
        f'<p class="welcome-sub">{w.get("subtitle", "")}</p>'
        f'<p class="welcome-body">{w.get("body", "")}</p>'
        f'<p class="welcome-foot">{w.get("footnote", "")}</p>'
        f'<p class="welcome-tip">{w.get("tip", "")}</p>'
        f'<div class="welcome-actions">'
        f'<button type="button" class="btn-ghost" id="welcome-close">Close</button>'
        f'<button type="button" class="btn-primary" id="welcome-go">{w.get("cta", "Explore the index")}</button>'
        f"</div></div></div>"
    )


def render_site_nav(*, active: str = "index") -> str:
    links = (
        ("index.html", "Live index", "index"),
        ("methodology.html", "Methodology", "methodology"),
        ("on-non-firm-risk.html", "On transformation", "thesis"),
    )
    parts = []
    for href, label, key in links:
        cls = ' class="on"' if active == key else ""
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    return f'<nav aria-label="Site">{"".join(parts)}</nav>'


def render_main_nav() -> str:
    return (
        '<nav aria-label="Sections">'
        '<a href="#benchmark">Benchmark</a>'
        '<a href="#cards">Explore</a>'
        '<a href="#index">Scatter</a>'
        '<a href="#table">Entities</a>'
        '<a href="#argument">Manifesto</a>'
        '<a href="methodology.html">Methodology</a>'
        '<a href="#foundations">References</a>'
        '<a href="on-non-firm-risk.html">On transformation</a>'
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
        f'<a class="hero-cta-btn" href="#benchmark">Explore the index →</a>{stats}'
        f'</div></div>'
        f'</div></div></section></header>'
    )


def render_mobile_dock(ds: dict) -> str:
    return (
        f'<div class="site-dock" role="navigation" aria-label="Quick actions">'
        f'{render_brand(ds, href="#index", compact=True)}'
        f'<a class="dock-cta" href="#benchmark">Explore index</a></div>'
    )
