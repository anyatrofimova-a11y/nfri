# NFRI frontend skeleton

Single contract for the static site. All UI work follows this file — no ad-hoc CSS in templates, no parallel style stacks.

## Source of truth

| Layer | Location | Role |
|-------|----------|------|
| Tokens | `contract/design_system.json` | Colors, type, spacing, motion |
| Styles | `harness/design_system.py` + `harness/frontend/styles/` | CSS generators only |
| Chrome | `harness/frontend/chrome.py` | Brand, nav, hero gate, dock |
| Page shell | `harness/frontend/template.py` | HTML zones + section slots |
| Client | `harness/frontend/client.py` | One JS bundle, one init |
| Assembly | `harness/frontend/assemble.py` | Wires payload → `site/index.html` |
| Data | `harness/build_frontend.py` | Records, payload, essays — no presentation |

## Page map (fixed order)

```
┌─ zone-dark ─────────────────────────────────────────┐
│  gate-shell: sticky nav + hero                      │
└─────────────────────────────────────────────────────┘
┌─ site-main (gray canvas) ───────────────────────────┐
│  status-strip: gate banner · meta · downloads       │
│  section--prose: argument, analysis, findings,      │
│                  methodology, data                  │
│  section--panel: scatter, table, rail, evidence,    │
│                  method                             │
└─────────────────────────────────────────────────────┘
┌─ zone-dark ─────────────────────────────────────────┐
│  references band (card grid)                        │
└─────────────────────────────────────────────────────┘
  overlay: drawer · mobile dock
```

## HTML grammar

Every section uses one of two patterns:

**Prose** (essays from `build_essays.py`):

```html
<section id="…" class="section section--prose">
  <div class="prose"><!-- essay HTML --></div>
</section>
```

**Panel** (interactive / data):

```html
<section id="…" class="section section--panel reveal">
  <header class="section-head">
    <p class="section-kicker">…</p>
    <h2 class="section-title">…</h2>
    <p class="section-lede">…</p>
  </header>
  <div class="panel">…</div>
</section>
```

Dark zones use `zone-dark` + domain classes (`gate-shell`, `ref-band`). Never nest a dark band inside `site-main`.

## CSS pipeline (strict order)

`frontend/css.py` → `render_site_css()` emits **one** `<style>` block:

1. **Tokens** — `:root` from JSON
2. **Shell** — reset, `.site`, `.wrap`, `.section`, typography, brand (light)
3. **Zone dark** — hero gate, references band (shared grid canvas)
4. **Zone panel** — scatter, table, filters, rail, drawer, eval chips
5. **Evidence** — kg shell (index UI)
6. **Motion** — `.reveal`, `.stagger`, reduced-motion
7. **Chrome** — floating dock
8. **Prose** — essay styles from `build_essays.ESSAY_CSS`

Forbidden: inline `<style>` blocks in `template.py`, duplicate rules in `build_frontend.py`, new CSS outside this pipeline.

## Class vocabulary

| Use | Class | Not |
|-----|-------|-----|
| White bordered container | `.panel` | `.card` |
| Section title block | `.section-head` + `.section-title` | bare `<h2>` + `.sec-sub` |
| Filter chips | `.filter-bar` + `.filter-btn` | `.controls` + `button.on` |
| Status row | `.status-strip` | loose `.wrap` + `.banner` |
| Dark full-bleed | `.zone-dark` | mixing `#0e0e0e` and `#1e1b18` ad hoc |

## Client JS

Single IIFE bundle in `client.py`. Modules by comment region only (no build step):

- `motion` — IntersectionObserver for `.reveal` / `.stagger`
- `status` — publication banner
- `scatter` — plot SVG
- `table` — sortable MoS table + drawer open
- `drawer` — entity detail panel
- `rail` — in-force cards
- `evidence` — knowledge index
- `evals` — L0–L8 chips

Init: `initMotion()` once; feature inits at bottom; `observeMotion(document)` after DOM fills.

## Adding a section

1. Add slot comment to `template.py` in the correct zone
2. If panel: use `section--panel` + `section-head`; add CSS to `styles/analytical.py` if new primitives needed
3. If prose: render via `build_essays` and inject HTML only
4. Wire slot in `assemble.py`
5. Rebuild: `python3 harness/build_frontend.py`

## Visual intent

- **Dark instrument** — hero + references: one canvas (`--canvas-dark`), grid overlay, mono stats, white CTA
- **Gray research surface** — `--bg-emphasis` main; panels are `--bg-default` with `--line-subtle` borders
- **Prose** — narrow `prose` column (~47rem), Playfair display headings, orange kickers sparingly
- **Motion** — scroll reveal only; no decorative animation on data
