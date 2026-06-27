# Entity profiles — carrier depth (ai-transformation.fyi pattern)

How ai-transformation.fyi treats a **PE fund** or **portfolio company**, what NFRI ships today, and the build contract for **per-carrier profiles** that expand on click into a page worth sharing.

Reference: [ai-transformation.fyi/funds](https://ai-transformation.fyi/funds) (fund cards), [on-transformation](https://ai-transformation.fyi/on-transformation) (firm-level swarm + portfolio split), NFRI `PRODUCT_MODEL.md` §5.

---

## 1. What the reference does (abstracted)

### Index surface (funds / companies)

Each **fund card** is a self-contained summary — not a table row:

| Field | PE fund card | NFRI carrier analogue |
|-------|----------------|------------------------|
| Identity | Fund name, AUM | Carrier / syndicate / MGA name, parent group, Lloyd's # |
| Universe size | N companies, N deal partners | N linked assets, N product lines, book segments |
| Axis scores | Durability 64 · Opportunity 52 | Exposure 46 · Preparedness 80 |
| Derived metric | Margin of Safety (dur − opp) | MoS (prep − exp) |
| Distribution | Min / Avg / Max AI score across portfolio | Min / Avg / Max MoS across linked L3 assets |
| Drill-down | Click → firm profile + portfolio swarm | Click → carrier profile + asset swarm |

Each **company profile** (opened from scatter, table, or on-transformation dot) carries:

- Full D1–D5 / O1–O4 sub-scores with **named definitions**
- Rationale per sub-factor (not truncated)
- Public comp linkage (their external validation layer)
- Sponsor / vertical context

### On-transformation firm-level block

The `/on-transformation` **FIRM-LEVEL DATA** section adds three viz primitives NFRI should mirror for **carriers**:

1. **Firm MoS vs outcome scatter** — 95 funds, dot size = portfolio size, R² annotated inline.
2. **Portfolio swarm** — one dot per portfolio company on a MoS axis; dashed line = firm average; **click dot → company profile**.
3. **Stacked quadrant split** — top 50 firms, bars = % Star / Fortress / Hail Mary / Cooked.

NFRI mapping:

| PE (reference) | NFRI |
|----------------|------|
| Fund | L1 carrier / syndicate / reinsurer |
| Portfolio company | L3 asset (data centre, BESS, solar) linked via `asset_link` or broker placement |
| Vertical (Insurance −9.7 MoS) | Entity type or book segment (renewable MGA, DC property, parametric) |
| Public comp 6M return | Measured share, or disclosed energy GWP share, or gate-status severity |
| Star / Fortress / Hail Mary / Cooked | earning_it / whitespace / sidelined / exposed |

---

## 2. What NFRI ships today (gap)

| Capability | Today | Gap |
|------------|-------|-----|
| Click target | `#drawer` overlay (`client.py` `openDrawer`) | No URL, no full page, no share link |
| Payload | `build_points()` → `D.pts[]` | Rationale capped 320 chars; 3 sources; `note` capped 240; no `asset_link`, no `measured_value` |
| Decomposition | `expLat` / `expDet` in drawer | Often **null** — `scores.blend` stripped in `records.optimized.json` |
| Citations | `citePop()` → `alert()` | Should use foundations / KG detail panel |
| Search / cards | Not built | `manifesto.json` Part I promises "cards, scatter, table" |
| Multi-page | Single `site/index.html` | No `/carrier/{id}` or `#/entity/{id}` |

The drawer HTML structure is **correct** (score row → axis decomp → 10 sub-factor cards). The problem is **payload depth** and **surface area** (overlay vs profile page).

---

## 3. Target UX — carrier profile

### Entry points (all route to same profile)

- Scatter dot click
- Table row click
- Card click (future carrier grid)
- Hash URL: `index.html#/carrier/beazley` (phase 1) → `carrier/beazley.html` (phase 2)
- Cross-link from on-transformation swarm chart

### Profile layout (zones)

```
┌─ profile-hero (zone-dark mini) ────────────────────────┐
│  Beazley · Lloyd's syndicate · Beazley plc             │
│  MoS +33.8 · Whitespace · confidence medium · 12% meas │
│  [Dataset row ↓] [Open in scatter]                     │
└────────────────────────────────────────────────────────┘
┌─ profile-main ─────────────────────────────────────────┐
│  § Score summary (4-up + quadrant badge)               │
│  § Axis decomposition (latent vs deterministic bars)   │
│  § Exposure sub-factors (5 cards, full text)           │
│  § Preparedness sub-factors (5 cards)                  │
│  § Portfolio / assets (swarm or table) — L1 only       │
│  § Products & placements (chips → KG nodes)            │
│  § Provenance (researched_by, last_checked, method)    │
│  § Related sources (KG neighborhood)                   │
└────────────────────────────────────────────────────────┘
```

### Sub-factor card (full depth — reference company page bar)

Each card must expose everything in `records.scored.json`:

```json
{
  "key": "non_firm_intensity",
  "label": "Non-firm intensity",
  "weight": 0.22,
  "lat": 2, "det": 3, "eff": 2.85,
  "mode": "fusion", "lambda": 0.85,
  "tier": "derived", "conf": "medium",
  "rationale": "<full text, not truncated>",
  "measured_value": "42% flexible connections (ECR)",
  "sources": ["<all URLs>"],
  "cites": ["OFGEM-DEMAND-REFORM", "..."],
  "evidence": [{ "field": "...", "value": "...", "source": "..." }]
}
```

### L3 asset profiles (extra blocks)

When `entity_type` ∈ {data_centre, battery, solar, …}:

- Register facts: MW, gate, connection type, DNO, constraint zone
- Map pin or constraint-zone label (static SVG, no API key phase 1)
- **Linked carriers** table (who writes this asset's risk)

### L1 carrier profiles (extra blocks — the PE fund analog)

- **Asset swarm chart** — dots = linked L3 entities on MoS axis; dashed = carrier average
- **Book concentration** — disclosed segment GWP when present (`book_inputs.json`)
- **Quadrant stack** — % of linked assets in each quadrant
- **Product rail** — Nimbus / DCLP / Parametrix / kWh Analytics chips when KG links exist

---

## 4. Data contract

### Phase 1 — enrich inline payload (minimal build change)

Extend `build_points()` → rename to `build_entity_summaries()` for scatter/table; add `build_entity_profiles()`:

```python
# harness/build_frontend.py
def build_entity_profiles(records):
    """Full-fidelity profiles keyed by entity_id. Source: records.scored.json (blend intact)."""
```

Output: `site/data/profiles.json` (or split `site/data/profiles/{id}.json` when >2MB).

**Rule:** profiles are built from **`records.scored.json`**, not optimized — blend, latent/det axis scores, and `provenance.evidence` must survive.

Scatter/table keep a **slim** `pts[]` slice; profiles are loaded on demand:

```javascript
async function openProfile(id) {
  const p = D.pts.find(x => x.id === id);
  const full = D.profiles?.[id] || await fetch(`data/profiles/${id}.json`).then(r => r.json());
  // render...
  history.pushState(null, '', `#/carrier/${id}`);
}
```

### Phase 2 — static HTML per carrier (SEO / share)

`harness/build_entity_pages.py` → `site/carrier/{entity_id}.html`

- Reuses profile template + embeds one profile JSON inline
- `<link rel="canonical">` from index
- Sitemap entry per L1 entity

### Fix: blend survival in optimize

`records.optimized.json` currently drops `scores.blend` and axis latent/det fields. Either:

- Preserve blend in optimize (preferred), or
- Always build profiles from scored source (document in RUNBOOK)

---

## 5. Client modules (add to `client.py`)

| Module | Responsibility |
|--------|----------------|
| `router` | Parse `#/carrier/:id`, `#/asset/:id`; back/forward |
| `profile` | Render full profile from fat payload; replace drawer for L1/L2 |
| `profile-charts` | Axis decomp bars, asset swarm (SVG, same grammar as scatter) |
| `cite-panel` | Reuse KG detail renderer for `citePop` — no alerts |

Drawer remains for **quick peek** on mobile; desktop click opens profile panel (full-width overlay) or navigates to hash route.

---

## 6. Carrier index grid (Part I — manifesto promise)

Before profiles, add **search + cards** on index (reference `/funds`):

```
/filter-bar: layer · type · quadrant · measured-only
/search: fuse name + parent + notes
/card-grid: sorted by |MoS| or name
  each card: name, type, exp, prep, mos, quad, meas%, conf
  mini sparkline: 5 exposure weights (optional phase 2)
```

Cards and table share `D.pts[]`; cards are the **discovery** surface, table the **ranking** surface, scatter the **thesis** surface.

---

## 7. Build checklist

- [ ] Preserve `blend` + axis decomp in scored → site pipeline
- [ ] `build_entity_profiles()` → `site/data/profiles.json`
- [ ] Remove 320-char rationale cap in profiles (keep cap in scatter hover only)
- [ ] `openProfile()` + hash router; table/scatter/card click → profile
- [ ] Asset swarm for carriers with `asset_link` edges (from records or `contract/links.json`)
- [ ] Replace `citePop` alert with KG citation drawer
- [ ] Carrier card grid + search (`#index-cards` section in template)
- [ ] Static `site/carrier/*.html` (phase 2)
- [ ] Wire on-transformation swarm clicks → profile routes

---

## 8. Content ownership

| Artifact | Owner |
|----------|-------|
| Sub-factor rationales, sources | `data/records.scored.json` (research pipeline) |
| Labels, weights | `contract/rubric.json` |
| Product / placement chips | `contract/knowledge/graph.json` edges |
| Book disclosed shares | `contract/book_inputs.json` |
| Profile copy (hero tagline) | optional `contract/entity_copy.json` overrides |

No hand-edited HTML. Profiles are **pure projection** of records + contract.
