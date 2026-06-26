# NFRI as a Product — modelling the space the way ai-transformation.fyi modelled PE

*Strategic companion to `METHODOLOGY.md` (method), `contract/MODEL_SPEC.md` (formalisation),
`DATA_ORCHESTRATION.md` (data triage). This note defines what we are building, why the space is
real and emerging, and how to present it: complex underneath, intelligible on the surface,
academic in its formalisation, thesis-driven in its framing.*

---

## 1. The reference pattern, abstracted

[ai-transformation.fyi](https://ai-transformation.fyi) (Felix Stocker & Jai Kondapalli) did four
things, in order, and that order *is* the product:

1. **Pick a population nobody had scored systematically** (PE portfolio companies).
2. **Encode a fuzzy-but-disciplined rubric in software** so it runs at scale ("Ben Graham with a
   Bloomberg terminal").
3. **Reduce each entity to a two-axis tension** (durability × opportunity) and a single derived
   number — the **Margin of Safety** — that ranks the field.
4. **Ship it clean, free, and downloadable**: the dataset *is* the artifact; the visualisation is
   the argument.

[doloop.energy](https://www.doloop.energy) supplies the second half: **ingest official sources,
rank by impact, separate "proposed" from an "in-force" register, and be explicit that AI summaries
are assistive, not authoritative.**

NFRI = (1) **non-firm power risk carriers**, an unscored population, scored by (2) a rubric encoded
in `harness/scoring.py`, reduced to (3) **Exposure × Preparedness → Margin of Safety**, ingested
from (doloop) official registers with an in-force regulatory rail, and shipped as a downloadable
index. The discipline that makes it defensible: **scoring is arithmetic in code, never an LLM
opinion**, and **no synthetic data** (`contract/DATA_POLICY.md`).

---

## 2. Why this is a real, *emerging* space (the justification)

Three forces converged in 2024–2026, and the insurance market is visibly repricing around them.
Every figure below is sourced in `contract/citations.json` and mapped in
`contract/knowledge/graph.json`.

**(a) The demand shock is structural, not cyclical.** UK grid-connection applications for data
centres reached ~50 GW against a ~45 GW national peak; the total demand queue grew to ~125 GW
(Ofgem CFI). ~32% of DC projects have no secured off-taker and ~81% are open to non-firm, phased
connection — i.e. they are *contractually* interruptible (`OFGEM-DEMAND-REFORM`, `ACAD-NONFIRM-REVIEW`).

**(b) The loss is non-damage, which legacy cover is least built for.** Power/supply failure is the
leading cause of data-centre outage (~45%, `ACAD-DC-OUTAGE`); the realisation is *interruption*,
not physical damage (`ACAD-CRI-GRID-SRI`). Conventional BI requires a damage trigger a curtailment
never pulls (`LMA-BI-GUIDE`) — the textbook definition of **basis risk** (`ACAD-BASIS-RISK-EXPECTILES`,
`ACAD-CLARKE-INDEX-DEMAND`).

**(c) The rulebook changed — and it is *in force*.** CMP434/435 Gate 1/2 (Jun 2025), CMP448
progression fee (Jan 2026), GC0166 limited-duration assets (Dec 2025) make "firmness" an objective
register fact, not an inference (`NESO-CMP434`, `NESO-CMP448`).

**The market response is the tell that this is emerging, not speculative.** In ~18 months: Marsh
**Nimbus** ($2.7bn DC facility, `BROK-MARSH-NIMBUS`), Aon **DCLP** ($3.5bn, `AON-DCLP`), WTW
**Digital Infrastructure Protector** (`BROK-WTW-DIP`); parametric DC products from **Parametrix**
(Lloyd's coverholder, SLA mirror, `MGA-PARAMETRIX-SLA`) and **Descartes** (up to $140M/policy,
`DESCARTES-DC-PARAMETRIC`); Munich Re **aiSure** performance guarantees (`MUNICHRE-GENAI-WP`); an
S&P-estimated **~$10bn premium runway** for hyperscale (`SP-HYPERSCALE-INSURABLE-POOL`) and a Swiss
Re **~$10bn single-event tail** on US DC (`SWISS-RE-DATA-CENTRE-AI`). New capacity is piling in
*before* anyone has scored who can actually carry the risk. That gap is the product.

**Why it correlates (the accumulation thesis).** AI compute and clean energy are financially
coupled — mean dynamic conditional correlation ~0.67, tightening under climate/financial-policy
shocks (`ACAD-AI-ENERGY-DCC`); finance↔grid is bidirectional (`ACAD-CRI-GRID-SRI`). So an insurer
writing renewable parametric *and* DC property is holding **one** correlated cluster, not two
diversified lines — exactly the aggregation a single grid-constraint event detonates (`LLOYDS-RDS`).

---

## 3. The thesis (one sentence, then the corollary)

> **Exposure** to non-firm power risk and **Preparedness** to underwrite it are orthogonal; the
> market is pricing capacity onto whoever *looks* exposed, but losses concentrate where exposure
> runs ahead of preparedness, while the genuinely capable sit in under-deployed **whitespace**.

Corollary the index exists to surface: a large negative **Margin of Safety = Preparedness −
Exposure** is a warning light — an entity accumulating non-firm risk faster than its data,
products and capital can support.

---

## 4. The formalisation (academic, but legible)

Full spec in `contract/MODEL_SPEC.md` + machine-readable `contract/risk_model.json`. The core moves:

- **Latent × deterministic fusion (credibility theory, Bühlmann–Gisler).** Each sub-factor has a
  research-derived latent rating `r_lat` and, where a register/filing permits, a deterministic
  rating `r_det`. The published rating is a precision-weighted blend
  `r_eff = clamp₀,₄(λ·r_det + (1−λ)·r_lat)`, with `λ` rising with evidence tier
  (measured 0.95 > derived 0.85 > disclosed 0.80 > assessed 0) and falling with low confidence.
  This is the formal answer to "how do we mix a register fact with a judgement without lying about
  either" — and it caps how far a latent prior can move a score when no measurement exists
  (the Strata/`CLAIMS-HISTORY-IMPORT` discipline).
- **Two axes as weighted anchored sums.** `E, P = (Σ wᵢ·r_eff,ᵢ / 4)·100` over five 0–4 anchored
  sub-factors each (`contract/rubric.json`).
- **Deterministic register maps.** `non_firm_intensity` = MW-weighted non-firm share from ECR/TEC;
  `aggregation_correlation` = Herfindahl index over grid geography (`ACT-HHI-EIOPA`);
  `capital_reinsurance` = FSR/SCR lookup; `pricing` framed as compound loss `E[L]=E[N]·E[S]`.
- **Relative calibration.** Quadrants use in-sample **median** cut-lines, not 50/50 — ranking
  relative firmness-risk, re-centring as the universe grows.
- **A systemic-risk horizon.** Che-Castaldo's CRI→SRI program (VAR/Granger over stacked indicators)
  is the academic frame for a future layer: entity sub-factors as CRIs, the universe as a network,
  correlated stress as shock propagation (`ACAD-CRI-GRID-SRI`, `sri-var-granger`).

Every formula cites a source; the verifier (`harness/verify_model_spec.py`, eval L8) enforces that
the citations resolve and that the knowledge base is actually wired into the machine model.

---

## 5. The presentation (data visualisation = the argument)

Four surfaces, matching reference + doloop, in build priority:

1. **The hero 2×2 scatter** — Exposure (x) × Preparedness (y), coloured by quadrant
   (earning-it / whitespace / exposed / sidelined), **dot size = confidence**, and an optional
   **opacity = measured/disclosed share** so the eye distinguishes *measured* dots from *assessed*
   ones. Median cut-lines drawn as axes. This single chart carries the thesis.
2. **The ranked Margin-of-Safety table** — sortable, with per-entity confidence and a latent vs
   deterministic decomposition (`scores.exposure_latent_0_100` / `_deterministic_0_100`) so a reader
   sees how much of a score is *measured* vs *assessed*.
3. **The in-force regulatory rail** (doloop) — CMP434/435, CMP448, GC0166, demand-flexibility SIs,
   each linked to the L3 records it re-prices; "what actually landed", not "what's proposed".
4. **The knowledge-graph explorer** — `contract/knowledge/graph.json` rendered as an interactive
   topic/citation network (topics → nodes → edges), so the evidence behind every sub-factor is one
   click from the score. This is the academic spine made browsable, and a differentiator the
   reference products don't have.

Plus **the downloadable dataset** (CSV + JSON, full inputs, sources, confidence, citations) — the
only one of its kind for this risk — and a short **thesis essay** landing §3.

**Honesty furniture (non-negotiable, from doloop):** every score links to its source; assessed
values are visibly marked; the publication gate (L5) is shown; anything below it is labelled
**PROVISIONAL**. The index never lets a striking number override its own confidence flag.

---

## 6. Intelligible-but-academic register — the writing rule

Surface text states the claim and the number in plain English; the formalism sits one layer down,
named and cited. E.g. *"Insurers writing both renewable parametric and data-centre property hold a
single correlated cluster (AI–energy correlation ≈ 0.67), not two diversified lines"* — then a
hover/footnote to `ACAD-AI-ENERGY-DCC` and the HHI/DCC formalism. Complex modelling, legible
delivery; academic rigour available on demand, never in the way.

---

## 7. Next iterations (product)

1. **Ship the static hero 2×2 + dataset** for the entities that clear L5; everything else PROVISIONAL.
2. **Wire the in-force rail** to live NESO/Ofgem/Elexon feeds (doloop cadence) so L3 firmness re-prices on register refresh.
3. **Render the knowledge graph** interactively from `graph.json` (already structured for it).
4. **Add the latent/deterministic decomposition** to every drill-down so "measured vs judged" is always visible.
5. **Prototype the SRI layer** (`sri-var-granger`) once the universe has register time-series — the genuinely novel, defensible-moat extension.

> The product is the contract + the dataset + the one chart that makes the thesis obvious. Build
> outward from there.
