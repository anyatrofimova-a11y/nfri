"""a16z Dynamism-style long-form essay surface — serif body, smooth scroll, reveal."""


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

  /* ----- essay column ----- */
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
    color:var(--section-accent);
    text-decoration:underline;
    text-decoration-thickness:1px;
    text-underline-offset:2px;
  }
  section.essay .prose a:hover{color:var(--ink)}

  /* act bands — section breaks like long-form essay parts */
  .act-band{margin:0 0 var(--space-md);padding:var(--space-md) 0 0}
  .act-title{
    font-family:var(--font-display);font-weight:600;
    font-size:clamp(var(--type-title-min),2.8vw,var(--type-title-max));
    line-height:var(--type-title-lead);letter-spacing:var(--type-title-track);
  }
  .act-sub{
    font-family:var(--font-essay);font-size:var(--type-essay-body);
    line-height:var(--type-essay-lead);color:var(--muted);
  }

  /* essay typography overrides (maps Domaine-text / Orpheus → Source Serif 4) */
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
    color:var(--ink);
    margin:0 0 calc(var(--essay-para-gap) + 4px);
  }
  section.essay .arg-lead.dropcap::first-letter{
    font-family:var(--font-display);
    font-size:3.5rem;line-height:.78;padding:6px 14px 0 0;
    color:var(--accent);font-weight:600;
  }
  section.essay .arg-h{
    font-family:var(--font-display);
    font-size:clamp(var(--type-title-min),2.6vw,var(--type-title-max));
    line-height:var(--type-title-lead);
    letter-spacing:var(--type-title-track);
    margin:4px 0 calc(var(--essay-para-gap) - 2px);
  }
  section.essay .arg-pull{
    font-family:var(--font-display);
    font-size:var(--type-essay-pull);
    line-height:var(--type-essay-pull-lead);
    margin:calc(var(--essay-para-gap) + 6px) 0;
    padding:2px 0 2px 18px;
    border-left:3px solid var(--section-accent);
    color:var(--ink);
    font-style:italic;font-weight:500;
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

  /* sticky TOC — a16z-style rail */
  .index-thesis-toc a,
  .thesis-toc-link{
    transition:color var(--dur-sm) var(--ease-out), border-color var(--dur-sm) var(--ease-out);
  }
  .index-thesis-toc a.on,
  .thesis-toc-link.on{
    border-left:2px solid var(--section-accent);
    padding-left:10px;margin-left:-10px;
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
