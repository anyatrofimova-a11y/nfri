"""Explore universe page — card grid with logos."""

EXPLORE_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Explore the universe · Non-Firm Power Risk Index · PRINCEPS</title>
<!--__FAVICON__-->
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<!--__SPLASH_PRELOAD__-->
<style>/*__SITE_CSS__*/</style>
<script>try{if(localStorage.getItem('nfri-splash-v1'))document.documentElement.classList.add('splash-skip');}catch(e){}</script>
</head>
<body class="site site--explore">
<!--__SPLASH__-->
<!--__EXPLORE_HERO__-->
<main class="site-main">
  <div class="wrap">
    <section id="cards" class="section section--panel section--explore-cards essay-reveal">
      <header class="section-head">
        <p class="section-kicker type-kicker">Explore the universe</p>
        <h1 class="section-title type-title">Insurance market &amp; grid assets — scored separately</h1>
        <p class="section-lede type-lead type-lead--muted">Carriers, MGAs and brokers are insurance market participants. Data centres, wind, solar and BESS sites are <b>grid assets (L3)</b> — the underlying exposure carriers may cover, not insurers themselves. Click any card for the full profile.</p>
      </header>
      <div id="layer-scope-note" class="layer-scope-host" hidden></div>
      <div class="idx-toolbar idx-toolbar--explore" id="idx-toolbar">
        <input type="search" class="idx-search" id="idx-search" placeholder="Search insurers, MGAs, assets…" aria-label="Search entities">
        <span class="idx-filter-label">View</span>
        <button type="button" class="idx-btn on" data-t="layer" data-v="market">Market</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="all">All</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="1">Carriers</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="2">MGAs &amp; brokers</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="3">Assets</button>
        <button type="button" class="idx-btn" data-t="layer" data-v="4">Reinsurers</button>
        <span class="idx-filter-label">Quadrant</span>
        <button type="button" class="idx-btn on" data-t="quad" data-v="all">All</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="exposed">Exposed</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="whitespace">Whitespace</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="earning_it">Earning</button>
        <button type="button" class="idx-btn" data-t="quad" data-v="sidelined">Sidelined</button>
        <span class="idx-meta" id="idx-count"></span>
      </div>
      <div class="card-list card-list--explore" id="card-list"></div>
      <p class="explore-foot-note type-meta"><a href="index.html#rankings">Ranked table view</a> on the live index · <a href="index.html#universe">Scatter plot</a> · <a href="methodology.html">Methodology</a></p>
    </section>
  </div>
</main>

<footer class="site-foot">
  <div class="wrap"><!--__SITE_FOOT__--></div>
</footer>

<div id="scrim" onclick="closeAllPanels()"></div>
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
