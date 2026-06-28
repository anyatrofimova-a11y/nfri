"""Brand, navigation, hero masthead, mobile bar."""

from __future__ import annotations


def _brand(ds: dict) -> dict:
    return ds.get("brand") or {}


def _glyph_src(b: dict) -> str:
    return b.get("glyph") or b.get("triquetra", "assets/brand/princeps-glyph.png")


def _wordmark_img(b: dict, key: str | None, *, cls: str, height: int, alt: str = "PRINCEPS") -> str | None:
    if not key or not b.get(f"{key}_ready"):
        return None
    src = b.get(key)
    if not src:
        return None
    return (
        f'<img class="{cls}" src="{src}" alt="{alt}" height="{height}"'
        f' decoding="async" fetchpriority="high">'
    )


def _publisher_markup(b: dict, *, compact: bool = False, splash: bool = False) -> str:
    pub = b.get("publisher", "PRINCEPS")
    if splash:
        stacked = _wordmark_img(
            b, b.get("splash_wordmark_key"), cls="splash-wordmark", height=48, alt=pub
        )
        if stacked:
            return stacked
    horizontal = _wordmark_img(
        b,
        b.get("header_wordmark_key", "wordmark_horizontal"),
        cls="splash-wordmark" if splash else "brand-wordmark",
        height=48 if splash else (13 if compact else 15),
        alt=pub,
    )
    if horizontal:
        return horizontal
    return f'<span class="brand-pub">{pub}</span>'


def render_splash(ds: dict) -> str:
    b = _brand(ds)
    tri = _glyph_src(b)
    tag = b.get("product_label", "Non-Firm Power Risk Index")
    pub = b.get("publisher", "PRINCEPS")
    stacked_ready = bool(
        b.get("splash_wordmark_key")
        and b.get(f'{b.get("splash_wordmark_key")}_ready')
    )
    if stacked_ready:
        inner = (
            f'{_publisher_markup(b, splash=True)}'
            f'<p class="splash-tag type-kicker">{tag}</p>'
        )
    else:
        inner = (
            f'<img class="splash-glyph" src="{tri}" alt="" width="72" height="72" aria-hidden="true"'
            f' fetchpriority="high" decoding="async">'
            f'{_publisher_markup(b, splash=True)}'
            f'<p class="splash-tag type-kicker">{tag}</p>'
        )
    return (
        f'<div id="splash" class="splash" role="dialog" aria-label="Welcome">'
        f'<div class="splash-inner">{inner}</div></div>'
    )


def render_brand(
    ds: dict,
    *,
    href: str | None = None,
    compact: bool = False,
    size: str = "md",
) -> str:
    b = _brand(ds)
    pub, prod = b.get("publisher", "PRINCEPS"), b.get("product", "Non-Firm Power Risk Index")
    tri = _glyph_src(b)
    cls = "brand" + (" brand--compact" if compact else "")
    glyph_px = 40 if size == "lg" else (24 if size == "sm" else 32)
    lockup = (
        f'<span class="brand-lockup">'
        f'{_publisher_markup(b, compact=compact)}'
        f'<span class="brand-index">{prod}</span>'
        f"</span>"
    )
    if compact:
        inner = (
            f'<img class="brand-glyph" src="{tri}" alt="" width="{glyph_px}" height="{glyph_px}"'
            f' aria-hidden="true" decoding="async">'
            f'{lockup}'
        )
    else:
        inner = (
            f'<img class="brand-glyph" src="{tri}" alt="" width="{glyph_px}" height="{glyph_px}"'
            f' aria-hidden="true" decoding="async" fetchpriority="high">'
            f'{lockup}'
        )
    label = f"{pub} {prod}"
    if href:
        return f'<a class="{cls}" href="{href}" aria-label="{label}">{inner}</a>'
    return f'<span class="{cls}" aria-label="{label}">{inner}</span>'


def render_foot_brand(ds: dict, *, entity_count: int = 0, gate_pct: int = 0) -> str:
    b = _brand(ds)
    pub = b.get("publisher", "PRINCEPS")
    prod_label = b.get("product_label", "Non-Firm Power Risk Index")
    url = b.get("publisher_url", "https://princeps.dev")
    tri = _glyph_src(b)
    producer = b.get("producer") or {}
    credit = producer.get("credit", "")
    linkedin_url = producer.get("linkedin_url", "")
    linkedin_label = producer.get("linkedin_label", "LinkedIn")
    rights = producer.get("rights", "all rights reserved")
    producer_html = ""
    if credit:
        producer_html += f'<span class="foot-producer type-meta">{credit}</span>'
    if linkedin_url:
        producer_html += (
            f'<a class="foot-linkedin type-meta" href="{linkedin_url}" rel="noopener noreferrer">'
            f"{linkedin_label}</a>"
        )
    if rights:
        producer_html += f'<span class="foot-rights type-meta">{rights}</span>'
    wm = _wordmark_img(
        b, b.get("header_wordmark_key", "wordmark_horizontal"), cls="foot-wordmark", height=14, alt=pub
    )
    if wm:
        pub_html = f'<a class="foot-pub foot-pub--img" href="{url}" rel="noopener">{wm}</a>'
    else:
        pub_html = f'<a class="foot-pub" href="{url}" rel="noopener">{pub}</a>'
    return (
        f'<span class="foot-brand">'
        f'<img class="brand-glyph" src="{tri}" alt="" width="22" height="22" aria-hidden="true">'
        f'<span class="foot-brand-text">'
        f'{pub_html}'
        f'<span class="foot-product">{prod_label}</span>'
        f"{producer_html}"
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


def render_section_tabs(ds: dict) -> str:
    tabs = ds.get("section_tabs") or [
        {"href": "#act-industry", "label": "Thesis"},
        {"href": "#index", "label": "Landscape"},
        {"href": "#act-proposal", "label": "Argument"},
        {"href": "#rankings", "label": "Rankings"},
        {"href": "#reference", "label": "Reference"},
        {"href": "#analytics-deep", "label": "Analytics"},
    ]
    links = "".join(
        f'<a class="section-tab" href="{t["href"]}">{t["label"]}</a>'
        for t in tabs
    )
    return (
        f'<nav id="section-tabs" class="section-tabs" aria-label="Page sections">'
        f"{links}</nav>"
    )


def render_index_thesis_toc(toc_labels: list[dict]) -> str:
    items = []
    for item in toc_labels:
        sub = item.get("sub")
        cls = "thesis-toc-link index-thesis-toc-link" + (" sub" if sub else "")
        items.append(f'<a class="{cls}" href="{item["href"]}">{item["label"]}</a>')
    return (
        f'<nav class="index-thesis-toc thesis-toc" aria-label="Contents">'
        f'<p class="thesis-toc-kicker type-kicker">Contents</p>'
        f"{''.join(items)}</nav>"
    )


def render_intro_pillars(pillars: list[dict] | None = None, *, acts: list[dict] | None = None) -> str:
    items = acts if acts else pillars
    if not items:
        return ""
    if acts:
        cards = "".join(
            f'<article class="intro-pillar">'
            f'<p class="intro-pillar-n">{a.get("roman", "")}</p>'
            f'<h3 class="intro-pillar-title">{a.get("title", "")}</h3>'
            f'<p class="intro-pillar-text">{a.get("subtitle", "")}</p>'
            f"</article>"
            for a in acts
        )
    else:
        cards = "".join(
            f'<article class="intro-pillar">'
            f'<p class="intro-pillar-n">{p.get("n", "")}</p>'
            f'<h3 class="intro-pillar-title">{p.get("title", "")}</h3>'
            f'<p class="intro-pillar-text">{p.get("text", "")}</p>'
            f"</article>"
            for p in pillars or []
        )
    return f'<div class="intro-pillar-grid">{cards}</div>'


def render_trust_strip(*, entity_count: int, gate_pct: int, cite_count: int = 0) -> str:
    gate = "Measured" if gate_pct >= 60 else "Provisional"
    cites = f' · <span class="trust-strip-item"><b>{cite_count}</b> cited sources</span>' if cite_count else ""
    return (
        f'<div class="trust-strip">'
        f'<div class="wrap trust-strip-inner">'
        f'<span class="trust-strip-item"><b>{entity_count}</b> scored entities</span>'
        f'<span class="trust-strip-item"><b>{gate_pct}%</b> measured gate · {gate}</span>'
        f'<span class="trust-strip-item">Every sub-factor traces to a register or filing</span>'
        f"{cites}</div></div>"
    )


def render_faq_band(faq: list[dict]) -> str:
    if not faq:
        return ""
    items = []
    for q in faq:
        body = q.get("paragraphs") or []
        if not body and q.get("a"):
            body = [p.strip() for p in str(q["a"]).split("\n\n") if p.strip()]
        paras = "".join(f"<p>{p}</p>" for p in body)
        items.append(
            f'<details class="faq-item">'
            f'<summary>{q.get("q", "")}</summary>'
            f'<div class="faq-body">{paras}</div>'
            f"</details>"
        )
    return (
        f'<div class="faq-band faq-band--compact">'
        f'<p class="section-kicker type-kicker">Objections</p>'
        f'<div class="faq-list">{"".join(items)}</div></div>'
    )


def render_hero_gate(ds: dict, *, entity_count: int = 0, gate_pct: int = 0) -> str:
    c = ds.get("site_hero") or {}
    kicker = c.get("kicker", "")
    title = c.get("title", "")
    lede = c.get("lede", "")
    return (
        f'<header class="gate-shell">'
        f'<div class="gate-bar"><div class="wrap">{render_brand(ds, href="index.html")}'
        f'<nav class="gate-nav" aria-label="Site">'
        f'<a class="section-tab" href="on-non-firm-risk.html">Full thesis</a>'
        f'<a class="section-tab" href="methodology.html">Methodology</a>'
        f"</nav></div></div>"
        f'<div class="section-tabs-wrap"><div class="wrap">{render_section_tabs(ds)}</div></div>'
        f"</header>"
        f'<section class="hero-gate" aria-label="Introduction"><div class="wrap"><div class="gate-grid">'
        f'<div class="gate-main">'
        f'<h1 class="hero-title hero-title--sr">{title}</h1>'
        f'<p class="hero-kicker type-kicker">{kicker}</p>'
        f'<p class="hero-lede type-lead">{lede}</p>'
        f'<div class="gate-foot">'
        f'<a class="hero-cta-btn" href="#argument">Read the thesis →</a>'
        f'<a class="hero-cta-btn hero-cta-btn--ghost" href="on-non-firm-risk.html">Full essay →</a>'
        f'<span class="gate-stats type-meta"><b>{entity_count}</b> entities · '
        f'<b>{gate_pct}%</b> measured gate</span>'
        f"</div></div>"
        f"</div></div></section>"
    )


def render_mobile_dock(ds: dict) -> str:
    return (
        f'<div class="site-dock" role="navigation" aria-label="Quick actions">'
        f'{render_brand(ds, href="#index", compact=True)}'
        f'<a class="dock-cta" href="#argument">Read thesis</a></div>'
    )
