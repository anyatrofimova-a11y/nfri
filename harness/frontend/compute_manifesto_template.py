"""CMUI manifesto page shell — on-compute-markets.html (lightweight, no explorer JS)."""

COMPUTE_MANIFESTO_TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>On Compute Markets · CMUI · PRINCEPS</title>
<!--__FAVICON__-->
<link rel="stylesheet" href="/*__FONTS_URL__*/">
<style>/*__SITE_CSS__*/</style>
</head>
<body class="site site--compute-manifesto">
<div class="arena-shell">
  <aside class="arena-sidebar" aria-label="Site navigation">
    <!--__COMPUTE_SIDEBAR__-->
  </aside>
  <div class="arena-stage">
    <!--__COMPUTE_HEADER__-->
    <main class="site-main">
      <article class="thesis-article compute-manifesto">
        <!--__COMPUTE_BODY__-->
      </article>
    </main>
    <footer class="ref-band">
      <div class="wrap">
        <p class="ref-kicker type-kicker">CMUI</p>
        <p class="type-body"><a href="index.html">← NFRI live index</a> · <a href="data/compute_dataset.csv">Download scored slice</a></p>
      </div>
    </footer>
    <footer class="site-foot">
      <div class="wrap"><!--__SITE_FOOT__--></div>
    </footer>
  </div>
</div>
</body></html>"""
