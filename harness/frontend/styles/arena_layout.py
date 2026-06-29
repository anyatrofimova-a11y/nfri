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
    font-family:var(--font-sans);font-size:1rem;font-weight:600;
    letter-spacing:.06em;text-transform:uppercase;line-height:1.1;padding:2px 0 4px;
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
    padding-left:10px;font-size:0.75rem;color:var(--muted);
  }
  .arena-sidebar-group + .arena-sidebar-group{
    padding-top:var(--space-sm);margin-top:var(--space-xs);
    border-top:1px solid var(--line-subtle);
  }

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
    font-family:var(--font-essay);font-weight:500;
    font-size:clamp(1.75rem,3.5vw,2.75rem);line-height:1.15;
    letter-spacing:-0.01em;color:var(--ink-headline);
    margin:0 0 var(--space-sm);max-width:24ch;
  }
  .arena-article-dek{
    font-family:var(--font-essay);font-size:clamp(1.0625rem,1.8vw,1.25rem);
    line-height:1.5;font-style:italic;font-weight:400;
    color:var(--ink2);margin:0;max-width:42ch;
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

  /* index hero — layout only; Ornn atmosphere in ornn_header.py */
  .arena-index-hero{padding:0;border-bottom:none;background:transparent}
  .arena-index-hero .gate-grid{display:block;max-width:none}
  .arena-index-hero .gate-grid--with-nav{
    display:grid;grid-template-columns:minmax(0,1fr) minmax(13rem,17rem);
    gap:clamp(var(--space-md),4vw,var(--space-xl));align-items:start;
  }
  .arena-index-hero .gate-main{max-width:min(52rem,100%)}
  .hero-gate.arena-index-hero .hero-lede{margin-top:var(--space-md);max-width:42ch}
  .arena-index-hero .gate-foot{margin-top:var(--space-md)}

  /* Sequoia-style numbered site nav — circle ring on hover / active */
  .arena-header-nav{
    display:flex;flex-direction:column;align-items:stretch;gap:6px;
    margin:0;padding:0;
  }
  .arena-nav-pill{
    position:relative;display:flex;align-items:center;justify-content:flex-end;gap:10px;
    padding:11px 16px 11px 12px;text-decoration:none;color:var(--ink2);
    font-family:var(--font-sans);border-radius:999px;
    transition:color .2s ease;
  }
  .arena-nav-ring{
    position:absolute;inset:0;border:1px solid transparent;border-radius:999px;
    transition:border-color .28s ease, transform .38s cubic-bezier(.22,1,.36,1);
    transform:scale(.88);pointer-events:none;
  }
  .arena-nav-pill:hover .arena-nav-ring,
  .arena-nav-pill.on .arena-nav-ring,
  .arena-nav-pill:focus-visible .arena-nav-ring{
    border-color:var(--ink-headline);transform:scale(1);
  }
  .arena-nav-pill:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
  .arena-nav-num{
    flex:0 0 auto;font-family:var(--font-mono);font-size:0.6875rem;font-weight:500;
    letter-spacing:.06em;color:var(--muted);font-variant-numeric:tabular-nums;
  }
  .arena-nav-pill.on .arena-nav-num{color:var(--accent)}
  .arena-nav-label{
    font-size:0.9375rem;font-weight:400;letter-spacing:-.01em;
    color:var(--ink2);text-align:right;line-height:1.2;
  }
  .arena-nav-pill.on .arena-nav-label{color:var(--ink-headline);font-weight:600}
  .arena-nav-pill:hover .arena-nav-label{color:var(--ink-headline)}

  .arena-page-header{
    border-bottom:1px solid var(--line-subtle);background:var(--bg-default);
    padding:var(--space-md) 0 var(--space-sm);
  }
  .arena-page-header-inner{
    display:flex;justify-content:flex-end;
    padding:0 clamp(var(--space-md),3vw,var(--space-xl));
  }

  .site--thesis .arena-stage .site-main,
  .site--methodology .arena-stage .site-main{
    background:var(--bg-default);
    padding:0 clamp(var(--space-md),3vw,var(--space-xl)) var(--space-xl);
  }
  .site--thesis .thesis-article,
  .site--methodology .thesis-article{
    max-width:none;width:100%;padding:0;
  }
  .site--thesis .prose,
  .site--methodology .prose{max-width:none}
  .site--thesis .arena-article-head,
  .site--methodology .arena-article-head{
    padding-right:min(20rem,38%);
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
    .arena-index-hero .gate-grid--with-nav{grid-template-columns:1fr}
    .arena-header-nav{
      flex-direction:row;flex-wrap:wrap;justify-content:flex-start;
      gap:8px;margin-top:var(--space-md);
    }
    .arena-nav-pill{
      flex:1 1 calc(33.333% - 8px);min-width:9rem;justify-content:center;padding:10px 12px;
    }
    .arena-nav-label{font-size:0.8125rem;text-align:center}
    .arena-page-header-inner{justify-content:stretch}
    .arena-article-title{max-width:none}
  }
"""
