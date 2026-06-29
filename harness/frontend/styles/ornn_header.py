"""Ornn-inspired masthead — dark canvas, vertical rib texture, film grain (CSS-only)."""


def ornn_header_css() -> str:
    return r"""
  /* ===== Ornn register — dark ribbed canvas (no blur orbs / watermark boxes) ===== */
  @keyframes ornn-grain{
    0%,100%{background-position:0 0}
    25%{background-position:12% 8%}
    50%{background-position:-8% 14%}
    75%{background-position:6% -6%}
  }
  @keyframes ornn-hero-in{
    from{opacity:0;transform:translateY(24px)}
    to{opacity:1;transform:none}
  }
  @keyframes ornn-rule-grow{
    from{transform:scaleX(0);opacity:0}
    to{transform:scaleX(1);opacity:1}
  }

  .hero-gate.arena-index-hero{
    --ornn-ink:#F5F2EB;
    --ornn-muted:rgba(245,242,235,.58);
    position:relative;overflow:hidden;isolation:isolate;
    color:var(--ornn-muted);
    border-bottom:1px solid rgba(255,255,255,.06);
    padding:clamp(2rem,7vw,5rem) 0 clamp(1.5rem,4vw,3rem);
    background:
      radial-gradient(ellipse 65% 50% at 10% 0%, rgba(184,90,50,.24) 0%, transparent 58%),
      radial-gradient(ellipse 45% 35% at 95% 15%, rgba(46,125,138,.1) 0%, transparent 52%),
      linear-gradient(175deg, #0a0a08 0%, var(--canvas-dark) 42%, #030302 100%);
  }

  .hero-gate.arena-index-hero::before{
    content:"";position:absolute;inset:0;
    pointer-events:none;z-index:1;opacity:.16;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.72' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size:180px 180px;
    animation:ornn-grain 8s steps(8) infinite;
  }

  .hero-gate.arena-index-hero::after{
    content:"";position:absolute;inset:0;pointer-events:none;z-index:1;opacity:.55;
    background-image:repeating-linear-gradient(
      90deg,
      transparent 0, transparent 11px,
      rgba(255,255,255,.018) 11px, rgba(255,255,255,.035) 12px,
      rgba(0,0,0,.22) 13px, rgba(255,255,255,.012) 14px,
      transparent 18px, transparent 34px
    );
    mask-image:linear-gradient(180deg, rgba(0,0,0,.92) 0%, rgba(0,0,0,.4) 88%, transparent 100%);
  }

  .hero-gate.arena-index-hero .wrap{position:relative;z-index:3}
  .hero-gate.arena-index-hero .gate-grid--with-nav{position:relative;overflow:hidden}

  .hero-gate-brand{
    display:inline-flex;align-items:center;
    margin:0 0 clamp(var(--space-md),3vw,var(--space-lg));
    text-decoration:none;
  }
  .hero-gate-brand:hover{text-decoration:none;opacity:.88}
  .hero-gate-glyph{
    display:block;
    background:var(--ornn-ink);
    -webkit-mask:center/contain no-repeat;
    -webkit-mask-mode:luminance;
    mask:center/contain no-repeat;
    mask-mode:luminance;
  }

  .hero-gate.arena-index-hero .arena-article-title{
    max-width:none;color:var(--ornn-ink);
    font-size:clamp(2rem,4.8vw,3.25rem);
    text-shadow:0 1px 24px rgba(0,0,0,.35);
  }
  .hero-gate.arena-index-hero .arena-article-dek{
    max-width:46ch;color:rgba(245,242,235,.78);font-style:italic;
  }
  .hero-gate.arena-index-hero .hero-lede{
    max-width:52ch;color:var(--ornn-muted);margin-top:var(--space-md);
  }

  .hero-gate.arena-index-hero .wrap::after{
    content:"";display:block;height:1px;margin-top:clamp(var(--space-md),3vw,var(--space-lg));
    background:linear-gradient(90deg, rgba(184,90,50,.95) 0%, rgba(184,90,50,.35) 38%, transparent 100%);
    transform-origin:left center;
    animation:ornn-rule-grow 1.1s var(--ease-out) .7s both;
  }

  .hero-gate.arena-index-hero .arena-nav-pill{color:rgba(245,242,235,.82)}
  .hero-gate.arena-index-hero .arena-nav-num{color:rgba(245,242,235,.42)}
  .hero-gate.arena-index-hero .arena-nav-label{color:rgba(245,242,235,.88)}
  .hero-gate.arena-index-hero .arena-nav-pill{background:rgba(255,255,255,.06)}
  .hero-gate.arena-index-hero .arena-nav-pill:hover,
  .hero-gate.arena-index-hero .arena-nav-pill.on{background:rgba(255,255,255,.11)}
  .hero-gate.arena-index-hero .arena-nav-pill.on .arena-nav-num{color:var(--accent)}
  .hero-gate.arena-index-hero .arena-nav-pill.on .arena-nav-label{color:var(--ornn-ink)}
  .hero-gate.arena-index-hero .arena-nav-pill:hover .arena-nav-ring,
  .hero-gate.arena-index-hero .arena-nav-pill.on .arena-nav-ring,
  .hero-gate.arena-index-hero .arena-nav-pill:focus-visible .arena-nav-ring{
    border-color:rgba(245,242,235,.55);
  }

  .hero-gate.arena-index-hero .gate-main > *,
  .hero-gate.arena-index-hero .arena-header-nav{
    opacity:0;animation:ornn-hero-in .95s var(--ease-out) both;
  }
  .hero-gate.arena-index-hero .gate-main > *:nth-child(1){animation-delay:.08s}
  .hero-gate.arena-index-hero .gate-main > *:nth-child(2){animation-delay:.18s}
  .hero-gate.arena-index-hero .gate-main > *:nth-child(3){animation-delay:.28s}
  .hero-gate.arena-index-hero .gate-main > *:nth-child(4){animation-delay:.38s}
  .hero-gate.arena-index-hero .arena-header-nav{animation-delay:.48s}

  .site--thesis .arena-stage > .arena-page-header,
  .site--methodology .arena-stage > .arena-page-header{
    position:relative;overflow:hidden;isolation:isolate;
    border-bottom:1px solid rgba(255,255,255,.06);
    padding:var(--space-md) 0 var(--space-sm);
    background:
      radial-gradient(ellipse 60% 100% at 100% 0%, rgba(184,90,50,.16) 0%, transparent 55%),
      linear-gradient(180deg, #0a0a08 0%, var(--canvas-dark) 100%);
  }
  .site--thesis .arena-stage > .arena-page-header::before,
  .site--methodology .arena-stage > .arena-page-header::before{
    content:"";position:absolute;inset:0;
    pointer-events:none;z-index:0;opacity:.12;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.78' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size:180px 180px;
  }
  .site--thesis .arena-stage > .arena-page-header::after,
  .site--methodology .arena-stage > .arena-page-header::after{
    content:"";position:absolute;inset:0;pointer-events:none;z-index:0;opacity:.45;
    background-image:repeating-linear-gradient(
      90deg,
      transparent 0, transparent 11px,
      rgba(255,255,255,.015) 11px, rgba(255,255,255,.03) 12px,
      rgba(0,0,0,.18) 13px, transparent 18px, transparent 34px
    );
  }
  .site--thesis .arena-stage > .arena-page-header .arena-page-header-inner,
  .site--methodology .arena-stage > .arena-page-header .arena-page-header-inner{
    position:relative;z-index:1;
  }
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill{color:rgba(245,242,235,.82);background:rgba(255,255,255,.06)}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-label,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-label{color:rgba(245,242,235,.88)}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-num,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-num{color:rgba(245,242,235,.42)}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill:hover,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill.on{background:rgba(255,255,255,.11)}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-num,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-num{color:var(--accent)}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-label,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-label{color:var(--ornn-ink);font-weight:600}
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill:hover .arena-nav-ring,
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-ring,
  .site--thesis .arena-stage > .arena-page-header .arena-nav-pill:focus-visible .arena-nav-ring,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill:hover .arena-nav-ring,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill.on .arena-nav-ring,
  .site--methodology .arena-stage > .arena-page-header .arena-nav-pill:focus-visible .arena-nav-ring{
    border-color:rgba(245,242,235,.55);
  }

  @media(prefers-reduced-motion:reduce){
    .hero-gate.arena-index-hero::before{animation:none}
    .hero-gate.arena-index-hero .wrap::after{animation:none;opacity:1;transform:none}
    .hero-gate.arena-index-hero .gate-main > *,
    .hero-gate.arena-index-hero .arena-header-nav{opacity:1;animation:none;transform:none}
  }
"""
