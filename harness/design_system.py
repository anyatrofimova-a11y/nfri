#!/usr/bin/env python3
"""Render harness CSS from contract/design_system.json — warm paper / terracotta rhythm."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS_PATH = os.path.join(ROOT, "contract", "design_system.json")


def load_design_system(path: str | None = None) -> dict:
    with open(path or DS_PATH) as f:
        ds = json.load(f)
    try:
        from brand_assets import load_brand_manifest, resolve_brand_paths

        ds = dict(ds)
        ds["brand"] = resolve_brand_paths(ds, load_brand_manifest())
    except Exception:
        pass
    return ds


def css_variables(ds: dict | None = None) -> str:
    ds = ds or load_design_system()
    c = ds["colors"]
    r = ds["radius"]
    s = ds.get("spacing", {})
    f = ds["fonts"]
    m = ds.get("motion", {})
    t = ds.get("typography", {})
    es = ds.get("essay_surface", {})
    sc = ds.get("scroll", {})
    k = t.get("kicker", {})
    d = t.get("display", {})
    tl = t.get("title", {})
    ld = t.get("lead", {})
    bd = t.get("body", {})
    es_typ = t.get("essay", {})
    mt = t.get("meta", {})
    nv = t.get("nav", {})
    bp = t.get("brand_pub", {})
    return f"""
  :root{{
    --bg-emphasis:{c['bg_emphasis']}; --bg-default:{c['bg_default']}; --bg-muted:{c['bg_muted']};
    --bg-subtle:{c.get('bg_subtle', '#F0F0F0')};
    --ink:{c['content_emphasis']}; --ink2:{c['content_default']}; --muted:{c['content_muted']};
    --ink-headline:{c.get('headline_ink', c['content_emphasis'])};
    --line:{c['border_default']}; --line-subtle:{c.get('border_subtle', '#E8E8E8')};
    --bg:{c['bg_emphasis']}; --card:{c['bg_default']};
    --accent:{c['accent']}; --accent-muted:{c.get('accent_muted', '#FCE7DD')};
    --accent2:{c['measured']}; --section-accent:{c['section_accent']};
    --exposed:{c['exposed']}; --earning-s:{c['earning']}; --whitespace:{c['whitespace']};
    --sidelined:{c['sidelined']}; --measured:{c['measured']};
    --warn:{c.get('warn', '#D8920F')}; --chart-grid:{c.get('chart_grid', c.get('border_subtle', '#E5E1DA'))};
    --warn-bg:{c.get('warn_bg', '#FFF7EC')}; --warn-border:{c.get('warn_border', '#F0DCB8')};
    --ok-bg:{c.get('ok_bg', '#EEF7F0')}; --ok-border:{c.get('ok_border', '#CFE6D4')};
    --canvas-dark:{c.get('canvas_dark', '#1e1b18')}; --canvas-grid:{c.get('canvas_grid', 'rgba(255,255,255,0.04)')};
    --glow-accent:{c.get('glow_accent', 'rgba(204,100,55,0.35)')};
    --ease-out:{m.get('ease_out', 'cubic-bezier(0.22, 1, 0.36, 1)')};
    --dur-sm:{m.get('duration_sm', '0.35s')}; --dur-md:{m.get('duration_md', '0.55s')};
    --dur-lg:{m.get('duration_lg', '0.85s')}; --dur-essay:{m.get('duration_essay', '0.72s')};
    --stagger:{m.get('stagger_step', '0.05s')};
    --radius-sm:{r['sm']}; --radius-md:{r['md']}; --radius-lg:{r['lg']}; --radius-card:{r['card']};
    --radius-pill:{r.get('pill', '999px')};
    --font-sans:{f['sans']}; --font-display:{f['display']}; --font-mono:{f['mono']};
    --font-essay:{f.get('essay', f['display'])}; --font-nav:{f.get('nav', f.get('essay', f['display']))};
    --font-brand:{f.get('brand', f.get('display', 'serif'))};
    --font-brand-product:{f.get('brand_product', f.get('mono', 'monospace'))};
    --essay-measure:{es.get('measure', '42rem')};
    --essay-para-gap:{es.get('paragraph_gap', '1.25em')};
    --type-essay-body:{es_typ.get('size', es.get('body_size', '1.125rem'))};
    --type-essay-lead:{es_typ.get('leading', es.get('body_leading', 1.68))};
    --type-essay-pull:{es.get('pull_size', '1.1875rem')};
    --type-essay-pull-lead:{es.get('pull_leading', 1.55)};
    --essay-reveal-y:18px;
    --max-w:{ds['layout']['max_width']};
    --header-h:{ds['layout'].get('header_height', '56px')};
    --space-xs:{s.get('xs', '8px')}; --space-sm:{s.get('sm', '16px')}; --space-md:{s.get('md', '24px')};
    --space-lg:{s.get('lg', '48px')}; --space-xl:{s.get('xl', '72px')};
    --section-y:{s.get('section_y', '56px')};
    --card-gap:{ds['layout'].get('card_gap', '10px')};
    --type-kicker:{k.get('size', '0.6875rem')}; --type-kicker-track:{k.get('tracking', '0.06em')};
    --type-display-min:{d.get('min', '2rem')}; --type-display-max:{d.get('max', '3rem')};
    --type-display-track:{d.get('tracking', '-0.025em')}; --type-display-lead:{d.get('leading', 1.08)};
    --type-title-min:{tl.get('min', '1.375rem')}; --type-title-max:{tl.get('max', '1.75rem')};
    --type-title-track:{tl.get('tracking', '-0.02em')}; --type-title-lead:{tl.get('leading', 1.2)};
    --type-lead:{ld.get('size', '1.125rem')}; --type-lead-lead:{ld.get('leading', 1.55)};
    --type-body:{bd.get('size', '0.9375rem')}; --type-body-lead:{bd.get('leading', 1.62)};
    --type-nav:{nv.get('size', '1.125rem')}; --type-nav-lead:{nv.get('leading', 1.4)};
    --type-brand-pub:{bp.get('size', '0.9375rem')}; --type-brand-track:{bp.get('tracking', '0.12em')};
    --type-meta:{mt.get('size', '0.75rem')}; --type-meta-lead:{mt.get('leading', 1.45)};
  }}
"""


def typography_css() -> str:
    """Shared type scale — one grammar for hero, sections, essays."""
    return r"""
  .type-kicker{
    font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;
    letter-spacing:var(--type-kicker-track);text-transform:uppercase;
    color:var(--accent);line-height:1.35;
  }
  .type-display{
    font-family:var(--font-display);font-weight:500;
    font-size:clamp(var(--type-display-min),5vw,var(--type-display-max));
    line-height:var(--type-display-lead);letter-spacing:var(--type-display-track);
    color:var(--ink-headline);font-optical-sizing:auto;
  }
  .type-title{
    font-family:var(--font-display);font-weight:500;
    font-size:clamp(var(--type-title-min),2.5vw,var(--type-title-max));
    line-height:var(--type-title-lead);letter-spacing:var(--type-title-track);
    color:var(--ink-headline);
  }
  .type-lead{
    font-family:var(--font-essay);font-size:var(--type-lead);line-height:var(--type-lead-lead);
    color:var(--ink2);
  }
  .type-lead--muted{color:var(--muted)}
  .type-body{font-size:var(--type-body);line-height:var(--type-body-lead);color:var(--ink2)}
  .type-meta{font-family:var(--font-mono);font-size:var(--type-meta);line-height:var(--type-meta-lead);color:var(--muted)}
"""


def hero_css() -> str:
    """Light editorial masthead — research index, not dark instrument gate."""
    return r"""
  .hero-gate{
    padding:var(--space-lg) 0 var(--space-md);position:relative;z-index:1;
    background:var(--bg-default);border-bottom:1px solid var(--line-subtle);
  }
  .hero-gate .wrap{max-width:var(--max-w);margin:0 auto;padding:0 var(--space-md)}
  .gate-grid{
    display:grid;grid-template-columns:minmax(0,1fr);gap:var(--space-md);align-items:start;
  }
  .gate-visual{display:none}
  .hero-publisher{margin:0 0 8px;color:var(--accent)}
  .hero-product-title{
    margin:0 0 var(--space-sm);max-width:24ch;
    font-family:var(--font-nav);font-size:clamp(1.75rem,4vw,2.625rem);
    font-weight:500;letter-spacing:0;text-transform:none;
    line-height:1.12;color:var(--ink-headline);
  }
  .hero-thesis{
    margin:0 0 var(--space-sm);max-width:42ch;
    font-family:var(--font-essay);font-weight:500;
    font-size:clamp(1.25rem,2.4vw,1.625rem);line-height:1.35;
    color:var(--ink-headline);
  }
  .hero-kicker{margin:0 0 var(--space-xs)}
  .hero-title{
    margin:0 0 var(--space-md);max-width:38ch;
  }
  .hero-title--sr{
    position:absolute;width:1px;height:1px;padding:0;margin:-1px;
    overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;
  }
  .hero-lede{
    max-width:54ch;margin:0 0 var(--space-md);
  }
  .gate-foot{
    display:flex;flex-wrap:wrap;align-items:center;gap:var(--space-sm) var(--space-md);
    padding-top:var(--space-md);margin-top:var(--space-xs);border-top:1px solid var(--line);
  }
  .hero-cta-btn{
    display:inline-flex;align-items:center;gap:6px;
    font-size:var(--type-body);font-weight:600;color:#fff;background:var(--accent);
    padding:11px 20px;border-radius:var(--radius-sm);text-decoration:none;
    transition:background .15s;font-family:var(--font-sans);
  }
  .hero-cta-btn:hover{background:var(--ink);color:#fff;text-decoration:none}
  .hero-cta-btn--ghost{
    color:var(--accent);background:transparent;border:1px solid var(--line);
  }
  .hero-cta-btn--ghost:hover{background:var(--bg-default);color:var(--ink);border-color:var(--line)}
  .gate-stats{font-family:var(--font-mono);font-size:var(--type-meta);color:var(--muted)}
  .gate-stats b{color:var(--ink2);font-weight:500}

  @media(max-width:780px){
    .hero-title{max-width:none}
    .hero-gate{padding:var(--space-lg) 0 var(--space-md)}
  }
"""


def shell_css() -> str:
    return r"""
  *{box-sizing:border-box}
  body{
    margin:0;font-family:var(--font-sans);font-size:var(--type-body);line-height:var(--type-body-lead);
    color:var(--ink2);background:var(--bg-emphasis);-webkit-font-smoothing:antialiased;
    font-feature-settings:"kern" 1,"liga" 1;
  }
  a{color:var(--section-accent);text-decoration:none}
  a:hover{text-decoration:underline}
  .wrap{max-width:var(--max-w);margin:0 auto;padding:0 var(--space-md)}

  header.top{
    position:sticky;top:0;z-index:30;background:var(--bg-default);
    border-bottom:1px solid var(--line-subtle);
  }
  .top .wrap{display:flex;align-items:center;min-height:var(--header-h);gap:var(--space-sm)}
  .brand{
    display:inline-flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);
  }
  .brand:hover{text-decoration:none;color:var(--ink)}
  .brand-mark{
    flex:0 0 32px;width:32px;height:32px;
    background:var(--ink);
    -webkit-mask:url(assets/brand/princeps-glyph.png) center/contain no-repeat;
    -webkit-mask-mode:luminance;
    mask:url(assets/brand/princeps-glyph.png) center/contain no-repeat;
    mask-mode:luminance;
  }
  .brand-mark.lg{flex:0 0 40px;width:40px;height:40px}
  .brand-mark.sm{flex:0 0 22px;width:22px;height:22px}
  .welcome-brand{display:flex;align-items:center;gap:12px;margin-bottom:var(--space-sm)}
  .foot-brand{display:inline-flex;align-items:flex-start;gap:10px;color:var(--muted);max-width:36rem}
  .foot-brand-text{display:flex;flex-direction:column;gap:2px;line-height:1.35}
  .foot-pub{
    font-family:var(--font-brand);font-size:var(--type-brand-pub);font-weight:600;
    letter-spacing:var(--type-brand-track);text-transform:uppercase;
    color:var(--ink-headline);text-decoration:none;
  }
  .foot-pub:hover{text-decoration:underline;color:var(--accent)}
  .foot-product{
    font-family:var(--font-nav);font-size:var(--type-nav);font-weight:500;
    color:var(--ink-headline);letter-spacing:0;text-transform:none;
  }
  .foot-tagline{color:var(--muted)}
  .foot-producer-row{
    display:inline-flex;align-items:center;gap:6px;margin-top:2px;
  }
  .foot-producer{color:var(--muted);margin-top:0}
  .foot-socials{display:inline-flex;align-items:center;gap:4px}
  .foot-social{
    display:inline-flex;align-items:center;justify-content:center;
    color:var(--accent);text-decoration:none;line-height:0;
    border-radius:2px;transition:color .15s ease;
  }
  .foot-social:hover{color:var(--ink)}
  .foot-social-icon{display:block}
  .foot-rights{color:var(--muted);margin-top:2px}
  .gate-bar nav,.site-foot-links{
    margin-left:auto;display:flex;align-items:center;gap:2px;
  }
  .index-thesis-toc,.thesis-toc{
    display:block;margin-left:0;flex-direction:column;align-items:stretch;gap:0;
  }
  .gate-bar nav a,.site-foot-links a{
    font-size:var(--type-body);font-weight:500;color:var(--ink2);padding:6px 10px;border-radius:var(--radius-sm);
    text-decoration:none;
  }
  .gate-bar nav a:hover,.site-foot-links a:hover{background:var(--bg-muted);text-decoration:none;color:var(--ink)}
  nav .nav-sep{width:1px;height:12px;background:var(--line);margin:0 4px}

  .section{padding:var(--section-y) 0;border-bottom:1px solid var(--line-subtle)}
  .section:last-of-type{border-bottom:none}
  .section-head{margin-bottom:var(--space-md)}
  .section-kicker{margin:0 0 var(--space-xs)}
  .section-title{margin:0}
  .section-lede{max-width:52ch;margin:var(--space-xs) 0 0}

  .part-band{
    padding:var(--space-lg) 0 var(--space-sm);border-top:1px solid var(--line);
    scroll-margin-top:calc(var(--header-h) + 12px);
  }
  .part-band:first-of-type{border-top:none;padding-top:var(--space-md)}
  .part-n{
    display:block;font-size:11px;font-weight:500;letter-spacing:.14em;
    text-transform:uppercase;color:var(--accent);margin-bottom:6px;
  }
  .part-t{
    font-family:var(--font-display);font-size:clamp(20px,2.5vw,26px);
    font-weight:500;letter-spacing:-.02em;color:var(--ink);margin:0;
  }

  .status-strip{
    display:flex;flex-wrap:wrap;align-items:center;gap:var(--space-sm) var(--space-md);
    padding:var(--space-md) 0;border-bottom:1px solid var(--line-subtle);
    margin-bottom:var(--space-md);
  }
  .status-strip .banner{
    flex:1 1 280px;margin:0;padding:12px 14px;font-size:14px;line-height:1.5;
    border-radius:var(--radius-md);border:1px solid var(--warn-border);background:var(--warn-bg);
  }
  .status-strip .banner.ok{border-color:var(--ok-border);background:var(--ok-bg)}
  .status-strip .banner b{font-weight:600;color:var(--ink)}
  .status-meta{display:flex;flex-wrap:wrap;gap:var(--space-sm) var(--space-md);font-size:13px;color:var(--muted)}
  .status-meta b{color:var(--ink);font-weight:600}
  .status-dl{display:flex;flex-wrap:wrap;gap:var(--space-sm);margin-left:auto}
  .status-dl a{
    font-family:var(--font-mono);font-size:var(--type-meta);color:var(--section-accent);
    padding:0;border:none;border-radius:0;background:none;text-decoration:none;
  }
  .status-dl a:hover{text-decoration:underline;color:var(--ink)}

  .idx-toolbar{
    display:flex;flex-wrap:wrap;gap:var(--space-xs);align-items:center;
    padding-bottom:var(--space-sm);margin-bottom:var(--space-sm);
    border-bottom:1px solid var(--line-subtle);
  }
  .idx-search{
    flex:1 1 180px;min-width:140px;padding:9px 12px;border:1px solid var(--line);
    border-radius:var(--radius-md);background:var(--bg-default);font-size:14px;
    font-family:var(--font-sans);color:var(--ink);
  }
  .idx-search:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 2px rgba(184,90,50,.12)}
  .idx-btn{
    padding:8px 12px;border:1px solid var(--line);border-radius:var(--radius-md);
    background:var(--bg-default);font-size:13px;color:var(--ink2);cursor:pointer;font-family:var(--font-sans);
  }
  .idx-btn.on{background:var(--bg-muted);color:var(--ink);font-weight:600;border-color:var(--line);box-shadow:inset 0 -2px 0 var(--accent)}
  .idx-meta{font-size:13px;color:var(--muted);margin-left:auto}

  .card-list{display:flex;flex-direction:column;gap:var(--card-gap)}
  .ent-card{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(220px,280px);
    gap:var(--space-md);align-items:center;
    padding:var(--space-sm) var(--space-md);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-card);
    cursor:pointer;
    transition:border-color var(--dur-sm);
  }
  .ent-card:hover{
    border-color:var(--line);
  }
  .ent-id{display:flex;gap:var(--space-sm);align-items:center;min-width:0}
  .ent-avatar{
    flex:0 0 36px;width:36px;height:36px;border-radius:var(--radius-md);
    background:var(--bg-subtle);display:flex;align-items:center;justify-content:center;
    font-size:12px;font-weight:600;color:var(--section-accent);overflow:hidden;
    border:1px solid var(--line-subtle);
  }
  .ent-avatar img{width:100%;height:100%;object-fit:contain;padding:4px;background:#fff}
  .ent-name{font-weight:600;font-size:15px;color:var(--ink);line-height:1.3;display:flex;align-items:center;flex-wrap:wrap;gap:6px}
  .ent-meta{font-size:13px;color:var(--muted);margin-top:2px}
  .quad-tag{
    font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;
    padding:2px 8px;border-radius:var(--radius-pill);
    background:var(--bg-muted);color:var(--muted);
  }
  .ent-viz{display:flex;flex-direction:column;gap:8px;min-width:0}
  .ent-mos-row{display:flex;align-items:baseline;justify-content:space-between;gap:var(--space-xs)}
  .ent-mos-label{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .ent-mos{
    font-family:var(--font-display);font-size:20px;font-weight:500;
    font-variant-numeric:tabular-nums;line-height:1;color:var(--ink);
  }
  .ent-mos.pos{color:var(--earning-s)}
  .ent-mos.neg{color:var(--exposed)}
  .ent-bar-row{display:grid;grid-template-columns:32px 1fr 34px;gap:8px;align-items:center}
  .ent-bar-lbl{font-size:10px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
  .ent-bar-track{height:7px;background:var(--bg-subtle);border-radius:var(--radius-pill);overflow:hidden}
  .ent-bar-fill{display:block;height:100%;border-radius:var(--radius-pill);min-width:2px}
  .ent-bar-fill.exp{background:var(--exposed);opacity:.85}
  .ent-bar-fill.prep{background:var(--earning-s);opacity:.85}
  .ent-bar-val{font-size:12px;font-variant-numeric:tabular-nums;color:var(--ink2);text-align:right}
  .spread-wrap{margin-top:2px}
  .spread-label{font-size:10px;color:var(--muted);margin-bottom:4px;letter-spacing:.04em}
  .spread-track{
    position:relative;height:8px;background:var(--bg-subtle);border-radius:var(--radius-pill);
  }
  .spread-band{
    position:absolute;top:0;bottom:0;border-radius:var(--radius-pill);opacity:.35;
  }
  .spread-tick{
    position:absolute;top:-2px;width:2px;height:12px;border-radius:1px;
    transform:translateX(-50%);background:var(--ink);
  }
  .spread-tick.prep{background:var(--earning-s)}
  .spread-tick.exp{background:var(--exposed)}

  .panel{
    background:var(--bg-default);border:1px solid var(--line-subtle);
    border-radius:var(--radius-card);padding:var(--space-sm);
  }
  .manifesto-deck{padding:var(--space-lg) 0 var(--space-md)}
  .manifesto-grid{
    display:grid;grid-template-columns:repeat(2,1fr);gap:var(--space-md);
    margin-top:var(--space-md);
  }
  .mf-pillar{padding:var(--space-sm) 0;border-top:1px solid var(--line-subtle)}
  .mf-n{font-size:11px;font-weight:500;letter-spacing:.12em;color:var(--accent);margin-bottom:4px}
  .mf-t{font-weight:600;font-size:15px;color:var(--ink);margin-bottom:4px;line-height:1.3}
  .mf-p{margin:0;font-size:14px;line-height:1.55;color:var(--ink2)}
  .steps-compact{margin:var(--space-md) 0 0;padding:0;list-style:none}
  .steps-compact li{
    padding:var(--space-xs) 0;border-top:1px solid var(--line-subtle);
    font-size:14px;line-height:1.5;color:var(--ink2);
  }
  .steps-compact b{color:var(--ink);font-weight:600}

  #welcome-scrim{
    position:fixed;inset:0;background:rgba(20,20,20,.35);z-index:100;
    display:flex;align-items:center;justify-content:center;padding:var(--space-md);
  }
  #welcome-scrim.hidden{display:none}
  .welcome-box{
    max-width:440px;width:100%;background:var(--bg-default);border-radius:var(--radius-lg);
    padding:var(--space-md);border:1px solid var(--line-subtle);
  }
  .welcome-box h2{
    font-family:var(--font-display);font-size:22px;font-weight:500;
    color:var(--ink);margin:0 0 6px;line-height:1.2;
  }
  .welcome-sub{font-size:14px;color:var(--muted);margin:0 0 var(--space-sm)}
  .welcome-body{font-size:14px;line-height:1.6;color:var(--ink2);margin:0 0 var(--space-sm)}
  .welcome-foot{font-size:13px;color:var(--muted);margin:0 0 var(--space-sm)}
  .welcome-tip{
    font-size:13px;line-height:1.5;color:var(--ink2);padding:10px 12px;
    background:var(--accent-muted);border-radius:var(--radius-md);margin:0 0 var(--space-md);
  }
  .welcome-actions{display:flex;justify-content:flex-end;gap:var(--space-xs)}
  .welcome-actions button{
    padding:8px 16px;border-radius:var(--radius-md);font-size:13px;font-weight:500;
    cursor:pointer;font-family:var(--font-sans);
  }
  .btn-primary{background:var(--section-accent);color:#fff;border:none}
  .btn-primary:hover{background:var(--ink)}
  .btn-ghost{background:var(--bg-default);color:var(--ink2);border:1px solid var(--line)}

  .site-foot{
    padding:var(--space-lg) 0;font-size:13px;color:var(--muted);
    background:var(--bg-muted);border-top:1px solid var(--line-subtle);
  }
  .site-foot-inner{
    display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;
    gap:var(--space-md) var(--space-lg);width:100%;
  }
  .site-foot-links{display:flex;flex-wrap:wrap;align-items:center;gap:var(--space-sm) var(--space-md)}
  .site-foot a{color:var(--ink2);text-decoration:none}
  .site-foot a:hover{text-decoration:underline;color:var(--section-accent)}

  @media(max-width:720px){
    nav a{padding:6px 8px;font-size:12px}
    .ent-card{grid-template-columns:1fr}
    .status-dl{margin-left:0;width:100%}
    .manifesto-grid{grid-template-columns:1fr}
  }
"""


def refs_css() -> str:
    """References band — light ruled index, not dark grid canvas."""
    return r"""
  .ref-band{
    position:relative;background:var(--bg-muted);color:var(--ink2);
    padding:var(--space-lg) 0 var(--space-xl);
    border-top:1px solid var(--line);
    scroll-margin-top:calc(var(--header-h) + 12px);
  }
  .ref-band > .wrap{
    position:relative;z-index:1;max-width:var(--max-w);margin:0 auto;padding:0 var(--space-md);
  }
  .ref-band-intro{margin-bottom:var(--space-md)}
  .ref-kicker{margin:0 0 var(--space-xs)}
  .ref-title{margin:0}
  .ref-lede{
    font-size:14px;line-height:1.6;color:var(--muted);max-width:52ch;margin:var(--space-xs) 0 0;
  }
  .ref-panel{
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);background:var(--bg-default);
    padding:var(--space-md);
  }
  .ref-panel-bar{
    display:flex;justify-content:flex-end;padding-bottom:var(--space-sm);
    border-bottom:1px solid var(--line-subtle);margin-bottom:var(--space-sm);
  }
  .ref-count{
    font-family:var(--font-mono);font-size:11px;letter-spacing:.04em;
    color:var(--muted);
  }
  .ref-grid{
    list-style:none;padding:0;margin:0;
    display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));
    gap:var(--space-sm);
  }
  .ref-card{
    border:1px solid var(--line-subtle);border-radius:var(--radius-sm);
    padding:var(--space-sm) var(--space-md);background:var(--bg-default);
    transition:border-color .15s;
  }
  .ref-card:hover{border-color:var(--line)}
  .ref-card:target{border-color:var(--section-accent);background:var(--accent-muted)}
  .ref-card-head{
    display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;
  }
  .ref-idx{
    font-family:var(--font-mono);font-size:11px;font-weight:500;
    color:var(--muted);font-variant-numeric:tabular-nums;
  }
  .ref-ext{
    font-size:14px;color:var(--muted);text-decoration:none;line-height:1;transition:color .15s;
  }
  .ref-ext:hover{color:var(--section-accent);text-decoration:none}
  .ref-name{
    font-family:var(--font-display);font-size:15px;font-weight:600;line-height:1.35;
    margin:0 0 8px;letter-spacing:-.01em;
  }
  .ref-name a{color:var(--ink);text-decoration:none}
  .ref-name a:hover{color:var(--section-accent);text-decoration:underline}
  .ref-meta{font-size:12px;line-height:1.5;color:var(--muted);margin:0 0 8px}
  .ref-pub{color:var(--muted)}
  .ref-use{
    font-size:11px;line-height:1.55;color:var(--muted);margin:0;
    padding-top:8px;border-top:1px solid var(--line-subtle);
  }
  @media(max-width:780px){.ref-grid{grid-template-columns:1fr}}
"""


def kg_css() -> str:
    """Evidence index — browsable knowledge product, not abstract graph."""
    return r"""
  #knowledge .section-head{margin-bottom:var(--space-md)}
  .kg-shell{
    display:grid;grid-template-columns:minmax(260px,320px) minmax(0,1fr);
    align-items:stretch;max-height:min(68vh,620px);min-height:320px;
    border:1px solid var(--line-subtle);border-radius:var(--radius-lg);
    background:var(--bg-default);overflow:hidden;
  }
  .kg-index{
    display:flex;flex-direction:column;border-right:1px solid var(--line-subtle);
    background:var(--bg-muted);min-height:0;max-height:min(68vh,620px);overflow:hidden;
  }
  .kg-toolbar{padding:var(--space-sm);border-bottom:1px solid var(--line-subtle);flex-shrink:0}
  .kg-search{
    width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:var(--radius-md);
    font-size:13px;font-family:var(--font-sans);background:var(--bg-default);color:var(--ink);
    margin-bottom:var(--space-xs);
  }
  .kg-search:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 2px rgba(184,90,50,.1)}
  .kg-topics{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--line);border-radius:var(--radius-sm);overflow:hidden;background:var(--bg-default)}
  .kg-topic{
    font-family:var(--font-mono);font-size:var(--type-kicker);letter-spacing:var(--type-kicker-track);
    text-transform:uppercase;padding:6px 10px;border:none;border-right:1px solid var(--line-subtle);
    background:transparent;color:var(--muted);cursor:pointer;font-weight:500;
  }
  .kg-topic:last-child{border-right:none}
  .kg-topic:hover{background:var(--bg-muted);color:var(--ink2)}
  .kg-topic.on{background:var(--bg-muted);color:var(--ink);font-weight:600;box-shadow:inset 0 -2px 0 var(--section-accent)}
  .kg-list{
    list-style:none;padding:0;margin:0;overflow-y:auto;flex:1;min-height:0;
  }
  .kg-row{
    display:block;width:100%;text-align:left;padding:10px var(--space-sm);
    border:none;border-bottom:1px solid var(--line-subtle);background:transparent;
    cursor:pointer;font-family:var(--font-sans);transition:background .12s;
  }
  .kg-row:hover{background:var(--bg-default)}
  .kg-row.on{background:var(--bg-default);box-shadow:inset 3px 0 0 var(--section-accent)}
  .kg-row-type{
    display:inline-block;font-size:9px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;
    padding:1px 6px;border-radius:var(--radius-md);margin-bottom:4px;
  }
  .kg-row-title{
    display:block;font-size:13px;font-weight:600;color:var(--ink);line-height:1.35;margin-bottom:2px;
  }
  .kg-row-meta{font-size:11px;color:var(--muted)}
  .kg-detail{
    padding:var(--space-md);overflow-y:auto;min-height:0;max-height:min(68vh,620px);
  }
  .kg-detail-head{margin-bottom:var(--space-sm)}
  .kg-type-pill{
    display:inline-block;font-size:10px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;
    padding:2px 8px;border-radius:var(--radius-md);margin-bottom:8px;
  }
  .kg-detail h3{
    font-family:var(--font-display);font-size:clamp(18px,2.2vw,22px);font-weight:500;
    line-height:1.25;margin:0 0 6px;color:var(--ink);letter-spacing:-.01em;
  }
  .kg-detail-meta{font-size:12px;color:var(--muted);margin:0 0 var(--space-xs);line-height:1.5}
  .kg-detail-meta a{color:var(--section-accent);text-decoration:none;font-weight:500}
  .kg-detail-meta a:hover{text-decoration:underline}
  .kg-block{margin:var(--space-sm) 0 0;padding-top:var(--space-sm);border-top:1px solid var(--line-subtle)}
  .kg-block:first-of-type{margin-top:0;padding-top:0;border-top:none}
  .kg-block h4{
    font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);margin:0 0 var(--space-xs);
  }
  .kg-findings{margin:0;padding-left:18px;font-size:14px;line-height:1.55;color:var(--ink2)}
  .kg-findings li{margin-bottom:6px}
  .kg-sf-chips,.kg-related{display:flex;flex-wrap:wrap;gap:6px}
  .kg-sf{
    font-size:11px;padding:3px 8px;border-radius:var(--radius-md);
    background:var(--bg-muted);color:var(--ink2);border:1px solid var(--line-subtle);
  }
  .kg-rel{
    font-size:12px;padding:4px 10px;border-radius:var(--radius-md);
    border:1px solid var(--line);background:var(--bg-default);color:var(--ink2);
    cursor:pointer;font-family:var(--font-sans);
  }
  .kg-rel:hover{border-color:var(--section-accent);color:var(--section-accent)}
  .kg-detail-grid{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(160px,220px);
    gap:var(--space-md);align-items:start;margin-top:var(--space-sm);
    padding-top:var(--space-sm);border-top:1px solid var(--line-subtle);
  }
  .kg-detail-grid .kg-block{margin:0;padding-top:0;border-top:none}
  .kg-detail-grid .kg-mini{margin:0;padding-top:0;border-top:none}
  @media(max-width:780px){
    .kg-detail-grid{grid-template-columns:1fr}
  }
  .kg-mini{
    margin-top:var(--space-md);padding-top:var(--space-sm);border-top:1px solid var(--line-subtle);
  }
  .kg-mini-label{
    font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);margin:0 0 6px;
  }
  #kgmini{
    width:100%;height:120px;display:block;background:var(--bg-muted);
    border-radius:var(--radius-md);border:1px solid var(--line-subtle);
  }
  .kgmini-node{cursor:pointer}
  .kgmini-node text{font-size:8px;fill:var(--ink2);pointer-events:none}
  .kg-topic-desc{
    font-size:12px;color:var(--muted);line-height:1.5;margin:0 0 var(--space-xs);padding:0 var(--space-sm);
  }
  @media(max-width:900px){
    .kg-shell{grid-template-columns:1fr;max-height:none;min-height:0}
    .kg-index{max-height:240px;border-right:none;border-bottom:1px solid var(--line-subtle)}
    .kg-detail{max-height:none}
  }
"""


def motion_css() -> str:
    """Scroll reveals, stagger, bar growth — ORO-style motion (respects reduced-motion)."""
    return r"""
  .reveal{
    opacity:0;transform:translateY(28px);
    transition:opacity var(--dur-md) var(--ease-out),transform var(--dur-md) var(--ease-out);
  }
  .reveal.in{opacity:1;transform:none}
  .stagger > *{
    opacity:0;transform:translateY(16px);
    transition:opacity var(--dur-md) var(--ease-out),transform var(--dur-md) var(--ease-out);
    transition-delay:calc(var(--delay, 0s) + var(--stagger) * var(--i, 0));
  }
  .stagger.in > *{opacity:1;transform:none}
  .stagger > *{--i:0}
  .stagger > *:nth-child(1){--i:0}.stagger > *:nth-child(2){--i:1}
  .stagger > *:nth-child(3){--i:2}.stagger > *:nth-child(4){--i:3}
  .stagger > *:nth-child(5){--i:4}.stagger > *:nth-child(6){--i:5}
  .stagger > *:nth-child(7){--i:6}.stagger > *:nth-child(8){--i:7}
  .stagger > *:nth-child(n+9){--i:8}
  .ent-bar-fill{
    transition:width var(--dur-md) var(--ease-out);
  }
  .splash{
    position:fixed;inset:0;z-index:10000;background:var(--bg-emphasis);
    display:flex;align-items:center;justify-content:center;
    transition:transform var(--dur-lg) var(--ease-out);
    will-change:transform;
  }
  .splash.is-out{transform:translateY(-100%);pointer-events:none}
  .splash-inner{
    display:flex;flex-direction:column;align-items:center;gap:var(--space-sm);
    animation:splash-logo-in var(--dur-md) var(--ease-out) both;
  }
  @keyframes splash-logo-in{
    from{opacity:0;transform:translateY(14px)}
    to{opacity:1;transform:none}
  }
  .splash-logo{width:min(320px,78vw);height:auto;display:block}
  .splash-glyph{width:72px;height:72px;display:block;margin:0 auto 16px}
  .splash-word{
    margin:0 0 8px;font-family:var(--font-brand);font-weight:600;
    font-size:clamp(1.75rem,5.5vw,2.5rem);letter-spacing:var(--type-brand-track);
    text-transform:uppercase;color:var(--ink-headline);line-height:1.1;
  }
  .splash-tag{margin:0;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
  html.splash-skip #splash{display:none!important}
  body.splash-active{overflow:hidden}
  html:not(.splash-skip):has(#splash) .gate-shell,
  html:not(.splash-skip):has(#splash) .site-main,
  html:not(.splash-skip):has(#splash) .site-foot,
  html:not(.splash-skip):has(#splash) .site-dock{visibility:hidden}
  @media(prefers-reduced-motion:reduce){
    .reveal,.stagger > *,.essay-reveal{opacity:1!important;transform:none!important;transition:none!important}
    .gate-wire{animation:none!important}
    .ent-bar-fill{transition:none!important}
    .splash{transition:none}
    .splash-inner{animation:none;opacity:1}
  }
"""


def visual_css() -> str:
    """Mobile nav bar — flat, not glassmorphism dock."""
    return r"""
  body{padding-bottom:56px}
  .site-dock{
    position:fixed;bottom:0;left:0;right:0;z-index:50;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    padding:10px var(--space-md);background:var(--bg-default);
    border-top:1px solid var(--line-subtle);
    max-width:100vw;
  }
  .site-dock .dock-brand{
    display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--ink);
    font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;
  }
  .site-dock .dock-brand:hover{text-decoration:none;opacity:.85}
  .site-dock .brand-glyph{width:20px;height:20px}
  .dock-cta{
    font-size:12px;font-weight:600;color:#fff;background:var(--accent);
    padding:8px 14px;border-radius:var(--radius-sm);text-decoration:none;white-space:nowrap;
    transition:background .15s;
  }
  .dock-cta:hover{
    color:#fff;text-decoration:none;background:var(--ink);
  }
  .zone-analytical .section.reveal{padding-top:var(--section-y)}
  @media(min-width:900px){
    .site-dock{display:none}
    body{padding-bottom:0}
  }
  body.ds-review .site-dock{display:none}
  body.ds-review{padding-bottom:0}
  body.ds-review::before{
    content:"Design system review · tokens from contract/design_system.json";
    display:block;position:sticky;top:0;z-index:100;
    font:500 11px/1 var(--font-mono);letter-spacing:.02em;
    color:var(--ink2);background:var(--accent-muted);
    border-bottom:1px solid var(--line);padding:6px var(--space-md);text-align:center;
  }
"""


def render_oro_css(ds: dict | None = None) -> str:
    """Deprecated — use frontend.css.render_site_css."""
    from frontend.css import render_site_css
    return render_site_css(ds)


def render_design_css(ds: dict | None = None) -> str:
    """Deprecated — use frontend.css.render_site_css."""
    from frontend.css import render_site_css
    return render_site_css(ds)
