# The Non-Firm Power Risk Index — Methodology & Data Harness

*A rigorous, reproducible method for scoring the UK insurance-market participants exposed to interruptible-power risk across energy assets and data centres.*

**Draft v0.3 · June 2026**
Modelled on the approach behind [ai-transformation.fyi](https://ai-transformation.fyi) (Felix Stocker & Jai Kondapalli) and the data-presentation discipline of [doloop.energy](https://www.doloop.energy).

> **v0.3 adds:** a hard **no-synthetic-data rule** with enforced evidence tiers (`contract/DATA_POLICY.md`), a measured **feature dictionary** mapping every sub-factor to a primary source (`contract/feature_dictionary.md`), real **ingestion adapters** for NESO and the DNO Embedded Capacity Registers (`harness/adapters.py`), an expanded **57-entity universe** (`contract/universe.seed.v2.json`), and an **eval harness at every level** (`harness/evals.py`). The 15-entity prototype is honestly graded **assessed-tier / PROVISIONAL** (2% measured) until re-based on measured features.

---

## 0. One-paragraph summary

The UK is connecting its most capital-intensive new infrastructure — hyperscale and AI data centres, and the generation behind them — on terms that are increasingly **not firm**: interruptible, curtailable, or contingent on a grid-connection queue that holds ~50 GW of data-centre demand against a ~45 GW national peak. The financial consequences of a curtailment land as breached SLAs and lost revenue, not physical damage — exactly the losses conventional insurance is least built for. Nobody has scored, end to end, **who carries this risk and who is actually equipped to underwrite it.** This document defines how we build that index: a typed data contract, a five-layer data universe fed from official registers, a two-axis scoring model (**Exposure vs Preparedness**, yielding a **Margin of Safety**), and a multi-agent harness whose defining feature is a set of explicit **loops** that ingest, research, score, adversarially validate, and continuously optimise the data. It is an outside-in estimate, transparent about confidence and provenance — assistive, not authoritative.

---

## 1. The premise and the method

### 1.1 What we are copying, and why it works

ai-transformation.fyi made one powerful move: take a population nobody had scored systematically (private-equity portfolio companies), define a *fuzzy but disciplined* rubric, then use AI research tools to score all ~5,000 of them and ship a clean, free, downloadable index. The headline was a **two-axis tension** — durability vs opportunity — and a derived *Margin of Safety* (durability − opportunity) that mapped surprisingly well onto public-market returns. The methodological unlock was encoding the rubric in software (via Claude Code) so it could run massively in parallel — "like giving Ben Graham a Bloomberg terminal."

doloop.energy adds the second half of the recipe: **how to present a living regulatory/data product.** It ingests GB energy publications daily via official APIs (Ofgem, NESO, DESNZ, Elexon), runs AI analysis to **rank every item by impact**, and — critically — separates *what is proposed* from an **"in force" register of what actually landed**, "the smaller, higher-signal set." It is explicit about its sources and equally explicit that "AI-generated summaries and impact scores are assistive, not authoritative."

We combine the two: ai-transformation.fyi's **scoring-an-unscored-population** with doloop's **official-source ingestion, impact ranking, in-force discipline, and provenance honesty.**

### 1.2 Why non-firm power risk, now

Three facts make this the right population at the right time:

1. **The queue.** UK grid-connection applications for data centres reached ~50 GW across ~140 facilities; the demand pipeline grew from 41 GW (Nov 2024) to ~125 GW (Jun 2025), with some sites facing 15-year waits.
2. **The rules changed.** Connections Reform is *in force*, not proposed: **CMP434/CMP435 "Implementing Connections Reform"** (in force 10 Jun 2025) introduced the Gate 1/Gate 2 readiness regime; **CMP448 "Progression Commitment Fee to the Gate 2 Connections Queue"** (in force 2 Jan 2026) hardened it; **GC0166 "Balancing Mechanism Parameters for Limited Duration Assets"** (in force 5 Dec 2025) governs how flexible/battery assets are dispatched. DESNZ is separately consulting on *mandatory demand flexibility* — the right to curtail very large users during system stress.
3. **The insurance mismatch.** Power supply causes ~45% of data-centre outages, yet conventional business-interruption cover is anchored to a physical-damage trigger a curtailment never pulls. That gap is where some underwriters quietly accumulate ruinous, correlated aggregation and others build the parametric/availability products that actually fit.

### 1.3 The thesis we score

> **Exposure** (how much non-firm power risk an entity carries) **vs Preparedness** (how well-equipped it is to carry it). The headline number is **Margin of Safety = Preparedness − Exposure.** The market is piling capacity onto whichever participants *look* exposed; but exposure without preparedness is where losses concentrate, while prepared-but-under-deployed players hold the real whitespace.

---

## 2. The data universe: five layers

ai-transformation.fyi scored one entity type with one nested layer. Our risk lives across a value chain *and* a rulebook, so we score **four entity layers plus a fifth "rules" feed** that re-prices the others when regulation changes (the doloop contribution).

| Layer | Who | Why in scope | First-run status |
|---|---|---|---|
| **L1 — Carriers & syndicates** | Insurers, Lloyd's syndicates writing energy/property/power/specialty | The balance sheets ultimately holding the risk; the primary unit of the index | 6 entities scored |
| **L2 — MGAs & brokers** | Coverholders/MGAs and specialty brokers placing the risk | Where product innovation and risk selection happen at the coalface | 5 entities scored |
| **L3 — Assets / projects** | UK data centres & energy assets in the connection pipeline | The underlying exposure; their firmness status drives everyone else's score | 4 entities scored |
| **L4 — Capacity & reinsurance** | Reinsurers, ILS, parametric capacity providers | Where tail risk is ceded; who survives a correlated event | deferred to scale-up |
| **L5 — Rules feed** *(doloop-style)* | In-force CUSC/Grid Code modifications, SIs, NESO/Ofgem/DESNZ decisions | Defines what "firm" legally means; re-scores L3 when Gate/curtailment terms change | design specified below |

**Layer 3 is the keystone.** Each asset's firmness status (firm / Gate 1 / Gate 2 / non-firm) is, post-CMP434, an *objective register fact* rather than an inference. Asset-level non-firm intensity then **propagates upward**: an insurer's Exposure is, in part, the weighted firmness of the assets it is known to cover.

**Layer 5 is what makes the index live.** When `CMP448` raised the cost of holding a Gate-2 queue place, or `GC0166` changed how limited-duration assets are dispatched, every L3 firmness assessment that depended on those terms is now stale. The rules feed watches the in-force register and **flags affected records for re-scoring** — exactly doloop's "what actually landed" discipline, wired into our scoring loop.

---

## 3. Data access points

Following doloop's lead, we lean on free, official, structured sources first and use LLM research only to fill qualitative gaps. Every datapoint carries its source.

| Source | Access point | What we extract | Feeds |
|---|---|---|---|
| **NESO TEC register** | Data Portal (machine-readable, refreshed ~twice weekly; "Gate" column since 21 Nov 2025) | Project list, MW, connection date, Gate 1/2 & firmness, location | L3; non-firm intensity; aggregation geography |
| **NESO connections registry & constraint data** | Data Portal; Modification Tracker (CUSC/Grid Code) | Curtailment/constraint costs by region; queue position | L3 curtailment prob; **L5** |
| **DNO Embedded Capacity Registers** | Opendatasoft v2.1 APIs: UK Power Networks, SSEN, Northern Powergrid (national combine), NGED | ≥1MW generation/storage/**flexible demand**: import/export MW, connection status, technology, **flexibility-service flag** | **non_firm_intensity (measured)**; aggregation geography |
| **Ofgem** | GOV.UK publications, Citizen Space, Daily Update | Decisions, charging methodology, code approvals | **L5**; cost/charge context |
| **DESNZ** | GOV.UK publications, Citizen Space, email alerts | Strategic demand policy, demand-flexibility consultations | **L5** |
| **Elexon** | BSC Change Register (weekly), RSS | Settlement/metering changes affecting availability | **L5** |
| **Companies House** | Filing API | Filed accounts, group structure, directors for UK insurers/MGAs/brokers | L1–L2 financials; book proxies |
| **FCA / PRA** | Financial Services Register | Authorisations, permissions, MGA/coverholder status | Universe construction; regulatory readiness |
| **Lloyd's / LMA / MGAA** | Market directory; membership lists | Syndicate, managing-agent, coverholder lists; class permissions | L1, L2, L4 |
| **Financials & ratings** | Syndicate results, listed-(re)insurer filings, AM Best/S&P | Loss/combined ratios, reserves, capacity, ratings | Preparedness (capital); §7 validation |
| **Trade press / company sites** | LLM-researched, source-captured | Product launches, hires, stated appetite | Qualitative scoring (product fit, expertise) |

The UK is unusually generous here: FCA-regulated intermediaries disclose on Companies House "far beyond anything an American company would be willing to make public," and the grid is a public dataset. **Discipline rule (from both references):** any field we cannot obtain for the whole population, or cannot verify, is *excluded from scoring* and shown at most as a flagged, low-confidence value.

---

## 4. The contract: one typed record

The contract is the product, not the agents. A single JSON Schema (`contract/entity.schema.json`) defines the record every agent reads and writes; agents are interchangeable workers. Key properties:

- **Identity** — `entity_id`, `name`, `layer`, `entity_type`, `parent_group`, `regulator_ids` (FCA FRN, Lloyd's ID, Companies House).
- **`exposure_inputs`** and **`preparedness_inputs`** — five sub-factors each, every sub-factor an object: `{ rating_0_4, rationale, sources[], confidence }`. *Ratings ≥ 1 must carry ≥ 1 source* (validator-enforced).
- **`asset_link`** (L3 / covering carriers) — `gate_status` ∈ {firm, gate_1, gate_2, non_firm, unknown}, `curtailment_exposure`, `backup_generation`, `covered_assets[]`.
- **`provenance`** — `researched_by`, `last_checked` (snapshot date), `method` ∈ {register, filing, llm_research, mixed}.
- **`scores`** — written by the scorer *only*: `exposure_0_100`, `preparedness_0_100`, `margin_of_safety`, `quadrant`, `overall_confidence`, `calibration`.

The hard rule that makes the index defensible: **scoring is computed in code, never by an LLM.** Agents *extract* fields and *rate* qualitative sub-factors against fixed anchors; the weighted arithmetic, quadrant assignment and Margin of Safety are deterministic and reproducible.

---

## 5. Scoring methodology

### 5.1 The two axes

Each entity is scored 0–100 on two orthogonal axes. Each axis is a weighted sum of five sub-factors, each rated on a 0–4 anchored scale (`contract/rubric.json`). **Axis score = (Σ wᵢ · ratingᵢ / 4) × 100.**

**Exposure** — *the size of the bet*

| Sub-factor | Weight | Captures |
|---|---|---|
| Book concentration | 0.30 | Share of the relevant book in UK power/energy/data-centre infrastructure |
| Non-firm intensity | 0.25 | Proportion of assets on non-firm / Gate-1 / interruptible connections |
| Aggregation / correlation | 0.20 | Vulnerability to one grid/curtailment event hitting many insureds |
| Trigger gap | 0.15 | Reliance on legacy physical-damage triggers against non-damage/SLA losses |
| Tenor mismatch | 0.10 | Long-dated cover written against a thin claims history |

**Preparedness** — *the ability to carry it well*

| Sub-factor | Weight | Captures |
|---|---|---|
| Data & monitoring | 0.25 | Availability/curtailment telemetry and loss data to price the risk |
| Product fit | 0.20 | Parametric / availability-trigger / non-damage BI vs off-the-shelf property/BI |
| Underwriting expertise | 0.20 | Specialist energy-plus-technology talent spanning power and cyber/tech |
| Capital & reinsurance | 0.20 | Depth/stability of capacity and reinsurance behind the line |
| Pricing & modelling | 0.15 | Sophistication modelling curtailment probability and correlation |

Each 0–4 anchor is defined verbally (e.g. Non-firm intensity: 0 = effectively all firm; 2 = mixed; 4 = almost entirely non-firm / Gate-1 / demand-flexibility terms). Anchors keep different agents — and different runs — consistent.

### 5.2 Margin of Safety and the 2×2

**Margin of Safety = Preparedness − Exposure** (range −100…+100). A large negative score is the warning light: an entity accumulating non-firm risk faster than its data, products and capital can support. The quadrant map:

| | Low Preparedness | High Preparedness |
|---|---|---|
| **High Exposure** | **Exposed** — loss concentration | **Earning it** — large book, matched capability |
| **Low Exposure** | **Sidelined** | **Whitespace** — capable but under-deployed |

### 5.3 Calibration is part of the method, not an afterthought

The quadrant cut-lines are **relative (in-sample medians), not fixed at 50/50.** This is a deliberate, evidence-driven choice: in the prototype, a fixed 50/50 line parked **11 of 15 entities in a single quadrant** because exposure scores cluster in a narrow band (see §6). Median (or tertile) cut-lines make the index rank *relative* firmness-risk — the correct framing for an outside-in product — and they re-centre automatically as the universe grows. The calibration used is recorded on every record's `scores.calibration` so the snapshot is self-describing.

### 5B. Hybrid scoring: latent × deterministic (v0.2)

Scoring combines **two input types**, fused in code — never by an LLM:

1. **Latent ratings** (`r_lat`) — research agents map evidence to 0–4 rubric anchors (broker press, product pages, market commentary). Capped at medium confidence without primary verification.
2. **Deterministic ratings** (`r_det`) — register pulls and filings mapped through fixed formulae in `contract/risk_model.json` (NESO Gate column, ECR flexible-connection MW share, SCR/FSR lookups, HHI).

**Fusion** uses actuarial credibility weighting (Bühlmann & Gisler, 2005 — citation `ACT-CREDIBILITY`):

\[
r_{\mathrm{eff}} = \lambda \cdot r_{\mathrm{det}} + (1-\lambda) \cdot r_{\mathrm{lat}}, \quad \lambda \in [0,1]
\]

where \(\lambda\) rises with evidence tier (measured → 0.95, disclosed → 0.80, assessed → 0). **Axis score** uses \(r_{\mathrm{eff}}\), not raw research ratings.

Every formula, threshold, and sub-factor weight cites **`contract/citations.json`** (regulatory, brokerage, actuarial, academic). Human-readable derivation: **`contract/MODEL_SPEC.md`**. Machine-readable: **`contract/risk_model.json`**.

Published scores include decomposition: `exposure_latent_0_100`, `exposure_deterministic_0_100`, and per-sub-factor `citation_ids` in `scores.blend`.

**Industry anchors include:** Solvency II SCR/segmental GWP (`PRA-SII-SCR`), Lloyd's RDS aggregation (`LLOYDS-RDS`), DCUSA ECR / NESO Connections Reform (`NESO-CMP434`), London Market facilities (Marsh Nimbus, WTW DIP, Lockton SLA), parametric basis-risk literature (European Actuarial Journal / arXiv:2505.02607), and compound loss frequency-severity (`ACT-COMP-LOSS`).

---

## 5A. No synthetic data — the hard rule

A 0–4 rating with a marketing URL stapled to it is an *opinion formatted as data*, not a measurement. The harness forbids this structurally (`contract/DATA_POLICY.md`). No value may be invented or produced "from model priors." Every input is one of four **evidence tiers**, and the tier caps how it may be used:

| Tier | Meaning | Requires | Max confidence |
|---|---|---|---|
| **measured** | figure read from a primary register/dataset | `measured_value`, `unit`, `as_of`, register URL | high |
| **disclosed** | figure from a regulated filing / rating / audited statement | specific figure, `as_of`, primary URL | high |
| **derived** | transparent computation over measured/disclosed inputs | the formula + input ids | high |
| **assessed** | sourced qualitative judgment (no measurement exists) | quoted evidence + URL | **medium** |
| *(rejected)* | vendor marketing, wikis, model priors | — | **not scorable** |

The **feature dictionary** (`contract/feature_dictionary.md`) maps every sub-factor to its measured/disclosed source and exact computation — e.g. `non_firm_intensity` is the MW-weighted share of an asset's capacity on flexible/curtailable connections, read directly from the **DNO Embedded Capacity Register** and the **NESO TEC "Gate" column**, not estimated. After this is applied at scale the Exposure axis is predominantly measured/disclosed, and only three Preparedness sub-factors (`data_monitoring`, `underwriting_expertise`, `pricing_modelling`) remain irreducibly `assessed` — and those are weight-capped (≤ 0.60 of the axis) and reported transparently. **Publication gate: measured + disclosed share ≥ 60% per axis.**

---

## 6. The harness and its loops

The build is a directed pipeline (orchestrator → universe → research → linker → scorer → validator → builder) over the shared contract, with concurrency at the entity level. Felix's "massive parallelisation" lives in the research stage. But the part that *perfects* the data is the set of **loops** layered on top — each with a trigger, an input, an output, and an exit criterion.

| Loop | Trigger | Does | Exit criterion |
|---|---|---|---|
| **Ingestion loop** | NESO register refresh (~2×/week); doloop in-force / Elexon / Ofgem updates | Re-pull registers; diff Gate status & in-force rules; flag changed entities | No un-ingested changes since last snapshot |
| **Research loop** | New or flagged entity | One agent per entity fills the contract with sources + confidence; unverifiable fields dropped | All required sub-factors populated or explicitly null |
| **Linking loop** | New L3 firmness facts | Propagate asset firmness upward into carrier Exposure; attach `covered_assets` | Every known coverage link resolved or flagged |
| **Scoring loop** | Any record change | Deterministic re-score; recompute median cut-lines | Scores reproducible from inputs |
| **Validation / adversary loop** | Each scored batch | Skeptical agent audits sourcing, calibration, over-confidence, regulatory linkage; emits versioned **deltas** | Zero hard violations; deltas triaged |
| **Optimization loop** | Adversary deltas + quality metrics | Apply audited deltas, recalibrate, measure redistribution | Quality targets met (below) |
| **Benchmarking loop** | New financial disclosures / curtailment events | Test Margin of Safety against loss ratios / event claims | Correlation tracked over time |
| **Eval / drift loop** | Each full run | Re-score the golden hand-scored set; flag rubric drift / run variance | Golden-set deltas within tolerance |

### 6.1 Data-optimization targets (objective, measurable)

The optimization loop runs against numbers, not vibes:

- **Source density** — sources per rating (prototype baseline: **1.01**; target ≥ 1.5, with ≥ 1 *primary/regulatory/financial* source per rating ≥ 2).
- **Confidence coverage** — share of low-confidence ratings (baseline: **49%**; target < 35%, driven down by register/Companies House evidence).
- **Completeness** — every required sub-factor populated for every entity (prototype: 100%).
- **Calibration health** — no quadrant holding > ~40% of the population at the chosen cut-lines; boundary entities (scores landing exactly on a cut-line) minimised.
- **Regulatory linkage** — every L3 `asset_link.gate_status` traceable to a NESO Gate-2 record or explicitly `unknown` (never inferred-as-firm).

### 6.2 Worked example — one optimization pass on the prototype

A live adversarial pass over the 15-entity prototype produced eight audited deltas and one calibration recommendation, which the optimization loop applied:

- **Calibration:** fixed 50/50 → **median cut-lines** (exposure ≥ 56.2, preparedness ≥ 70.0).
- **Corrections:** down-rated `book_concentration` for three generalist carriers whose own rationales called the book "secondary" (Hiscox, AXA XL, Chubb); fixed a broker pass-through over-rating (WTW); cut over-confident self-/wiki-sourced confidence (Parametrix data-monitoring, Descartes capital); reset Ark's *inferred* "firm" gate status to `unknown` pending a Gate-2 record.

**Result — the field went from undifferentiated to discriminating:**

| | Before (fixed 50/50, raw) | After (deltas + median) |
|---|---|---|
| earning_it | 11 | 6 |
| whitespace | 2 | 3 |
| sidelined | 1 | 4 |
| exposed | 1 | 2 |

Six entities moved quadrant. Crucially, the two assets with the weakest firmness — **Kao Data Harlow** and **Latos Bridgend** — separated cleanly into **Exposed**, which is precisely the signal the index exists to surface. The deltas are versioned in `contract/deltas.json`, so the pass is reproducible and auditable.

> **Honesty note (doloop principle):** Latos Bridgend produces the most negative Margin of Safety (−37.5) off an asset the research itself flagged as *not separately confirmed in public sources.* It is shown as provisional, low-confidence, pending verification of its queue position — the index never lets a striking number override its own confidence flag.

---

## 6A. Evals at every level

The harness is graded by an eval suite (`harness/evals.py`), not by inspection. Each level has an objective metric and a threshold; the provenance eval is the publication gate.

| Level | Eval | Metric | Prototype result |
|---|---|---|---|
| L0 | Contract validity | records well-formed | **PASS** 15/15 |
| L1 | Ingestion adapters wired | NESO + DNO ECR present | **PASS** |
| L2 | Extraction completeness | all 10 sub-factors per entity | **PASS** 15/15 |
| L3 | Scoring reproducibility | identical across re-runs | **PASS** |
| L4 | Calibration health | no quadrant > 40% at median cut-lines | **PASS** (40%) |
| L5 | **Provenance / no-synthetic** | measured+disclosed share ≥ 60% | **FAIL — 2%** |
| L6 | Scoring math (golden fixture) | all-4 → 100, all-0 → 0 | **PASS** |

This is the honest headline: **the machine works, the data does not yet meet the bar.** Six levels pass; L5 fails because the prototype is assessed-tier (103 of 150 ratings rest on vendor/wiki sources). That failure is the point — the eval makes the gap between "plausible" and "measured" impossible to paper over, and defines exactly what the scale-up must fix.

---

## 7. Benchmarking & validation

As with the reference, credibility comes from showing the scores track observable ground truth:

- **Financial outcomes** — for listed (re)insurers and disclosing syndicates, test whether a low Margin of Safety precedes deteriorating loss/combined ratios or reserve strengthening in the relevant lines.
- **Market-pricing proxy** — rate-on-line and capacity movements in data-centre / power BI as a read on where the market itself prices stress.
- **Event back-test** — when a real curtailment or grid-constraint event occurs, check that high-Exposure / low-Preparedness entities show the largest claims or repricing.

This is explicitly an **outside-in** exercise. We rarely know an insurer's exact position size, so a true exposure-weighted average is impossible; we score disclosed and inferable posture, not audited books.

---

## 8. Presentation (the front-end)

Three deliverables, matching the reference + doloop patterns:

1. **The dataset** — full, downloadable, entity-level, with scores, inputs, sources and confidence. The only one of its kind for this risk.
2. **The index** — a filterable front-end with the **2×2 scatter as the hero** (Exposure × Preparedness, coloured by quadrant, dot size = confidence), drill-downs by layer/region/firmness, and a ranked Margin-of-Safety table. A working prototype exists (`site/index.html`).
3. **The "in force" rail** *(doloop-style)* — a live panel of the connection-reform modifications driving firmness (CMP434/435, CMP448, GC0166, demand-flexibility SIs), each linked to the L3 records it re-prices.
4. **The thesis write-up** — a short essay landing the headline: *capacity is piling onto exposed-but-under-prepared participants while the genuinely capable sit in whitespace.*

---

## 9. Known half-knowns & limitations

Borrowing both references' candour:

- **Position sizing is opaque.** We see appetite and disclosed coverage, not line size or net retention — so no true exposure-weighting.
- **Coverage linkage is inferred.** Which insurer covers which asset is rarely public; L3 propagation is a modelled estimate with a confidence flag.
- **Firmness moves.** Gate status and curtailment terms change continuously; the index is a *dated snapshot*, re-run on a cadence — never a static claim.
- **Non-damage exposure is young.** Thin claims history means Preparedness leans on structural signals (product, data, capital) more than loss experience.
- **AI assistance is assistive, not authoritative** (doloop's own caveat). Summaries and scores are a research aid; the source is the truth, and every rating links to it.

---

## 10. Roadmap

1. **Lock the full universe** — pull NESO TEC + FCA + Lloyd's/LMA/MGAA + Companies House to enumerate L1–L4 (est. ~300–500 entities) and stand up the L5 rules feed.
2. **Wire Gate-2 linkage** — make `asset_link.gate_status` a register fact for every L3 asset; this is the single highest-value data upgrade.
3. **Hit the optimization targets** — drive source density ≥ 1.5 and low-confidence < 35% via primary-source passes.
4. **Harden as a Claude Agent SDK project** — semaphore-bounded `asyncio` fan-out, `output_format` schema enforcement, per-entity idempotent checkpoints, the golden-set eval in CI. Run it the way Felix used Claude Code.
5. **Ship the live index** — dataset + 2×2 + in-force rail, re-running on the NESO refresh cadence.

---

### Appendix — repository layout

```
nfri/
├── METHODOLOGY.md                 ← this document
├── contract/
│   ├── entity.schema.json         ← the typed record (the contract)
│   ├── rubric.json                ← weights + 0–4 anchors + quadrant rule
│   ├── DATA_POLICY.md             ← the no-synthetic-data rule + evidence tiers
│   ├── feature_dictionary.md      ← every sub-factor → measured primary source
│   ├── universe.seed.json         ← prototype universe (15 entities)
│   ├── universe.seed.v2.json      ← expanded universe (57 real entities, L1–L4)
│   └── deltas.json                ← versioned optimization-loop corrections
├── data/
│   ├── records.json               ← researched records (source of truth)
│   ├── records.scored.json        ← + deterministic scores
│   ├── records.optimized.json     ← + applied deltas & median calibration
│   ├── dataset.csv                ← flat export
│   ├── validation_report.txt      ← validator output (0 problems)
│   └── eval_report.txt            ← eval harness output (L0–L6)
├── harness/
│   ├── score_and_validate.py      ← Stages 3–5: link, score, validate
│   ├── adapters.py                ← MEASURED ingestion: NESO + DNO ECR APIs
│   ├── measure_non_firm.py        ← ECR import-MW + flex flag → measured non_firm_intensity
│   ├── measure_capital.py         ← FSR rating + SCR coverage → disclosed capital_reinsurance
│   ├── measure_book.py            ← disclosed energy-premium share → book_concentration
│   ├── fixtures/ecr_fixture.json  ← quarantined unit-test rows (real columns, fake MW)
│   ├── fixtures/capital_fixture.json ← quarantined unit-test capital inputs
│   ├── fixtures/book_fixture.json ← quarantined unit-test premium inputs
│   ├── data_quality.py            ← optimization metrics & threshold sensitivity
│   ├── optimize.py                ← the data-optimization loop
│   ├── evals.py                   ← eval harness at every level (L0–L6)
│   └── build_frontend.py          ← Stage 6: static 2×2 front-end
└── site/
    └── index.html                 ← the index prototype
```

*v0.2 for discussion. Counts, weights and cut-lines are calibrated against the first real pull and will move as the universe grows.*
