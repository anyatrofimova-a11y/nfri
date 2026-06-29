#!/usr/bin/env python3
"""Build site/design-system.html — component gallery for design agent review."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import ESSAY_CSS  # noqa: E402
from design_system import load_design_system  # noqa: E402
from frontend.chrome import FAVICON_HEAD, render_hero_gate  # noqa: E402
from frontend.css import render_site_css  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "design-system.html")


def _swatch(name: str, var: str) -> str:
    return (
        f'<div class="ds-swatch"><span class="ds-swatch-fill" style="background:var({var})"></span>'
        f'<span class="ds-swatch-name">{name}</span><code>{var}</code></div>'
    )


def build() -> str:
    from build_frontend import authoritative_share, load_records

    records, _ = load_records()
    share = authoritative_share(records)
    n = len(records)
    gate_pct = int(round(share * 100))
    exposed = sum(1 for r in records if (r.get("scores") or {}).get("quadrant") == "exposed")
    ds = load_design_system()
    c = ds["colors"]
    swatches = "".join([
        _swatch("Emphasis bg", "--bg-emphasis"),
        _swatch("Default bg", "--bg-default"),
        _swatch("Muted bg", "--bg-muted"),
        _swatch("Ink", "--ink"),
        _swatch("Body", "--ink2"),
        _swatch("Muted", "--muted"),
        _swatch("Accent", "--accent"),
        _swatch("Brand accent", "--accent"),
        _swatch("Exposed", "--exposed"),
        _swatch("Earning", "--earning-s"),
        _swatch("Whitespace", "--whitespace"),
    ])
    extra_css = r"""
  .ds-page{padding:var(--space-lg) 0 var(--space-xl)}
  .ds-intro{margin-bottom:var(--space-lg);max-width:52ch}
  .ds-intro h1{font-family:var(--font-display);font-size:clamp(24px,3vw,32px);margin:0 0 8px;font-weight:600}
  .ds-intro p{margin:0;color:var(--muted);line-height:1.55}
  .ds-block{margin-bottom:var(--space-lg);padding-top:var(--space-md);border-top:1px solid var(--line-subtle)}
  .ds-block h2{font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 var(--space-sm)}
  .ds-swatches{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:var(--space-sm)}
  .ds-swatch{font-size:11px;color:var(--muted)}
  .ds-swatch-fill{display:block;height:48px;border:1px solid var(--line-subtle);border-radius:var(--radius-sm);margin-bottom:6px}
  .ds-swatch-name{display:block;font-weight:600;color:var(--ink2);margin-bottom:2px}
  .ds-type h3{font-family:var(--font-display);font-size:28px;margin:0 0 8px;font-weight:600}
  .ds-type .sans{font-family:var(--font-sans);font-size:15px;line-height:1.6;color:var(--ink2);max-width:48ch}
  .ds-type .mono{font-family:var(--font-mono);font-size:12px;color:var(--muted);margin-top:8px}
  .ds-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
"""
    body = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NFRI design system · PRINCEPS</title>
{FAVICON_HEAD}
<link rel="stylesheet" href="{ds['fonts']['google_url']}">
<style>{render_site_css(ds, prose_css=ESSAY_CSS)}{extra_css}</style>
</head>
<body class="site ds-review">
<main class="site-main"><div class="wrap ds-page">
  <div class="ds-intro">
    <h1>NFRI design system</h1>
    <p>Tokens from <code>contract/design_system.json</code>. See <code>DESIGN.md</code> for intent.
      Live index: <a href="index.html?v=design-system">index.html?v=design-system</a></p>
  </div>
  <section class="ds-block"><h2>Color</h2><div class="ds-swatches">{swatches}</div></section>
  <section class="ds-block"><h2>Typography scale</h2>
    <p class="type-kicker">Kicker · mono · accent</p>
    <h3 class="type-display" style="margin:12px 0">Display heading</h3>
    <h4 class="type-title" style="margin:0 0 8px">Section title</h4>
    <p class="type-lead" style="margin:0 0 8px">Lead paragraph for introductions and section ledes.</p>
    <p class="type-body" style="margin:0 0 8px">Body text for long-form analysis and table cells.</p>
    <p class="type-meta" style="margin:0">Meta · {n} entities · gate {gate_pct}%</p>
  </section>
  <section class="ds-block"><h2>Brand + hero</h2>
    {render_hero_gate(ds, entity_count=n, gate_pct=gate_pct)}
  </section>
  <section class="ds-block"><h2>Section head</h2>
    <header class="section-head">
      <p class="section-kicker type-kicker">Findings</p>
      <h2 class="section-title type-title">What the data shows</h2>
      <p class="section-lede type-lead type-lead--muted">Honest about provisional status until the publication gate clears.</p>
    </header>
  </section>
  <section class="ds-block"><h2>Stats (essay)</h2>
    <div class="st-row">
      <div class="st-cell"><span class="st-v">{n}</span><span class="st-l">Entities scored</span><span class="st-s">carriers, MGAs, assets</span></div>
      <div class="st-cell"><span class="st-v">{exposed}</span><span class="st-l">Exposed</span><span class="st-s">exposure ahead of preparedness</span></div>
      <div class="st-cell"><span class="st-v">{gate_pct}%</span><span class="st-l">Measured share</span><span class="st-s">below 60% gate</span></div>
    </div>
  </section>
  <section class="ds-block"><h2>Controls</h2>
    <div class="filter-bar">
      <div class="filter-grp"><span class="filter-label">Layer</span>
        <span class="filter-seg">
          <button type="button" class="filter-btn on">All layers</button>
          <button type="button" class="filter-btn">Assets</button>
        </span>
      </div>
      <div class="filter-grp"><span class="filter-label">Quadrant</span>
        <span class="filter-seg">
          <button type="button" class="filter-btn on">All</button>
          <button type="button" class="filter-btn">Exposed</button>
        </span>
      </div>
    </div>
  </section>
  <section class="ds-block"><h2>Table row</h2>
    <div class="panel">
      <table class="data-table"><thead><tr>
        <th>Entity</th><th class="num">MoS</th><th>Quadrant</th><th class="num">Measured</th>
      </tr></thead><tbody><tr class="row">
        <td>Aviva</td><td class="num"><b>+12</b></td>
        <td><span class="quad-label" style="color:var(--earning-s)">Earning it</span></td>
        <td class="num"><span class="meas-track"><span class="meas-bar" style="width:42%"></span></span> 42%</td>
      </tr></tbody></table>
    </div>
  </section>
  <section class="ds-block"><h2>Eval chips</h2>
    <div class="eval-chips">
      <span class="eval-chip PASS"><span class="eval-dot"></span><b>L5</b> PASS · Publication gate</span>
      <span class="eval-chip WARN"><span class="eval-dot"></span><b>L3</b> WARN · Blend integrity</span>
    </div>
  </section>
  <section class="ds-block"><h2>Knowledge topics</h2>
    <div class="kg-topics">
      <button type="button" class="kg-topic on">All</button>
      <button type="button" class="kg-topic">Register</button>
      <button type="button" class="kg-topic">Regulatory</button>
    </div>
  </section>
  <section class="ds-block"><h2>Rail card</h2>
    <div class="rail-grid">
      <div class="rail-card">
        <div class="rail-id">CMP434/435</div>
        <div class="rail-status">In force · 10 Jun 2025</div>
        <p>Gate status becomes an objective register fact for every L3 firmness score.</p>
        <div class="chip-row"><span class="chip"><a href="#">NESO-CMP434</a></span></div>
      </div>
    </div>
  </section>
  <section class="ds-block"><h2>Panel</h2>
    <div class="panel"><p style="margin:0;color:var(--ink2)">Scatter, table, and knowledge index panels use <code>.panel</code> on warm paper.</p></div>
  </section>
</div></main>
</body></html>"""
    return body


def main() -> None:
    html = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(html)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
