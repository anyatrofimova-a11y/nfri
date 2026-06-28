"""Brand, navigation, hero masthead, mobile bar."""

from __future__ import annotations

_LINKEDIN_ICON = (
    '<svg class="foot-social-icon" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">'
    '<path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'
    "</svg>"
)
_X_ICON = (
    '<svg class="foot-social-icon" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">'
    '<path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>'
    "</svg>"
)


def _foot_social_link(url: str, icon: str, label: str) -> str:
    return (
        f'<a class="foot-social" href="{url}" rel="noopener noreferrer"'
        f' aria-label="{label}">{icon}</a>'
    )


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


def _wordmark_ready(b: dict, key: str | None) -> bool:
    return bool(key and b.get(f"{key}_ready"))


def _glyph_img(
    b: dict,
    *,
    cls: str,
    width: int,
    height: int,
    wordmark_key: str | None = None,
    fetchpriority: str = "",
) -> str:
    """Standalone triquetra — omit when the wordmark lockup already includes it."""
    key = wordmark_key or b.get("header_wordmark_key", "wordmark_horizontal")
    if _wordmark_ready(b, key):
        return ""
    tri = _glyph_src(b)
    fp = f' fetchpriority="{fetchpriority}"' if fetchpriority else ""
    return (
        f'<img class="{cls}" src="{tri}" alt="" width="{width}" height="{height}"'
        f' aria-hidden="true" decoding="async"{fp}>'
    )


def _splash_has_wordmark(b: dict) -> bool:
    splash_key = b.get("splash_wordmark_key")
    if _wordmark_ready(b, splash_key):
        return True
    return _wordmark_ready(b, b.get("header_wordmark_key", "wordmark_horizontal"))


def _publisher_markup(
    b: dict,
    *,
    compact: bool = False,
    splash: bool = False,
    wm_height: int | None = None,
) -> str:
    pub = b.get("publisher", "PRINCEPS")
    if splash:
        stacked = _wordmark_img(
            b, b.get("splash_wordmark_key"), cls="splash-wordmark", height=48, alt=pub
        )
        if stacked:
            return stacked
    height = wm_height if wm_height is not None else (48 if splash else (32 if compact else 64))
    horizontal = _wordmark_img(
        b,
        b.get("header_wordmark_key", "wordmark_horizontal"),
        cls="splash-wordmark" if splash else "brand-wordmark",
        height=height,
        alt=pub,
    )
    if horizontal:
        return horizontal
    return f'<span class="brand-pub">{pub}</span>'


def _product_label(b: dict) -> str:
    return b.get("product_label") or b.get("product", "Non-Firm Power Risk Index")


def _product_block(b: dict, href: str, *, compact: bool = False) -> str:
    prod = _product_label(b)
    tag = b.get("tagline", "A PRINCEPS research index")
    title_cls = "brand-product-title" + (" brand-product-title--compact" if compact else "")
    tag_html = "" if compact else f'<span class="brand-product-tag">{tag}</span>'
    return (
        f'<a class="brand-product-link" href="{href}" aria-label="{prod}">'
        f'<span class="{title_cls}">{prod}</span>{tag_html}</a>'
    )


def render_splash(ds: dict) -> str:
    b = _brand(ds)
    prod = _product_label(b)
    tag = b.get("tagline", "A PRINCEPS research index")
    glyph = ""
    if not _splash_has_wordmark(b):
        glyph = _glyph_img(b, cls="splash-glyph", width=72, height=72, fetchpriority="high")
    inner = (
        f"{glyph}"
        f'{_publisher_markup(b, splash=True)}'
        f'<p class="splash-product-title">{prod}</p>'
        f'<p class="splash-product-tag type-kicker">{tag}</p>'
    )
    return (
        f'<div id="splash" class="splash" role="dialog" aria-label="Welcome">'
        f'<div class="splash-inner">{inner}</div></div>'
    )


def render_brand(
    ds: dict,
    *,
    publisher_href: str | None = None,
    product_href: str | None = None,
    href: str | None = None,
    compact: bool = False,
    size: str = "md",
) -> str:
    b = _brand(ds)
    pub = b.get("publisher", "PRINCEPS")
    pub_url = publisher_href or b.get("publisher_url", "https://princeps.dev")
    prod_url = product_href if product_href is not None else (href or "index.html")
    cls = "brand" + (" brand--compact" if compact else "")
    wm_key = b.get("header_wordmark_key", "wordmark_horizontal")
    wm_h = 32 if compact else (72 if size == "lg" else 64)
    glyph_px = 72 if size == "lg" else (36 if compact else 56)
    fp = "high" if not compact else ""
    pub_inner = _publisher_markup(b, compact=compact, wm_height=wm_h)
    if not _wordmark_ready(b, wm_key):
        pub_inner = (
            _glyph_img(
                b,
                cls="brand-glyph",
                width=glyph_px,
                height=glyph_px,
                wordmark_key=wm_key,
                fetchpriority=fp,
            )
            + pub_inner
        )
    pub_link = (
        f'<a class="brand-pub-link" href="{pub_url}" rel="noopener" aria-label="{pub}">'
        f"{pub_inner}</a>"
    )
    product_block = _product_block(b, prod_url, compact=compact)
    lockup_cls = "brand-lockup brand-lockup--product" + (" brand-lockup--compact" if compact else "")
    return (
        f'<span class="{cls}">'
        f'<span class="{lockup_cls}">{pub_link}'
        f'<span class="brand-product-block">{product_block}</span>'
        f"</span></span>"
    )


def render_foot_brand(ds: dict, *, entity_count: int = 0, gate_pct: int = 0) -> str:
    b = _brand(ds)
    pub = b.get("publisher", "PRINCEPS")
    prod_label = b.get("product_label", "Non-Firm Power Risk Index")
    url = b.get("publisher_url", "https://princeps.dev")
    producer = b.get("producer") or {}
    credit = producer.get("credit", "")
    linkedin_url = producer.get("linkedin_url", "")
    linkedin_label = producer.get("linkedin_label", "LinkedIn")
    x_url = producer.get("x_url", "")
    rights = producer.get("rights", "all rights reserved")
    producer_html = ""
    if credit or linkedin_url or x_url:
        row = '<span class="foot-producer-row type-meta">'
        if credit:
            row += f'<span class="foot-producer">{credit}</span>'
        socials = []
        if linkedin_url:
            label = linkedin_label if linkedin_label != "LinkedIn" else "Anya Trofimova on LinkedIn"
            socials.append(_foot_social_link(linkedin_url, _LINKEDIN_ICON, label))
        if x_url:
            socials.append(_foot_social_link(x_url, _X_ICON, "Anya Trofimova on X"))
        if socials:
            row += f'<span class="foot-socials">{"".join(socials)}</span>'
        row += "</span>"
        producer_html += row
    if rights:
        producer_html += f'<span class="foot-rights type-meta">{rights}</span>'
    wm_key = b.get("header_wordmark_key", "wordmark_horizontal")
    wm = _wordmark_img(b, wm_key, cls="foot-wordmark", height=32, alt=pub)
    if wm:
        pub_html = f'<a class="foot-pub foot-pub--img" href="{url}" rel="noopener">{wm}</a>'
    else:
        pub_html = f'<a class="foot-pub" href="{url}" rel="noopener">{pub}</a>'
    glyph = _glyph_img(b, cls="brand-glyph", width=40, height=40, wordmark_key=wm_key)
    return (
        f'<span class="foot-brand">'
        f"{glyph}"
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
    b = _brand(ds)
    c = ds.get("site_hero") or {}
    product = _product_label(b)
    tagline = b.get("tagline", "A PRINCEPS research index")
    kicker = c.get("kicker", "")
    thesis = c.get("title", "")
    lede = c.get("lede", "")
    return (
        f'<header class="gate-shell">'
        f'<div class="gate-bar"><div class="wrap">{render_brand(ds, product_href="index.html")}'
        f'<nav class="gate-nav" aria-label="Site">'
        f'<a class="section-tab" href="on-non-firm-risk.html">Full thesis</a>'
        f'<a class="section-tab" href="methodology.html">Methodology</a>'
        f"</nav></div></div>"
        f'<div class="section-tabs-wrap"><div class="wrap">{render_section_tabs(ds)}</div></div>'
        f"</header>"
        f'<section class="hero-gate" aria-label="Introduction"><div class="wrap"><div class="gate-grid">'
        f'<div class="gate-main">'
        f'<p class="hero-publisher type-kicker">{tagline}</p>'
        f'<h1 class="hero-product-title">{product}</h1>'
        f'<p class="hero-thesis type-title">{thesis}</p>'
        f'<p class="hero-kicker type-kicker">{kicker}</p>'
        f'<p class="hero-lede type-lead">{lede}</p>'
        f'<div class="gate-foot">'
        f'<a class="hero-cta-btn" href="#argument">Read the thesis →</a>'
        f'<a class="hero-cta-btn hero-cta-btn--ghost" href="on-non-firm-risk.html">Full essay →</a>'
        f"</div></div>"
        f"</div></div></section>"
    )


def render_mobile_dock(ds: dict) -> str:
    return (
        f'<div class="site-dock" role="navigation" aria-label="Quick actions">'
        f'{render_brand(ds, product_href="#index", compact=True)}'
        f'<a class="dock-cta" href="#argument">Read thesis</a></div>'
    )
