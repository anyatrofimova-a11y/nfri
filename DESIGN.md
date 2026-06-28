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
- Filled pill toggles (filters use segmented `.filter-seg` controls)
- Rounded white cards with drop shadows everywhere
- Hover lift + glow on static content
- Dual dark bands (hero + footer) framing a gray middle

## Typography

Unified scale in `contract/design_system.json` → CSS vars `--type-*` → utility classes `.type-kicker`, `.type-display`, `.type-title`, `.type-lead`, `.type-body`, `.type-meta`.

| Role | Class | Family | Usage |
|------|-------|--------|-------|
| Kicker | `.type-kicker` | IBM Plex Mono | Section labels, metadata rails — terracotta, uppercase |
| Display | `.type-display` | Source Serif 4 | Page H1 (hero) only |
| Title | `.type-title` | Source Serif 4 | Section H2, essay `.arg-h` |
| Lead | `.type-lead` | IBM Plex Sans | Hero lede, section intro, essay lead |
| Body | `.type-body` | IBM Plex Sans | Prose paragraphs, nav, UI |
| Meta | `.type-meta` | IBM Plex Mono | Gate stats, register IDs, footnote indices |

Brand lockup: **PRINCEPS** (serif, all caps) over **NFRI** (mono acronym).

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

## Gary Tan principles (via gstack)

Stored in `contract/design_principles.json`. These are Garry Tan's startup-design
framework, bridged through gstack `plan-design-review` and mapped to this index.

| Principle | NFRI application |
|-----------|------------------|
| **Empathize** | Reader has no insider context — gate, kickers, and axes must explain state alone |
| **Illuminate the path** | Kicker → display → lead → instruments; copy is UI (provisional banner, section labels) |
| **Minimize** | Subtraction default — flat panels, no chartjunk; see Don't list above |
| **Create** | Contrast + closeness — `.filter-seg` groups, ruled stat grids, semantic scatter colors only |
| **Copy is UI** | Hero lede and drawer labels stand alone; no "as you know" |
| **Progressive disclosure** | Summary on index; methodology and record detail in drawer/essays |
| **Trust at pixel level** | Honest gate from `authoritative_share`; provisional tiers labeled (gstack #9) |

gstack Design Principles 1–9 in the same file. Review skill: `skills/nfri-design-review/SKILL.md`.
Invoke gstack `/plan-design-review` with those artifacts as the review target.

## Princeps brand alignment (princeps.dev)

NFRI is a **research product** under Princeps — not a separate brand. The triquetra mark
(`assets/princeps-triquetra.png`) and **Princeps / NFRI** lockup should anchor trust the way
[princeps.dev](https://princeps.dev) does: first, foremost, principal — without turning the
index into a startup landing page.

| Surface | Today | Closer to princeps.dev |
|---------|--------|-------------------------|
| **Header / dock** | Triquetra + text lockup | Keep — this is correct editorial chrome |
| **Footer (`ref-band`)** | References only, no mark | Add `.foot-brand`: triquetra + “Princeps” + link to princeps.dev; NFRI as product line below |
| **Welcome modal** | CSS exists (`.welcome-brand`) but unused | Lead with lockup before title — first touch should feel Princeps-hosted |
| **Thesis / methodology footers** | Back link only | Same foot colophon on every page (consistency = trust) |
| **Hero masthead** | Text-only kicker | Optional larger mark beside kicker (40px `.brand-mark.lg`) — one beat, not a logo billboard |
| **Attribution copy** | Scattered “Princeps Research” | Use `design_system.json` → `brand.tagline` / `attribution` everywhere metadata appears |
| **External link** | None to princeps.dev | Footer + `<meta>` / JSON-LD publisher — signals index is published research, not orphan microsite |

**Do not** import princeps.dev’s full-bleed “POWERING THE WORLD” hero — that is company marketing.
**Do** reuse triquetra, publisher name, and footer colophon so the index reads as Princeps research
(Gary Tan: copy is UI; gstack #9 trust at pixel level).

Pipeline: `render_brand()` in `harness/frontend/chrome.py`; add `render_footer_brand()` for footers;
tokens in `contract/design_system.json` → `brand.*`.

## Design agent handoff

When iterating with a design agent (Framer, gstack design, or manual review):

1. Read this file + `contract/design_system.json` + `contract/design_principles.json`
2. Preview at `http://localhost:8765/design-system.html` (component gallery) or live index
3. Propose token/CSS changes in the pipeline files above — never inline styles in `site/index.html`
4. Map findings to a named principle (Gary Tan or gstack #) before changing
5. Rebuild: `python3 harness/build_frontend.py`
