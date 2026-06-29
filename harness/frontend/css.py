"""Single CSS pipeline — see ARCHITECTURE.md."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import (  # noqa: E402
    css_variables,
    hero_css,
    motion_css,
    refs_css,
    shell_css,
    typography_css,
    visual_css,
)
from frontend.styles.analytical import analytical_css  # noqa: E402
from frontend.styles.explore import explore_css  # noqa: E402
from frontend.styles.brand_chrome import brand_chrome_css  # noqa: E402
from frontend.styles.essay_surface import essay_surface_css  # noqa: E402
from frontend.styles.index_layout import index_layout_css  # noqa: E402
from frontend.styles.arena_layout import arena_layout_css  # noqa: E402
from frontend.styles.section_tabs import section_tabs_css  # noqa: E402
from frontend.styles.ornn_header import ornn_header_css  # noqa: E402


def layout_css() -> str:
    """Site zones and section variants."""
    return r"""
  .site{min-height:100vh}
  .site-main{background:var(--bg-default)}
  section.section--prose,
  section.section--panel{scroll-margin-top:var(--sticky-offset)}
  section.section--panel:last-of-type{border-bottom:none}
  .prose{max-width:var(--essay-measure)}
"""


def render_site_css(ds: dict | None = None, *, prose_css: str = "") -> str:
    """One style block. Order is fixed in ARCHITECTURE.md."""
    return (
        css_variables(ds)
        + typography_css()
        + shell_css()
        + layout_css()
        + brand_chrome_css()
        + arena_layout_css()
        + index_layout_css()
        + section_tabs_css()
        + hero_css()
        + ornn_header_css()
        + refs_css()
        + analytical_css()
        + explore_css()
        + motion_css()
        + visual_css()
        + prose_css
        + essay_surface_css()
    )
