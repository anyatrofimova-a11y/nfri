# Claude handoff (Cursor → Cowork, 2026-06-26)

**Read this first.** There is no direct chat link between Cowork-Claude and Cursor — **this repo + git is the bridge.**

| | |
|---|---|
| **Repo** | https://github.com/anyatrofimova-a11y/nfri |
| **Branch** | `framework` (active; pushed) |
| **Local path** | `~/Developer/nfri` |
| **Clone** | `git clone -b framework https://github.com/anyatrofimova-a11y/nfri.git` |

---

## TL;DR — run this first

```bash
cd ~/Developer/nfri
git pull origin framework
python3 harness/run_loop.py --check    # non-destructive: L0–L8 + industry stress + model-spec verify
python3 harness/run_loop.py --list    # METHODOLOGY §6 loop → script map
python3 harness/run_loop.py --full    # ingest → score → optimize → eval → build (regenerates data/ + site/)
```

**Current status (`--check`, 2026-06-26):** mechanics **PASS**; honest red = **L5 publication gate FAIL at ~4% blended measured/disclosed** (prototype is PROVISIONAL by design until live register + filings land).

---

## What Cursor completed (this arc)

### Citation-backed framework
- **`contract/citations.json`** — **66** stable IDs (actuarial, basis-risk, non-firm grid, DC insurance, placement)
- **`contract/MODEL_SPEC.md`** — every formula/threshold with citations; Maier & Scherer authorship corrected on expectiles
- **`contract/risk_model.json`** v0.2 — hybrid latent×deterministic fusion (Bühlmann λ)
- **`harness/scoring.py`** — implements fusion; **`harness/citations.py`** — resolver

### Knowledge graph (triangulated research)
- **`contract/knowledge/graph.json`** v0.3 — **52 nodes**, **58 edges**, 6 topics
- Extracts under `contract/knowledge/` + `contract/knowledge/sources/`
- **`harness/knowledge_graph.py`** — CLI: `topics`, `topic`, `path`, `neighbours`, `node <id> check`
- Parallel literature miners covered: non-firm grid (NESO/Ofgem/ECR), DC SLA/facilities, pricing models, existing NFRI refs
- Personal skill (Cursor): `~/.cursor/skills/research-triangulation/SKILL.md` — workflow for future mining passes

### Stress & verification harnesses
- **`contract/stress_tests.json`** + **`harness/industry_stress.py`** — 9 industry scenarios (RDS, Solvency, basis risk, Gate shock, etc.); **L7 eval: 9/9 pass**
- **`harness/stress_test.py`** — methodology meta-stress S1–S7 (gate math, calibration)
- **`harness/verify_model_spec.py`** — model-spec ↔ knowledge integrity (**L8**)
- **`harness/run_loop.py`** — orchestrator tying METHODOLOGY §6 loops together

### Data & site (15-entity slice)
- Scored/optimized records in `data/records.optimized.json`, mirrored to `site/data/`
- Median-calibrated frontend: `site/index.html`, downloadable CSV/JSON
- Measure fixtures: `measure_non_firm.py`, `measure_capital.py`, `measure_book.py` (`--fixture` / `--live`)

### Docs for you
| File | Purpose |
|---|---|
| `METHODOLOGY.md` | Index thesis, layers, publication gate |
| `PRODUCT_MODEL.md` | Felix-style thesis / formalisation / viz |
| `DATA_ORCHESTRATION.md` | Triage path 4% → 60%, stress findings |
| `SETUP_CURSOR.md` | Cowork⇄Cursor setup + harness commands |
| `CURSOR_HANDOFF.md` | Earlier Cowork→Cursor notes (some superseded below) |

### Resolved since last Cowork pass
- **Publication gate definition:** **blended ≥ 60%** adopted everywhere (`evals.py`, `DATA_POLICY.md`, `METHODOLOGY.md`, `feature_dictionary.md`) — commit `26a6997`
- **Second-pass citations** merged (Teh-Woolnough, Elabed, Woodard, NESO-GC0166, Marsh UK SLA, etc.)
- **Git remote:** `origin` → `anyatrofimova-a11y/nfri`, branch `framework` pushed

---

## Open items for Claude (priority order)

### 1. Graph integrity (L8 / verify V3 — **blocking FAIL**)
Dangling edge: `acad-woodard-basis → act-hhi-eiopa` — target node missing.

```bash
python3 harness/knowledge_graph.py node acad-woodard-basis check
python3 harness/verify_model_spec.py
```

**Fix:** add `act-hhi-eiopa` node to `graph.json`, or repoint edge to `act-hhi-eiopa` citation anchor (EIOPA HHI is in `citations.json` as `ACT-HHI-EIOPA`).

### 2. Orphan citations (verify V2 — **WARN**)
4 defined-but-unreferenced in graph/risk_model: `ACAD-CCM-NF-LOAD`, `INDUSTRY-PARAMETRIC-DC-FINANCING`, `MARSH-NIMBUS-UK-LAUNCH`, `REG-IAIS-PARAMETRIC` — wire into nodes/sub-factors or drop.

### 3. Publication gate (L5 — **intentional FAIL**)
Blended measured+disclosed = **~4%** on 15 entities. Path to ≥ 60%:

1. **Live NESO TEC + DNO ECR** → measured `non_firm_intensity` for every L3 asset (`harness/ingest_live.py`, `measure_non_firm.py --live`)
2. **Populate** `contract/capital_inputs.json`, `contract/book_inputs.json` from real FSR/SFCR/Lloyd's filings (templates are empty — no synthetic values)
3. Lock **57-entity universe**, then re-derive median cut-lines (`stress_test.py` S4: not before)
4. Asset-specific rubric anchors before publishing any L3 score (`stress_test.py` S6)

See `DATA_ORCHESTRATION.md` for full triage playbook.

### 4. Frontend / product (when data ready)
- Render knowledge graph + hero 2×2 in site (`PRODUCT_MODEL.md` §5)
- Reconcile derived artifacts with `records.json`; output-vs-source check (`stress_test.py` S7)

---

## Key architecture (don't re-litigate)

```
records.json (research)
    → ingest_live / measure_*  (registers + filings)
    → scoring.py               (latent × det fusion, Bühlmann λ)
    → optimize.py              (audited deltas + median cut-lines)
    → evals.py L0–L8           (L5 = publication gate)
    → build_frontend.py        (site/)
```

**Thesis stack (citations):** Che-Castaldo CRI→SRI (interruption ≠ damage) + Maier & Scherer expectiles (basis risk) + Klugman compound loss (curtailment frequency×severity) + Bühlmann credibility (λ fusion). Insurance gap = LMA physical-damage BI vs parametric SLA/NDBI (Parametrix, Descartes, Lloyd's 2020 precedent).

**Non-firm measurement:** weight **NESO TEC Gate + demand CFI** over DNO ECR alone for DC load (`OFGEM-DEMAND-REFORM`, `NESO-DEMAND-CFI`).

---

## Harness reference

| Script | Output |
|---|---|
| `harness/run_loop.py --check` | All read-only gates |
| `harness/evals.py` | `data/eval_report.txt` (L0–L8) |
| `harness/industry_stress.py` | `data/industry_stress_report.txt` |
| `harness/stress_test.py` | `data/stress_test_report.txt` |
| `harness/verify_model_spec.py` | `data/model_spec_verification.txt` |
| `harness/knowledge_graph.py path register-ecr parametrix-sla-dc` | Example graph path |

**Do not treat as index:** `data/records.measured_demo.json` (fixture demo only).

---

## Collaboration protocol

1. **Pull** `framework` before editing: `git pull origin framework`
2. **Branch** for substantial work: `git checkout -b claude/<topic>`
3. **Run** `python3 harness/run_loop.py --check` before handoff back
4. **Commit** with why-focused message; push; Cursor reviews the **diff**
5. **Do not** invent measured numbers — assessed tier is explicit; L5 exists to block publication until evidence lands

---

## Suggested first Claude session

```bash
git pull origin framework
python3 harness/run_loop.py --check
# Fix V3: add act-hhi-eiopa node + edge in contract/knowledge/graph.json
python3 harness/verify_model_spec.py
git add contract/knowledge/graph.json
git commit -m "Fix graph dangling edge to ACT-HHI-EIOPA."
git push origin framework   # or feature branch → PR
```

Then start live ingest planning per `DATA_ORCHESTRATION.md` §4.
