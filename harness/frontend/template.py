"""Page shell — zones and slots only. See ARCHITECTURE.md."""

PAGE_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Non-Firm Power Risk Index · PRINCEPS</title>
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<!--__SPLASH_PRELOAD__-->
<style>/*__SITE_CSS__*/</style>
<script>try{if(localStorage.getItem('nfri-splash-v1'))document.documentElement.classList.add('splash-skip');}catch(e){}</script>
</head>
<body class="site">
<!--__SPLASH__-->
<!--__HERO_GATE__-->
<main class="site-main">
  <div class="layout-band layout-band--thesis essay-reveal">
    <div class="wrap">
      <div class="index-thesis-shell">
        <aside class="index-thesis-aside" aria-label="Contents">
          <!--__THESIS_TOC__-->
        </aside>
        <div class="index-thesis-body">
          <section id="argument" class="section section--prose essay act-section essay-reveal"><div class="prose"><!--__ACT_INDUSTRY__--></div></section>
          <section id="landscape" class="section section--prose essay act-section essay-reveal"><div class="prose"><!--__ACT_LANDSCAPE__--></div></section>
          <section id="mechanics" class="section section--prose essay act-section essay-reveal"><div class="prose"><!--__ACT_MECHANICS__--></div></section>
          <section id="analysis" class="section section--prose essay act-section essay-reveal"><div class="prose"><!--__ACT_PROPOSAL__--></div></section>
        </div>
      </div>
    </div>
  </div>

  <div class="wrap">
    <section id="index" class="section section--panel act-viz-band essay-reveal">
      <div class="viz-bento">
        <!--__VIZ_SCATTER__-->
        <div class="filter-bar" id="scatter-filters"></div>
        <div class="panel">
          <svg id="plot" class="chart" viewBox="0 0 960 580" role="img" aria-label="Exposure vs Preparedness"></svg>
          <div class="scatter-legend">
            <span><i class="lg-earning"></i><span class="scatter-leg-main">Earning it</span><span class="scatter-leg-tag">Carrying the bet</span></span>
            <span><i class="lg-exposed"></i><span class="scatter-leg-main">Exposed</span><span class="scatter-leg-tag">Cleared on damage</span></span>
            <span><i class="lg-whitespace"></i><span class="scatter-leg-main">Whitespace</span><span class="scatter-leg-tag">Judgement surplus</span></span>
            <span><i class="lg-sidelined"></i><span class="scatter-leg-main">Sidelined</span><span class="scatter-leg-tag">Off the bet</span></span>
            <span>· dashed = median cuts · hover for name</span>
          </div>
        </div>
        <!--__VIZ_LAYER__-->
        <div class="panel layer-mos-panel">
          <div id="hero-layer-chart" class="hero-layer-chart" aria-label="Margin of Safety by layer"></div>
        </div>
      </div>
    </section>
  </div>

  <div class="layout-band layout-band--thesis essay-reveal">
    <div class="wrap">
      <div class="index-thesis-shell index-thesis-shell--continued">
        <aside class="index-thesis-aside index-thesis-aside--spacer" aria-hidden="true"></aside>
        <div class="index-thesis-body">
          <section id="findings" class="section section--prose essay essay-reveal"><div class="prose"><!--__FINDINGS__--></div></section>
        </div>
      </div>
    </div>
  </div>

  <div class="wrap">
    <section id="rankings" class="section section--panel section--rankings">
      <!--__VIZ_TABLE__-->
      <div class="idx-toolbar idx-toolbar--rankings" id="idx-toolbar">
        <input type="search" class="idx-search" id="idx-search" placeholder="Search entities…" aria-label="Search entities">
        <span class="idx-filter-label">Layer</span>
        <button type="button" class="idx-btn on" data-t="layer" data-v="all">All</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="1">L1</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="2">L2</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="3">L3</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="4">L4</button>
        <span class="idx-filter-label">Quadrant</span>
        <button type="button" class="idx-btn on" data-t="quad" data-v="all">All</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="exposed">Exposed</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="whitespace">Whitespace</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="earning_it">Earning</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="sidelined">Sidelined</button>
        <span class="idx-meta" id="idx-count"></span>
      </div>
      <div class="panel rankings-table-panel">
        <table class="data-table" id="tbl"><thead><tr>
          <th data-k="name">Entity</th><th data-k="layer" class="num">L</th>
          <th data-k="exp" class="num">Exposure</th><th data-k="prep" class="num">Prepared</th>
          <th data-k="mos" class="num">Margin</th><th data-k="quad">Quadrant</th>
          <th data-k="meas" class="num">Measured</th><th data-k="conf">Conf.</th>
        </tr></thead><tbody></tbody></table>
      </div>
    </section>

    <p class="explore-universe-cta type-body"><a href="explore.html">Browse the full universe as cards with logos →</a></p>

    <details id="reference" class="layout-disclosure">
      <summary>Reference — objections, rules, sources &amp; method</summary>
      <div class="layout-disclosure-body">
        <!--__FAQ_BAND__-->
        <section id="rail" class="section section--panel section--nested">
          <header class="section-head section-head--compact">
            <p class="section-kicker type-kicker">Rules in force</p>
            <h2 class="section-title type-title">Rules that re-price firmness</h2>
          </header>
          <div class="rail-grid" id="railcards"></div>
        </section>
        <section id="methodology" class="section section--prose essay section--nested"><div class="prose"><!--__METHODOLOGY__--></div></section>
        <section id="data" class="section section--prose essay section--nested"><div class="prose"><!--__DATA__--></div></section>
        <section id="knowledge" class="section section--panel section--nested">
          <header class="section-head section-head--compact">
            <p class="section-kicker type-kicker">Knowledge graph</p>
            <h2 class="section-title type-title">Sources &amp; knowledge graph</h2>
          </header>
          <div class="kg-shell">
            <aside class="kg-index" aria-label="Source index">
              <div class="kg-toolbar">
                <input type="search" class="kg-search" id="kgsearch" placeholder="Search sources…" autocomplete="off">
                <div class="kg-topics" id="kgfilters"></div>
              </div>
              <p class="kg-topic-desc" id="kgtopicdesc"></p>
              <ol class="kg-list" id="kglist" role="listbox"></ol>
            </aside>
            <div class="kg-detail" id="kgdetail" aria-live="polite"></div>
          </div>
        </section>
        <section id="method" class="section section--panel section--nested">
          <header class="section-head section-head--compact">
            <p class="section-kicker type-kicker">Eval harness</p>
            <h2 class="section-title type-title">Method &amp; evals</h2>
          </header>
          <div class="eval-chips" id="eval-chips"></div>
          <p class="site-footnote">
            Scoring is arithmetic in code (<code>harness/scoring.py</code>).
            Ratings fuse latent and deterministic inputs by credibility weighting.
            Below the publication gate = <b>PROVISIONAL</b>. Not investment advice.
          </p>
        </section>
      </div>
    </details>

    <details id="analytics-deep" class="layout-disclosure">
      <summary>Open deeper analytics</summary>
      <div class="layout-disclosure-body">
        <section id="benchmark" class="section section--panel bench-section" aria-label="Carrier benchmarks">
          <!--__VIZ_BENCH__-->
          <div class="bench-split">
            <aside class="bench-rail">
              <nav class="bench-tabs" id="bench-tabs" aria-label="Benchmark metric">
                <button type="button" class="bench-tab on" data-m="mos">Margin of Safety</button>
                <button type="button" class="bench-tab" data-m="exp">Exposure</button>
                <button type="button" class="bench-tab" data-m="prep">Preparedness</button>
                <button type="button" class="bench-tab" data-m="meas">Measured share</button>
              </nav>
              <p class="bench-note" id="bench-note">MoS = Preparedness − Exposure. Positive margin means preparedness exceeds exposure.</p>
              <div class="bench-filters" id="bench-filters">
                <button type="button" class="bench-filter on" data-f="l1">All L1</button>
                <button type="button" class="bench-filter" data-f="insurer">Carriers</button>
                <button type="button" class="bench-filter" data-f="lloyds_syndicate">Syndicates</button>
                <button type="button" class="bench-filter" data-f="reinsurer">Reinsurers</button>
                <button type="button" class="bench-filter" data-f="all">Full universe</button>
              </div>
            </aside>
            <div class="bench-panel">
              <div class="bench-head">
                <div>
                  <p class="bench-metric-label" id="bench-metric-label">Sorted by <b>Margin of Safety</b></p>
                  <p class="bench-hint">Click any bar or row for the full score decomposition</p>
                </div>
                <div class="bench-legend" id="bench-legend"></div>
              </div>
              <div class="bench-chart-wrap" id="bench-chart"></div>
              <div class="bench-list-head"><span>Ranked entities</span><span id="bench-count"></span></div>
              <div class="bench-list" id="bench-list" role="list"></div>
            </div>
          </div>
        </section>

        <section id="terminal" class="section section--panel term-section" aria-label="Index analytics">
          <!--__TERM_SECTION__-->
          <div class="term-view-tabs" id="term-view-tabs" role="tablist" aria-label="Analytics views">
            <button type="button" class="term-view-tab on" data-view="overview" role="tab">Overview</button>
            <button type="button" class="term-view-tab" data-view="segments" role="tab">Segments</button>
            <button type="button" class="term-view-tab" data-view="carriers" role="tab">Carriers</button>
            <button type="button" class="term-view-tab" data-view="compare" role="tab">Compare</button>
          </div>
          <div class="term-grid-bento" id="term-grid-bento">
            <div class="term-panel on" data-term-view="overview">
              <!--__TERM_REGRESSION__-->
            </div>
            <div class="term-panel" data-term-view="overview">
              <!--__TERM_STRATEGY__-->
            </div>
            <div class="term-panel" data-term-view="segments">
              <!--__TERM_SCOREBOARD__-->
            </div>
            <div class="term-panel term-wide" data-term-view="carriers">
              <!--__TERM_SWARM__-->
            </div>
            <div class="term-panel term-wide" data-term-view="carriers">
              <!--__TERM_QUAD__-->
            </div>
            <div class="term-panel" data-term-view="compare">
              <!--__TERM_ALPHA__-->
            </div>
            <div class="term-panel" data-term-view="compare">
              <!--__TERM_COMPARE__-->
            </div>
          </div>
        </section>
      </div>
    </details>
  </div>
</main>

<footer id="foundations" class="ref-band reveal">
  <div class="wrap">
    <div class="ref-band-intro">
      <p class="ref-kicker type-kicker">Sources</p>
      <h2 class="ref-title type-title">References</h2>
    </div>
    <!--__FOUNDATIONS__-->
  </div>
</footer>

<footer class="site-foot">
  <div class="wrap"><!--__SITE_FOOT__--></div>
</footer>

<div id="scrim" onclick="closeAllPanels()"></div>
<!--__MOBILE_DOCK__-->
<aside id="profile" class="profile-panel" aria-hidden="true">
  <div class="profile-head">
    <button type="button" class="drawer-close" onclick="closeProfile()" aria-label="Close">✕</button>
    <div id="profile-hero"></div>
  </div>
  <div class="profile-body" id="profile-body"></div>
</aside>
<aside id="drawer">
  <div class="drawer-head">
    <button type="button" class="drawer-close" onclick="closeDrawer()" aria-label="Close">✕</button>
    <h3 id="drawer-name"></h3>
    <div class="text-muted" id="drawer-meta"></div>
  </div>
  <div class="drawer-body" id="drawer-body"></div>
</aside>

<script>
/*__CLIENT_JS__*/
</script>
</body></html>"""
