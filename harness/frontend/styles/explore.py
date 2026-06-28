"""Exa-style benchmark panel, entity cards, and logo chrome."""


def explore_css() -> str:
    return r"""
  .idx-toolbar{
    display:flex;flex-wrap:wrap;gap:var(--space-xs);align-items:center;
    padding-bottom:var(--space-sm);margin-bottom:var(--space-sm);
    border-bottom:1px solid var(--line-subtle);
  }
  .idx-search{
    flex:1 1 180px;min-width:140px;padding:9px 12px;border:1px solid var(--line);
    border-radius:var(--radius-md);background:var(--bg-default);font-size:14px;
    font-family:var(--font-sans);color:var(--ink);
  }
  .idx-search:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 2px rgba(184,90,50,.12)}
  .idx-btn{
    padding:8px 12px;border:1px solid var(--line);border-radius:var(--radius-md);
    background:var(--bg-default);font-size:13px;color:var(--ink2);cursor:pointer;font-family:var(--font-sans);
  }
  .idx-btn.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .idx-meta{font-size:13px;color:var(--muted);margin-left:auto;white-space:nowrap}
  .idx-filter-label{
    font-family:var(--font-mono);font-size:10px;font-weight:500;letter-spacing:.08em;
    text-transform:uppercase;color:var(--muted);padding:0 2px;
  }

  .card-list{
    display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
    gap:var(--space-sm);
  }
  .ent-card{
    display:grid;grid-template-columns:1fr;
    gap:var(--space-xs);align-items:start;
    padding:var(--space-sm);background:var(--bg-default);
    border:1px solid var(--line-subtle);border-radius:var(--radius-card);
    cursor:pointer;transition:border-color .15s;
  }
  .ent-card:hover{border-color:var(--line)}
  .ent-id{display:flex;gap:var(--space-sm);align-items:center;min-width:0}
  .ent-avatar{
    flex:0 0 36px;width:36px;height:36px;border-radius:var(--radius-md);
    background:var(--bg-subtle);display:flex;align-items:center;justify-content:center;
    font-size:12px;font-weight:600;color:var(--section-accent);overflow:hidden;
    border:1px solid var(--line-subtle);
  }
  .ent-avatar img{width:100%;height:100%;object-fit:contain;padding:4px;background:#fff}
  .ent-name{font-weight:600;font-size:15px;color:var(--ink);line-height:1.3;display:flex;align-items:center;flex-wrap:wrap;gap:6px}
  .ent-meta{font-size:13px;color:var(--muted);margin-top:2px}
  .quad-tag{
    font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;
    padding:2px 8px;border-radius:var(--radius-pill);
    background:var(--bg-muted);color:var(--muted);
  }
  .ent-viz{display:flex;flex-direction:column;gap:4px;min-width:0}
  .ent-mos-row{display:flex;align-items:baseline;justify-content:space-between;gap:var(--space-xs)}
  .ent-mos-label{font-size:9px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .ent-mos{
    font-family:var(--font-sans);font-size:17px;font-weight:500;
    font-variant-numeric:tabular-nums;line-height:1;color:var(--ink);
  }
  .ent-card .spread-wrap{display:none}
  .ent-mos.pos{color:var(--earning-s)}
  .ent-mos.neg{color:var(--exposed)}
  .ent-bar-row{display:grid;grid-template-columns:32px 1fr 34px;gap:8px;align-items:center}
  .ent-bar-lbl{font-size:10px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
  .ent-bar-track{height:7px;background:var(--bg-subtle);border-radius:var(--radius-pill);overflow:hidden}
  .ent-bar-fill{display:block;height:100%;border-radius:var(--radius-pill);min-width:2px}
  .ent-bar-fill.exp{background:var(--exposed);opacity:.85}
  .ent-bar-fill.prep{background:var(--earning-s);opacity:.85}
  .ent-bar-val{font-size:12px;font-variant-numeric:tabular-nums;color:var(--ink2);text-align:right}
  .spread-wrap{margin-top:2px}
  .spread-label{font-size:10px;color:var(--muted);margin-bottom:4px;letter-spacing:.04em}
  .spread-track{position:relative;height:8px;background:var(--bg-subtle);border-radius:var(--radius-pill)}
  .spread-band{position:absolute;top:0;bottom:0;border-radius:var(--radius-pill);opacity:.35}
  .spread-tick{position:absolute;top:-2px;width:2px;height:12px;border-radius:1px;transform:translateX(-50%)}
  .spread-tick.prep{background:var(--earning-s)}
  .spread-tick.exp{background:var(--exposed)}

  .ent-logo-wrap{
    flex:0 0 36px;width:36px;height:36px;border-radius:var(--radius-md);
    background:var(--bg-default);border:1px solid var(--line-subtle);
    display:flex;align-items:center;justify-content:center;overflow:hidden;
  }
  .ent-logo{width:100%;height:100%;object-fit:contain;padding:4px;background:#fff}
  .ent-logo-fallback{
    display:flex;align-items:center;justify-content:center;width:100%;height:100%;
    font-size:11px;font-weight:600;color:var(--section-accent);background:var(--bg-subtle);
  }
  .ent-logo-wrap.sm{flex:0 0 32px;width:32px;height:32px}
  .ent-logo-wrap.xs{flex:0 0 26px;width:26px;height:26px;border-radius:4px;flex-shrink:0}
  .tbl-name{display:flex;align-items:center;gap:8px;min-width:0}
  .tbl-entity-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
  .drawer-logo-row{display:flex;align-items:center;gap:12px;margin-bottom:6px}

  .bench-section{margin:0 0 var(--space-lg)}
  .bench-split{
    display:grid;grid-template-columns:minmax(240px,280px) minmax(0,1fr);
    min-height:560px;border-radius:var(--radius-lg);overflow:hidden;
    border:1px solid var(--line-subtle);background:var(--bg-default);
  }
  .bench-rail{
    background:#111;color:#fff;padding:var(--space-md) var(--space-md) var(--space-lg);
    display:flex;flex-direction:column;
  }
  .bench-kicker{
    font-size:11px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;
    color:#888;margin:0 0 var(--space-xs);
  }
  .bench-title{
    font-family:var(--font-sans);font-size:clamp(20px,2.2vw,26px);
    font-weight:500;line-height:1.15;letter-spacing:-.02em;margin:0 0 var(--space-xs);
  }
  .bench-lede{font-size:14px;color:#aaa;line-height:1.55;margin:0 0 var(--space-md);max-width:28ch}
  .bench-tabs{display:flex;flex-direction:column;gap:2px;margin-bottom:var(--space-sm)}
  .bench-tab{
    text-align:left;padding:9px 0 9px 14px;border:none;border-left:2px solid transparent;
    background:none;color:#888;font-size:14px;cursor:pointer;font-family:var(--font-sans);
    transition:color .15s,border-color .15s;
  }
  .bench-tab:hover{color:#ccc}
  .bench-tab.on{color:#fff;border-left-color:#fff}
  .bench-filters{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:var(--space-md)}
  .bench-filter{
    font-size:11px;padding:4px 10px;border-radius:var(--radius-pill);
    border:1px solid #333;background:transparent;color:#888;cursor:pointer;font-family:var(--font-sans);
  }
  .bench-filter:hover{border-color:#555;color:#ccc}
  .bench-filter.on{background:#fff;color:#111;border-color:#fff}
  .bench-note{font-size:13px;color:#777;line-height:1.5;margin-top:var(--space-sm)}
  .bench-panel{padding:var(--space-md);display:flex;flex-direction:column;min-width:0;min-height:0}
  .bench-head{
    display:flex;align-items:flex-start;justify-content:space-between;gap:var(--space-md);
    margin-bottom:var(--space-sm);flex-shrink:0;
  }
  .bench-metric-label{font-size:13px;color:var(--muted);margin:0}
  .bench-metric-label b{color:var(--ink);font-weight:600}
  .bench-hint{font-size:12px;color:var(--muted);margin:4px 0 0}
  .bench-legend{display:flex;flex-wrap:wrap;gap:10px 16px;font-size:12px;color:var(--muted);align-items:center}
  .bench-legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
  .bench-chart-wrap{
    flex-shrink:0;background:var(--bg-muted);border:1px solid var(--line-subtle);
    border-radius:var(--radius-md);padding:var(--space-sm) var(--space-xs) 0;margin-bottom:var(--space-sm);
    overflow-x:auto;
  }
  .bench-svg{display:block;width:100%;min-width:520px;height:auto}
  .bench-svg-col{cursor:pointer;transition:opacity .15s}
  .bench-svg-col:hover{opacity:.85}
  .bench-list-head{
    display:flex;justify-content:space-between;align-items:center;
    font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
    color:var(--muted);padding:0 2px var(--space-xs);flex-shrink:0;
  }
  .bench-list{
    flex:1;overflow-y:auto;overflow-x:hidden;min-height:200px;max-height:420px;
    border:1px solid var(--line-subtle);border-radius:var(--radius-md);background:var(--bg-default);
  }
  .bench-row{
    display:grid;grid-template-columns:28px 32px minmax(120px,1.4fr) minmax(140px,2fr) auto 24px;
    gap:10px;align-items:center;padding:10px 12px;border-bottom:1px solid var(--line-subtle);
    cursor:pointer;transition:background .12s;text-align:left;width:100%;
    background:var(--bg-default);border-left:none;border-right:none;border-top:none;
    font-family:var(--font-sans);
  }
  .bench-row:last-child{border-bottom:none}
  .bench-row:hover,.bench-row:focus-visible{background:var(--bg-muted);outline:none}
  .bench-row.on{background:var(--accent-muted)}
  .bench-rank{font-size:12px;font-weight:600;color:var(--muted);font-variant-numeric:tabular-nums;text-align:center}
  .bench-row-id{min-width:0}
  .bench-row-name{
    display:block;font-size:14px;font-weight:600;color:var(--ink);line-height:1.25;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  }
  .bench-row-tag{
    display:inline-block;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;
    padding:1px 6px;border-radius:var(--radius-pill);margin-top:3px;
  }
  .bench-row-tag.quad-exposed{background:#fde8e7;color:#cf4a45}
  .bench-row-tag.quad-earning_it{background:#e8f3ea;color:#34894b}
  .bench-row-tag.quad-whitespace{background:#e8f0f8;color:#3f7fb0}
  .bench-row-tag.quad-sidelined{background:var(--bg-subtle);color:var(--muted)}
  .bench-row-track{
    position:relative;height:28px;background:var(--bg-subtle);border-radius:var(--radius-md);
    overflow:hidden;display:flex;align-items:center;
  }
  .bench-row-fill{position:absolute;left:0;top:0;bottom:0;border-radius:var(--radius-md);transition:width .3s ease;min-width:2px}
  .bench-row-fill.quad-exposed{background:var(--exposed)}
  .bench-row-fill.quad-earning_it{background:var(--earning-s)}
  .bench-row-fill.quad-whitespace{background:var(--whitespace)}
  .bench-row-fill.quad-sidelined{background:var(--sidelined)}
  .bench-row-val{
    position:relative;z-index:1;font-size:13px;font-weight:600;color:var(--ink);
    padding-left:10px;font-variant-numeric:tabular-nums;
  }
  .bench-row-stats{display:flex;gap:10px;font-size:11px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
  .bench-row-stats b{color:var(--ink);font-weight:600}
  .bench-row-action{font-size:16px;color:var(--muted);opacity:0;transition:opacity .12s}
  .bench-row:hover .bench-row-action{opacity:1}

  @media(max-width:900px){
    .bench-row{grid-template-columns:24px 28px 1fr auto;grid-template-rows:auto auto;gap:6px 10px}
    .bench-row-track{grid-column:1/-1}
    .bench-row-stats,.bench-row-action{display:none}
  }
  @media(min-width:1100px){
    .card-list{grid-template-columns:repeat(3,1fr)}
  }
  .fund-card{grid-template-rows:auto auto 1fr}
  .fund-card .ent-name{font-size:14px}
  .fund-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px;font-size:11px;font-variant-numeric:tabular-nums}
  .fund-stats span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.06em}
  .fund-stats b{font-size:13px;color:var(--ink);font-weight:600}
  .fund-portfolio{font-size:11px;color:var(--muted);margin-top:4px;padding-top:4px;border-top:1px solid var(--line-subtle)}

  .term-section{margin-bottom:var(--space-lg)}
  .term-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:var(--space-sm)}
  .term-panel{
    padding:var(--space-sm);background:var(--bg-default);border:1px solid var(--line-subtle);
    border-radius:var(--radius-md);min-height:180px;display:flex;flex-direction:column;
  }
  .term-panel.term-wide{grid-column:1/-1}
  .term-panel-title{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
  .term-stats{font-size:12px;color:var(--ink2);margin:0;font-variant-numeric:tabular-nums;line-height:1.4}
  .term-note{color:var(--warn);font-weight:600}
  .term-hint{font-size:11px;color:var(--muted);margin:0 0 8px;line-height:1.45}
  .term-chart{min-height:120px;overflow-x:auto}
  .term-chart svg,.term-swarm-chart svg,.term-quad-svg svg{display:block;width:100%;height:auto;max-height:340px}
  .term-swarm-wrap{display:flex;flex-direction:column;gap:8px;width:100%}
  .term-swarm-seg{display:flex;flex-wrap:wrap;gap:6px}
  .term-swarm-btn{
    font-size:11px;padding:5px 10px;border:1px solid var(--line);border-radius:var(--radius-pill);
    background:var(--bg-default);cursor:pointer;font-family:var(--font-sans);color:var(--ink2);
  }
  .term-swarm-btn.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .term-swarm-meta{margin:0}
  .term-swarm-chart{min-height:140px;padding:0}
  .term-tabs{display:flex;gap:4px;margin-bottom:8px}
  .term-tab{font-size:11px;padding:4px 10px;border:1px solid var(--line);border-radius:var(--radius-pill);background:var(--bg-default);cursor:pointer;font-family:var(--font-sans)}
  .term-tab.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .term-table{width:100%;border-collapse:collapse;font-size:12px}
  .term-table th,.term-table td{padding:6px 8px;border-bottom:1px solid var(--line-subtle);text-align:left}
  .term-table tr{cursor:pointer}
  .term-table tr:hover{background:var(--bg-muted)}
  .term-table .num{text-align:right;font-variant-numeric:tabular-nums}
  .term-table-wrap{max-height:280px;overflow-y:auto}
  .term-empty{font-size:12px;color:var(--muted);margin:0;padding:var(--space-sm) 0}
  .alpha-list{display:flex;flex-direction:column;gap:4px}
  .alpha-row{
    display:grid;grid-template-columns:22px 1fr auto 36px;gap:8px;align-items:center;
    width:100%;padding:8px 10px;border:1px solid var(--line-subtle);border-radius:var(--radius-sm);
    background:var(--bg-default);cursor:pointer;text-align:left;font-family:var(--font-sans);
    transition:border-color .12s,background .12s;
  }
  .alpha-row:hover{border-color:var(--line);background:var(--bg-muted)}
  .alpha-rank{font-size:11px;font-weight:600;color:var(--muted);font-variant-numeric:tabular-nums}
  .alpha-id{min-width:0}
  .alpha-name{display:block;font-size:13px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .alpha-bars{display:flex;flex-direction:column;gap:3px;margin-top:4px}
  .alpha-bar{height:4px;background:var(--bg-subtle);border-radius:2px;overflow:hidden}
  .alpha-bar i{display:block;height:100%;background:var(--earning-s);border-radius:2px}
  .alpha-bar.exp i{background:var(--exposed);opacity:.85}
  .alpha-gap{font-size:14px;font-weight:600;color:var(--earning-s);font-variant-numeric:tabular-nums}
  .alpha-meas{font-size:11px;color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
  .alpha-legend{display:flex;flex-wrap:wrap;gap:8px 14px;margin-top:8px;font-size:10px;color:var(--muted)}
  .alpha-legend .leg-swatch::before{content:'';display:inline-block;width:8px;height:4px;margin-right:4px;vertical-align:middle;border-radius:1px}
  .alpha-legend .leg-prep::before{background:var(--earning-s)}
  .alpha-legend .leg-exp::before{background:var(--exposed)}
  .term-compare-pick{display:flex;gap:8px;align-items:center;margin-bottom:8px;flex-wrap:wrap}
  .term-compare-pick select{font-size:12px;padding:6px 8px;border:1px solid var(--line);border-radius:var(--radius-sm);font-family:var(--font-sans)}

  .profile-panel{
    position:fixed;top:0;right:0;width:min(720px,100vw);height:100vh;background:var(--bg-default);
    border-left:1px solid var(--line-subtle);z-index:60;transform:translateX(100%);
    transition:transform .22s ease;display:flex;flex-direction:column;
  }
  .profile-panel.on{transform:translateX(0)}
  .profile-head{padding:var(--space-md);border-bottom:1px solid var(--line-subtle);flex-shrink:0}
  .profile-body{flex:1;overflow-y:auto;padding:var(--space-md)}
  .profile-hero-row{display:flex;align-items:center;gap:12px;margin-top:8px}
  .profile-hero-title{font-family:var(--font-sans);font-size:22px;font-weight:500;margin:0}
  .profile-swarm{margin:var(--space-md) 0;border:1px solid var(--line-subtle);border-radius:var(--radius-md);padding:var(--space-sm)}

  @media(max-width:900px){.term-grid{grid-template-columns:1fr}}
"""
