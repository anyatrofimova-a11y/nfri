"""Princeps brand chrome — textured gate bar, logo lockup, terracotta accent."""


def brand_chrome_css() -> str:
    return r"""
  /* ----- textured masthead bar (Princeps — not blue) ----- */
  .gate-shell{
    position:relative;background:var(--bg-default);color:var(--ink);
    border-bottom:1px solid var(--line-subtle);
  }
  .gate-bar{
    position:sticky;top:0;z-index:51;
    background-color:var(--bg-muted);
    background-image:
      linear-gradient(180deg,rgba(255,255,255,.72) 0%,rgba(245,243,239,.95) 100%),
      repeating-linear-gradient(
        -12deg,transparent,transparent 3px,rgba(18,18,16,.018) 3px,rgba(18,18,16,.018) 4px
      );
    border-bottom:1px solid var(--line-subtle);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.65);
  }
  .gate-bar::after{
    content:"";position:absolute;inset:0;pointer-events:none;opacity:.22;mix-blend-mode:multiply;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.78' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E");
  }
  .gate-bar .wrap{
    position:relative;z-index:1;
    display:flex;align-items:center;justify-content:flex-start;
    min-height:var(--header-h);gap:var(--space-md);
  }

  .brand{
    display:inline-flex;align-items:center;gap:12px;
    text-decoration:none;color:var(--ink);flex:0 0 auto;
  }
  .brand:hover{text-decoration:none;color:var(--ink);opacity:.94}
  .brand-glyph{
    display:block;flex:0 0 auto;object-fit:contain;
    width:32px;height:32px;
  }
  .brand--compact .brand-glyph{width:24px;height:24px}
  .brand-lockup{display:flex;flex-direction:column;align-items:flex-start;gap:1px;line-height:1.12}
  .brand--compact .brand-lockup{flex-direction:row;align-items:baseline;gap:8px}
  .brand-pub{
    font-family:var(--font-display);font-size:1.0625rem;font-weight:600;
    letter-spacing:.06em;text-transform:uppercase;color:var(--ink);
  }
  .brand-index{
    font-family:var(--font-mono);font-size:10px;font-weight:500;
    letter-spacing:.1em;text-transform:uppercase;color:var(--accent);
  }
  .brand--compact .brand-index{font-size:10px;letter-spacing:.08em}

  .gate-nav{
    margin-left:auto;display:flex;align-items:center;gap:4px;flex-wrap:wrap;
  }
  .gate-bar .section-tab{
    font-size:13px;font-weight:500;color:var(--ink2);
    padding:7px 12px;border:1px solid transparent;border-radius:var(--radius-sm);
    background:transparent;
  }
  .gate-bar .section-tab:hover{
    color:var(--ink);background:rgba(255,255,255,.55);
    border-color:var(--line-subtle);text-decoration:none;
  }

  .section-tabs-wrap{
    position:sticky;top:var(--header-h);z-index:50;
    background-color:var(--bg-subtle);
    background-image:
      linear-gradient(180deg,var(--bg-muted) 0%,var(--bg-subtle) 100%),
      repeating-linear-gradient(
        8deg,transparent,transparent 4px,rgba(18,18,16,.012) 4px,rgba(18,18,16,.012) 5px
      );
    border-bottom:1px solid var(--line-subtle);
    box-shadow:inset 0 1px 0 rgba(255,255,255,.4);
  }
  .section-tabs-wrap .wrap{padding:0 var(--space-md);position:relative;z-index:1}
"""
