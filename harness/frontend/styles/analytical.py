"""Zone-panel styles: scatter, table, filters, rail, drawer, method. Tokens only — no raw hex except quadrant fills."""


def analytical_css() -> str:
    return r"""
  /* --- filters (segmented control) --- */
  .filter-bar{display:flex;gap:var(--space-sm);flex-wrap:wrap;align-items:center;margin:0 0 var(--space-sm)}
  .filter-bar .filter-grp{display:flex;gap:8px;align-items:center}
  .filter-bar .filter-label{font-family:var(--font-mono);font-size:var(--type-kicker);letter-spacing:var(--type-kicker-track);text-transform:uppercase;color:var(--muted)}
  .filter-seg{display:inline-flex;border:1px solid var(--line);border-radius:var(--radius-sm);overflow:hidden;background:var(--bg-default)}
  .filter-btn{
    border:none;border-right:1px solid var(--line-subtle);background:transparent;color:var(--ink2);
    padding:7px 12px;font-size:var(--type-body);cursor:pointer;font-family:var(--font-sans);
    transition:background .12s,color .12s;
  }
  .filter-btn:last-child{border-right:none}
  .filter-btn:hover{background:var(--bg-muted);color:var(--ink)}
  .filter-btn.on{background:var(--bg-muted);color:var(--ink);font-weight:600;box-shadow:inset 0 -2px 0 var(--section-accent)}

  /* --- scatter --- */
  .scatter-legend{
    display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);
    margin:10px 4px 2px;align-items:center;
  }
  .scatter-legend i{
    display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px;
  }
  .scatter-legend .lg-exposed{background:var(--exposed)}
  .scatter-legend .lg-earning{background:var(--earning-s)}
  .scatter-legend .lg-whitespace{background:var(--whitespace)}
  .scatter-legend .lg-sidelined{background:var(--sidelined)}
  .scatter-leg-main{font-weight:600;color:var(--ink2)}
  .scatter-leg-tag{margin-left:.35em;font-size:10px;font-weight:500;color:var(--muted);font-style:italic}

  /* --- layer MoS stack --- */
  .layer-mos-chart{display:flex;flex-direction:column;gap:var(--space-xs)}
  .layer-mos-head,
  .layer-mos-row{
    display:grid;grid-template-columns:minmax(108px,132px) minmax(0,1fr) 52px;
    gap:var(--space-sm);align-items:center;
  }
  .layer-mos-head{
    font-family:var(--font-mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;
    color:var(--muted);padding:0 2px 4px;
  }
  .layer-mos-axis{
    display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:6px;
    min-width:0;
  }
  .layer-mos-axis-side{font-size:10px;line-height:1.2}
  .layer-mos-axis-side.neg{justify-self:start;color:var(--exposed)}
  .layer-mos-axis-side.pos{justify-self:end;color:var(--earning-s)}
  .layer-mos-axis-zero{
    font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink2);text-transform:none;
    padding:1px 7px;border:1px dashed var(--line);border-radius:var(--radius-sm);background:var(--bg-muted);
  }
  .layer-mos-head-val{text-align:right}
  .layer-mos-rows{display:flex;flex-direction:column;gap:1px}
  .layer-mos-row{
    width:100%;padding:8px 2px;border:none;border-radius:var(--radius-sm);
    background:transparent;cursor:default;font:inherit;text-align:left;
    transition:background .12s, box-shadow .12s;
  }
  .hero-layer-chart .layer-mos-row{cursor:pointer}
  .hero-layer-chart .layer-mos-row:hover,
  .hero-layer-chart .layer-mos-row:focus-visible{background:var(--bg-muted);outline:none}
  .hero-layer-chart .layer-mos-row.on{
    background:var(--bg-muted);box-shadow:inset 3px 0 0 var(--section-accent);
  }
  .layer-mos-row.is-neg{background:color-mix(in srgb,var(--exposed) 4%,var(--bg-default))}
  .hero-layer-chart .layer-mos-row.is-neg:hover{
    background:color-mix(in srgb,var(--exposed) 7%,var(--bg-muted));
  }
  .layer-mos-label{display:flex;flex-direction:column;gap:1px;line-height:1.25;min-width:0}
  .layer-mos-tag{
    font-family:var(--font-mono);font-size:10px;font-weight:600;letter-spacing:.08em;color:var(--accent);
  }
  .layer-mos-name{font-size:12px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .layer-mos-track{
    position:relative;height:28px;border-radius:var(--radius-sm);
    background:var(--bg-muted);border:1px solid var(--line-subtle);overflow:hidden;
  }
  .layer-mos-zero{
    position:absolute;top:4px;bottom:4px;left:50%;width:0;border-left:2px dashed var(--line);
    transform:translateX(-50%);z-index:2;
  }
  .layer-mos-whisker{
    position:absolute;top:50%;height:3px;border-radius:2px;transform:translateY(-50%);
    opacity:.45;z-index:1;
  }
  .layer-mos-row:not(.is-neg) .layer-mos-whisker{background:var(--earning-s)}
  .layer-mos-row.is-neg .layer-mos-whisker{background:var(--exposed)}
  .layer-mos-bar{
    position:absolute;top:7px;bottom:7px;border-radius:999px;z-index:3;
    box-shadow:0 1px 2px rgba(20,20,20,.06);
  }
  .layer-mos-row:not(.is-neg) .layer-mos-bar{background:var(--earning-s)}
  .layer-mos-row.is-neg .layer-mos-bar{background:var(--exposed)}
  .layer-mos-val{
    display:flex;flex-direction:column;align-items:flex-end;gap:1px;
    font-family:var(--font-mono);font-size:14px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1;
  }
  .layer-mos-val.pos{color:var(--earning-s)}
  .layer-mos-val.neg{color:var(--exposed)}
  .layer-mos-n{font-size:9px;font-weight:500;color:var(--muted)}
  .layer-mos-foot{margin:4px 0 0;font-family:var(--font-mono);font-size:10px;color:var(--muted)}
  @media(max-width:640px){
    .layer-mos-head{display:none}
    .layer-mos-row{grid-template-columns:minmax(0,1fr) 48px;grid-template-rows:auto auto;row-gap:6px}
    .layer-mos-label{grid-column:1/-1}
    .layer-mos-track{grid-column:1}
    .layer-mos-val{grid-column:2;grid-row:2}
  }

  svg.chart{width:100%;height:auto;display:block}
  .plot-dot{cursor:pointer}
  .plot-tip{
    position:fixed;pointer-events:none;background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-sm);
    padding:10px 12px;max-width:280px;font-size:var(--type-body);
    z-index:50;transition:opacity .1s;line-height:var(--type-body-lead);
  }
  .plot-tip .tip-quad{font-family:var(--font-mono);font-size:var(--type-kicker);letter-spacing:var(--type-kicker-track);text-transform:uppercase;font-weight:500}
  .plot-tip .tip-name{font-weight:600;color:var(--ink);margin:2px 0}
  .plot-tip .tip-meta{font-family:var(--font-mono);font-size:var(--type-meta);color:var(--muted)}

  /* --- table --- */
  .data-table{width:100%;border-collapse:collapse;font-size:13px}
  .data-table th,.data-table td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line-subtle)}
  .data-table th{color:var(--muted);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
  .data-table th.sorted{color:var(--ink)}
  .data-table td.num,.data-table th.num{text-align:right;font-variant-numeric:tabular-nums}
  .data-table tr.row{cursor:pointer}
  .data-table tr.row:hover{background:var(--bg-muted)}
  .quad-label{
    font-family:var(--font-mono);font-size:var(--type-kicker);letter-spacing:var(--type-kicker-track);
    text-transform:uppercase;font-weight:500;white-space:nowrap;
  }
  .meas-bar{display:inline-block;height:7px;border-radius:var(--radius-pill);background:var(--measured);vertical-align:middle}
  .meas-track{
    display:inline-block;width:54px;height:7px;border-radius:var(--radius-pill);
    background:var(--bg-subtle);vertical-align:middle;overflow:hidden;
  }
  .text-muted{font-size:11px;color:var(--muted)}

  /* --- rail --- */
  .rail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(248px,1fr));gap:var(--space-sm)}
  .rail-card{
    border:1px solid var(--line-subtle);border-radius:var(--radius-sm);
    padding:var(--space-sm);background:var(--bg-default);
  }
  .rail-card .rail-id{font-weight:600;font-size:var(--type-body)}
  .rail-card .rail-status{font-family:var(--font-mono);font-size:var(--type-meta);color:var(--earning-s);font-weight:500}
  .rail-card p{margin:7px 0 0;font-size:var(--type-body);line-height:var(--type-body-lead);color:var(--ink2)}
  .chip-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
  .chip{
    font-family:var(--font-mono);font-size:var(--type-meta);color:var(--muted);
    padding:0;background:none;border:none;
  }
  .chip a{color:var(--section-accent);text-decoration:none}
  .chip a:hover{text-decoration:underline}

  /* --- drawer --- */
  #scrim{
    position:fixed;inset:0;background:rgba(20,20,20,.32);opacity:0;pointer-events:none;
    transition:opacity .18s;z-index:55;
  }
  #scrim.on{opacity:1;pointer-events:auto}
  #drawer{
    position:fixed;top:0;right:0;height:100%;width:min(680px,96vw);background:var(--bg-default);
    border-left:1px solid var(--line);transform:translateX(100%);
    transition:transform .22s cubic-bezier(.4,0,.2,1);z-index:56;overflow:auto;
  }
  #drawer.on{transform:none}
  .drawer-head{
    padding:18px 20px;border-bottom:1px solid var(--line-subtle);position:sticky;top:0;
    background:var(--bg-default);z-index:2;
  }
  .drawer-head h3{margin:0;font-family:var(--font-sans);font-weight:600;font-size:var(--type-title-min)}
  .drawer-head .drawer-close{
    position:absolute;top:14px;right:16px;cursor:pointer;font-size:20px;
    color:var(--muted);border:none;background:none;
  }
  .drawer-body{padding:16px 20px 40px}
  .drawer-method-tag{
    font-family:var(--font-mono);font-size:var(--type-kicker);font-weight:500;
    letter-spacing:var(--type-kicker-track);text-transform:uppercase;color:var(--muted);
  }
  .method-drawer-lead{font-size:15px;font-weight:600;color:var(--ink);margin:0 0 10px;line-height:1.4}
  .method-drawer-body{font-size:13.5px;color:var(--ink2);line-height:1.55;margin:0 0 14px}
  .method-drawer-criteria,.method-drawer-role{font-size:12.5px;color:var(--muted);line-height:1.5;margin:0 0 12px}
  .method-drawer-stats{margin-top:18px;padding-top:14px;border-top:1px solid var(--line-subtle)}
  .method-drawer-foot{margin:20px 0 0;font-size:13px}
  .method-drawer-foot a{color:var(--accent2);text-decoration:none;font-weight:600}
  .method-drawer-foot a:hover{text-decoration:underline}
  .drawer-section{margin:20px 0 0;padding-top:16px;border-top:1px solid var(--line-subtle)}
  .drawer-section-kicker{
    font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
    margin:0 0 10px;display:flex;align-items:center;gap:8px;
  }
  .drawer-section-kicker::before{content:'';width:3px;height:14px;background:var(--accent);border-radius:1px}
  .infirm-dim-grid{display:grid;gap:10px;margin-top:8px}
  .infirm-dim-head{display:flex;justify-content:space-between;font-size:12px;font-weight:600;margin-bottom:4px}
  .infirm-dim-r{color:var(--accent);font-variant-numeric:tabular-nums}
  .infirm-dim-note{font-size:11px;line-height:1.4;margin:4px 0 0}
  .drawer-section-note{font-size:12px;color:var(--muted);margin:0 0 10px}
  .drawer-overview-grid{
    display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:0 0 4px;
  }
  .drawer-kpi{
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:10px 12px;background:var(--bg-muted);
  }
  .drawer-kpi>span:first-child{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
  .drawer-kpi b{display:block;font-size:20px;font-variant-numeric:tabular-nums;margin:4px 0 2px;color:var(--ink)}
  .drawer-kpi-sub{font-size:11px;color:var(--muted);line-height:1.35}
  .drawer-risk-card{
    border:1px solid var(--line-subtle);border-left:3px solid var(--warn);border-radius:var(--radius-md);
    padding:10px 12px;margin-bottom:10px;background:var(--bg-default);
  }
  .drawer-risk-title{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:4px}
  .drawer-risk-body{font-size:12.5px;color:var(--ink2);line-height:1.5;margin:0}
  .drawer-risk-sev{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-left:8px}
  .drawer-risk-gap{font-size:11px;margin:6px 0 0}
  .drawer-risk-sources{margin-top:8px;font-size:11px}
  .drawer-risk-sources a{color:var(--accent2)}
  .drawer-risk-high{border-left-color:var(--exposed)}
  .drawer-risk-medium{border-left-color:var(--warn)}
  .drawer-risk-low{border-left-color:var(--muted)}
  .drawer-risk-entities{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
  .drawer-entity-chip{
    font-size:11px;padding:4px 10px;border-radius:999px;border:1px solid var(--line);
    background:var(--bg-muted);color:var(--ink2);cursor:pointer;
  }
  .drawer-entity-chip:hover{border-color:var(--accent);color:var(--accent2)}
  .drawer-roster-wrap{overflow:auto;max-height:min(52vh,420px);border:1px solid var(--line-subtle);border-radius:var(--radius-md)}
  .drawer-roster{width:100%;border-collapse:collapse;font-size:12.5px}
  .drawer-roster th{
    position:sticky;top:0;background:var(--bg-muted);text-align:left;padding:8px 10px;
    font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);border-bottom:1px solid var(--line-subtle);
  }
  .drawer-roster th.num,.drawer-roster td.num{text-align:right;font-variant-numeric:tabular-nums}
  .drawer-roster-row{cursor:pointer;transition:background .12s}
  .drawer-roster-row:hover{background:var(--bg-muted)}
  .drawer-roster td{padding:8px 10px;border-bottom:1px solid var(--line-subtle);vertical-align:middle}
  .profile-overview-table{
    display:grid;grid-template-columns:1fr 1fr;gap:10px 20px;margin:0;
  }
  .profile-overview-table dt{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
  .profile-overview-table dd{font-size:13px;margin:3px 0 0;font-weight:500;line-height:1.4}
  .score-row{display:flex;gap:18px;flex-wrap:wrap;margin:4px 0 14px}
  .score-row .score-cell{font-size:12px;color:var(--muted)}
  .score-row .score-cell b{display:block;font-size:21px;color:var(--ink);font-variant-numeric:tabular-nums}
  .score-decomp{font-size:12px;color:var(--muted);margin:2px 0 16px}
  .sf-head{
    font-weight:700;font-size:13px;margin:16px 0 6px;display:flex;justify-content:space-between;
  }
  .sf-card{border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:9px 11px;margin-bottom:8px}
  .sf-card .sf-top{display:flex;align-items:center;gap:8px;font-size:13px}
  .sf-card .sf-name{font-weight:600}
  .sf-card .sf-weight{color:var(--muted);font-size:11px;margin-left:auto}
  .sf-mode{
    font-size:10px;text-transform:uppercase;letter-spacing:.04em;padding:1px 6px;
    border-radius:var(--radius-md);font-weight:700;
  }
  .sf-mode.latent{background:var(--bg-subtle);color:var(--muted)}
  .sf-mode.hybrid{background:var(--accent-muted);color:var(--accent2)}
  .sf-mode.deterministic{background:var(--ok-bg);color:var(--earning-s)}
  .sf-card .sf-rationale{font-size:12px;color:var(--ink2);margin:6px 0 0;line-height:1.55}
  .sf-card .sf-evidence{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px;align-items:center}
  .sf-card .sf-evidence a{font-size:11px}
  .sf-question{font-size:11.5px;color:var(--muted);margin:6px 0 0;line-height:1.45}
  .sf-measured{font-size:12px;color:var(--measured);margin:4px 0 0}
  .sf-gap-note{font-size:11px;color:var(--warn);margin:6px 0 0;font-style:italic}
  .profile-block{margin:var(--space-md) 0;padding-top:var(--space-sm);border-top:1px solid var(--line-subtle)}
  .profile-block:first-child{border-top:none;padding-top:0}
  .profile-exec .profile-prose{font-family:var(--font-prose);font-size:1.05rem;line-height:1.55}
  .profile-prose{font-size:13px;line-height:1.55;color:var(--ink2);margin:0}
  .profile-kicker{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:10px 0 4px}
  .profile-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px 16px;margin:0}
  .profile-facts dt{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
  .profile-facts dd{font-size:13px;margin:2px 0 0;font-weight:500}
  .risk-card{border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:10px 12px;margin-bottom:8px;font-size:12.5px;line-height:1.5}
  .risk-card p{margin:4px 0 0}
  .cover-list{margin:0 0 8px;padding-left:18px;font-size:12.5px;line-height:1.5;color:var(--ink2)}
  .cover-inferred li{color:var(--muted)}
  .cover-absent li{color:var(--warn)}
  .profile-mining-note{font-size:11px;margin:8px 0 var(--space-md)}
  .profile-method-strip{font-size:11px;margin-top:var(--space-md);padding-top:var(--space-sm);border-top:1px solid var(--line-subtle)}
  .ev-tier{font-size:10px;padding:1px 6px;border-radius:var(--radius-md);background:var(--bg-muted);color:var(--muted)}
  .ratbar{display:inline-flex;gap:2px;margin-left:2px}
  .ratbar i{width:7px;height:11px;border-radius:1px;background:var(--bg-subtle)}
  .ratbar i.on{background:var(--accent2)}

  /* --- entity profile posture viz --- */
  .profile-panel{width:min(920px,100vw)}
  .profile-section{margin:var(--space-lg) 0 0}
  .profile-section:first-child{margin-top:0}
  .profile-section-kicker{
    display:flex;align-items:center;gap:10px;margin:0 0 var(--space-sm);
    font-family:var(--font-mono);font-size:11px;font-weight:600;letter-spacing:.12em;
    text-transform:uppercase;color:var(--ink-headline);
  }
  .profile-section-kicker::before{
    content:'';width:3px;height:16px;border-radius:1px;background:var(--accent);flex-shrink:0;
  }
  .profile-section-kicker--prep::before{background:var(--earning-s)}
  .profile-section-kicker--risk::before{background:var(--warn)}
  .profile-section-kicker--exp::before{background:var(--exposed)}
  .profile-posture{
    border:1px solid var(--line-subtle);border-radius:var(--radius-lg);
    background:var(--bg-default);padding:var(--space-md);margin-bottom:var(--space-md);
  }
  .profile-posture-top{
    display:grid;grid-template-columns:minmax(180px,220px) 1fr;gap:var(--space-md);
    align-items:start;padding-bottom:var(--space-md);border-bottom:1px solid var(--line-subtle);
  }
  .profile-posture-map{display:flex;flex-direction:column;align-items:center;gap:6px}
  .profile-posture-svg{display:block;width:100%;max-width:220px;height:auto}
  .profile-axis-lbl{font-size:9px;fill:var(--muted);font-family:var(--font-mono);letter-spacing:.04em}
  .profile-posture-quad{
    font-family:var(--font-mono);font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
  }
  .profile-carry{min-width:0}
  .profile-carry-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:10px}
  .profile-carry-lbl{
    font-family:var(--font-mono);font-size:10px;font-weight:600;letter-spacing:.1em;
    text-transform:uppercase;color:var(--muted);
  }
  .profile-carry-val{
    font-family:var(--font-display);font-size:2rem;font-weight:500;line-height:1;
    font-variant-numeric:tabular-nums;
  }
  .profile-carry-val.surplus{color:var(--earning-s)}
  .profile-carry-val.deficit{color:var(--exposed)}
  .profile-carry-track{position:relative;padding:28px 0 18px}
  .profile-carry-bar{
    position:relative;height:10px;background:var(--bg-subtle);border-radius:var(--radius-pill);overflow:visible;
  }
  .profile-carry-fill{
    position:absolute;top:0;bottom:0;border-radius:var(--radius-pill);opacity:.45;pointer-events:none;
  }
  .profile-carry-fill.surplus{background:var(--earning-s)}
  .profile-carry-fill.deficit{background:var(--exposed)}
  .profile-carry-pin{
    position:absolute;top:50%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;
    gap:2px;min-width:0;
  }
  .profile-carry-pin i{display:block;width:3px;height:18px;border-radius:2px}
  .profile-carry-pin.exp i{background:var(--exposed)}
  .profile-carry-pin.prep i{background:var(--earning-s)}
  .profile-carry-pin b{
    font-size:15px;font-weight:600;font-variant-numeric:tabular-nums;color:var(--ink);line-height:1;
  }
  .profile-carry-pin em{
    font-style:normal;font-size:9px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
    color:var(--muted);white-space:nowrap;
  }
  .profile-carry-ticks{
    position:relative;height:14px;margin-top:6px;font-size:9px;color:var(--muted);font-variant-numeric:tabular-nums;
  }
  .profile-carry-ticks span{position:absolute;transform:translateX(-50%)}
  .profile-carry-note{font-size:12px;color:var(--muted);margin:8px 0 0;line-height:1.45}
  .profile-ledger{margin-top:var(--space-md);display:grid;grid-template-columns:1fr 1fr;gap:var(--space-md)}
  .profile-ledger-h{
    display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0 0 8px;
    font-family:var(--font-mono);font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
    color:var(--ink-headline);
  }
  .profile-ledger-h b{font-size:18px;font-variant-numeric:tabular-nums;font-weight:600}
  .profile-ledger-h.exp b{color:var(--exposed)}
  .profile-ledger-h.prep b{color:var(--earning-s)}
  .profile-ledger-row{
    display:grid;grid-template-columns:minmax(0,1fr) 72px 28px auto;gap:8px;align-items:center;
    padding:5px 0;border-bottom:1px solid var(--line-subtle);font-size:12px;
  }
  .profile-ledger-row:last-child{border-bottom:none}
  .profile-ledger-name{color:var(--ink2);line-height:1.3;min-width:0}
  .profile-ledger-bar{height:6px;background:var(--bg-subtle);border-radius:var(--radius-pill);overflow:hidden}
  .profile-ledger-bar span{display:block;height:100%;border-radius:var(--radius-pill);min-width:2px}
  .profile-ledger-bar.exp span{background:var(--exposed);opacity:.82}
  .profile-ledger-bar.prep span{background:var(--earning-s);opacity:.82}
  .profile-ledger-val{
    font-weight:600;font-variant-numeric:tabular-nums;text-align:right;color:var(--ink);
  }
  .profile-ledger-tier{font-size:9px;padding:1px 5px;border-radius:var(--radius-pill);white-space:nowrap}
  .sf-score-pill{
    display:inline-flex;align-items:center;justify-content:center;
    min-width:28px;height:28px;padding:0 6px;border-radius:999px;
    font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;color:#fff;
  }
  .sf-score-pill.exp-0,.sf-score-pill.exp-1{background:var(--earning-s)}
  .sf-score-pill.exp-2{background:var(--warn)}
  .sf-score-pill.exp-3,.sf-score-pill.exp-4{background:var(--exposed)}
  .sf-score-pill.prep-0,.sf-score-pill.prep-1{background:var(--exposed)}
  .sf-score-pill.prep-2{background:var(--warn)}
  .sf-score-pill.prep-3,.sf-score-pill.prep-4{background:var(--earning-s)}
  .sf-profile-card{
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);
    padding:var(--space-sm) var(--space-md);margin-bottom:var(--space-sm);background:var(--bg-default);
  }
  .sf-profile-head{
    display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px;
  }
  .sf-profile-name{font-weight:600;font-size:14px;color:var(--ink);flex:1 1 160px}
  .sf-profile-weight{font-size:11px;color:var(--muted);margin-left:auto}
  .tier-pill{
    font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
    padding:2px 8px;border-radius:var(--radius-pill);background:var(--bg-muted);color:var(--muted);
  }
  .tier-pill.t-meas{background:var(--ok-bg);color:var(--earning-s)}
  .tier-pill.t-disc{background:var(--accent-muted);color:var(--accent)}
  .tier-pill.t-deriv{background:#e8f0f8;color:var(--accent2)}
  .sf-profile-evidence{
    font-size:13px;color:var(--accent2);font-weight:500;margin:0 0 8px;line-height:1.45;
  }
  .sf-profile-rationale{font-size:13px;color:var(--ink2);line-height:1.6;margin:0}
  .sf-profile-question{
    font-size:12px;color:var(--muted);margin:8px 0 0;line-height:1.5;
    padding-left:12px;border-left:2px solid var(--line-subtle);
  }
  .sf-profile-sources{
    display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px;
    font-size:11px;color:var(--muted);
  }
  .sf-profile-sources a{color:var(--accent)}
  .sf-profile-fusion{margin-top:8px;font-size:11px;color:var(--muted)}
  .sf-profile-fusion summary{cursor:pointer;font-weight:500;color:var(--ink2)}
  .sf-profile-fusion[open] summary{margin-bottom:6px}
  .profile-hero-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;align-items:center}
  .profile-hero-badge{
    font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
    padding:3px 10px;border-radius:var(--radius-pill);background:var(--bg-muted);color:var(--muted);
  }
  .profile-hero-mos{
    font-family:var(--font-mono);font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;
  }
  @media(max-width:720px){
    .profile-posture-top{grid-template-columns:1fr}
    .profile-ledger{grid-template-columns:1fr}
  }

  /* --- method / evals --- */
  .site-footnote{
    color:var(--muted);font-size:12.5px;line-height:1.6;padding:26px 0 60px;margin:0;
  }
  .eval-chips{display:flex;gap:var(--space-sm);flex-wrap:wrap;margin:6px 0 12px}
  .eval-chip{
    font-family:var(--font-mono);font-size:var(--type-meta);color:var(--ink2);
    padding:0;display:flex;gap:6px;align-items:center;background:none;border:none;
  }
  .eval-chip b{font-variant-numeric:tabular-nums}
  .eval-dot{width:8px;height:8px;border-radius:50%}
  .eval-chip.PASS .eval-dot{background:var(--earning-s)}
  .eval-chip.FAIL .eval-dot{background:var(--exposed)}
  .eval-chip.WARN .eval-dot{background:var(--warn)}

  .site-lede{
    flex:1 1 100%;width:100%;font-size:var(--type-lead);line-height:var(--type-lead-lead);
    color:var(--ink2);max-width:54ch;border-left:2px solid var(--section-accent);
    padding:2px 0 2px 18px;margin:0 0 var(--space-sm);
  }
  .site-lede b{font-weight:600;color:var(--ink)}
"""
