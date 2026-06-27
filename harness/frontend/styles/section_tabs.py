"""Persistent section tabs — top-of-page navigation."""


def section_tabs_css() -> str:
    return r"""
  :root{--nav-tabs-h:44px}
  .section-tabs{
    display:flex;align-items:stretch;gap:2px;
    overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;
    margin:0;padding:6px 0;list-style:none;
  }
  .section-tabs::-webkit-scrollbar{display:none}
  .section-tab{
    flex:0 0 auto;padding:8px 14px;border-radius:var(--radius-sm);
    font-size:13px;font-weight:500;color:var(--ink2);text-decoration:none;
    white-space:nowrap;font-family:var(--font-sans);border:1px solid transparent;
    transition:background .2s ease,color .2s ease,border-color .2s ease;
  }
  .section-tab:hover{
    background:var(--bg-default);color:var(--ink);text-decoration:none;
    border-color:var(--line-subtle);
  }
  .section-tab.on{
    background:var(--accent);color:#fff;border-color:var(--accent);
  }
  .section-tab.on:hover{background:var(--ink);border-color:var(--ink);color:#fff}
  @media(max-width:720px){
    .section-tab{padding:7px 12px;font-size:12px}
  }
"""
