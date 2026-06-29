"""Thesis page shell — on-non-firm-risk.html (Arena editorial layout)."""

THESIS_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>On Non-Firm Risk · The Non-Firm Power Insurance Risk Index · PRINCEPS</title>
<!--__FAVICON__-->
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<style>/*__SITE_CSS__*/</style>
</head>
<body class="site site--thesis">
<div class="arena-shell">
  <aside class="arena-sidebar" aria-label="Site navigation">
    <!--__THESIS_SIDEBAR__-->
  </aside>
  <div class="arena-stage">
    <!--__THESIS_HEADER__-->
    <main class="site-main">
      <article class="thesis-article">
        <!--__THESIS_BODY__-->
      </article>
    </main>
    <footer class="ref-band">
      <div class="wrap">
        <p class="ref-kicker type-kicker">Index</p>
        <p class="type-body"><a href="index.html">← Back to the live explorer</a> · Dataset and scatter on the main index.</p>
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
