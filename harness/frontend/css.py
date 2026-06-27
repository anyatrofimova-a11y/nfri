"""Single CSS pipeline — see ARCHITECTURE.md."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import (  # noqa: E402
    css_variables,
    hero_css,
    kg_css,
    motion_css,
    refs_css,
    shell_css,
    typography_css,
    visual_css,
)
from frontend.styles.analytical import analytical_css  # noqa: E402
from frontend.styles.explore import explore_css  # noqa: E402


def layout_css() -> str:
    """Site zones and section variants."""
    return r"""
  .site{min-height:100vh}
  .site-main{background:var(--bg-emphasis)}
  section.section--prose{padding:40px 0 38px;border-bottom:1px solid var(--line-subtle);scroll-margin-top:calc(var(--header-h) + 12px)}
  section.section--panel{padding:var(--section-y) 0;border-bottom:1px solid var(--line-subtle);scroll-margin-top:calc(var(--header-h) + 12px)}
  section.section--panel:last-of-type{border-bottom:none}
  .prose{max-width:47rem}
  #knowledge.section--panel{border-bottom:none}
"""


def render_site_css(ds: dict | None = None, *, prose_css: str = "") -> str:
    """One style block. Order is fixed in ARCHITECTURE.md."""
    return (
        css_variables(ds)
        + typography_css()
        + shell_css()
        + layout_css()
        + hero_css()
        + refs_css()
        + kg_css()
        + analytical_css()
        + explore_css()
        + motion_css()
        + visual_css()
        + prose_css
    )
