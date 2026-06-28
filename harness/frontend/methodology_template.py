"""Methodology tab shell — methodology.html (Arena editorial layout)."""

METHODOLOGY_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Methodology · The Non-Firm Power Risk Index · PRINCEPS</title>
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<style>/*__SITE_CSS__*/</style>
</head>
<body class="site site--methodology">
<div class="arena-shell">
  <aside class="arena-sidebar" aria-label="Site navigation">
    <!--__METHODOLOGY_SIDEBAR__-->
  </aside>
  <div class="arena-stage">
    <!--__METHODOLOGY_HEADER__-->
    <main class="site-main">
      <article class="thesis-article">
        <!--__METHODOLOGY_BODY__-->
      </article>
    </main>
    <footer class="ref-band">
      <div class="wrap">
        <p class="ref-kicker type-kicker">Index</p>
        <p class="type-body"><a href="index.html">← Back to the live explorer</a> · Scatter, benchmark and entity drill-down on the main index.</p>
      </div>
    </footer>
    <footer class="site-foot">
      <div class="wrap"><!--__SITE_FOOT__--></div>
    </footer>
  </div>
</div>
<div id="scrim" onclick="closeDrawer()"></div>
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
