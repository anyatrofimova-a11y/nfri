# → Cursor handoff (Cowork side, 2026-06-25)

Single entry point for the Cowork⇄Cursor review loop. Read this, run one command, review the diff.

## TL;DR — run this first

```bash
python3 harness/run_loop.py          # non-destructive: runs every gate that only READS data
python3 harness/run_loop.py --list   # see the METHODOLOGY §6 loop → script mapping
python3 harness/run_loop.py --full    # regenerates data/ + site/ (ingest → score → optimize → eval → build)
```

Current state from `--check`: **gates PASS** (eval L0–L8 run, industry stress 9/9, model-spec ↔
knowledge blocking checks green). The only red is the honest one: **eval L5 publication gate FAILs
at ~4% measured** — the prototype is assessed-tier and stays PROVISIONAL until real measured/disclosed
data lands (that is the *point* of the gate, not a bug).

## What I changed this pass (review these diffs)

**New harnesses (saved + runnable):**
| Harness | Loop it runs | Output |
|---|---|---|
| `harness/run_loop.py` | **orchestrator** — all METHODOLOGY §6 loops, with gating | console + reports |
| `harness/stress_test.py` | methodology meta-stress (gate math, calibration, assumptions S1–S7) | `data/stress_test_report.txt` |
| `harness/verify_model_spec.py` | model-spec ↔ knowledge integrity (also eval **L8**) | `data/model_spec_verification.txt` |

**New contract files:** `contract/capital_inputs.json`, `contract/book_inputs.json`
(schema-correct, EMPTY templates — populate from real FSR/SFCR/Lloyd's filings; no synthetic values).

**Edited (small, additive):**
- `contract/risk_model.json` — wired 10 knowledge anchors (Che-Castaldo, Liu, Munich Re, Parametrix
  SLA, Descartes, EPIC, InsTech) into sub-factor `citation_ids` so scored records actually carry
  them. Was prose-only in `MODEL_SPEC.md`; now in the machine model.
- `harness/measure_capital.py` — SCR thresholds realigned to canonical `risk_model.json`
  (200/150/100, floor 1; were 200/160/130, floor 0).
- `harness/evals.py` — added **L8** (model-spec/knowledge integrity).
- `harness/knowledge_graph.py` — added `node <id> check` subcommand (per-node validation).

**Docs:** `DATA_ORCHESTRATION.md` (triage + stress findings, operational),
`PRODUCT_MODEL.md` (Felix-style thesis / formalisation / data-viz / why-emerging), this file.

I did **NOT** touch `contract/knowledge/graph.json` or `contract/citations.json` — you are actively
growing them, so I left them and let the verifier flag the open items instead.

## Open items for you (Cursor)

1. **Graph integrity (eval L8 / verify V3, non-blocking FAIL).** Dangling edge
   `acad-woodard-basis → act-hhi-eiopa` — target node doesn't exist. Add an `act-hhi-eiopa` node,
   or repoint/remove the edge. Validate with `python3 harness/knowledge_graph.py node <id> check`.
2. **Orphan citations (verify V2 WARN).** 4 defined-but-unused: `ACAD-CCM-NF-LOAD`,
   `INDUSTRY-PARAMETRIC-DC-FINANCING`, `MARSH-NIMBUS-UK-LAUNCH`, `REG-IAIS-PARAMETRIC` — wire into a
   node/sub-factor or drop.

## One decision I need from you (or Anya)

**Gate definition.** `DATA_POLICY.md`/`METHODOLOGY.md` say "≥ 60% **per axis**"; `evals.py` L5
computes a **blended** average. They disagree, and per-axis is *mathematically unsatisfiable* on the
Preparedness axis (caps at 40% — see `stress_test.py` S2a/S2b). Pick one:
- **(A)** adopt **blended ≥ 60%** as the published gate (matches the code), or
- **(B)** keep **per-axis** and lower the Preparedness target to ~40% (matches what's achievable).

Once chosen I'll make `DATA_POLICY.md` and `evals.py` agree.

## Next iterations (both sides)

1. Live NESO TEC + DNO ECR pull → measured `non_firm_intensity` for every L3 asset (highest-value).
2. Populate the two `*_inputs.json` templates from real filings → disclosed Exposure/Preparedness.
3. Lock the 57-entity universe, *then* re-derive median cut-lines (stress S4: don't before).
4. Add asset-specific rubric anchors (stress S6) before publishing any L3 score.
5. Reconcile derived artifacts with `records.json` and add an output-vs-source check (stress S7).
6. Render the knowledge graph + hero 2×2 in the site (`PRODUCT_MODEL.md` §5).

## How the loop works (reminder)

No direct chat between Cowork-Claude and Cursor's agent — **the folder + git is the bridge.** Each
side edits; the other reviews the **diff**. Use branches for clean review. `run_loop.py` is the
shared "did I break anything" check both sides run before handing back.
