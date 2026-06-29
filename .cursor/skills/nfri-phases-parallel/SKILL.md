---
name: nfri-phases-parallel
description: >-
  Run NFRI platform Phases 2–4 (accumulation graph, pricing engine, CSaaS embed)
  in parallel via separate agents, then cross-verify no synthetic data. Use when
  the user asks to run Phase 2/3/4 together, parallel platform build, graph/RDS,
  pricing engine, active bundling, or CSaaS embed wedge.
---

# NFRI Phases 2–4 — Parallel Execution

Run accumulation graph, pricing engine, and active bundling **concurrently** with three agents, then verify exit gates and synthetic-data policy.

Playbook: `BUILD_SEQUENCE.md` · Architecture: `PLATFORM_ARCHITECTURE.md`

## When to use

- User says "run phase 2/3/4", "parallel platform build", or "go on graph + pricing + CSaaS"
- Phase 1 may still be PROVISIONAL (L5 < 60%) — phases 2–4 can ship in parallel per Felix fan-out model, but programme exit still requires L5

## Parallel agent fan-out

Launch **three Task agents** in one message:

| Agent | Phase | Primary deliverables | Exit orchestrator |
|-------|-------|---------------------|-------------------|
| A | 2 Accumulation graph | `graph.py`, `/graph/propagate`, RDS PASS | `harness/platform/phase2.py` |
| B | 3 Pricing engine | stages 01–05, IC-06 audit, verify_pricing_spec | `harness/platform/phase3.py` |
| C | 4 Active + CSaaS | telemetry ingest, embed API, broker handoff demo | `harness/platform/phase4.py` |

Each agent prompt must include:
- Read `BUILD_SEQUENCE.md` phase section first
- **No synthetic data** — register/filing/disclosed only on index paths; `FIXTURE_DEMO` quarantined to `data/fixtures/` and demo harnesses only
- **No LLM scores** — ADR-003; pricing deterministic in `harness/pricing/`
- **No git commits** unless user explicitly asks
- Write `data/phaseN_report.txt` with PASS/FAIL

## Post-parallel verification (parent agent)

Run sequentially after all three agents complete:

```bash
python3 harness/platform/programme_verify.py   # all phases + synthetic check
python3 harness/platform/phase2.py --check-only
python3 harness/platform/phase3.py --check-only
python3 harness/platform/phase4.py --check-only
python3 harness/publication_gate.py --check-only
python3 harness/platform/document_ai.py --verify
python3 harness/platform/fixtures_check.py --strict
```

### Cohort split (Phase 2+)

| Cohort | IDs | Used for |
|--------|-----|----------|
| `stress_cohort_ids()` | gate + L2 brokers (120) | `records.measured.json`, industry stress 9/9 |
| `publication_gate_cohort_ids()` | gate only, no brokers (106) | L5 eval, `records.publication_gate_cohort.json` |

Brokers are excluded from L5 because they have no scorable FSR/book by design (`measure_capital.py`). They remain in the stress universe for PLACEMENT-CHAIN-INTEGRITY.

Bootstrap flags: `--stress-cohort` (Phase 2) · `--gate-cohort` (L5-only rebuild)

### Synthetic-data rules (must PASS)

| Check | Pass condition |
|-------|----------------|
| `FIXTURE_DEMO` in `records.measured.json` / `records.json` | **0** sub-factors |
| ADR-003 `document_ai --verify` | PASS |
| Pricing audit `premium_source` | never `llm` |
| Telemetry/alerts | `data_source: fixture` OK in `data/alerts.json`; must not write index scores |
| L5 gate cohort | Report share; PROVISIONAL banner OK if < 60% |

### Phase exit commands

**Phase 2**
```bash
python3 harness/industry_stress.py data/records.measured.json   # 9/9
python3 harness/platform/graph_acceptance.py --strict
python3 harness/platform/index_api.py --export   # graph.json + graph_propagate.example.json
```

**Phase 3**
```bash
python3 harness/pricing/run_pipeline.py
python3 harness/pricing/verify_pricing_spec.py   # P1–P6 PASS
python3 harness/product_readiness.py
```

**Phase 4**
```bash
python3 harness/platform/active_bundle.py        # alert→broker→policy PASS
python3 harness/platform/embed_api.py --verify   # rejects missing broker_id (ADR-002)
```

## Agent deploy manifest

```bash
python3 harness/agent_deploy.py --platform --phase 2
python3 harness/agent_deploy.py --platform --phase 3
python3 harness/agent_deploy.py --platform --phase 4
```

## Common fixes

- **P5 index traceability FAIL**: run `phase3.py` (includes `score_measured()` on `records.measured.json`)
- **PLACEMENT-CHAIN-INTEGRITY FAIL**: ensure L2 brokers in gate cohort; disclosed `trigger_inputs` for MGAs with n≥2 products
- **RDS FAIL**: graph must apply `measured_value` stress overrides, not latent rating edits

## Reports

| File | Content |
|------|---------|
| `data/phase2_report.txt` | RDS, industry stress, graph API |
| `data/phase3_report.txt` | verify_pricing_spec, audit trail |
| `data/phase4_report.txt` | active bundle demo, embed verify |
