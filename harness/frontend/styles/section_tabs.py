"""Persistent section tabs — editorial text nav (felixstocker.com register)."""


def section_tabs_css() -> str:
    return r"""
  :root{--nav-tabs-h:46px}
  .section-tabs{
    display:flex;align-items:center;gap:var(--space-md);
    overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;
    margin:0;padding:10px 0;list-style:none;
  }
  .section-tabs::-webkit-scrollbar{display:none}
  .section-tab{
    flex:0 0 auto;padding:4px 0;
    font-family:var(--font-nav);font-size:var(--type-nav);font-weight:400;
    line-height:var(--type-nav-lead);color:var(--ink2);text-decoration:none;
    white-space:nowrap;border:none;border-radius:0;background:transparent;
    transition:color .2s ease, box-shadow .2s ease;
  }
  .section-tab:hover{
    color:var(--ink-headline);text-decoration:none;background:transparent;
  }
  .section-tab.on{
    color:var(--ink-headline);font-weight:500;background:transparent;
    box-shadow:inset 0 -1px 0 var(--ink-headline);
  }
  .section-tab.on:hover{color:var(--ink-headline)}
  .section-tabs--sidebar{
    flex-direction:column;align-items:stretch;gap:1px;
    overflow:visible;padding:0;margin:0;
  }
  .section-tabs--sidebar .section-tab{
    padding:3px 0;font-family:var(--font-sans);font-size:0.8125rem;
    box-shadow:none;
  }
  .section-tabs--sidebar .section-tab.on{
    font-weight:500;box-shadow:none;
  }
  @media(max-width:720px){
    .section-tabs{gap:var(--space-sm)}
    .section-tab{font-size:1rem}
  }
"""
