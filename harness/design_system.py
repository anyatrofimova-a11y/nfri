#!/usr/bin/env python3
"""Render harness CSS from contract/design_system.json."""
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
    p = ds.get("palette", {})
    o = p.get("ocean", {})
    r = ds["radius"]
    f = ds["fonts"]
    return f"""
  :root{{
    --bg-emphasis:{c['bg_emphasis']}; --bg-default:{c['bg_default']}; --bg-muted:{c['bg_muted']};
    --bg-subtle:{c.get('bg_subtle', '#F0F0F0')};
    --ink:{c['content_emphasis']}; --ink2:{c['content_default']}; --muted:{c['content_muted']};
    --line:{c['border_default']}; --line-subtle:{c.get('border_subtle', '#E8E8E8')};
    --bg:{c['bg_emphasis']}; --card:{c['bg_default']};
    --accent:{c['accent']}; --accent-muted:{c['accent_muted']}; --accent2:{c['measured']};
    --section-accent:{c['section_accent']};
    --ocean-deep:{o.get('deep', c.get('ocean_deep', '#0047E6'))};
    --ocean-dark:{o.get('deep_dark', '#003BB8')};
    --ocean-glow:{o.get('glow', c.get('ocean_glow', '#1A6BFF'))};
    --ocean-on:{o.get('on_deep', '#FFFFFF')};
    --ocean-on-muted:{o.get('on_deep_muted', 'rgba(255,255,255,0.72)')};
    --exposed:{c['exposed']}; --earning-s:{c['earning']}; --whitespace:{c['whitespace']};
    --sidelined:{c['sidelined']}; --measured:{c['measured']}; --assessed:#B8C2C6;
    --tip-bg:{c['tip_bg']}; --tip-border:{c['tip_border']};
    --radius-sm:{r['sm']}; --radius-md:{r['md']}; --radius-lg:{r['lg']}; --radius-card:{r['card']};
    --font-sans:{f['sans']}; --font-display:{f['display']}; --font-hero:{f.get('hero_sans', f['sans'])};
    --font-mono:{f['mono']};
    --max-w:{ds['layout']['max_width']};
    --cinematic-min:{ds['layout'].get('cinematic_min_height', 'min(88vh,720px)')};
  }}
"""


def shell_css() -> str:
    return r"""
  body{font-family:var(--font-sans);color:var(--ink2);background:var(--bg-emphasis);line-height:1.5}
  a{color:var(--section-accent)}
  .wrap{max-width:var(--max-w);margin:0 auto;padding:0 20px}
  header.top{
    position:sticky;top:0;z-index:30;background:var(--bg-default);
    border-bottom:1px solid var(--line);height:52px;
  }
  .top .wrap{display:flex;align-items:center;gap:16px;height:52px}
  .brand{font-weight:600;font-size:14px;letter-spacing:-.01em;color:var(--ink)}
  .brand small{color:var(--muted);font-weight:400;margin-left:4px}
  .brand-mark{
    width:28px;height:28px;border-radius:var(--radius-md);
    background:var(--section-accent);color:#fff;font-size:11px;font-weight:700;
    display:inline-flex;align-items:center;justify-content:center;margin-right:8px;
    vertical-align:middle;letter-spacing:.04em;
  }
  nav{margin-left:auto;display:flex;gap:2px;flex-wrap:wrap;align-items:center}
  nav a{font-size:12px;color:var(--ink2);text-decoration:none;padding:5px 8px;border-radius:var(--radius-md)}
  nav a:hover{background:var(--bg-subtle)}
  nav .nav-sep{width:1px;height:14px;background:var(--line);margin:0 3px}
  nav .nav-grp{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:0 5px}
  .site-foot{
    border-top:1px solid var(--line);padding:20px 0 48px;margin-top:8px;
    font-size:12px;color:var(--muted);display:flex;flex-wrap:wrap;gap:12px 18px;
  }
  .site-foot a{color:var(--ink2);text-decoration:none}
  .site-foot a:hover{text-decoration:underline}
  /* index toolbar */
  .idx-toolbar{
    display:flex;flex-wrap:wrap;gap:8px;align-items:center;
    padding:14px 0 12px;position:sticky;top:52px;z-index:15;
    background:var(--bg-emphasis);border-bottom:1px solid var(--line-subtle);margin-bottom:12px;
  }
  .idx-search{
    flex:1 1 200px;min-width:160px;padding:8px 12px;border:1px solid var(--line);
    border-radius:var(--radius-md);background:var(--bg-default);font-size:13px;
    font-family:var(--font-sans);color:var(--ink);
  }
  .idx-search:focus{outline:2px solid var(--section-accent);outline-offset:0;border-color:var(--section-accent)}
  .idx-btn,.idx-select{
    padding:7px 12px;border:1px solid var(--line);border-radius:var(--radius-md);
    background:var(--bg-default);font-size:12px;color:var(--ink2);cursor:pointer;font-family:var(--font-sans);
  }
  .idx-btn.on{background:var(--section-accent);color:#fff;border-color:var(--section-accent)}
  .idx-meta{font-size:12px;color:var(--muted);margin-left:auto}
  /* entity cards */
  .card-list{display:flex;flex-direction:column;gap:var(--card-gap,12px);margin:8px 0 24px}
  .ent-card{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(180px,280px);
    gap:16px;align-items:center;padding:16px 18px;
    background:var(--bg-default);border:1px solid var(--line);border-radius:var(--radius-card);
    cursor:pointer;transition:box-shadow .15s,border-color .15s;
  }
  .ent-card:hover{box-shadow:0 2px 12px rgba(0,0,0,.06);border-color:var(--border-default,#dcdcdc)}
  .ent-id{display:flex;gap:12px;align-items:flex-start;min-width:0}
  .ent-avatar{
    flex:0 0 40px;width:40px;height:40px;border-radius:var(--radius-md);
    background:var(--bg-subtle);border:1px solid var(--line);
    display:flex;align-items:center;justify-content:center;
    font-size:13px;font-weight:700;color:var(--section-accent);
  }
  .ent-name{font-weight:600;font-size:15px;color:var(--ink);line-height:1.25}
  .ent-meta{font-size:12px;color:var(--muted);margin-top:3px}
  .ent-badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
  .score-badge{
    display:inline-flex;align-items:center;gap:6px;padding:4px 10px 4px 6px;
    border-radius:var(--radius-pill);font-size:12px;font-weight:600;border:1px solid var(--line);
    background:var(--bg-muted);
  }
  .score-badge .dot{width:8px;height:8px;border-radius:50%}
  .score-badge.exp .dot{background:var(--exposed)}
  .score-badge.prep .dot{background:var(--earning-s)}
  .score-badge.mos .dot{background:var(--whitespace)}
  .range-wrap{padding:4px 0 0}
  .range-label{font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
  .range-track{position:relative;height:8px;border-radius:var(--radius-pill);background:linear-gradient(90deg,var(--exposed),#d4a017,var(--earning-s));margin:0 0 4px}
  .range-tick{position:absolute;top:-3px;width:2px;height:14px;background:var(--ink);border-radius:1px;transform:translateX(-50%)}
  .range-tick.avg{background:var(--accent);width:3px}
  .range-nums{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums}
  .quad-pill{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;padding:2px 8px;border-radius:var(--radius-pill);color:#fff}
  /* welcome modal */
  #welcome-scrim{
    position:fixed;inset:0;background:rgba(20,20,20,.45);z-index:100;
    display:flex;align-items:center;justify-content:center;padding:20px;
  }
  #welcome-scrim.hidden{display:none}
  .welcome-box{
    max-width:520px;width:100%;background:var(--bg-default);border-radius:var(--radius-lg);
    padding:28px 28px 22px;box-shadow:0 20px 60px rgba(0,0,0,.18);
  }
  .welcome-box h2{
    font-family:var(--font-display);font-size:22px;font-weight:600;
    letter-spacing:.02em;text-transform:uppercase;color:var(--ink);margin:0 0 6px;line-height:1.2;
  }
  .welcome-sub{font-size:14px;color:var(--muted);margin:0 0 16px}
  .welcome-body{font-size:14px;line-height:1.6;color:var(--ink2);margin:0 0 14px}
  .welcome-foot{font-size:12px;color:var(--muted);margin:0 0 14px}
  .welcome-tip{
    font-size:13px;line-height:1.5;color:var(--ink2);padding:10px 12px;
    background:var(--tip-bg);border:1px solid var(--tip-border);border-radius:var(--radius-md);margin:0 0 18px;
  }
  .welcome-actions{display:flex;justify-content:flex-end;gap:8px}
  .welcome-actions button{
    padding:8px 16px;border-radius:var(--radius-md);font-size:13px;font-weight:600;cursor:pointer;
    font-family:var(--font-sans);
  }
  .btn-primary{background:var(--section-accent);color:#fff;border:none}
  .btn-ghost{background:var(--bg-default);color:var(--ink2);border:1px solid var(--line)}
  @media(max-width:720px){
    .ent-card{grid-template-columns:1fr}
    .idx-meta{width:100%;margin-left:0}
  }
"""


def cinematic_css() -> str:
    """theoceancompany.com — full-bleed cobalt hero, uppercase kicker, white type."""
    return r"""
  .cinematic-hero{
    position:relative;min-height:var(--cinematic-min);width:100%;
    display:flex;flex-direction:column;justify-content:flex-end;
    background:linear-gradient(165deg,var(--ocean-glow) 0%,var(--ocean-deep) 42%,var(--ocean-dark) 100%);
    color:var(--ocean-on);overflow:hidden;
  }
  .cinematic-hero::before,.cinematic-hero::after{
    content:'';position:absolute;pointer-events:none;border-radius:50%;
  }
  .cinematic-hero::before{
    width:120%;height:80%;top:-20%;left:-10%;
    background:radial-gradient(ellipse at 30% 20%,var(--ocean-on) 0%,transparent 55%);
    opacity:.14;
  }
  .cinematic-hero::after{
    width:90%;height:60%;bottom:-10%;right:-15%;
    background:radial-gradient(ellipse at 70% 80%,rgba(255,255,255,.25) 0%,transparent 60%);
    opacity:.08;
  }
  .cinematic-nav{
    position:absolute;top:0;left:0;right:0;z-index:2;
    display:flex;align-items:center;justify-content:space-between;
    padding:20px 24px;max-width:1400px;margin:0 auto;width:100%;
  }
  .cinematic-logo{
    font-family:var(--font-hero);font-weight:700;font-style:italic;
    font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--ocean-on);
  }
  .cinematic-nav a{
    color:var(--ocean-on-muted);text-decoration:none;font-size:12px;
    letter-spacing:.06em;text-transform:uppercase;font-weight:600;
  }
  .cinematic-nav a:hover{color:var(--ocean-on)}
  .cinematic-inner{
    position:relative;z-index:1;max-width:var(--max-w);margin:0 auto;
    padding:0 24px 56px;width:100%;
  }
  .cinematic-kicker{
    font-family:var(--font-hero);font-size:11px;font-weight:600;
    letter-spacing:.22em;text-transform:uppercase;
    color:var(--ocean-on-muted);margin:0 0 16px;
  }
  .cinematic-title{
    font-family:var(--font-hero);font-weight:500;
    font-size:clamp(28px,4.5vw,44px);line-height:1.12;
    letter-spacing:-.02em;max-width:22ch;margin:0 0 18px;color:var(--ocean-on);
  }
  .cinematic-lede{
    font-size:clamp(15px,2vw,18px);line-height:1.55;
    color:var(--ocean-on-muted);max-width:52ch;margin:0 0 24px;
  }
  .cinematic-scroll{
    display:inline-flex;align-items:center;gap:8px;
    font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
    color:var(--ocean-on);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.35);
    padding-bottom:2px;
  }
  .zone-analytical{background:var(--bg-emphasis)}
  .zone-transition{
    height:6px;background:linear-gradient(180deg,var(--ocean-dark),var(--bg-emphasis));
  }
  .steps-grid{
    display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0 8px;
  }
  .step-card{
    border:1px solid var(--line);border-radius:var(--radius-md);padding:14px;
    background:var(--bg-default);border-top:3px solid var(--section-accent);
  }
  .step-n{font-size:10px;font-weight:700;letter-spacing:.12em;color:var(--accent);margin-bottom:6px}
  .step-t{font-weight:600;font-size:13px;color:var(--ink);margin-bottom:4px;line-height:1.25}
  .step-p{margin:0;font-size:12px;line-height:1.48;color:var(--ink2)}
  @media(max-width:960px){.steps-grid{grid-template-columns:1fr 1fr}}
  @media(max-width:560px){.steps-grid{grid-template-columns:1fr}}
"""


def render_design_css(ds: dict | None = None) -> str:
    ds = ds or load_design_system()
    return css_variables(ds) + cinematic_css() + shell_css()
