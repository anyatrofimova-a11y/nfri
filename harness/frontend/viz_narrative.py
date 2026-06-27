"""Chart narrative blocks — ai-transformation / Saspo prose → viz → stats → so what."""

from __future__ import annotations


def chart_narrative_ctx(
    *,
    n: int,
    cut_exp: float,
    cut_prep: float,
    share: float,
    pts: list[dict],
) -> dict[str, str | int]:
    quads = {}
    for p in pts:
        q = p.get("quad") or "sidelined"
        quads[q] = quads.get(q, 0) + 1
    return {
        "n": n,
        "cutExp": int(round(cut_exp)),
        "cutPrep": int(round(cut_prep)),
        "sharePct": int(round(share * 100)),
        "nWhitespace": quads.get("whitespace", 0),
        "nExposed": quads.get("exposed", 0),
    }


def resolve_tokens(text: str, ctx: dict) -> str:
    out = text or ""
    for key, val in ctx.items():
        out = out.replace(f"{{{key}}}", str(val))
    return out


def render_viz_head(chart_id: str, charts: dict, ctx: dict) -> str:
    c = charts.get(chart_id) or {}
    kicker = resolve_tokens(c.get("kicker", ""), ctx)
    title = resolve_tokens(c.get("title", ""), ctx)
    return (
        f'<p class="section-kicker type-kicker">{kicker}</p>'
        f'<h2 class="section-title type-title">{title}</h2>'
    )


def render_viz_body(chart_id: str, charts: dict, ctx: dict) -> str:
    c = charts.get(chart_id) or {}
    if not c:
        return ""
    title = resolve_tokens(c.get("title", ""), ctx)
    stats = resolve_tokens(c.get("stats", ""), ctx)
    if c.get("density") == "compact":
        return (
            f'<div class="viz-block viz-block--compact" data-viz="{chart_id}">'
            f'<h2 class="viz-title type-title">{title}</h2>'
            f'<p class="viz-stats type-meta">{stats}</p>'
            f"</div>"
        )
    lede = resolve_tokens(c.get("lede", ""), ctx)
    read = resolve_tokens(c.get("read", ""), ctx)
    so_what = resolve_tokens(c.get("so_what", ""), ctx)
    return (
        f'<div class="viz-block" data-viz="{chart_id}">'
        f'<p class="viz-lede type-lead">{lede}</p>'
        f'<p class="viz-read type-body">{read}</p>'
        f'<p class="viz-stats type-meta">{stats}</p>'
        f'<p class="viz-sowhat type-body"><strong>So what.</strong> {so_what}</p>'
        f"</div>"
    )


def render_viz_block(chart_id: str, charts: dict, ctx: dict) -> str:
    c = charts.get(chart_id) or {}
    body = render_viz_body(chart_id, charts, ctx)
    if not body:
        return ""
    if c.get("density") == "compact":
        return body
    head = render_viz_head(chart_id, charts, ctx)
    return body.replace(
        f'<div class="viz-block" data-viz="{chart_id}">',
        f'<div class="viz-block" data-viz="{chart_id}"><header class="viz-head">{head}</header>',
        1,
    )


def render_term_panel(
    chart_id: str,
    charts: dict,
    ctx: dict,
    *,
    mount_id: str,
    mount_class: str = "term-chart",
    stats_id: str | None = None,
    controls: str = "",
) -> str:
    """Terminal bento card: prose → controls → chart → stats → so what (Ciridae order)."""
    c = charts.get(chart_id) or {}
    kicker = resolve_tokens(c.get("kicker", ""), ctx)
    title = resolve_tokens(c.get("title", ""), ctx)
    lede = resolve_tokens(c.get("lede", ""), ctx)
    read = resolve_tokens(c.get("read", ""), ctx)
    stats = resolve_tokens(c.get("stats", ""), ctx)
    so_what = resolve_tokens(c.get("so_what", ""), ctx)
    stats_attr = f' id="{stats_id}"' if stats_id else ""
    live_attr = f' data-live="{chart_id}"' if stats_id else ""
    return (
        f'<div class="term-viz-card viz-block" data-viz="{chart_id}">'
        f'<header class="term-viz-head">'
        f'<p class="term-viz-kicker">{kicker}</p>'
        f'<h3 class="term-viz-title">{title}</h3>'
        f"</header>"
        f'<p class="term-viz-lede">{lede}</p>'
        f'<p class="term-viz-read">{read}</p>'
        f"{controls}"
        f'<div class="term-chart-shell">'
        f'<div class="{mount_class}" id="{mount_id}"></div>'
        f"</div>"
        f'<p class="viz-stats type-meta"{stats_attr}{live_attr}>{stats}</p>'
        f'<p class="term-viz-sowhat"><strong>So what.</strong> {so_what}</p>'
        f"</div>"
    )


def render_term_section_head(charts: dict, ctx: dict) -> str:
    c = charts.get("terminal_hub") or {}
    kicker = resolve_tokens(c.get("kicker", "Terminal"), ctx)
    title = resolve_tokens(c.get("title", ""), ctx)
    lede = resolve_tokens(c.get("lede", ""), ctx)
    if not title:
        return ""
    return (
        f'<header class="term-section-head">'
        f'<p class="section-kicker type-kicker">{kicker}</p>'
        f'<h2 class="section-title type-title">{title}</h2>'
        f'<p class="section-lede type-lead type-lead--muted">{lede}</p>'
        f"</header>"
    )
