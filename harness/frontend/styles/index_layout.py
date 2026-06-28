"""Index narrative layout — thesis shell, viz blocks, progressive disclosure."""


def index_layout_css() -> str:
    return r"""
  :root{--nav-tabs-h:50px;--sticky-offset:calc(var(--header-h) + var(--nav-tabs-h) + 12px)}
  section.section--prose,
  section.section--panel{scroll-margin-top:var(--sticky-offset)}
  details.layout-disclosure{scroll-margin-top:var(--sticky-offset)}

  .layout-band{padding:var(--space-lg) 0}
  .layout-band--thesis{background:var(--bg-default);border-bottom:none}
  .layout-band--thesis > .wrap{
    max-width:none;width:100%;padding:0 clamp(var(--space-md),3vw,var(--space-lg));
  }
  .layout-band--faq{background:var(--bg-muted);border-top:1px solid var(--line-subtle);padding:var(--space-lg) 0}

  /* TOC + wide essay column — body fills remaining width */
  .index-thesis-shell{
    display:grid;
    grid-template-columns:min(10rem,100%) minmax(0,1fr);
    gap:var(--space-lg);align-items:start;width:100%;
    max-width:min(1440px,calc(100vw - 2 * var(--space-md)));
    margin:0 auto;
  }
  .index-thesis-aside{
    grid-column:1;width:min(10rem,100%);
    padding-right:0;
  }
  .index-thesis-body{
    grid-column:2;min-width:0;
    max-width:none;
  }
  .index-thesis-shell--continued .index-thesis-aside--spacer{
    visibility:hidden;pointer-events:none;
  }
  .index-thesis-toc,
  .thesis-toc.index-thesis-toc{
    position:sticky;top:var(--sticky-offset);
    display:block;margin-left:0;padding:var(--space-sm) 0 var(--space-md);
    border-right:1px solid var(--line-subtle);padding-right:var(--space-md);
  }
  .thesis-toc-kicker{margin:0 0 var(--space-sm)}
  .index-thesis-toc a,
  .thesis-toc-link{
    display:block;font-family:var(--font-nav);font-size:var(--type-nav);font-weight:400;
    color:var(--ink2);padding:6px 0;text-decoration:none;line-height:var(--type-nav-lead);
  }
  .index-thesis-toc a.sub{padding-left:12px;font-size:1rem;color:var(--muted)}
  .index-thesis-toc a.on,
  .thesis-toc-link.on{color:var(--ink-headline);font-weight:500}
  .index-thesis-body .section--prose{padding:36px 0 40px;border-bottom:1px solid var(--line-subtle)}
  .index-thesis-body .section--prose:last-child{border-bottom:none}
  .index-thesis-aside--spacer{visibility:hidden;pointer-events:none}

  .act-band{
    margin:0 0 var(--space-md);padding:var(--space-md) 0 var(--space-sm);
    border-top:2px solid var(--line);
  }
  .act-band:first-child{border-top:none;padding-top:0}
  .act-n{
    display:block;font-family:var(--font-mono);font-size:11px;font-weight:500;
    letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 6px;
  }
  .act-section:first-of-type .act-band{border-top:none}
  .act-viz-band{padding-top:var(--space-md)}

  .intro-pillar-grid{
    display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--space-sm);
    padding:var(--space-md) 0 var(--space-lg);
  }
  .intro-pillar{
    padding:var(--space-sm);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-card);
  }
  .intro-pillar-n{
    font-family:var(--font-mono);font-size:11px;font-weight:500;
    letter-spacing:.08em;color:var(--accent);margin:0 0 6px;
  }
  .intro-pillar-title{margin:0 0 6px;font-size:15px;font-weight:600;color:var(--ink)}
  .intro-pillar-text{margin:0;font-size:13px;line-height:1.5;color:var(--ink2)}

  .viz-block--compact{margin:0 0 var(--space-md)}
  .viz-block--compact .viz-title{
    margin:0 0 6px;font-family:var(--font-display);font-size:clamp(1.75rem,3vw,2.2rem);
    font-weight:500;line-height:1.4;color:var(--ink-headline);
  }
  .viz-block--compact .viz-stats{margin:0;font-size:var(--type-meta)}

  .section--rankings{padding-top:var(--space-md)}
  .section--nested{padding:var(--space-md) 0;border-top:1px solid var(--line-subtle)}
  .section--nested:first-child{border-top:none;padding-top:0}
  .section-head--compact{margin-bottom:var(--space-sm)}
  .section-head--compact .section-title{font-size:1.125rem;margin:0}
  .idx-toolbar--rankings{margin:var(--space-sm) 0 var(--space-md)}
  .rankings-table-panel{margin:0}
  .rankings-cards-disclosure{
    margin-top:var(--space-md);border:1px solid var(--line-subtle);
    border-radius:var(--radius-md);background:var(--bg-muted);
  }
  .rankings-cards-disclosure>summary{
    cursor:pointer;padding:var(--space-sm) var(--space-md);
    font-size:14px;font-weight:600;color:var(--ink2);list-style:none;
  }
  .rankings-cards-disclosure>summary::-webkit-details-marker{display:none}
  .rankings-cards-disclosure .card-list{padding:0 var(--space-md) var(--space-md)}
  .layout-disclosure--reference{margin-top:var(--space-lg)}
  .faq-band--compact{margin:0 0 var(--space-md);max-width:none}
  .faq-band--compact .faq-list{gap:var(--space-xs)}
  .viz-block .viz-head{margin-bottom:var(--space-sm)}
  .viz-lede{margin:0 0 var(--space-sm);max-width:54ch}
  .viz-read{margin:0 0 var(--space-sm);max-width:54ch;color:var(--ink2)}
  .viz-stats{
    margin:var(--space-sm) 0;font-family:var(--font-mono);
    font-variant-numeric:tabular-nums;color:var(--muted);
  }
  .viz-sowhat{margin:var(--space-sm) 0 0;max-width:54ch}

  .viz-bento{display:flex;flex-direction:column;gap:var(--space-lg)}
  .layer-mos-panel{border:none;padding:var(--space-md) 0}
  .hero-layer-chart{min-height:0}

  .trust-strip{
    border-top:1px solid var(--line-subtle);
    border-bottom:1px solid var(--line-subtle);margin:var(--space-md) 0;
  }
  .trust-strip-inner{
    display:flex;flex-wrap:wrap;gap:var(--space-sm) var(--space-lg);
    padding:var(--space-md) 0;
  }
  .trust-strip-item{font-size:13px;color:var(--ink2)}
  .trust-strip-item b{font-weight:600;color:var(--ink)}

  .faq-band{max-width:52rem}
  .faq-band-title{margin:0 0 var(--space-md)}
  .faq-list{display:flex;flex-direction:column;gap:var(--space-sm)}
  .faq-item{
    padding:var(--space-sm) var(--space-md);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);
  }
  .faq-item summary{
    cursor:pointer;font-weight:600;color:var(--ink);list-style:none;
  }
  .faq-item summary::-webkit-details-marker{display:none}
  .faq-item p{margin:var(--space-xs) 0 0;font-size:14px;line-height:1.55;color:var(--ink2)}
  .faq-item .faq-body{margin-top:var(--space-xs)}
  .faq-item .faq-body p:first-child{margin-top:0}
  .faq-item .faq-body p + p{margin-top:var(--space-sm)}
  .faq-item p:first-child{margin-top:var(--space-sm)}
  .faq-body{padding:0 var(--space-sm) var(--space-sm) 0}

  .layout-disclosure{
    margin:var(--space-lg) 0 var(--space-xl);
    border:1px solid var(--line-subtle);border-radius:var(--radius-lg);
    background:var(--bg-default);overflow:hidden;
  }
  .layout-disclosure>summary{
    cursor:pointer;padding:var(--space-md) var(--space-md);
    font-family:var(--font-nav);font-size:var(--type-nav);font-weight:500;
    color:var(--ink-headline);list-style:none;background:var(--bg-default);
    border-bottom:1px solid transparent;
  }
  .layout-disclosure[open]>summary{border-bottom-color:var(--line-subtle)}
  .layout-disclosure>summary::-webkit-details-marker{display:none}
  .layout-disclosure .layout-disclosure-body{padding:0 var(--space-md) var(--space-md)}

  .term-view-tabs{
    display:flex;flex-wrap:wrap;gap:6px;margin:0 0 var(--space-md);
    padding-bottom:var(--space-sm);border-bottom:1px solid var(--line-subtle);
  }
  .term-view-tab{
    padding:8px 14px;border:1px solid var(--line);border-radius:var(--radius-sm);
    background:var(--bg-default);font-size:13px;font-weight:500;color:var(--ink2);
    cursor:pointer;font-family:var(--font-sans);
  }
  .term-view-tab.on{background:var(--section-accent);color:#fff;border-color:var(--section-accent)}
  .term-grid-bento{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--space-sm)}
  .term-grid-bento .term-panel{
    display:none;background:var(--bg-default);border:1px solid var(--line-subtle);
    border-radius:var(--radius-card);padding:var(--space-md);
  }
  .term-grid-bento .term-panel.on{display:flex;flex-direction:column}
  .term-grid-bento .term-panel.term-wide{grid-column:1/-1}
  .term-section-head{margin-bottom:var(--space-md);padding-bottom:var(--space-sm);border-bottom:1px solid var(--line-subtle)}
  .term-viz-card{display:flex;flex-direction:column;gap:0;min-height:0;flex:1}
  .term-viz-kicker{
    font-family:var(--font-mono);font-size:10px;font-weight:500;letter-spacing:.1em;
    text-transform:uppercase;color:var(--accent);margin:0 0 4px;
  }
  .term-viz-title{
    font-family:var(--font-display);font-size:clamp(1.5rem,2.5vw,2rem);
    font-weight:500;line-height:1.35;letter-spacing:0;color:var(--ink-headline);margin:0;
  }
  .term-viz-lede{margin:var(--space-sm) 0 var(--space-xs);font-size:14px;line-height:1.5;color:var(--ink);max-width:58ch}
  .term-viz-read{margin:0 0 var(--space-sm);font-size:13px;line-height:1.55;color:var(--ink2);max-width:58ch}
  .term-viz-sowhat{
    margin:var(--space-sm) 0 0;padding-top:var(--space-sm);border-top:1px solid var(--line-subtle);
    font-size:13px;line-height:1.55;color:var(--ink2);max-width:58ch;
  }
  .term-viz-card .viz-stats{margin:var(--space-sm) 0 0}
  .term-chart-shell{
    flex:1;min-height:160px;background:var(--bg-muted);border:1px solid var(--line-subtle);
    border-radius:var(--radius-md);padding:var(--space-sm);margin:0;
  }
  .term-chart-shell .term-chart,.term-chart-shell .term-table-wrap{min-height:140px}
  .term-chart-shell .term-swarm-wrap{width:100%}

  .status-strip--subordinate{
    padding:var(--space-md) 0;border-bottom:1px solid var(--line-subtle);
    opacity:.95;
  }
  .status-strip--subordinate .site-lede{font-size:15px;max-width:52ch}

  @media(max-width:900px){
    .index-thesis-shell{grid-template-columns:1fr;max-width:100%}
    .index-thesis-aside{grid-column:1;justify-self:stretch;width:auto;padding-right:0}
    .index-thesis-body{grid-column:1;max-width:100%}
    .index-thesis-toc{
      position:relative;top:auto;border-right:none;border-bottom:1px solid var(--line-subtle);
      padding-right:0;padding-bottom:var(--space-sm);
    }
    .intro-pillar-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    .term-grid-bento{grid-template-columns:1fr}
  }
  @media(max-width:560px){
    .intro-pillar-grid{grid-template-columns:1fr}
  }
"""
