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
    position:fixed;top:0;right:0;height:100%;width:min(560px,94vw);background:var(--bg-default);
    border-left:1px solid var(--line);transform:translateX(100%);
    transition:transform .22s cubic-bezier(.4,0,.2,1);z-index:56;overflow:auto;
  }
  #drawer.on{transform:none}
  .drawer-head{
    padding:18px 20px;border-bottom:1px solid var(--line-subtle);position:sticky;top:0;
    background:var(--bg-default);z-index:2;
  }
  .drawer-head h3{margin:0;font-family:var(--font-display);font-weight:600;font-size:var(--type-title-min)}
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
  .ev-tier{font-size:10px;padding:1px 6px;border-radius:var(--radius-md);background:var(--bg-muted);color:var(--muted)}
  .ratbar{display:inline-flex;gap:2px;margin-left:2px}
  .ratbar i{width:7px;height:11px;border-radius:1px;background:var(--bg-subtle)}
  .ratbar i.on{background:var(--accent2)}

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
