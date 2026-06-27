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
    lede = resolve_tokens(c.get("lede", ""), ctx)
    read = resolve_tokens(c.get("read", ""), ctx)
    stats = resolve_tokens(c.get("stats", ""), ctx)
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
    head = render_viz_head(chart_id, charts, ctx)
    body = render_viz_body(chart_id, charts, ctx)
    if not body:
        return ""
    return body.replace(
        f'<div class="viz-block" data-viz="{chart_id}">',
        f'<div class="viz-block" data-viz="{chart_id}"><header class="viz-head">{head}</header>',
        1,
    )
