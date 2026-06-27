# NFRI · Design source of truth

Princeps research index — not a SaaS landing page. The product is the dataset and the argument; the UI should read like a working paper with an interactive appendix.

## Aesthetic

**Institutional editorial.** Financial Times / Economist Intelligence / Brookings working paper — flat, ruled, typographic. Data panels are instruments, not marketing cards.

### Do

- Warm paper surfaces (`#F5F3EF` canvas, `#FFFFFF` panels)
- Hairline rules (`1px` `--line-subtle`) to separate sections
- One serif for display (Source Serif 4), one sans for UI (IBM Plex Sans)
- Navy (`--section-accent`) for links and structural emphasis
- Terracotta (`--accent`) only for kickers, key figures, and CTAs — never glow
- Monospace for metadata, gate stats, register IDs
- Quadrant colors are semantic only (scatter, pills, charts)

### Don't (vibecode anti-patterns)

- Dark grid-canvas heroes with wireframe SVGs
- Glassmorphism floating docks / pill nav bars
- Playfair Display + Inter pairing
- Uppercase letter-spaced pill kickers with borders
- Rounded white cards with drop shadows everywhere
- Hover lift + glow on static content
- Dual dark bands (hero + footer) framing a gray middle

## Typography

| Role | Family | Usage |
|------|--------|-------|
| Display | Source Serif 4 | H1, section titles, pull quotes, stat values |
| UI / body | IBM Plex Sans | Body, nav, labels, table text |
| Data | IBM Plex Mono | Gate stats, eval chips, reference indices |

Scale: body 15px / 1.6; display H1 clamp(2rem, 4vw, 2.75rem); section titles 1.5–1.75rem.

## Color

Tokens live in `contract/design_system.json`. CSS variables are emitted by `harness/design_system.py`.

## Layout

- Max width `1040px`, generous vertical rhythm (`--section-y: 64px`)
- Prose column `47rem`; panels full wrap width inside `.panel`
- Hero is **light masthead** inside the page — not a full-bleed dark gate

## Motion

- Scroll reveal only (`.reveal`), no decorative float loops
- `prefers-reduced-motion` disables all transitions

## Pipeline

```
contract/design_system.json → harness/design_system.py → harness/frontend/css.py
harness/build_essays.py (ESSAY_CSS) → prose block styles
harness/frontend/chrome.py → hero, nav, dock
python3 harness/build_frontend.py → site/index.html
```

Preview tokens/components: `site/design-system.html` or `/?v=design-system`.

## References (harmony, not copy)

- [AI Transformation Index](https://ai-transformation.fyi) — gray research surface, orange accent discipline
- [Vannevar](https://www.vannevarlabs.com) — institutional density
- Motion restraint only from [ORO](https://www.getoro.xyz) — no grid canvas

## Design agent handoff

When iterating with a design agent (Framer, gstack design, or manual review):

1. Read this file + `contract/design_system.json`
2. Preview at `http://localhost:8765/design-system.html` (component gallery) or live index
3. Propose token/CSS changes in the pipeline files above — never inline styles in `site/index.html`
4. Rebuild: `python3 harness/build_frontend.py`
