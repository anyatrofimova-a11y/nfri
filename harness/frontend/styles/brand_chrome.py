"""Princeps brand chrome — clean editorial masthead (felixstocker.com register)."""


def brand_chrome_css() -> str:
    return r"""
  /* ----- clean editorial masthead ----- */
  .gate-shell{
    position:relative;background:var(--bg-default);color:var(--ink);
    border-bottom:1px solid var(--line-subtle);
  }
  .gate-bar{
    position:sticky;top:0;z-index:51;
    background:var(--bg-default);
    border-bottom:1px solid var(--line-subtle);
  }
  .gate-bar .wrap{
    display:flex;align-items:center;justify-content:flex-start;
    min-height:var(--header-h);gap:var(--space-md);
  }

  .brand{
    display:inline-flex;align-items:center;gap:12px;
    text-decoration:none;color:var(--ink-headline);flex:0 0 auto;
  }
  .brand:hover{text-decoration:none;color:var(--ink-headline);opacity:.88}
  .brand-glyph{
    display:block;flex:0 0 auto;object-fit:contain;
    width:32px;height:32px;
  }
  .brand--compact .brand-glyph{width:24px;height:24px}
  .brand-lockup{display:flex;flex-direction:column;align-items:flex-start;gap:2px;line-height:1.2}
  .brand--compact .brand-lockup{flex-direction:row;align-items:baseline;gap:10px}
  .brand-pub{
    font-family:var(--font-nav);font-size:var(--type-nav);font-weight:500;
    letter-spacing:0;text-transform:none;color:var(--ink-headline);
  }
  .brand-index{
    font-family:var(--font-mono);font-size:10px;font-weight:500;
    letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
  }
  .brand--compact .brand-index{font-size:10px}

  .gate-nav{
    margin-left:auto;display:flex;align-items:center;gap:var(--space-sm);flex-wrap:wrap;
  }
  .gate-bar .section-tab{
    font-family:var(--font-nav);font-size:var(--type-nav);font-weight:400;
    color:var(--ink2);padding:4px 0;border:none;border-radius:0;background:transparent;
  }
  .gate-bar .section-tab:hover{
    color:var(--ink-headline);background:transparent;text-decoration:none;
  }
  .gate-bar .section-tab.on{
    color:var(--ink-headline);font-weight:500;background:transparent;
    box-shadow:inset 0 -1px 0 var(--ink-headline);
  }

  .section-tabs-wrap{
    position:sticky;top:var(--header-h);z-index:50;
    background:var(--bg-default);
    border-bottom:1px solid var(--line-subtle);
  }
  .section-tabs-wrap .wrap{padding:0 var(--space-md)}
"""
