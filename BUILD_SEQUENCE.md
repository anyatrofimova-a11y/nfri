# Build sequence — Felix phased delivery

*Standalone execution guide. Architecture: `PLATFORM_ARCHITECTURE.md`. Supersedes parallel-all-at-once model in `PARALLEL_EXECUTION.md`.*

Five non-negotiable criteria govern build order:

1. **Sequence like Felix** — index credibility → accumulation graph → pricing engine → active bundling
2. **Value-chain seat in ontology** — MGA / broker / carrier / reinsurer (+ CSaaS embed)
3. **Deterministic scoring** — LLMs extract and cite; they never rank
4. **CSaaS/embed as distribution wedge** — alongside direct MGA, not instead of brokers
5. **RDS stress PASS** — graph layer acceptance test (`harness/platform/graph.py`)

---

## Phase map

```
Phase 1  INDEX CREDIBILITY          L5 gate ≥60%; deterministic E×P→MoS; dataset + scatter
    │
Phase 2  ACCUMULATION GRAPH        RDS PASS; scenario propagation; shared dependency scores
    │
Phase 3  PRICING ENGINE            Auditable Layer 2; verify_pricing_spec; separate service
    │
Phase 4  ACTIVE BUNDLING + CSaaS   Mitigation + transfer; embed API; broker handoff
```

**Do not start Phase N+1 until Phase N exit criteria pass.**

| Phase | Weeks | Agents (primary) | Exit gate |
|-------|-------|------------------|-----------|
| **1** Index credibility | 2–3 | ingestion, ontology-schema, document-ai, storage-retrieval, backend-api, frontend, Qa-evals | L5 ≥60%; `build_frontend` clean; ADR-003 enforced |
| **2** Accumulation graph | 2 | pricing-simulation (graph), insurance-domain, Qa-evals | **RDS-CORRELATED-CURTAILMENT PASS**; graph API live |
| **3** Pricing engine | 3–4 | pricing-simulation, insurance-domain, security-devops | `verify_pricing_spec` pass; quote audit trail |
| **4** Active + CSaaS | 2–3 | ingestion, backend-api, insurance-domain | Alert→policy demo; embed docs; broker handoff |

---

## Criterion 1 — Felix sequence

### Phase 1: Index credibility

**Goal:** Ship the ai-transformation pattern for non-firm power — unscored population, rubric in code, two-axis scatter, downloadable dataset.

**Deliverables**

- Live NESO TEC + DNO ECR pulls; L5 in-force register feed
- `value_chain_seat` on all entities (`contract/platform/value_chain_seats.json`)
- Document-AI extractions with clause citations → scoring **inputs only**
- Hero 2×2, regulatory rail, dataset export
- PROVISIONAL banner from live L5 eval

**Hard rule (Criterion 3):** `harness/scoring.py` computes E, P, MoS. LLM outputs validate against
`contract/platform/schemas/extraction/`; never write `scores` on records.

**Exit**

```bash
python3 harness/run_loop.py --check          # L5 PASS
python3 harness/build_frontend.py
python3 harness/platform/fixtures_check.py --strict
```

---

### Phase 2: Accumulation graph

**Goal:** Data moat for correlated curtailment — Coalition Active Data Graph analogue for grid constraint accumulation.

**Deliverables**

- `harness/platform/graph.py` — scenario propagation (implemented)
- `data/fixtures/graph_edges.json` + live geography join from ECR/TEC
- `/graph` and `/graph/propagate` on index API
- Interactive graph explorer fed by propagation output

**Acceptance test (Criterion 5)**

```bash
python3 harness/industry_stress.py          # RDS-CORRELATED-CURTAILMENT PASS
python3 harness/platform/graph_acceptance.py
```

RDS applies **measured-value stress overrides** (simulation), not latent rating edits — so fusion discipline holds under stress.

**Exit:** L7 industry stress 9/9 PASS; max MoS drop ≥10 on correlated event; chubb-class carriers surface Exposed.

---

### Phase 3: Pricing engine

**Goal:** Separate auditable Layer 2 service — deploy capital only with differentiated view.

**Deliverables**

- `harness/pricing/` stages 01–05 per `PRODUCT_SCAFFOLD.md`
- IC-06 pricing I/O schema; audit log on every quote
- Stress invariants preserved: Parametrix > Chubb under MGA-CAPITAL-PULL

**Exit**

```bash
python3 harness/pricing/verify_pricing_spec.py
python3 harness/product_readiness.py
```

---

### Phase 4: Active bundling + CSaaS embed

**Goal:** Coalition Active Insurance pattern for power firmness — predict curtailment + parametric transfer. Felix CSaaS breakout as **second distribution wedge**.

| Wedge | Seat | Channel |
|-------|------|---------|
| **Direct MGA** | `mga` | Broker-placed parametric (Parametrix model) |
| **CSaaS embed** | `csaas_embed` | DC operator / cloud vendor embed API → **broker handoff** |

**Deliverables**

- Telemetry ingest (DCIM/BMS/cloud) → `curtailment_alert.schema.json`
- Curtailment alerting + policy linkage
- `/embed/policy-offer` with mandatory `broker_id`
- Active Availability bundle docs

**Exit:** Demo alert → broker → policy on fixture; no consumer-direct bypass (ADR-002).

---

## Criterion 2 — Value-chain seat in ontology

Every entity record carries `value_chain_seat` (or inherits default):

| Seat | NFRI signature | Stress invariant |
|------|----------------|------------------|
| `asset` | L3; firmness register fact | GATE-REGIME-SHOCK |
| `mga` | High product_fit, low capital | MGA-CAPITAL-PULL |
| `broker` | Facility access, no balance sheet | BINDER-FACILITY-EXHAUSTION, PLACEMENT-CHAIN-INTEGRITY |
| `carrier` | Capital + aggregation under tower | SHARED-LAYERED-TOWER, RDS |
| `reinsurer` | Tail capacity (L4) | deferred scale-up |
| `csaas_embed` | Platform embed; broker handoff | Phase 4 only |

Schema: `contract/entity.schema.json` · defaults: `contract/platform/value_chain_seats.json` · facility graph: `contract/platform/schemas/facility.schema.json`

```bash
python3 harness/platform/value_chain.py --backfill   # populate missing seats on records.json
```

---

## Criterion 3 — Deterministic scoring

| Layer | Owner | LLM role |
|-------|-------|----------|
| Index E×P→MoS | `harness/scoring.py` | Extract sub-factor inputs only |
| Pricing premium | `harness/pricing/` | None on headline number |
| Underwriting prose | document-ai | Cite `source_text`; human review if confidence < 0.7 |

ADR: `docs/adr/003-llm-extract-code-score.md`

Fusion caps (`CLAIMS-HISTORY-IMPORT`) apply when latent/det spread ≥ 2 without measured tier.

---

## Criterion 4 — CSaaS embed wedge

Felix's breakout category (Authentic): infrastructure for platforms to sell insurance to their customers.

**NFRI application:** DC operators, cloud vendors, grid-adjacent SaaS offer availability/parametric cover via embed SDK — **broker remains in chain** (Marsh Nimbus / Miller parametric model, not disintermediation).

Dual wedge strategy:

1. **Direct MGA** — specialty parametric at the coalface (whitespace quadrant in index)
2. **CSaaS embed** — lower activation threshold for platforms with existing customer relationships

Both map to `contract/platform/value_chain_seats.json` → `distribution_wedges`.

---

## Criterion 5 — RDS as graph acceptance test

| Before | After |
|--------|-------|
| RDS FAIL — max MoS drop 3.8 | RDS **PASS** — max MoS drop 31.9 |
| Perturbation set `rating_0_4` only | Graph sets `measured_value` stress overrides |
| Ignored measured-tier fusion | Respects fusion; simulates register shock |

Implementation: `contract/stress_tests.json` → `graph_scenario: RDS-CORRELATED-CURTAILMENT` → `harness/platform/graph.py`

**Do not weaken pass criteria** (`min_mos_drop_top_exposed: 10`) to green CI.

---

## Agent fan-out by phase

```bash
python3 harness/agent_deploy.py --platform --phase 1
python3 harness/agent_deploy.py --platform --phase 2
# ...
python3 harness/agent_deploy.py --platform --json
```

Phase assignments: `contract/platform/sprints.json`

---

## Integration contracts (by phase)

| ID | Artifact | Phase |
|----|----------|-------|
| IC-01 | `entity.schema.json` + facility + **value_chain_seat** | 1 |
| IC-02 | `data/fixtures/register_snapshot.json` → live register | 1 |
| IC-03 | Extraction schemas | 1 |
| IC-04 | `openapi.index.yaml` | 1 |
| IC-05 | Graph edges + **graph.py propagation** | 2 |
| IC-06 | Pricing I/O | 3 |
| IC-07 | Curtailment alert + embed routes | 4 |
| IC-08 | Provenance headers + CI | 1 start, 3 harden |

Fixtures (`data/fixtures/`) used in Phase 1 until live data replaces in-place.

---

## Verification checklist (full programme)

```bash
# Phase 1
python3 harness/run_loop.py --check
python3 harness/build_frontend.py

# Phase 2 — graph acceptance
python3 harness/industry_stress.py
python3 harness/platform/graph_acceptance.py

# Phase 3
python3 harness/pricing/verify_pricing_spec.py

# Phase 4
python3 harness/platform/fixtures_check.py --strict

# Integrity (all phases)
python3 harness/verify_model_spec.py
```

---

## Related documents

| Document | Role |
|----------|------|
| `PLATFORM_ARCHITECTURE.md` | Full stack spec |
| `PARALLEL_EXECUTION.md` | Deprecated parallel wave (historical) |
| `agents/README.md` | Agent briefs by phase |
| `contract/platform/sprints.json` | Phase → agent mapping |
| `docs/adr/` | ADR-001–003 |

---

*Updated 2026-06-27 · RDS PASS via graph propagation · phased Felix sequence.*
