"""Zone-panel styles: scatter, table, filters, rail, drawer, method. Tokens only — no raw hex except quadrant fills."""


def analytical_css() -> str:
    return r"""
  /* --- filters --- */
  .filter-bar{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin:0 0 var(--space-sm)}
  .filter-bar .filter-grp{display:flex;gap:6px;align-items:center;margin-right:10px}
  .filter-bar .filter-label{font-size:12.5px;color:var(--muted)}
  .filter-btn{
    border:1px solid var(--line);background:var(--bg-default);color:var(--ink2);
    border-radius:var(--radius-pill);padding:5px 12px;font-size:12.5px;cursor:pointer;
    font-family:var(--font-sans);
  }
  .filter-btn.on{background:var(--ink);color:#fff;border-color:var(--ink)}

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

  /* --- table --- */
  .data-table{width:100%;border-collapse:collapse;font-size:13px}
  .data-table th,.data-table td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line-subtle)}
  .data-table th{color:var(--muted);font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
  .data-table td.num,.data-table th.num{text-align:right;font-variant-numeric:tabular-nums}
  .data-table tr.row{cursor:pointer}
  .data-table tr.row:hover{background:var(--bg-muted)}
  .quad-pill{font-size:11px;padding:1px 8px;border-radius:var(--radius-pill);color:#fff;white-space:nowrap}
  .meas-bar{display:inline-block;height:7px;border-radius:var(--radius-pill);background:var(--measured);vertical-align:middle}
  .meas-track{
    display:inline-block;width:54px;height:7px;border-radius:var(--radius-pill);
    background:var(--bg-subtle);vertical-align:middle;overflow:hidden;
  }
  .text-muted{font-size:11px;color:var(--muted)}

  /* --- rail --- */
  .rail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(248px,1fr));gap:var(--space-sm)}
  .rail-card{
    border:1px solid var(--line-subtle);border-radius:var(--radius-lg);
    padding:13px;background:var(--bg-default);
  }
  .rail-card .rail-id{font-weight:700;font-size:14px}
  .rail-card .rail-status{font-size:11.5px;color:var(--earning-s);font-weight:600}
  .rail-card p{margin:7px 0 0;font-size:12.5px;color:var(--ink2)}
  .chip-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
  .chip{
    font-size:11px;border:1px solid var(--line);border-radius:var(--radius-md);
    padding:2px 8px;color:var(--ink2);background:var(--bg-default);
  }

  /* --- drawer --- */
  #scrim{
    position:fixed;inset:0;background:rgba(20,20,20,.32);opacity:0;pointer-events:none;
    transition:opacity .18s;z-index:40;
  }
  #scrim.on{opacity:1;pointer-events:auto}
  #drawer{
    position:fixed;top:0;right:0;height:100%;width:min(560px,94vw);background:var(--bg-default);
    box-shadow:-12px 0 40px rgba(0,0,0,.18);transform:translateX(100%);
    transition:transform .22s cubic-bezier(.4,0,.2,1);z-index:41;overflow:auto;
  }
  #drawer.on{transform:none}
  .drawer-head{
    padding:18px 20px;border-bottom:1px solid var(--line-subtle);position:sticky;top:0;
    background:var(--bg-default);z-index:2;
  }
  .drawer-head h3{margin:0;font-size:20px;font-family:var(--font-display)}
  .drawer-head .drawer-close{
    position:absolute;top:14px;right:16px;cursor:pointer;font-size:20px;
    color:var(--muted);border:none;background:none;
  }
  .drawer-body{padding:16px 20px 40px}
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
  .sf-mode.latent{background:#eef0f1;color:#6b7780}
  .sf-mode.hybrid{background:#e3f0f2;color:#1F4E5C}
  .sf-mode.deterministic{background:#dcefe2;color:#2c7a43}
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
  .eval-chips{display:flex;gap:7px;flex-wrap:wrap;margin:6px 0 12px}
  .eval-chip{
    font-size:11.5px;border:1px solid var(--line);border-radius:var(--radius-md);
    padding:3px 9px;display:flex;gap:6px;align-items:center;
  }
  .eval-chip b{font-variant-numeric:tabular-nums}
  .eval-dot{width:8px;height:8px;border-radius:50%}
  .eval-chip.PASS .eval-dot{background:var(--earning-s)}
  .eval-chip.FAIL .eval-dot{background:var(--exposed)}
  .eval-chip.WARN .eval-dot{background:#d8920f}

  .site-lede{
    flex:1 1 100%;width:100%;
    font-size:15px;color:var(--ink2);max-width:74ch;border-left:3px solid var(--section-accent);
    padding:4px 0 4px 16px;margin:0 0 var(--space-sm);line-height:1.55;
  }
  .site-lede b{font-weight:600;color:var(--ink)}
"""
