"""a16z Dynamism-style long-form essay surface — Libre Caslon body, smooth scroll, reveal."""


def essay_surface_css() -> str:
    return r"""
  /* ----- scroll surface (contract/scroll_typography.json) ----- */
  html{
    scroll-behavior:smooth;
    scroll-padding-top:var(--sticky-offset);
    scrollbar-gutter:stable;
  }
  html,body{overscroll-behavior:none}
  @media(prefers-reduced-motion:reduce){
    html{scroll-behavior:auto}
  }

  /* ----- essay column — Libre Caslon throughout (matches Contents nav) ----- */
  .layout-band--thesis{background:var(--bg-default)}
  section.act-section.section--prose{background:var(--bg-default)}
  section.essay .prose{
    max-width:none;
    font-family:var(--font-essay);
    font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);
    color:var(--ink2);
  }
  section.essay .prose a{
    color:var(--ink-headline);
    text-decoration:underline;
    text-decoration-thickness:1px;
    text-underline-offset:3px;
  }
  section.essay .prose a:hover{color:var(--accent)}

  /* act bands — section breaks like long-form essay parts */
  .act-band{margin:0 0 var(--space-sm);padding:0}
  .act-section:first-of-type .act-band{margin-top:0}
  .act-headline{
    display:flex;flex-wrap:wrap;align-items:baseline;gap:0 .75em;
  }
  .act-title{
    font-family:var(--font-essay);font-weight:500;
    font-size:clamp(1.375rem,2.2vw,var(--type-title-max));
    line-height:var(--type-title-lead);letter-spacing:var(--type-title-track);
    color:var(--ink-headline);margin:0;flex:0 0 auto;
  }
  .act-sub{
    font-family:var(--font-essay);font-size:var(--type-body);
    line-height:var(--type-body-lead);color:var(--muted);
    margin:0;flex:1 1 16rem;min-width:0;
  }
  .act-sub::before{content:"—";margin-right:.75em;color:var(--line)}
  .act-lede{
    font-family:var(--font-essay);font-size:var(--type-lead);
    line-height:var(--type-lead-lead);color:var(--ink-headline);
    font-style:italic;font-weight:400;
    margin:var(--space-sm) 0 0;max-width:44ch;
    padding:0 0 0 14px;border-left:2px solid var(--line);
  }
  .act-lede strong{font-style:normal;font-weight:600}
  section.essay .act-band + .arg-kicker{margin-top:var(--space-md)}

  /* essay typography — single serif register */
  section.essay .arg-p{
    font-family:var(--font-essay);
    font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);
    margin:0 0 var(--essay-para-gap);
    color:var(--ink2);
  }
  section.essay .arg-lead{
    font-family:var(--font-essay);
    font-size:var(--type-lead);
    line-height:var(--type-lead-lead);
    color:var(--ink2);
    margin:0 0 calc(var(--essay-para-gap) + 4px);
  }
  section.essay .arg-lead.dropcap::first-letter{
    font-family:var(--font-essay);
    font-size:3.75rem;line-height:.76;padding:4px 12px 0 0;
    color:var(--ink-headline);font-weight:500;
  }
  section.essay .arg-h{
    font-family:var(--font-essay);
    font-size:clamp(var(--type-title-min),2.6vw,var(--type-title-max));
    font-weight:500;
    line-height:var(--type-title-lead);
    letter-spacing:var(--type-title-track);
    color:var(--ink-headline);
    margin:calc(var(--essay-para-gap) + 12px) 0 calc(var(--essay-para-gap) - 2px);
  }
  section.essay .arg-pull{
    font-family:var(--font-essay);
    font-size:var(--type-essay-pull);
    line-height:var(--type-essay-pull-lead);
    margin:calc(var(--essay-para-gap) + 10px) 0;
    padding:0 0 0 18px;
    border-left:2px solid var(--line);
    color:var(--ink-headline);
    font-style:italic;font-weight:400;
  }
  section.essay .arg-kicker{
    margin:calc(var(--essay-para-gap) + 8px) 0 10px;
  }
  section.essay .col > .arg-kicker:first-child,
  section.essay .prose > .arg-kicker:first-child{margin-top:0}
  section.essay .arg-ul li{
    font-family:var(--font-essay);
    font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);
  }

  /* sticky TOC — compact sans register in sidebar */
  .index-thesis-toc a,
  .thesis-toc-link{
    font-family:var(--font-sans);
    transition:color var(--dur-sm) var(--ease-out), border-color var(--dur-sm) var(--ease-out);
  }
  .index-thesis-toc a.on,
  .thesis-toc-link.on{
    color:var(--ink-headline);font-weight:500;
    border-left:2px solid var(--ink-headline);
    padding-left:8px;margin-left:-8px;
  }

  /* essay scroll reveal — softer than panel reveals */
  .essay-reveal{
    opacity:0;transform:translateY(var(--essay-reveal-y, 18px));
    transition:opacity var(--dur-essay) var(--ease-out),transform var(--dur-essay) var(--ease-out);
  }
  .essay-reveal.in{opacity:1;transform:none}
  @media(prefers-reduced-motion:reduce){
    .essay-reveal{opacity:1!important;transform:none!important;transition:none!important}
  }
"""
