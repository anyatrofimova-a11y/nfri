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
    color:var(--ink-headline);flex:0 0 auto;
  }
  .brand-pub-link,.brand-product-link{
    text-decoration:none;color:inherit;display:inline-flex;align-items:center;gap:10px;
  }
  .brand-pub-link:hover,.brand-product-link:hover{text-decoration:none;opacity:.88}
  .brand-glyph{
    display:block;flex:0 0 auto;object-fit:contain;
    width:56px;height:56px;
  }
  .brand--compact .brand-glyph{width:36px;height:36px}
  .brand-lockup{display:flex;flex-direction:column;align-items:flex-start;gap:5px;line-height:1.2;max-width:28rem}
  .brand-lockup--product{
    flex-direction:row;align-items:center;gap:var(--space-sm);
    max-width:min(52rem,100%);
  }
  .brand-lockup--compact.brand-lockup--product{gap:10px;max-width:20rem}
  .brand--compact{align-items:flex-start}
  .brand--compact .brand-lockup{max-width:20rem}
  .brand--compact .brand-pub{font-size:0.875rem}
  .brand-product-block{
    display:flex;flex-direction:column;justify-content:center;gap:3px;
    padding-left:var(--space-sm);border-left:1px solid var(--line-subtle);
    min-width:0;
  }
  .brand-lockup--compact .brand-product-block{padding-left:10px}
  .brand-product-link{
    display:flex;flex-direction:column;align-items:flex-start;gap:3px;
    text-decoration:none;color:inherit;
  }
  .brand-product-link:hover{text-decoration:none;opacity:.88}
  .brand-product-title{
    font-family:var(--font-nav);font-size:clamp(1.0625rem,1.8vw,1.3125rem);
    font-weight:500;letter-spacing:0;text-transform:none;
    color:var(--ink-headline);line-height:1.25;
  }
  .brand-product-title--compact{
    font-family:var(--font-essay);font-size:0.8125rem;font-weight:400;
    line-height:1.2;letter-spacing:-0.015em;
    display:flex;flex-direction:column;align-items:flex-start;gap:1px;
  }
  .brand-product-main{color:var(--ink-headline)}
  .brand-product-suffix{
    font-family:var(--font-mono);font-size:0.5625rem;font-weight:500;
    letter-spacing:0.08em;text-transform:uppercase;color:var(--muted);
    line-height:1.2;
  }
  .brand-product-tag{
    font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;
    letter-spacing:var(--type-kicker-track);text-transform:uppercase;color:var(--muted);
    line-height:1.25;
  }
  .brand-pub{
    font-family:var(--font-brand);font-size:1.125rem;font-weight:600;
    letter-spacing:var(--type-brand-track);text-transform:uppercase;
    color:var(--ink-headline);line-height:1.1;
  }
  .brand-wordmark,.foot-wordmark,.splash-wordmark{
    display:block;width:auto;max-width:100%;height:auto;object-fit:contain;
  }
  .brand-wordmark{max-height:64px}
  .brand--compact .brand-wordmark{max-height:32px}
  .foot-wordmark{max-height:32px}
  .splash-wordmark{max-width:min(320px,78vw);max-height:56px;margin:0 auto}
  .splash-product-title{
    font-family:var(--font-nav);font-size:clamp(1.375rem,3.5vw,2rem);
    font-weight:500;letter-spacing:0;text-transform:none;
    color:var(--ink-headline);line-height:1.2;margin:var(--space-sm) 0 0;
    text-align:center;max-width:20rem;
  }
  .splash-product-tag{margin:6px 0 0;text-align:center}

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

  @media(max-width:720px){
    .brand-lockup--product{align-items:flex-start}
    .brand-product-title{font-size:0.8125rem}
    .brand-product-tag{font-size:0.5625rem}
  }
"""
