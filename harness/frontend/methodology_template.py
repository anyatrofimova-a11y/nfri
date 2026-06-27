"""Methodology tab shell — methodology.html."""

METHODOLOGY_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Methodology · The Non-Firm Power Insurance Risk Index · PRINCEPS</title>
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<style>/*__SITE_CSS__*/</style>
</head>
<body class="site site--methodology">
<!--__METHODOLOGY_HEADER__-->
<main class="site-main">
  <div class="thesis-shell">
    <!--__METHODOLOGY_TOC__-->
    <article class="thesis-article">
      <!--__METHODOLOGY_BODY__-->
    </article>
  </div>
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
