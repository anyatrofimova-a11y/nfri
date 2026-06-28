"""Arena Magazine–style editorial shell — sidebar nav, wide article column, utility bar."""


def arena_layout_css() -> str:
    return r"""
  /* ===== Arena editorial shell (arenamag.com register) ===== */
  body.site{background:var(--bg-emphasis);color:var(--ink2)}

  .arena-shell{
    display:grid;grid-template-columns:var(--arena-sidebar-w) minmax(0,1fr);
    min-height:100vh;align-items:start;
  }
  .arena-sidebar{
    position:sticky;top:0;align-self:start;
    height:100vh;max-height:100vh;overflow-y:auto;
    padding:var(--space-md) var(--space-sm) var(--space-lg);
    border-right:1px solid var(--line-subtle);
    background:var(--bg-emphasis);
    display:flex;flex-direction:column;gap:var(--space-md);
  }
  .arena-wordmark{
    display:block;text-decoration:none;color:var(--ink-headline);
    font-family:var(--font-display);font-size:1.625rem;font-weight:400;
    letter-spacing:-0.01em;line-height:1.1;padding:2px 0 4px;
  }
  .arena-wordmark:hover{text-decoration:none;opacity:.85}
  .arena-wordmark img{display:block;max-width:100%;height:auto;max-height:36px}

  .arena-sidebar-group{margin:0}
  .arena-sidebar-label{
    font-family:var(--font-sans);font-size:0.6875rem;font-weight:500;
    letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
    margin:0 0 6px;
  }
  .arena-sidebar-nav{display:flex;flex-direction:column;gap:1px}
  .arena-sidebar-nav a{
    font-family:var(--font-sans);font-size:0.8125rem;font-weight:400;
    color:var(--ink2);text-decoration:none;padding:3px 0;line-height:1.35;
  }
  .arena-sidebar-nav a:hover{color:var(--ink-headline)}
  .arena-sidebar-nav a.on{color:var(--ink-headline);font-weight:500}
  .arena-sidebar-nav a.sub{
    padding-left:12px;font-size:0.75rem;color:var(--muted);
    position:relative;
  }
  .arena-sidebar-nav a.sub::before{
    content:"";position:absolute;left:0;top:0.55em;
    width:6px;height:6px;border-left:1px solid var(--line);border-bottom:1px solid var(--line);
  }

  .arena-sidebar-cta{
    margin-top:auto;padding:var(--space-sm);
    border:1px solid var(--line-subtle);border-radius:var(--radius-sm);
    background:var(--bg-default);font-size:0.8125rem;line-height:1.45;color:var(--ink2);
  }
  .arena-sidebar-cta strong{
    display:block;font-family:var(--font-sans);font-size:0.6875rem;
    letter-spacing:.06em;text-transform:uppercase;color:var(--ink-headline);
    margin-bottom:4px;
  }
  .arena-sidebar-cta a{color:var(--link);font-weight:500}

  .arena-stage{min-width:0;background:var(--bg-default)}
  .arena-utility{
    display:flex;align-items:center;justify-content:flex-end;gap:var(--space-md);
    flex-wrap:wrap;padding:10px var(--space-md);
    border-bottom:1px solid var(--line-subtle);background:var(--bg-default);
    font-size:0.8125rem;
  }
  .arena-utility-nav{display:flex;gap:var(--space-sm);flex-wrap:wrap;margin-left:auto}
  .arena-utility-nav a{
    font-family:var(--font-sans);color:var(--ink2);text-decoration:none;padding:2px 0;
  }
  .arena-utility-nav a:hover{color:var(--ink-headline)}
  .arena-utility-nav a.on{
    color:var(--ink-headline);font-weight:500;
    box-shadow:inset 0 -1px 0 var(--ink-headline);
  }
  .arena-gate-banner{
    flex:1 1 100%;margin:0;padding:8px 12px;border-radius:var(--radius-sm);
    font-size:0.8125rem;line-height:1.45;
  }
  .arena-gate-banner.warn{background:var(--warn-bg);border:1px solid var(--warn-border)}
  .arena-gate-banner.ok{background:var(--ok-bg);border:1px solid var(--ok-border)}

  /* article masthead — category • date / title / dek / byline */
  .arena-article-head{padding:var(--space-lg) 0 var(--space-md);margin:0 0 var(--space-sm)}
  .arena-article-meta{
    font-family:var(--font-sans);font-size:0.6875rem;font-weight:500;
    letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
    margin:0 0 var(--space-sm);
  }
  .arena-article-meta .sep{margin:0 .45em;opacity:.55}
  .arena-article-title{
    font-family:var(--font-display);font-weight:400;
    font-size:clamp(2rem,4.5vw,3.25rem);line-height:1.12;
    letter-spacing:-0.015em;color:var(--ink-headline);
    margin:0 0 var(--space-sm);max-width:20ch;
  }
  .arena-article-dek{
    font-family:var(--font-display);font-size:clamp(1.125rem,2vw,1.375rem);
    line-height:1.45;font-style:italic;font-weight:400;
    color:var(--ink2);margin:0 0 var(--space-md);max-width:42ch;
  }
  .arena-article-by{
    font-family:var(--font-sans);font-size:0.6875rem;font-weight:500;
    letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0;
  }
  .arena-article-by span{color:var(--ink-headline)}

  .arena-section-meta{
    font-family:var(--font-sans);font-size:0.6875rem;font-weight:500;
    letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
    margin:0 0 12px;
  }

  /* index hero — Arena masthead in gate band */
  .arena-index-hero{background:var(--bg-emphasis);border-bottom:1px solid var(--line-subtle)}
  .arena-index-hero .gate-grid{display:block;max-width:none}
  .arena-index-hero .gate-main{max-width:min(52rem,100%)}
  .arena-index-hero .hero-lede{margin-top:var(--space-md);max-width:42ch;color:var(--ink2)}
  .arena-index-hero .gate-foot{margin-top:var(--space-md)}

  .site--thesis .arena-stage .site-main,
  .site--methodology .arena-stage .site-main{background:var(--bg-default)}
  .site--thesis .thesis-article,
  .site--methodology .thesis-article{
    max-width:var(--essay-measure);padding:0 var(--space-md) var(--space-xl);
  }

  /* index: persistent sidebar replaces top section tabs */
  .site:not(.site--thesis):not(.site--methodology) .gate-shell .section-tabs-wrap{display:none}
  .site:not(.site--thesis):not(.site--methodology) .index-thesis-aside .arena-wordmark{margin-bottom:var(--space-xs)}
  .site:not(.site--thesis):not(.site--methodology) .index-thesis-shell{
    grid-template-columns:var(--arena-sidebar-w) minmax(0,1fr);
    max-width:none;margin:0;
  }
  .site:not(.site--thesis):not(.site--methodology) .index-thesis-aside{
    position:sticky;top:0;align-self:start;
    height:100vh;max-height:100vh;overflow-y:auto;
    padding:var(--space-md) var(--space-sm) var(--space-lg);
    border-right:1px solid var(--line-subtle);background:var(--bg-emphasis);
    width:auto;
  }
  .site:not(.site--thesis):not(.site--methodology) .index-thesis-toc{
    position:static;border-right:none;padding-right:0;
  }
  .site:not(.site--thesis):not(.site--methodology) .layout-band--thesis > .wrap{padding:0}

  @media(max-width:960px){
    .arena-shell{grid-template-columns:1fr}
    .arena-sidebar{
      position:relative;height:auto;max-height:none;
      border-right:none;border-bottom:1px solid var(--line-subtle);
    }
    .site:not(.site--thesis):not(.site--methodology) .index-thesis-aside{
      position:relative;height:auto;max-height:none;
    }
    .arena-article-title{max-width:none}
  }
"""
