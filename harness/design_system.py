#!/usr/bin/env python3
"""Render harness CSS from contract/design_system.json — AITFYI gray/navy/orange rhythm."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS_PATH = os.path.join(ROOT, "contract", "design_system.json")


def load_design_system(path: str | None = None) -> dict:
    with open(path or DS_PATH) as f:
        return json.load(f)


def css_variables(ds: dict | None = None) -> str:
    ds = ds or load_design_system()
    c = ds["colors"]
    r = ds["radius"]
    s = ds.get("spacing", {})
    f = ds["fonts"]
    m = ds.get("motion", {})
    return f"""
  :root{{
    --bg-emphasis:{c['bg_emphasis']}; --bg-default:{c['bg_default']}; --bg-muted:{c['bg_muted']};
    --bg-subtle:{c.get('bg_subtle', '#F0F0F0')};
    --ink:{c['content_emphasis']}; --ink2:{c['content_default']}; --muted:{c['content_muted']};
    --line:{c['border_default']}; --line-subtle:{c.get('border_subtle', '#E8E8E8')};
    --bg:{c['bg_emphasis']}; --card:{c['bg_default']};
    --accent:{c['accent']}; --accent-muted:{c.get('accent_muted', '#FCE7DD')};
    --accent2:{c['measured']}; --section-accent:{c['section_accent']};
    --exposed:{c['exposed']}; --earning-s:{c['earning']}; --whitespace:{c['whitespace']};
    --sidelined:{c['sidelined']}; --measured:{c['measured']};
    --warn-bg:{c.get('warn_bg', '#FFF7EC')}; --warn-border:{c.get('warn_border', '#F0DCB8')};
    --ok-bg:{c.get('ok_bg', '#EEF7F0')}; --ok-border:{c.get('ok_border', '#CFE6D4')};
    --canvas-dark:{c.get('canvas_dark', '#1e1b18')}; --canvas-grid:{c.get('canvas_grid', 'rgba(255,255,255,0.04)')};
    --glow-accent:{c.get('glow_accent', 'rgba(204,100,55,0.35)')};
    --ease-out:{m.get('ease_out', 'cubic-bezier(0.22, 1, 0.36, 1)')};
    --dur-sm:{m.get('duration_sm', '0.35s')}; --dur-md:{m.get('duration_md', '0.55s')};
    --dur-lg:{m.get('duration_lg', '0.85s')}; --stagger:{m.get('stagger_step', '0.05s')};
    --radius-sm:{r['sm']}; --radius-md:{r['md']}; --radius-lg:{r['lg']}; --radius-card:{r['card']};
    --radius-pill:{r.get('pill', '999px')};
    --font-sans:{f['sans']}; --font-display:{f['display']}; --font-mono:{f['mono']};
    --max-w:{ds['layout']['max_width']};
    --header-h:{ds['layout'].get('header_height', '56px')};
    --space-xs:{s.get('xs', '8px')}; --space-sm:{s.get('sm', '16px')}; --space-md:{s.get('md', '24px')};
    --space-lg:{s.get('lg', '48px')}; --space-xl:{s.get('xl', '72px')};
    --section-y:{s.get('section_y', '56px')};
    --card-gap:{ds['layout'].get('card_gap', '10px')};
  }}
"""


def hero_css() -> str:
    """Dark index gate — ORO grid canvas, wireframe visual, flows into benchmark."""
    return r"""
  .gate-shell{
    position:relative;background:var(--canvas-dark);color:#ccc;overflow:hidden;
  }
  .gate-shell::before{
    content:"";position:absolute;inset:0;pointer-events:none;opacity:.9;
    background-image:
      linear-gradient(var(--canvas-grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--canvas-grid) 1px, transparent 1px);
    background-size:48px 48px;
  }
  .gate-shell::after{
    content:"";position:absolute;inset:0;pointer-events:none;opacity:.04;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  .gate-bar{
    position:sticky;top:0;z-index:40;background:rgba(30,27,24,.92);
    backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    border-bottom:1px solid rgba(255,255,255,.06);
  }
  .gate-bar .wrap{
    display:flex;align-items:center;min-height:var(--header-h);gap:var(--space-sm);
  }
  .gate-shell .brand{color:#fff;text-decoration:none}
  .gate-shell .brand:hover{color:#fff;text-decoration:none;opacity:.92}
  .gate-shell .brand-mark{
    flex:0 0 28px;width:28px;height:28px;background:#fff;
    -webkit-mask:url(assets/princeps-triquetra.png) center/contain no-repeat;
    -webkit-mask-mode:luminance;
    mask:url(assets/princeps-triquetra.png) center/contain no-repeat;
    mask-mode:luminance;
  }
  .site-dock .brand-mark{flex:0 0 20px;width:20px;height:20px;background:var(--section-accent)}
  .gate-shell .brand-word{color:#fff}
  .gate-shell .brand-product{color:#888}
  .gate-shell .brand-sep{color:#333}
  .gate-shell .brand-lockup{display:inline-flex;align-items:baseline;gap:6px}
  .gate-shell .brand-word{font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase}
  .gate-shell nav{margin-left:auto}
  .gate-shell nav a{
    font-size:13px;color:#888;padding:6px 10px;border-radius:var(--radius-md);text-decoration:none;
  }
  .gate-shell nav a:hover{background:#1a1a1a;color:#fff;text-decoration:none}
  .gate-shell nav .nav-sep{background:#333}

  .hero-gate{padding:var(--space-lg) 0 var(--space-md);position:relative;z-index:1}
  .hero-gate .wrap{max-width:var(--max-w);margin:0 auto;padding:0 var(--space-md)}
  .gate-grid{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(160px,260px);
    gap:var(--space-lg);align-items:center;
  }
  .gate-visual{
    display:flex;align-items:center;justify-content:center;
    min-height:240px;pointer-events:none;
  }
  .gate-wire{
    width:min(240px,100%);height:auto;
    animation:gate-float var(--dur-lg) var(--ease-out) infinite alternate;
  }
  @keyframes gate-float{
    from{transform:translateY(0) rotate(0deg)}
    to{transform:translateY(-8px) rotate(1deg)}
  }
  .hero-kicker{
    display:inline-block;font-size:10px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
    color:#c8d4e8;padding:5px 12px;margin:0 0 var(--space-sm);
    border:1px solid rgba(200,212,232,.25);border-radius:var(--radius-pill);
    background:rgba(200,212,232,.06);
  }
  .hero-title{
    font-family:var(--font-display);font-weight:500;
    font-size:clamp(32px,4.8vw,48px);line-height:1.08;
    letter-spacing:-.03em;max-width:16ch;margin:0 0 var(--space-sm);color:#fff;
  }
  .hero-lede{
    font-size:15px;line-height:1.6;color:#999;
    max-width:46ch;margin:0 0 var(--space-md);
  }
  .gate-foot{
    display:flex;flex-wrap:wrap;align-items:center;gap:var(--space-sm) var(--space-md);
  }
  .hero-cta-btn{
    display:inline-flex;align-items:center;gap:6px;
    font-size:13px;font-weight:600;color:var(--canvas-dark);background:#fff;
    padding:11px 20px;border-radius:var(--radius-pill);text-decoration:none;
    transition:transform var(--dur-sm) var(--ease-out),box-shadow var(--dur-sm),background .15s;
    box-shadow:0 0 0 0 var(--glow-accent);
  }
  .hero-cta-btn:hover{
    background:#f5f5f5;color:#000;text-decoration:none;
    transform:translateY(-1px);box-shadow:0 8px 28px var(--glow-accent);
  }
  .gate-stats{
    font-family:var(--font-mono);font-size:11px;letter-spacing:.06em;
    text-transform:uppercase;color:#555;
  }
  .gate-stats b{color:#888;font-weight:500}

  @media(max-width:780px){
    .gate-grid{grid-template-columns:1fr}
    .gate-visual{display:none}
    .hero-title{max-width:none}
  }
"""


def shell_css() -> str:
    return r"""
  *{box-sizing:border-box}
  body{
    margin:0;font-family:var(--font-sans);font-size:15px;line-height:1.55;
    color:var(--ink2);background:var(--bg-emphasis);-webkit-font-smoothing:antialiased;
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
    display:inline-flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);
    letter-spacing:-.01em;
  }
  .brand:hover{text-decoration:none;color:var(--ink)}
  .brand-mark{
    flex:0 0 28px;width:28px;height:28px;
    background:var(--section-accent);
    -webkit-mask:url(assets/princeps-triquetra.png) center/contain no-repeat;
    -webkit-mask-mode:luminance;
    mask:url(assets/princeps-triquetra.png) center/contain no-repeat;
    mask-mode:luminance;
  }
  .brand-mark.lg{flex:0 0 40px;width:40px;height:40px}
  .brand-mark.sm{flex:0 0 18px;width:18px;height:18px}
  .brand-lockup{display:inline-flex;align-items:baseline;gap:6px;line-height:1}
  .brand-word{
    font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink);
  }
  .brand-sep{color:var(--line);font-weight:400;font-size:12px}
  .brand-product{font-size:13px;font-weight:500;color:var(--muted)}
  .welcome-brand{display:flex;align-items:center;gap:12px;margin-bottom:var(--space-sm)}
  .welcome-brand .brand-word{font-size:12px}
  .foot-brand{display:inline-flex;align-items:center;gap:8px;color:var(--muted)}
  nav{margin-left:auto;display:flex;align-items:center;gap:2px}
  nav a{
    font-size:13px;color:var(--ink2);padding:6px 10px;border-radius:var(--radius-md);
    text-decoration:none;
  }
  nav a:hover{background:var(--bg-muted);text-decoration:none;color:var(--ink)}
  nav .nav-sep{width:1px;height:12px;background:var(--line);margin:0 4px}

  .section{padding:var(--section-y) 0;border-bottom:1px solid var(--line-subtle)}
  .section:last-of-type{border-bottom:none}
  .section-head{margin-bottom:var(--space-md)}
  .section-kicker{
    display:inline-block;font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--accent);margin:0 0 var(--space-xs);padding:4px 10px;
    border:1px solid var(--line);border-radius:var(--radius-pill);background:var(--bg-default);
  }
  .section-title{
    font-family:var(--font-display);font-size:clamp(22px,2.8vw,28px);
    font-weight:500;line-height:1.15;letter-spacing:-.02em;color:var(--ink);margin:0;
  }
  .section-lede{font-size:15px;color:var(--muted);max-width:52ch;margin:var(--space-xs) 0 0;line-height:1.55}

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
  .status-dl{display:flex;flex-wrap:wrap;gap:var(--space-xs);margin-left:auto}
  .status-dl a{
    font-size:12px;color:var(--ink2);padding:5px 10px;border:1px solid var(--line);
    border-radius:var(--radius-md);background:var(--bg-default);text-decoration:none;
  }
  .status-dl a:hover{border-color:var(--section-accent);text-decoration:none}

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
  .idx-search:focus{outline:none;border-color:var(--section-accent);box-shadow:0 0 0 2px rgba(27,58,107,.1)}
  .idx-btn{
    padding:8px 12px;border:1px solid var(--line);border-radius:var(--radius-md);
    background:var(--bg-default);font-size:13px;color:var(--ink2);cursor:pointer;font-family:var(--font-sans);
  }
  .idx-btn.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .idx-meta{font-size:13px;color:var(--muted);margin-left:auto}

  .card-list{display:flex;flex-direction:column;gap:var(--card-gap)}
  .ent-card{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(220px,280px);
    gap:var(--space-md);align-items:center;
    padding:var(--space-sm) var(--space-md);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-card);
    cursor:pointer;
    transition:border-color var(--dur-sm),transform var(--dur-sm) var(--ease-out),box-shadow var(--dur-sm);
  }
  .ent-card:hover{
    border-color:var(--line);transform:translateY(-2px);
    box-shadow:0 12px 32px rgba(20,20,20,.06);
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
    border-radius:var(--radius-lg);padding:var(--space-sm);
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
    box-shadow:0 12px 40px rgba(0,0,0,.08);
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
    display:flex;flex-wrap:wrap;gap:var(--space-sm) var(--space-md);
  }
  .site-foot a{color:var(--ink2);text-decoration:none}
  .site-foot a:hover{text-decoration:underline}

  @media(max-width:720px){
    nav a{padding:6px 8px;font-size:12px}
    .ent-card{grid-template-columns:1fr}
    .status-dl{margin-left:0;width:100%}
    .manifesto-grid{grid-template-columns:1fr}
    .bench-split{grid-template-columns:1fr}
    .bench-rail{padding:var(--space-md)}
  }
"""


def bench_css() -> str:
    return """
  .ent-logo-wrap{
    flex:0 0 36px;width:36px;height:36px;border-radius:var(--radius-md);
    background:var(--bg-default);border:1px solid var(--line-subtle);
    display:flex;align-items:center;justify-content:center;overflow:hidden;
  }
  .ent-logo{width:100%;height:100%;object-fit:contain;padding:4px;background:#fff}
  .ent-logo-fallback{
    display:flex;align-items:center;justify-content:center;width:100%;height:100%;
    font-size:11px;font-weight:600;color:var(--section-accent);background:var(--bg-subtle);
  }
  .ent-logo-wrap.sm{flex:0 0 32px;width:32px;height:32px}
  .ent-logo-wrap.xs{flex:0 0 22px;width:22px;height:22px;border-radius:4px}

  .bench-section{margin:0 0 var(--space-lg)}
  .bench-section--flush{margin-top:0}
  .bench-section--flush .bench-split{
    border-radius:0;border-left:none;border-right:none;border-top:none;
  }
  .bench-split{
    display:grid;grid-template-columns:minmax(240px,280px) minmax(0,1fr);
    min-height:560px;border-radius:var(--radius-lg);overflow:hidden;
    border:1px solid var(--line-subtle);background:var(--bg-default);
  }
  .bench-rail{
    background:#111;color:#fff;padding:var(--space-md) var(--space-md) var(--space-lg);
    display:flex;flex-direction:column;
  }
  .bench-kicker{
    font-size:11px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;
    color:#888;margin:0 0 var(--space-xs);
  }
  .bench-title{
    font-family:var(--font-display);font-size:clamp(20px,2.2vw,26px);
    font-weight:500;line-height:1.15;letter-spacing:-.02em;margin:0 0 var(--space-xs);
  }
  .bench-lede{font-size:14px;color:#aaa;line-height:1.55;margin:0 0 var(--space-md);max-width:28ch}
  .bench-tabs{display:flex;flex-direction:column;gap:2px;margin-bottom:var(--space-sm)}
  .bench-tab{
    text-align:left;padding:9px 0 9px 14px;border:none;border-left:2px solid transparent;
    background:none;color:#888;font-size:14px;cursor:pointer;font-family:var(--font-sans);
    transition:color .15s,border-color .15s;
  }
  .bench-tab:hover{color:#ccc}
  .bench-tab.on{color:#fff;border-left-color:#fff}
  .bench-filters{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:var(--space-md)}
  .bench-filter{
    font-size:11px;padding:4px 10px;border-radius:var(--radius-pill);
    border:1px solid #333;background:transparent;color:#888;cursor:pointer;font-family:var(--font-sans);
  }
  .bench-filter:hover{border-color:#555;color:#ccc}
  .bench-filter.on{background:#fff;color:#111;border-color:#fff}
  .bench-note{font-size:13px;color:#777;line-height:1.5;margin-top:var(--space-sm)}
  .bench-panel{padding:var(--space-md);display:flex;flex-direction:column;min-width:0;min-height:0}
  .bench-head{
    display:flex;align-items:flex-start;justify-content:space-between;gap:var(--space-md);
    margin-bottom:var(--space-sm);flex-shrink:0;
  }
  .bench-metric-label{font-size:13px;color:var(--muted);margin:0}
  .bench-metric-label b{color:var(--ink);font-weight:600}
  .bench-hint{font-size:12px;color:var(--muted);margin:4px 0 0}
  .bench-legend{display:flex;flex-wrap:wrap;gap:10px 16px;font-size:12px;color:var(--muted);align-items:center}
  .bench-legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}

  .bench-chart-wrap{
    flex-shrink:0;background:var(--bg-muted);border:1px solid var(--line-subtle);
    border-radius:var(--radius-md);padding:var(--space-sm) var(--space-xs) 0;margin-bottom:var(--space-sm);
    overflow-x:auto;
  }
  .bench-svg{display:block;width:100%;min-width:520px;height:auto}
  .bench-svg-col{cursor:pointer;transition:opacity .15s}
  .bench-svg-col:hover{opacity:.85}
  .bench-svg-col.on rect{stroke:#141414;stroke-width:2}

  .bench-list-head{
    display:flex;justify-content:space-between;align-items:center;
    font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);padding:0 2px var(--space-xs);flex-shrink:0;
  }
  .bench-list{
    flex:1;overflow-y:auto;overflow-x:hidden;min-height:200px;max-height:420px;
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);background:var(--bg-default);
  }
  .bench-row{
    display:grid;grid-template-columns:28px 32px minmax(120px,1.4fr) minmax(140px,2fr) auto 24px;
    gap:10px;align-items:center;padding:10px 12px;border-bottom:1px solid var(--line-subtle);
    cursor:pointer;transition:background .12s;text-align:left;width:100%;
    background:var(--bg-default);border-left:none;border-right:none;border-top:none;
    font-family:var(--font-sans);
  }
  .bench-row:last-child{border-bottom:none}
  .bench-row:hover,.bench-row:focus-visible{background:var(--bg-muted);outline:none}
  .bench-row.on{background:var(--accent-muted)}
  .bench-rank{
    font-size:12px;font-weight:600;color:var(--muted);font-variant-numeric:tabular-nums;text-align:center;
  }
  .bench-row-id{min-width:0}
  .bench-row-name{
    display:block;font-size:14px;font-weight:600;color:var(--ink);line-height:1.25;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  }
  .bench-row-tag{
    display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
    padding:1px 6px;border-radius:var(--radius-pill);margin-top:3px;
  }
  .bench-row-tag.quad-exposed{background:#fde8e7;color:#cf4a45}
  .bench-row-tag.quad-earning_it{background:#e8f3ea;color:#34894b}
  .bench-row-tag.quad-whitespace{background:#e8f0f8;color:#3f7fb0}
  .bench-row-tag.quad-sidelined{background:var(--bg-subtle);color:var(--muted)}
  .bench-row-track{
    position:relative;height:28px;background:var(--bg-subtle);border-radius:var(--radius-md);
    overflow:hidden;display:flex;align-items:center;
  }
  .bench-row-fill{
    position:absolute;left:0;top:0;bottom:0;border-radius:var(--radius-md);
    transition:width .3s ease;min-width:2px;
  }
  .bench-row-fill.quad-exposed{background:#cf4a45}
  .bench-row-fill.quad-earning_it{background:#34894b}
  .bench-row-fill.quad-whitespace{background:#3f7fb0}
  .bench-row-fill.quad-sidelined{background:#9aa7ad}
  .bench-row-val{
    position:relative;z-index:1;font-size:13px;font-weight:600;color:var(--ink);
    padding-left:10px;font-variant-numeric:tabular-nums;
  }
  .bench-row-stats{
    display:flex;gap:10px;font-size:11px;color:var(--muted);white-space:nowrap;
    font-variant-numeric:tabular-nums;
  }
  .bench-row-stats b{color:var(--ink);font-weight:600}
  .bench-row-action{font-size:16px;color:var(--muted);opacity:0;transition:opacity .12s}
  .bench-row:hover .bench-row-action{opacity:1}

  .tbl-logo{display:inline-flex;vertical-align:middle;margin-right:8px}
  .tbl-name{display:inline-flex;align-items:center;gap:0;min-width:0}

  @media(max-width:900px){
    .bench-row{
      grid-template-columns:24px 28px 1fr auto;
      grid-template-rows:auto auto;gap:6px 10px;
    }
    .bench-row-track{grid-column:1/-1}
    .bench-row-stats{display:none}
    .bench-row-action{display:none}
  }
"""


def refs_css() -> str:
    """References band — dark industrial index (NOX / Hades / Cowboy Space cues)."""
    return r"""
  .ref-band{
    position:relative;background:var(--canvas-dark);color:#ccc;
    padding:var(--space-lg) 0 var(--space-xl);overflow:hidden;
    scroll-margin-top:calc(var(--header-h) + 12px);
  }
  .ref-band::before{
    content:"";position:absolute;inset:0;pointer-events:none;opacity:.85;
    background-image:
      linear-gradient(var(--canvas-grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--canvas-grid) 1px, transparent 1px);
    background-size:48px 48px;
  }
  .ref-band > .wrap{
    position:relative;z-index:1;max-width:var(--max-w);margin:0 auto;padding:0 var(--space-md);
  }
  .ref-band-intro{margin-bottom:var(--space-md)}
  .ref-kicker{
    font-size:11px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;
    color:#666;margin:0 0 var(--space-xs);
  }
  .ref-title{
    font-family:var(--font-display);font-size:clamp(24px,3vw,32px);
    font-weight:500;letter-spacing:-.02em;color:#fff;margin:0;line-height:1.15;
  }
  .ref-lede{
    font-size:14px;line-height:1.6;color:#888;max-width:52ch;margin:0 0 var(--space-md);
  }
  .ref-panel{
    border:1px solid #222;border-radius:16px;background:#141414;padding:var(--space-md);
  }
  .ref-panel-bar{
    display:flex;justify-content:flex-end;padding-bottom:var(--space-sm);
    border-bottom:1px solid #222;margin-bottom:var(--space-sm);
  }
  .ref-count{
    font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;
    text-transform:uppercase;color:#555;
  }
  .ref-grid{
    list-style:none;padding:0;margin:0;
    display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));
    gap:var(--space-sm);
  }
  .ref-card{
    border:1px solid #222;border-radius:12px;padding:var(--space-sm) var(--space-md);
    background:#0e0e0e;transition:border-color .15s,background .15s;
  }
  .ref-card:hover{border-color:#333;background:#111}
  .ref-card:target{border-color:var(--accent);box-shadow:0 0 0 1px rgba(204,100,55,.2)}
  .ref-card-head{
    display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;
  }
  .ref-idx{
    font-family:var(--font-mono);font-size:11px;font-weight:500;letter-spacing:.06em;
    color:#555;font-variant-numeric:tabular-nums;
  }
  .ref-ext{
    font-size:14px;color:#555;text-decoration:none;line-height:1;transition:color .15s;
  }
  .ref-ext:hover{color:#fff;text-decoration:none}
  .ref-name{
    font-family:var(--font-display);font-size:15px;font-weight:500;line-height:1.35;
    margin:0 0 8px;letter-spacing:-.01em;
  }
  .ref-name a{color:#eee;text-decoration:none}
  .ref-name a:hover{color:#fff;text-decoration:underline}
  .ref-meta{font-size:12px;line-height:1.5;color:#777;margin:0 0 8px}
  .ref-pub{color:#555}
  .ref-use{
    font-size:11px;line-height:1.55;color:#555;margin:0;letter-spacing:.01em;
    padding-top:8px;border-top:1px solid #1a1a1a;
  }
  @media(max-width:780px){.ref-grid{grid-template-columns:1fr}}
"""


def kg_css() -> str:
    """Evidence index — browsable knowledge product, not abstract graph."""
    return r"""
  #knowledge .section-head{margin-bottom:var(--space-md)}
  .kg-shell{
    display:grid;grid-template-columns:minmax(280px,340px) minmax(0,1fr);
    gap:var(--space-md);min-height:520px;
    border:1px solid var(--line-subtle);border-radius:var(--radius-lg);
    background:var(--bg-default);overflow:hidden;
  }
  .kg-index{
    display:flex;flex-direction:column;border-right:1px solid var(--line-subtle);
    background:var(--bg-muted);min-height:0;
  }
  .kg-toolbar{padding:var(--space-sm);border-bottom:1px solid var(--line-subtle);flex-shrink:0}
  .kg-search{
    width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:var(--radius-md);
    font-size:13px;font-family:var(--font-sans);background:var(--bg-default);color:var(--ink);
    margin-bottom:var(--space-xs);
  }
  .kg-search:focus{outline:none;border-color:var(--section-accent);box-shadow:0 0 0 2px rgba(27,58,107,.08)}
  .kg-topics{display:flex;flex-wrap:wrap;gap:4px}
  .kg-topic{
    font-size:10px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;
    padding:4px 8px;border-radius:var(--radius-pill);border:1px solid var(--line);
    background:var(--bg-default);color:var(--muted);cursor:pointer;font-family:var(--font-sans);
  }
  .kg-topic:hover{border-color:var(--line);color:var(--ink2)}
  .kg-topic.on{background:var(--ink);color:#fff;border-color:var(--ink)}
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
    padding:var(--space-md);overflow-y:auto;min-height:0;display:flex;flex-direction:column;
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
  .kg-mini{
    margin-top:auto;padding-top:var(--space-sm);border-top:1px solid var(--line-subtle);flex-shrink:0;
  }
  .kg-mini-label{
    font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);margin:0 0 6px;
  }
  #kgmini{width:100%;height:140px;display:block;background:var(--bg-muted);border-radius:var(--radius-md)}
  .kgmini-node{cursor:pointer}
  .kgmini-node text{font-size:8px;fill:var(--ink2);pointer-events:none}
  .kg-topic-desc{
    font-size:12px;color:var(--muted);line-height:1.5;margin:0 0 var(--space-xs);padding:0 var(--space-sm);
  }
  @media(max-width:900px){
    .kg-shell{grid-template-columns:1fr;min-height:0}
    .kg-index{max-height:280px;border-right:none;border-bottom:1px solid var(--line-subtle)}
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
  .bench-row-fill,.ent-bar-fill{
    transition:width var(--dur-md) var(--ease-out);
  }
  @media(prefers-reduced-motion:reduce){
    .reveal,.stagger > *{opacity:1!important;transform:none!important;transition:none!important}
    .gate-wire{animation:none!important}
    .bench-row-fill,.ent-bar-fill{transition:none!important}
  }
"""


def visual_css() -> str:
    """Floating dock, zone rhythm — ORO product chrome."""
    return r"""
  body{padding-bottom:72px}
  .site-dock{
    position:fixed;bottom:16px;left:50%;transform:translateX(-50%);z-index:50;
    display:flex;align-items:center;gap:12px;
    padding:8px 8px 8px 16px;background:rgba(255,255,255,.92);
    border:1px solid var(--line-subtle);border-radius:var(--radius-pill);
    box-shadow:0 8px 32px rgba(0,0,0,.12),0 2px 8px rgba(0,0,0,.06);
    backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
    max-width:calc(100vw - 32px);
  }
  .site-dock .dock-brand{
    display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--ink);
    font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap;
  }
  .site-dock .dock-brand:hover{text-decoration:none;opacity:.85}
  .site-dock .brand-mark{flex:0 0 20px;width:20px;height:20px}
  .dock-cta{
    font-size:12px;font-weight:600;color:#fff;background:var(--accent);
    padding:10px 18px;border-radius:var(--radius-pill);text-decoration:none;white-space:nowrap;
    transition:transform var(--dur-sm) var(--ease-out),box-shadow var(--dur-sm);
  }
  .dock-cta:hover{
    color:#fff;text-decoration:none;transform:translateY(-1px);
    box-shadow:0 6px 20px var(--glow-accent);
  }
  .zone-analytical .section.reveal{padding-top:var(--section-y)}
  @media(min-width:900px){
    .site-dock{display:none}
    body{padding-bottom:0}
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
