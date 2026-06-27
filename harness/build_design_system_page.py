#!/usr/bin/env python3
"""Build site/design-system.html — component gallery for design agent review."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_system import load_design_system  # noqa: E402
from frontend.css import render_site_css  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "design-system.html")


def _swatch(name: str, var: str) -> str:
    return (
        f'<div class="ds-swatch"><span class="ds-swatch-fill" style="background:var({var})"></span>'
        f'<span class="ds-swatch-name">{name}</span><code>{var}</code></div>'
    )


def build() -> str:
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
        _swatch("Navy", "--section-accent"),
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
<title>NFRI design system · Princeps</title>
<link rel="stylesheet" href="{ds['fonts']['google_url']}">
<style>{render_site_css(ds)}{extra_css}</style>
</head>
<body class="site ds-review">
<main class="site-main"><div class="wrap ds-page">
  <div class="ds-intro">
    <h1>NFRI design system</h1>
    <p>Tokens from <code>contract/design_system.json</code>. See <code>DESIGN.md</code> for intent.
      Live index: <a href="index.html?v=design-system">index.html?v=design-system</a></p>
  </div>
  <section class="ds-block"><h2>Color</h2><div class="ds-swatches">{swatches}</div></section>
  <section class="ds-block"><h2>Typography</h2>
    <div class="ds-type">
      <h3>Source Serif 4 — display</h3>
      <p class="sans">IBM Plex Sans — body and UI. The index reads as a research working paper, not a SaaS landing page.</p>
      <p class="mono">IBM Plex Mono · 115 entities · gate 16% · snapshot 2026-06-25</p>
    </div>
  </section>
  <section class="ds-block"><h2>Hero masthead</h2>
    <header class="gate-shell" style="border:1px solid var(--line-subtle);border-radius:var(--radius-md);overflow:hidden">
      <div class="hero-gate"><div class="wrap">
        <p class="hero-kicker">Research index · UK insurance market</p>
        <h1 class="hero-title" style="max-width:none">Who carries non-firm power risk</h1>
        <p class="hero-lede">Two scored axes reduce to a Margin of Safety the market does not yet publish.</p>
        <div class="gate-foot"><a class="hero-cta-btn" href="#">Explore the index →</a>
          <span class="gate-stats"><b>115</b> entities · <b>16%</b> measured gate</span></div>
      </div></div>
    </header>
  </section>
  <section class="ds-block"><h2>Section head</h2>
    <header class="section-head">
      <p class="section-kicker">Findings</p>
      <h2 class="section-title">What the data shows</h2>
      <p class="section-lede">Honest about provisional status until the publication gate clears.</p>
    </header>
  </section>
  <section class="ds-block"><h2>Stats (essay)</h2>
    <div class="st-row">
      <div class="st-cell"><span class="st-v">115</span><span class="st-l">Entities scored</span><span class="st-s">carriers, MGAs, assets</span></div>
      <div class="st-cell"><span class="st-v">30</span><span class="st-l">Exposed</span><span class="st-s">exposure ahead of preparedness</span></div>
      <div class="st-cell"><span class="st-v">16%</span><span class="st-l">Measured share</span><span class="st-s">below 60% gate</span></div>
    </div>
  </section>
  <section class="ds-block"><h2>Controls</h2>
    <div class="ds-row">
      <button type="button" class="filter-btn on">All layers</button>
      <button type="button" class="filter-btn">Exposed</button>
      <button type="button" class="idx-btn">Sort by MoS</button>
      <a class="hero-cta-btn" href="#">Primary action</a>
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
