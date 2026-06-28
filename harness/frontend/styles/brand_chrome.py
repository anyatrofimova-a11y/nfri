"""Princeps brand chrome — clean editorial masthead (felixstocker.com register)."""


def brand_chrome_css() -> str:
    return r"""
  @font-face{
    font-family:"Princeps Geist Sans";font-style:normal;font-weight:100 900;font-display:swap;
    src:url(assets/brand/fonts/geist-sans.woff2) format("woff2");
  }
  @font-face{
    font-family:"Princeps Geist Mono";font-style:normal;font-weight:100 900;font-display:swap;
    src:url(assets/brand/fonts/geist-mono.woff2) format("woff2");
  }

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
  .brand-lockup{display:flex;flex-direction:column;align-items:flex-start;gap:2px;line-height:1.2;max-width:11.5rem}
  .brand--compact{align-items:flex-start}
  .brand--compact .brand-lockup{max-width:9.5rem}
  .brand--compact .brand-pub{font-size:0.8125rem}
  .brand-pub{
    font-family:var(--font-brand);font-size:var(--type-brand-pub);font-weight:600;
    letter-spacing:var(--type-brand-track);text-transform:uppercase;
    color:var(--ink-headline);line-height:1.1;
  }
  .brand-wordmark,.foot-wordmark,.splash-wordmark{
    display:block;width:auto;max-width:100%;height:auto;object-fit:contain;
  }
  .brand-wordmark{max-height:15px}
  .brand--compact .brand-wordmark{max-height:13px}
  .foot-wordmark{max-height:13px}
  .splash-wordmark{max-width:min(280px,72vw);max-height:48px;margin:0 auto}
  .splash-tag{font-family:var(--font-brand-product);letter-spacing:.14em}
  .brand-index{
    font-family:var(--font-brand-product);font-size:9px;font-weight:500;
    letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
    line-height:1.3;
  }
  .brand--compact .brand-index{font-size:8px;line-height:1.25}

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
