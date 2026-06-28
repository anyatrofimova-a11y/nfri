# Platform architecture — non-firm power insurtech vertical

*Strategic companion to `PRODUCT_MODEL.md` (index thesis), `PRODUCT_SCAFFOLD.md` (pricing
pipeline), `METHODOLOGY.md` (data harness), and `DATA_ORCHESTRATION.md` (publication gate).*

This document maps the full platform stack for a new insurtech vertical — **interruptible-power /
data-centre availability risk** — against (a) stored NFRI industry data and stress tests, and
(b) the insurtech playbook encoded in Felix Stocker's published work (value-chain decomposition,
Active Insurance bundling, ai-transformation index pattern, CSaaS distribution wedge).

**Status:** architecture specification · sprints not yet started · index Layer 1 built, pricing
Layer 2 scaffolded.

---

## 1. Executive summary

The platform has **four separable surfaces**, not one monolith:

| Surface | Question it answers | Primary artifact | Status |
|---------|---------------------|------------------|--------|
| **Index** | Who is exposed? Who can underwrite it? | `harness/scoring.py`, `contract/MODEL_SPEC.md` | Built (L5 provisional) |
| **Knowledge** | What evidence supports each score? | `contract/knowledge/graph.json`, citations | Built |
| **Pricing** | What is fair premium / trigger / payout? | `contract/products/pricing/` | Scaffold |
| **Active Availability** *(optional wedge)* | Can we predict curtailment and transfer loss? | Not started | Design |

Felix's vertical optimisation pattern (Coalition cyber → non-firm power analogue):

1. Score an **unscored population** with a deterministic rubric (ai-transformation move).
2. **Decompose the insurance value chain** — risk × distribution × pricing × balance sheet.
3. Build a **data moat for accumulation** where reinsurers disagree (graph + stress tests).
4. Ship **pricing as a separate auditable service**; deploy capital only with a differentiated view.
5. Optionally **bundle mitigation + transfer** (Active Insurance) or **embed via CSaaS** (B2B2C
   infrastructure for DC operators / cloud vendors).

**Execution model:** **Felix phased sequence** — index credibility → accumulation graph → pricing engine → active bundling + CSaaS embed. See **`BUILD_SEQUENCE.md`** for the operational playbook.

Five governing criteria: value-chain seat in ontology; deterministic scoring; CSaaS embed wedge; RDS PASS as graph acceptance test.

---

## 2. Felix Stocker — insurtech plays (external reference)

Internal citations use desk-synthesised keys (`IND-VALUECHAIN`, `IND-BROKING`,
`IND-BROKER-CHAIN`) derived from this analysis. External names do not appear on the public site.

### 2.1 Three insurtech categories

| Category | Target metric | Examples | Risk |
|----------|---------------|----------|------|
| **I — vSaaS to insurers** | Expense ratio | Guidewire, Indio | Long enterprise sales |
| **II — Data / analytics** | Loss ratio | RMS, Tractable | Hard to unicorn |
| **III — Direct competitors** | Distribution + innovation | Coalition, Lemonade | Incumbent distribution |

**Breakout:** CSaaS — infrastructure for platforms to sell insurance to their customers (Authentic
captive for Mindbody; Imprint co-branded cards). Lowers the scale at which ancillary insurance
lines make sense.

### 2.2 Coalition / Active Insurance template

The cyber vertical winner bundles **mitigation + transfer**:

- **Mitigation:** attack-surface scanning, MDR, incident response (Coalition Control).
- **Transfer:** cyber BI, breach response, kinetic cyber extensions.
- **Value chain:** MGAs price without balance sheet; brokers distribute; carriers hold aggregation.
  Do not disintermediate brokers.
- **Data moat:** portfolio-level event graph (48T events/month) for accumulation modelling.
- **Capital path:** retain risk via captive + reinsurer when underwriting view is differentiated;
  reinsurance arbitrage when market overprices cat accumulation.

### 2.3 ai-transformation index template

1. Pick population nobody scored systematically.
2. Encode fuzzy-but-disciplined rubric in software → massive parallelisation.
3. Two-axis tension + derived number (Margin of Safety).
4. Dataset is the artifact; visualisation is the argument.
5. **Exclude** fields not obtainable or verifiable for the whole universe.
6. **Scoring is arithmetic in code** — LLMs assist research, not headline numbers.

NFRI implements this in `PRODUCT_MODEL.md` §1 and `METHODOLOGY.md` §1.1.

### 2.4 Vertical analogue — cyber → non-firm power

| Cyber (reference pattern) | Non-firm power (this vertical) |
|---------------------------|--------------------------------|
| No consensus on cyber cat shape | No index of who carries curtailment accumulation |
| CrowdStrike = dependency cascade | Single constraint zone = correlated curtailment |
| Continuous attack-surface scan | Register fusion (TEC + ECR) + telemetry |
| Active Insurance = prevent + pay | Active Availability = predict curtailment + parametric pay |
| Reinsurers overprice cyber cat | Traditional BI wordings → basis gap → parametric whitespace |
| Active Data Graph | Knowledge graph + register in-force rail + scenario propagation |

---

## 3. Platform modules

### 3.1 Data ingestion

**Scope**

| Stream | Examples | NFRI today |
|--------|----------|------------|
| Public registers | NESO TEC, DNO ECR, CUSC/Grid Code mods, Ofgem/DESNZ | Adapters in `harness/adapters.py`; L5 design in `METHODOLOGY.md` §3 |
| Filings & wordings | SFCR segmental GWP, binder schedules, policy wordings | Templates: `contract/capital_inputs.json`, `contract/book_inputs.json` |
| Private documents | Contracts, policies, loss runs, engineering reports | Not wired |
| Telemetry | DCIM, BMS, EPMS, cloud uptime, network, power | Not wired — defer until L5 gate |
| Market / grid | Energy prices, congestion, weather, interconnection queues | Partial in knowledge graph |

**Discipline (Felix + `contract/DATA_POLICY.md`)**

- No synthetic values. Every field carries evidence tier: measured > derived > disclosed > assessed.
- Exclude population-wide fields that cannot be verified for all entities.
- AI summaries are assistive, not authoritative (doloop rule).

### 3.2 Canonical ontology

Target entity graph — maps to NFRI layers and `contract/entity.schema.json`:

```
Facility
  ├── PowerDependency
  ├── CoolingDependency
  ├── NetworkDependency
  ├── ComputeCluster
  ├── CustomerContract
  ├── SLA
  ├── InsurancePolicy
  ├── FailureMode
  ├── Trigger
  ├── LossType
  ├── Exclusion
  ├── ReinsuranceLayer
  └── AccumulationGroup
```

**Value-chain seat** (required on every insurance entity — from `IND-VALUECHAIN`):

| Seat | Role | NFRI sub-factor signature |
|------|------|---------------------------|
| MGA / coverholder | Price, external paper | High `product_fit`, low `capital_reinsurance` |
| Broker | Distribute, facility access | High `product_fit`, low `capital_reinsurance` |
| Carrier | Balance sheet, aggregation | High `capital_reinsurance`, rising `aggregation_correlation` under tower stress |
| Reinsurer / ILS | Tail capacity | Layer 4 (deferred in index v0.3) |

**Infirm connection profile** (`contract/knowledge/infirm-connection-risk-profile.md`) supplies
the eight-dimension operational assessment feeding L3 `non_firm_intensity` interpretation.

### 3.3 Storage and retrieval

| Store | Contents |
|-------|----------|
| `data/records.json` | Universe + inputs |
| `data/records.scored.json` | Deterministic scores |
| `contract/knowledge/graph.json` | Evidence network |
| `contract/citations.json` | Stable citation registry |
| Future | Vector index for clause-level RAG; time-series register snapshots |

Registers remain source of truth. DataHub integration spec: `contract/DATAHUB_INTEGRATION.md`.

### 3.4 AI and ML system

#### LLM layer

- Model router (easy tasks → lighter models e.g. GLM; complex extraction → frontier).
- RAG over filings, wordings, regulatory corpus.
- **Clause-level citations** — every extracted obligation links to source text.
- JSON-schema constrained outputs.
- Confidence scoring per field.
- Human review queue for high-impact outputs (wordings, capital, book concentration).
- **No ungrounded answers in underwriting artifacts.**

**Hard split:** LLM extracts and summarises; **`harness/scoring.py` computes E, P, MoS**. Same
discipline as Strata fusion caps (`CLAIMS-HISTORY-IMPORT` in `contract/stress_tests.json`).

#### ML layer (post–L5 gate)

| Capability | Use |
|------------|-----|
| Failure / outage classification | Map telemetry → infirm profile dimensions |
| Event clustering | Common-cause detection |
| Outage severity prediction | Scenario inputs for pricing |
| Missing data imputation | Register gaps only — flagged, never silent |
| Anomaly detection | Telemetry drift |
| Risk scoring | Feature inputs to pricing engine, not index headline |
| Entity resolution / dedup | Universe hygiene |
| Document classification | Route filings to extraction pipelines |

#### Probabilistic modelling layer

Feeds **pricing engine only** (`contract/products/pricing/`):

- Bayesian hierarchical models
- Poisson / negative-binomial frequency
- Survival / hazard models
- Extreme value / lognormal / gamma / Pareto severity
- Copulas for correlation
- Hawkes processes for clustered events
- Monte Carlo simulation
- Bayesian updating as loss data arrives

#### Graph layer

| Capability | NFRI anchor |
|------------|-------------|
| Centrality | Knowledge graph explorer |
| Community detection | Grid geography clusters |
| Shared dependency scores | HHI over ECR/TEC (`ACT-HHI-EIOPA`) |
| Scenario propagation | Lloyd's RDS (`RDS-CORRELATED-CURTAILMENT`) |
| Common-cause stress | `contract/stress_tests.json` L7 |

**Acceptance test:** `RDS-CORRELATED-CURTAILMENT` must pass (currently **FAIL** — max MoS drop
3.8 vs required 10; graph layer not yet wired hard enough).

Future: Che-Castaldo CRI→SRI layer (`contract/knowledge/che-castaldo-grid-cri-sri.md`).

### 3.5 Pricing and simulation engine

**Separate, auditable service.** Accepts structured inputs; produces structured outputs.

Pipeline (`PRODUCT_SCAFFOLD.md`):

1. Curtailment intensity
2. Compound loss N×S
3. Expectile payout g*
4. Hybrid tower
5. Premium + capital load

Does not mix premium math into `contract/risk_model.json`.

Commercial offerings gate: `contract/products/commercial_offerings.json`,
`python3 harness/product_readiness.py`.

### 3.6 Frontend

Surfaces (from `PRODUCT_MODEL.md` §5):

1. Hero 2×2 scatter — Exposure × Preparedness, quadrant colour, dot size = confidence.
2. Ranked MoS table with latent/deterministic decomposition.
3. In-force regulatory rail (CMP434, CMP448, GC0166).
4. Knowledge-graph explorer.
5. Downloadable CSV + JSON.

Register: editorial chrome per `contract/design_system.json`.

### 3.7 Security and backend

- Provenance chain on every extracted and scored field.
- Audit logs on pricing engine inputs/outputs.
- CI golden-set eval: `python3 harness/run_loop.py --check` (L0–L8).
- API layer serves index + dataset; pricing engine behind separate auth when live.

---

## 4. Crosswalk — stored NFRI data validates the architecture

### 4.1 Five-layer universe (`METHODOLOGY.md` §2)

| Layer | Who | Role in platform |
|-------|-----|------------------|
| L1 | Carriers & syndicates | Balance sheet; aggregation under tower stress |
| L2 | MGAs & brokers | Product innovation; facility placement |
| L3 | Assets / projects | Keystone — firmness is register fact post-CMP434 |
| L4 | Reinsurance / ILS | Tail capacity (scale-up) |
| L5 | Rules feed | In-force register re-prices L3 on regulatory change |

### 4.2 Industry stress tests encode value-chain invariants

| Scenario | What it proves | Status |
|----------|----------------|--------|
| `MGA-CAPITAL-PULL` | Parametrix MoS > Chubb when paper withdraws | PASS |
| `BASIS-RISK-EVENT` | Parametric beats L1 median on trigger gap | PASS |
| `BINDER-FACILITY-EXHAUSTION` | Brokers don't appear earning-it without preparedness | PASS |
| `GATE-REGIME-SHOCK` | L3 assets land exposed under firmness shock | PASS |
| `SHARED-LAYERED-TOWER` | Lead DC writer MoS < whitespace specialist | PASS |
| `PLACEMENT-CHAIN-INTEGRITY` | Brokers lower capital than carriers (structural) | PASS |
| `RDS-CORRELATED-CURTAILMENT` | Correlated curtailment surfaces exposed entities | **FAIL** |
| `CLAIMS-HISTORY-IMPORT` | Latent cannot silently override measured spread | PASS |

Report: `data/industry_stress_report.txt`.

### 4.3 Publication gate

`DATA_ORCHESTRATION.md`: **L5 blended measured/disclosed ~4%** (target ≥60%). Ingestion sprint
is the product gate — not optional polish.

Priority pulls: `non_firm_intensity` → `capital_reinsurance` → `book_concentration` →
`trigger_gap` (load-bearing for blended gate).

### 4.4 Whitespace signal

Scored universe shows brokers/MGAs with high preparedness and low measured exposure (whitespace
quadrant) — Felix's "market fleeing to safety" inversion. Parametric specialists (Parametrix,
Miller) score trigger_gap 0/4 by design; traditional carriers widen basis gap under curtailment.

---

## 5. Agent roster

Parallel agent passes follow the Felix pattern in `harness/agent_deploy.py` (essay/findings
bots today). Platform agents extend that model to engineering sprints.

| Agent | Owns | Key outputs |
|-------|------|-------------|
| `chief-architect` | ADRs, service boundaries, ontology ↔ NFRI layer map | Architecture decision records |
| `insurance-domain` | Value-chain seat, stress scenarios, commercial offerings | Domain specs, stress pass criteria |
| `ingestion` | Register adapters, filing pulls, evidence tiers | Measured L3/L1 fields |
| `ontology-schema` | Facility graph, JSON Schema, entity resolution rules | `contract/entity.schema.json` extensions |
| `storage-retrieval` | Records pipeline, snapshots, vector index | `data/` integrity, reproducibility |
| `document-ai` | RAG, clause extraction, confidence, human review queue | Grounded extractions only |
| `pricing-simulation` | Stages 01–05, graph accumulation, Monte Carlo | Auditable pricing service |
| `backend-api` | Index API, dataset export, provenance headers | REST/GraphQL layer |
| `frontend` | Scatter, rail, graph explorer, download | `site/` pages |
| `security-devops` | CI evals, audit logs, secrets, deployment | L0–L8 green in CI |
| `Qa-evals` | Golden set, fusion checks, stress regression | `harness/evals.py` extensions |

Agent briefs: `agents/README.md`.

---

## 6. Build sequence — Felix phases

**Do not run all layers in parallel.** Four sequential phases; each blocks the next until exit gates pass.

Full playbook: **`BUILD_SEQUENCE.md`**

| Phase | Focus | Acceptance |
|-------|-------|------------|
| **1** Index credibility | Ingestion, extraction, deterministic index, frontend | L5 ≥60% |
| **2** Accumulation graph | `harness/platform/graph.py`, propagation API | **RDS PASS** |
| **3** Pricing engine | Auditable Layer 2 service | `verify_pricing_spec` |
| **4** Active + CSaaS | Mitigation + transfer; embed wedge + broker handoff | Alert→policy demo |

```bash
python3 harness/agent_deploy.py --platform
python3 harness/agent_deploy.py --platform --phase 2
python3 harness/platform/graph_acceptance.py --strict
```

---

## 7. Parallel scope rules

All streams run together; these rules prevent merge conflicts and credibility leaks:

| Rule | Applies to |
|------|------------|
| Fixture data validates against production schemas | All sprints |
| Telemetry ingested but not scored until evidence tier assigned | Sprint 6 → 1 |
| ML classifiers train only on measured-tier rows | Sprint 2, 4, 5 |
| Frontend shows PROVISIONAL until L5 ≥60% (live eval, not hard-coded) | Sprint 3 |
| No synthetic values in scored outputs | All sprints |
| Pricing math stays out of `risk_model.json` | Sprint 5 |
| Broker channel preserved in embed paths | Sprint 6 |
| Do not weaken RDS pass criteria to green CI | Sprint 4, Qa-evals |

---

## 8. Verification checklist

```bash
# Publication gate + mechanics
python3 harness/run_loop.py --check

# Industry stress (target: 9/9 PASS including RDS)
python3 harness/industry_stress.py

# Model spec ↔ knowledge integrity
python3 harness/verify_model_spec.py

# Pricing spec (when Sprint 5 starts)
python3 harness/pricing/verify_pricing_spec.py

# Commercial readiness
python3 harness/product_readiness.py
```

---

## 9. Related documents

| Document | Contents |
|----------|----------|
| `PRODUCT_MODEL.md` | Index thesis, Felix + doloop pattern |
| `PRODUCT_SCAFFOLD.md` | Pricing pipeline stages |
| `METHODOLOGY.md` | Data universe, loops, adapters |
| `DATA_ORCHESTRATION.md` | L5 triage, gate math |
| `contract/MODEL_SPEC.md` | Formulas, stress §8, value-chain |
| `contract/stress_tests.json` | L7 scenario catalogue |
| `contract/knowledge/infirm-connection-risk-profile.md` | Eight-dimension loss channels |
| `agents/README.md` | Agent roster briefs |
| `PARALLEL_EXECUTION.md` | Deprecated parallel wave (superseded by BUILD_SEQUENCE.md) |
| `BUILD_SEQUENCE.md` | **Phased Felix playbook** — 5 criteria, phase exits, RDS acceptance |

---

*Last updated: 2026-06-27 · execution: all sprints parallel · baseline: L5 FAIL ~4%, RDS stress FAIL.*
