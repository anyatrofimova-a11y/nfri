---
name: nfri-design-review
description: Run Gary Tan / gstack-aligned design review on NFRI surfaces. Use before shipping index, design-system, or essay layout changes; when invoking gstack plan-design-review or design-review; or when auditing for vibecode / AI-slop drift.
---

# NFRI design review

Principles are stored in `contract/design_principles.json` (Gary Tan core + gstack
`plan-design-review` mapping). Visual tokens live in `contract/design_system.json`.
Aesthetic rules in `DESIGN.md`.

## Gary Tan core (apply on every review)

1. **Empathize** — Simulate a reader with zero methodology context. Where do they stall?
2. **Illuminate** — Scan order: kicker → display → lead → instruments. Copy is UI.
3. **Minimize** — Subtraction default. Cut chrome that doesn't serve dataset or argument.
4. **Create** — Contrast + closeness: group related controls (`.filter-seg`), rule panels flat.
5. **Sand edges** — Sharp edges = places users misunderstand coverage, tiers, or filters.

Extended: progressive disclosure (drawer/essays, not hero dump), show examples
(`design-system.html`), trust at pixel level (honest gate, no synthetic stats).

## gstack bridge

When running gstack **`/plan-design-review`** or **`/design-review`** on NFRI:

1. Confirm target: live index (`/?v=design-system`), `site/design-system.html`, or essay page.
2. Read `DESIGN.md` + `contract/design_principles.json` + `contract/design_system.json`.
3. Map every finding to a principle id (`illuminate`, `minimize`, gstack #5, etc.) — no
   unprincipled "feels off."
4. Propose changes in pipeline files only (`harness/frontend/*`, `build_essays.py`,
   `design_system.json`) — never hand-edit generated `site/index.html`.
5. Rebuild: `python3 harness/build_frontend.py`

## NFRI-specific anti-patterns (Gary Tan "minimize" + gstack #5)

Reject on sight:

- Dark grid-canvas heroes, glass docks, pill nav, filled black filter pills
- Rounded shadow cards for static stats, hover lift/glow on prose
- Playfair + Inter, uppercase letter-spaced logotypes
- Marketing hero above the dataset; dual dark hero + footer bands

Prefer:

- Light masthead, Princeps/NFRI lockup, segmented filters, flat `.panel`, hairline rules
- Terracotta kickers only; navy structural links; semantic scatter colors only

## Three-agent pass (manual or parallel)

| Agent | Reads | Checks |
|-------|-------|--------|
| Tokens | `design_system.json`, `design-system.html` | Scale, color discipline, components |
| Editorial | `DESIGN.md`, essay CSS | Institutional tone, no vibecode |
| Live | `http://localhost:8765/?v=design-system` | Scan hierarchy, gate honesty, filter UX |

## Verify

```bash
python3 harness/build_frontend.py
python3 -m http.server 8765 --directory site
# open http://localhost:8765/?v=design-system
```

## Seed gstack project learnings (optional, once per machine)

`contract/design_principles.json` includes `gstack_learnings_seed` entries for
`~/.gstack/projects/<slug>/learnings.jsonl`:

```bash
BIN=~/.claude/skills/gstack/bin/gstack-learnings-log
python3 -c "
import json, subprocess
for row in json.load(open('contract/design_principles.json'))['gstack_learnings_seed']:
    subprocess.run(['$BIN', json.dumps(row)], check=True)
"
```
