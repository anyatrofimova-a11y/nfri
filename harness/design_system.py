#!/usr/bin/env python3
"""Render harness CSS from contract/design_system.json — one rhythm, one palette."""
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
    o = ds.get("palette", {}).get("ocean", {})
    r = ds["radius"]
    s = ds.get("spacing", {})
    f = ds["fonts"]
    return f"""
  :root{{
    --bg-emphasis:{c['bg_emphasis']}; --bg-default:{c['bg_default']}; --bg-muted:{c['bg_muted']};
    --bg-subtle:{c.get('bg_subtle', '#EFEFEF')};
    --ink:{c['content_emphasis']}; --ink2:{c['content_default']}; --muted:{c['content_muted']};
    --line:{c['border_default']}; --line-subtle:{c.get('border_subtle', '#E5E5E5')};
    --bg:{c['bg_emphasis']}; --card:{c['bg_default']};
    --accent:{c['accent']}; --accent2:{c['measured']}; --section-accent:{c['section_accent']};
    --ocean-deep:{o.get('deep', '#0047E6')}; --ocean-dark:{o.get('deep_dark', '#003BB8')};
    --ocean-glow:{o.get('glow', '#1A6BFF')}; --ocean-on:{o.get('on_deep', '#FFF')};
    --ocean-on-muted:{o.get('on_deep_muted', 'rgba(255,255,255,.72)')};
    --exposed:{c['exposed']}; --earning-s:{c['earning']}; --whitespace:{c['whitespace']};
    --sidelined:{c['sidelined']}; --measured:{c['measured']};
    --warn-bg:{c.get('warn_bg', '#FAF6EF')}; --warn-border:{c.get('warn_border', '#E8DCC4')};
    --ok-bg:{c.get('ok_bg', '#F2F7F3')}; --ok-border:{c.get('ok_border', '#D4E8DA')};
    --radius-sm:{r['sm']}; --radius-md:{r['md']}; --radius-lg:{r['lg']}; --radius-card:{r['card']};
    --radius-pill:{r.get('pill', '999px')};
    --font-sans:{f['sans']}; --font-display:{f['display']}; --font-hero:{f.get('hero_sans', f['sans'])};
    --font-mono:{f['mono']};
    --max-w:{ds['layout']['max_width']};
    --header-h:{ds['layout'].get('header_height', '56px')};
    --cinematic-min:{ds['layout'].get('cinematic_min_height', 'min(72vh,600px)')};
    --space-xs:{s.get('xs', '8px')}; --space-sm:{s.get('sm', '16px')}; --space-md:{s.get('md', '24px')};
    --space-lg:{s.get('lg', '48px')}; --space-xl:{s.get('xl', '72px')};
    --section-y:{s.get('section_y', '56px')};
    --card-gap:{ds['layout'].get('card_gap', '10px')};
  }}
"""


def cinematic_css() -> str:
    return r"""
  .cinematic-hero{
    position:relative;min-height:var(--cinematic-min);width:100%;
    display:flex;flex-direction:column;justify-content:flex-end;
    background:linear-gradient(168deg,var(--ocean-glow) 0%,var(--ocean-deep) 45%,var(--ocean-dark) 100%);
    color:var(--ocean-on);overflow:hidden;
  }
  .cinematic-nav{
    position:absolute;top:0;left:0;right:0;z-index:2;
    display:flex;align-items:center;justify-content:space-between;
    padding:var(--space-sm) var(--space-md);max-width:calc(var(--max-w) + 48px);margin:0 auto;width:100%;
  }
  .cinematic-logo{
    font-family:var(--font-hero);font-weight:600;font-size:13px;
    letter-spacing:.16em;text-transform:uppercase;color:var(--ocean-on);
  }
  .cinematic-nav a{
    color:var(--ocean-on-muted);text-decoration:none;font-size:11px;
    letter-spacing:.08em;text-transform:uppercase;font-weight:500;
  }
  .cinematic-nav a:hover{color:var(--ocean-on)}
  .cinematic-inner{
    position:relative;z-index:1;max-width:var(--max-w);margin:0 auto;
    padding:0 var(--space-md) var(--space-lg);width:100%;
  }
  .cinematic-kicker{
    font-size:11px;font-weight:500;letter-spacing:.2em;text-transform:uppercase;
    color:var(--ocean-on-muted);margin:0 0 var(--space-sm);
  }
  .cinematic-title{
    font-family:var(--font-display);font-weight:500;
    font-size:clamp(28px,4vw,40px);line-height:1.14;
    letter-spacing:-.02em;max-width:18ch;margin:0 0 var(--space-sm);color:var(--ocean-on);
  }
  .cinematic-lede{
    font-size:16px;line-height:1.55;color:var(--ocean-on-muted);
    max-width:46ch;margin:0 0 var(--space-md);
  }
  .cinematic-scroll{
    font-size:11px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;
    color:var(--ocean-on);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.3);
    padding-bottom:2px;
  }
  .zone-analytical{background:var(--bg-emphasis)}
  .zone-transition{height:1px;background:var(--line)}
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

  /* —— header —— */
  header.top{
    position:sticky;top:0;z-index:30;background:rgba(255,255,255,.94);
    backdrop-filter:blur(8px);border-bottom:1px solid var(--line-subtle);
  }
  .top .wrap{display:flex;align-items:center;min-height:var(--header-h);gap:var(--space-sm)}
  .brand{font-weight:600;font-size:14px;color:var(--ink);letter-spacing:-.01em}
  .brand-mark{
    display:inline-flex;align-items:center;justify-content:center;
    width:26px;height:26px;margin-right:8px;border-radius:var(--radius-md);
    background:var(--section-accent);color:#fff;font-size:10px;font-weight:700;
    vertical-align:middle;
  }
  nav{margin-left:auto;display:flex;align-items:center;gap:2px}
  nav a{
    font-size:13px;color:var(--ink2);padding:6px 10px;border-radius:var(--radius-md);
    text-decoration:none;
  }
  nav a:hover{background:var(--bg-subtle);text-decoration:none}
  nav .nav-sep{width:1px;height:12px;background:var(--line);margin:0 4px}

  /* —— sections —— */
  .section{padding:var(--section-y) 0;border-bottom:1px solid var(--line-subtle)}
  .section:last-of-type{border-bottom:none}
  .section-head{margin-bottom:var(--space-md)}
  .section-kicker{
    font-size:11px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;
    color:var(--muted);margin:0 0 var(--space-xs);
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
    text-transform:uppercase;color:var(--muted);margin-bottom:6px;
  }
  .part-t{
    font-family:var(--font-display);font-size:clamp(20px,2.5vw,26px);
    font-weight:500;letter-spacing:-.02em;color:var(--ink);margin:0;
  }

  /* —— status strip —— */
  .status-strip{
    display:flex;flex-wrap:wrap;align-items:center;gap:var(--space-sm) var(--space-md);
    padding:var(--space-sm) 0 var(--space-md);border-bottom:1px solid var(--line-subtle);
    margin-bottom:var(--space-md);
  }
  .status-strip .banner{
    flex:1 1 280px;margin:0;padding:12px 14px;font-size:14px;line-height:1.5;
    border-radius:var(--radius-md);border:1px solid var(--warn-border);background:var(--warn-bg);
  }
  .status-strip .banner.ok{border-color:var(--ok-border);background:var(--ok-bg)}
  .status-strip .banner b{font-weight:600}
  .status-meta{display:flex;flex-wrap:wrap;gap:var(--space-sm) var(--space-md);font-size:13px;color:var(--muted)}
  .status-meta b{color:var(--ink);font-weight:600}
  .status-dl{display:flex;flex-wrap:wrap;gap:var(--space-sm);margin-left:auto}
  .status-dl a{
    font-size:12px;color:var(--ink2);padding:5px 10px;border:1px solid var(--line);
    border-radius:var(--radius-md);background:var(--bg-default);text-decoration:none;
  }
  .status-dl a:hover{border-color:var(--section-accent);text-decoration:none}

  /* —— index toolbar —— */
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
  .idx-search:focus{outline:none;border-color:var(--section-accent);box-shadow:0 0 0 2px rgba(27,58,107,.12)}
  .idx-btn{
    padding:8px 12px;border:1px solid var(--line);border-radius:var(--radius-md);
    background:var(--bg-default);font-size:13px;color:var(--ink2);cursor:pointer;font-family:var(--font-sans);
  }
  .idx-btn.on{background:var(--section-accent);color:#fff;border-color:var(--section-accent)}
  .idx-meta{font-size:13px;color:var(--muted);margin-left:auto}

  /* —— entity cards —— */
  .card-list{display:flex;flex-direction:column;gap:var(--card-gap)}
  .ent-card{
    display:grid;grid-template-columns:1fr auto;gap:var(--space-md);align-items:center;
    padding:var(--space-sm) var(--space-md);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-card);
    cursor:pointer;transition:border-color .15s,background .15s;
  }
  .ent-card:hover{border-color:var(--line);background:var(--bg-muted)}
  .ent-id{display:flex;gap:var(--space-sm);align-items:center;min-width:0}
  .ent-avatar{
    flex:0 0 36px;width:36px;height:36px;border-radius:var(--radius-md);
    background:var(--bg-subtle);display:flex;align-items:center;justify-content:center;
    font-size:12px;font-weight:600;color:var(--section-accent);
  }
  .ent-name{font-weight:600;font-size:15px;color:var(--ink);line-height:1.3}
  .ent-meta{font-size:13px;color:var(--muted);margin-top:2px}
  .ent-scores{text-align:right;white-space:nowrap}
  .ent-mos{
    font-family:var(--font-display);font-size:22px;font-weight:500;
    color:var(--ink);font-variant-numeric:tabular-nums;line-height:1;
  }
  .ent-mos.neg{color:var(--exposed)}
  .ent-mos.pos{color:var(--earning-s)}
  .ent-pair{font-size:12px;color:var(--muted);margin-top:4px;font-variant-numeric:tabular-nums}
  .quad-tag{
    display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;
    letter-spacing:.04em;padding:2px 7px;border-radius:var(--radius-pill);color:#fff;margin-left:6px;
  }

  /* —— panels —— */
  .panel{
    background:var(--bg-default);border:1px solid var(--line-subtle);
    border-radius:var(--radius-lg);padding:var(--space-sm);
  }
  .manifesto-deck{padding:var(--space-lg) 0 var(--space-md)}
  .manifesto-grid{
    display:grid;grid-template-columns:repeat(2,1fr);gap:var(--space-sm);
    margin-top:var(--space-md);
  }
  .mf-pillar{
    padding:var(--space-sm) 0;border-top:1px solid var(--line-subtle);
  }
  .mf-n{font-size:11px;font-weight:500;letter-spacing:.12em;color:var(--muted);margin-bottom:4px}
  .mf-t{font-weight:600;font-size:15px;color:var(--ink);margin-bottom:4px;line-height:1.3}
  .mf-p{margin:0;font-size:14px;line-height:1.55;color:var(--ink2)}
  .steps-compact{margin:var(--space-md) 0 0;padding:0;list-style:none}
  .steps-compact li{
    padding:var(--space-xs) 0;border-top:1px solid var(--line-subtle);
    font-size:14px;line-height:1.5;color:var(--ink2);
  }
  .steps-compact b{color:var(--ink);font-weight:600}

  /* —— welcome —— */
  #welcome-scrim{
    position:fixed;inset:0;background:rgba(17,17,17,.4);z-index:100;
    display:flex;align-items:center;justify-content:center;padding:var(--space-md);
  }
  #welcome-scrim.hidden{display:none}
  .welcome-box{
    max-width:440px;width:100%;background:var(--bg-default);border-radius:var(--radius-lg);
    padding:var(--space-md);box-shadow:0 16px 48px rgba(0,0,0,.12);
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
    background:var(--bg-muted);border-radius:var(--radius-md);margin:0 0 var(--space-md);
  }
  .welcome-actions{display:flex;justify-content:flex-end;gap:var(--space-xs)}
  .welcome-actions button{
    padding:8px 16px;border-radius:var(--radius-md);font-size:13px;font-weight:500;
    cursor:pointer;font-family:var(--font-sans);
  }
  .btn-primary{background:var(--section-accent);color:#fff;border:none}
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
    .ent-scores{text-align:left;margin-top:var(--space-xs)}
    .status-dl{margin-left:0;width:100%}
    .manifesto-grid{grid-template-columns:1fr}
  }
"""


def render_design_css(ds: dict | None = None) -> str:
    return css_variables(ds) + cinematic_css() + shell_css()
