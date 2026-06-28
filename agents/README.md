# Platform agents

Phased engineering agents per **`BUILD_SEQUENCE.md`** (Felix sequence — not all parallel).

Pattern: `harness/agent_deploy.py --platform [--phase N]`

**Scoring is deterministic** (`harness/scoring.py`). LLM agents extract and cite only.

---

## Phases

| Phase | Agents | Exit |
|-------|--------|------|
| **1** Index | ingestion, ontology-schema, storage-retrieval, document-ai, backend-api, frontend, Qa-evals, chief-architect, insurance-domain | L5 ≥60% |
| **2** Graph | pricing-simulation, insurance-domain, Qa-evals | **RDS PASS** |
| **3** Pricing | pricing-simulation, insurance-domain, security-devops | verify_pricing_spec |
| **4** Active+CSaaS | ingestion, backend-api, insurance-domain | embed + broker handoff |

Distribution wedges (Phase 4): **direct MGA** + **CSaaS embed** — see `contract/platform/value_chain_seats.json`.

---

### chief-architect

**Role:** Service boundaries, ADRs, integration contracts.

**Ask:** Publish schema/API contracts day 1–3. All sprints bind to versioned interfaces. Resolve
schema drift via ADR before merge.

**Output:** `docs/adr/` — four surfaces, value-chain seat, LLM-extract/code-score, integration matrix.

**Ban:** Greenfield schemas duplicating `contract/entity.schema.json` or `risk_model.json`.

**Sprint:** Phase 1 lead; reviews all phases.

---

### insurance-domain

**Role:** Underwriting domain logic, stress scenarios, commercial offerings.

**Ask:** Encode value-chain invariants from `contract/stress_tests.json` and
`contract/MODEL_SPEC.md` §8. Support sprints 4, 5, 6 in parallel.

**Output:** Domain specs, stress pass criteria, `commercial_offerings.json` alignment.

**Ban:** Synthetic loss history; ungrounded market claims without citation ID.

**Sprint:** 0, 4, 5, 6 (parallel).

---

### ingestion

**Role:** Register adapters, filing pulls, evidence tier assignment.

**Ask:** Live NESO TEC, DNO ECR, L5 in-force feed in parallel with Sprint 6 telemetry stub ingest.
Publish `data/fixtures/register_snapshot.json` for downstream streams by day 5.

**Output:** Measured L3 firmness; populated capital/book inputs; fixture snapshot.

**Ban:** Synthetic register values; assessed tier as measured.

**Sprint:** 1, 6 (parallel).

---

### ontology-schema

**Role:** Facility graph, JSON Schema, entity resolution.

**Ask:** Extend `contract/entity.schema.json` early (week 1) so sprints 2–6 build against it.

**Output:** Schema extensions; validation in contract harness.

**Ban:** Breaking entity IDs without migration ADR.

**Sprint:** 1 (parallel).

---

### storage-retrieval

**Role:** Records pipeline, snapshots, RAG store interface.

**Ask:** Records reproducibility from day 1. Snapshot API for sprints 3–5. RAG store interface for
sprint 2 (can be empty corpus initially).

**Output:** Integrity checks; `data/fixtures/`; snapshot metadata.

**Ban:** Scored files that don't reconcile with scorer re-run.

**Sprint:** 1, 2 interface (parallel).

---

### document-ai

**Role:** RAG, clause extraction, confidence, human review.

**Ask:** Build extractors against Sprint 0 schemas immediately. Use fixture filings until live
corpus lands. Do not block on Sprint 1 register pull.

**Output:** Grounded extractions with `source_text` + `citation_id`.

**Ban:** Ungrounded UW text; LLM-computed E/P/MoS.

**Sprint:** 2 (parallel).

---

### pricing-simulation

**Role:** Graph accumulation (sprint 4) + pricing pipeline (sprint 5) — same agent, two workstreams.

**Ask:** Graph propagation and pricing stages 01–05 in parallel. Both consume fixture L3 until live
merge. Separate deployable pricing service.

**Output:** Stress harness hook; quote API; `verify_pricing_spec.py` pass.

**Ban:** Premium math in `risk_model.json` or `scoring.py`.

**Sprint:** 4, 5 (parallel workstreams).

---

### backend-api

**Role:** Index API, dataset export, embed API (sprint 6).

**Ask:** OpenAPI from Sprint 0 contract. Serve fixtures and live sources through same routes.
Provenance headers per Sprint 7 spec (stub headers OK week 1).

**Output:** `/entities`, `/dataset`, `/graph`, `/alerts`, `/embed` routes.

**Ban:** Response fields without provenance metadata.

**Sprint:** 3, 6 (parallel).

---

### frontend

**Role:** Scatter, regulatory rail, graph explorer, download UX.

**Ask:** Wire to Sprint 3 API immediately using fixtures. PROVISIONAL banner from live L5 eval.
Graph explorer accepts Sprint 4 feed when ready (empty state until then).

**Output:** `site/` via `harness/build_frontend.py`.

**Ban:** External author names on public site.

**Sprint:** 3 (parallel).

---

### security-devops

**Role:** CI, audit logs, secrets, deployment.

**Ask:** CI scaffold day 1; tighten gates as streams land. Pricing audit log in parallel with
Sprint 5. Register secrets for Sprint 1 live pulls.

**Output:** CI config; audit schema; deploy runbook.

**Ban:** Secrets in repo; `--no-verify` commits.

**Sprint:** 7 (parallel with all streams).

---

### Qa-evals

**Role:** Golden set, fusion checks, cross-stream regression.

**Ask:** Weekly cross-stream eval: L5, L7, fusion, pricing verify. Block merges on regression.
Do not weaken RDS criteria.

**Output:** Eval reports in `data/`; strict exit codes.

**Ban:** Greenwashing failing scenarios.

**Sprint:** 2, 4, 7 + weekly programme gate (parallel).

---

## Coordination

| When | Who | Action |
|------|-----|--------|
| Day 1–3 | `chief-architect` | Merge integration contracts |
| Daily | Sprint leads | Flag breaking schema/API changes |
| Weekly | `Qa-evals` | Programme regression report |
| Every PR | `security-devops` + `Qa-evals` | Eval pass on touched surfaces |

**Fixtures:** `data/fixtures/` — committed stubs all streams use until live data replaces them.

---

## Deploy manifest (future)

```bash
python3 harness/agent_deploy.py --platform
python3 harness/agent_deploy.py --platform --json
```

Operational playbook: **`PARALLEL_EXECUTION.md`** (fixtures, checklists, coordination).

---

## Links

- `PLATFORM_ARCHITECTURE.md` §6 — parallel sprint plan + integration contracts
- `harness/agent_deploy.py` — content-bot parallel passes
- `PRODUCT_SCAFFOLD.md` — pricing pipeline
- `DATA_ORCHESTRATION.md` — L5 gate triage
