# NFRI Data Orchestration & Triage — assessment, harness, and Cowork⇄Cursor handoff

*Cowork-side working note, 2026-06-25. Operational companion to `METHODOLOGY.md` (method),
`contract/MODEL_SPEC.md` (formalisation) and `PRODUCT_MODEL.md` (presentation/thesis).*

This note answers one question: **what data must we triage, in what order, to make the index
publishable** — i.e. to clear the no-synthetic publication gate (`contract/DATA_POLICY.md`,
eval **L5**, measured/disclosed share ≥ 60%) without inventing a single number. It records the
stress-tests run against the methodology, the model-spec ↔ knowledge integrity checks, the
fixes applied, and the open items handed to Cursor.

---

## 1. Where the data actually stands

| Gate | Status | Reading |
|---|---|---|
| L0–L4, L6 (mechanics) | **PASS** | contract, completeness, reproducibility, calibration, scoring math all hold |
| L7 industry stress | **PASS** 9/9 | RDS, Solvency, Felix/Strata scenarios (`contract/stress_tests.json`) |
| L8 model-spec/knowledge | **WARN** | citations resolve, knowledge wired, thresholds aligned; 1 graph edge open |
| **L5 provenance (PUBLICATION GATE)** | **FAIL — 4%** | 102/150 ratings rest on non-scorable (vendor/press/wiki) sources |

The machine works; the data does not yet meet the bar. L5 is the honest headline and the entire
job of triage is to move it from 4% → ≥ 60% **with measured/disclosed evidence only**.

---

## 2. The triage strategy — flip the most axis-weight per unit of effort

Each axis weight sums to 1.0; the gate is a blended measured/disclosed share across both axes.
The feature dictionary tells us which sub-factors *can* be measured. Ranking by
`weight × population-coverage × ease-of-pull`:

| # | Sub-factor (axis, weight) | Source to pull | Tier won | Wired? |
|---|---|---|---|---|
| 1 | **non_firm_intensity** (E, 0.25) — L3 assets | NESO TEC "Gate" column + DNO ECR flex flag (`adapters.py`) | measured | adapter ready; needs live pull |
| 2 | **capital_reinsurance** (P, 0.20) — carriers | AM Best/S&P FSR + Solvency II SCR coverage | disclosed | `contract/capital_inputs.json` template created — populate |
| 3 | **book_concentration** (E, 0.30) — carriers | Lloyd's class-of-business / SFCR segmental GWP | disclosed | `contract/book_inputs.json` template created — populate |
| 4 | **aggregation_correlation** (E, 0.20) | HHI over ECR/TEC grid geography (GSP/licence area) | derived | formula specified; needs geography join |
| 5 | **product_fit** (P, 0.20) | named evidenced parametric/availability products | disclosed | partially evidenced in knowledge graph |
| 6 | **trigger_gap** (E, 0.15) | filed product wordings / binder class | disclosed→assessed | **load-bearing** (see §3) |

**Do 1–3 first**: they are the highest-weight, highest-coverage, lowest-ambiguity pulls and they
move L5 fastest. The two `contract/*_inputs.json` templates are now in place (empty, schema-correct,
no synthetic values) so `measure_capital.py --live` / `measure_book.py --live` are wired the moment
real figures are entered.

---

## 3. Methodology stress-test — what the gate math actually permits

`harness/stress_test.py` turns the eval discipline on the **method** (not the data). Run it:
`python3 harness/stress_test.py` → `data/stress_test_report.txt`. Key findings:

- **S2a — the Preparedness axis can never reach 60% measured.** Only `product_fit` (0.20) +
  `capital_reinsurance` (0.20) are disclosable; `data_monitoring`+`underwriting_expertise`+
  `pricing_modelling` (0.60 combined) are irreducibly assessed. A *strict per-axis* 60% gate is
  **mathematically unsatisfiable** on Preparedness.
- **S2b — doc vs code mismatch.** `DATA_POLICY.md`/`METHODOLOGY.md` say "≥ 60% **per axis**";
  `evals.py` L5 computes a **blended** average of the two axes. They disagree. **Recommendation:**
  adopt blended ≥ 60% as the published gate (and say so), or keep per-axis and lower the
  Preparedness target to ~40%.
- **S2c/S3 — trigger_gap is load-bearing.** Even blended, a carrier reaches only ~45% on the
  obviously-measurable factors; clearing 60% **requires** upgrading a normally-assessed sub-factor
  (`trigger_gap` via filed wordings) to disclosed. Treat it as a measured-tier target, not polish.
- **S4 — calibration is fragile at n=15.** 7/15 entities sit within one rating-step of a median
  cut-line; the 15→57 universe will move every quadrant. Re-derive cut-lines only on the full pull.
- **S5 — the sharpest signal is the weakest-sourced.** The most extreme Margin-of-Safety records
  (e.g. Latos) rest on the lowest mean confidence. Flag low-confidence extremes as **measure-first**.
- **S6 — the rubric is carrier-shaped but scored on assets.** ~half of each L3 asset's score comes
  from sub-factors a data centre has no analogue for (book, reinsurance, underwriting expertise).
  Add asset-specific anchors or score assets on firmness only and propagate upward.
- **S7 — artifact drift.** `records.scored/optimized.json` did not reconcile with re-running the
  scorer on `records.json` (Latos exposure 67.5 in source vs 48.8 in derived); the L3
  "reproducibility PASS" eval only re-scores the *same* file twice. Add an output-vs-source check.

---

## 4. Model-spec ↔ knowledge integrity (new harness)

`harness/verify_model_spec.py` (also wired as eval **L8**) checks that Cursor's model layer agrees
with the curated knowledge base:

- **V1 citation integrity** — every citation handle in `risk_model.json`, `stress_tests.json`,
  `MODEL_SPEC.md`, `graph.json` resolves in `citations.json`. **PASS** (62 referenced / 66 defined).
- **V4 knowledge wired into the machine model** — *was FAIL.* The three knowledge notes
  (Che-Castaldo CRI/SRI, Liu AI–energy DCC, Munich Re aiSure) plus the DC-product anchors
  (Parametrix SLA, Descartes, EPIC, InsTech) were cited in `MODEL_SPEC.md` prose but **not** in the
  machine-readable `risk_model.json`, so scored records never carried them. **Fixed** — wired into
  the relevant sub-factor `citation_ids`; now **PASS** (scorer emits e.g. `MUNICHRE-GENAI-WP`).
- **V5 threshold consistency** — *was WARN.* Legacy `measure_capital.py` used SCR thresholds
  (200/160/130, floor 0) diverging from the canonical `risk_model.json` (200/150/100, floor 1).
  **Fixed** — `measure_capital.py` realigned. Now **PASS**.

Per-node validation is also available: `python3 harness/knowledge_graph.py node <id> check`.

---

## 5. What changed this pass (for Cursor to review in the diff)

**New (Cowork):** `harness/stress_test.py`, `harness/verify_model_spec.py`,
`contract/capital_inputs.json`, `contract/book_inputs.json`, this note, `PRODUCT_MODEL.md`.
**Edited (Cowork):** `contract/risk_model.json` (wired 10 knowledge anchors into sub-factor
citations), `harness/measure_capital.py` (SCR thresholds → canonical), `harness/evals.py` (added
L8), `harness/knowledge_graph.py` (added `node <id> check`).

I deliberately did **not** edit `contract/knowledge/graph.json` or `citations.json` — Cursor is
actively growing them. The verifier instead **flags** the open items below.

---

## 6. Open items handed to Cursor

1. **Graph integrity (L8/V3 FAIL).** One dangling edge: `acad-woodard-basis → act-hhi-eiopa`
   (target node does not exist). Either add an `act-hhi-eiopa` node or repoint/remove the edge.
2. **Orphan citations (V2 WARN).** 4 defined-but-unused: `ACAD-CCM-NF-LOAD`,
   `INDUSTRY-PARAMETRIC-DC-FINANCING`, `MARSH-NIMBUS-UK-LAUNCH`, `REG-IAIS-PARAMETRIC` — wire into a
   node/sub-factor or drop.
3. **Gate definition (S2b).** Pick per-axis vs blended and make `DATA_POLICY.md` and `evals.py` agree.
4. **Artifact reconciliation (S7).** Re-run the pipeline so `records.scored/optimized` match
   `records.json`, and add an output-vs-source reproducibility check to CI.

## 7. Next iterations (data)

1. Live NESO TEC + DNO ECR pull → measured `non_firm_intensity` for every L3 asset (highest-value upgrade).
2. Populate `capital_inputs.json` + `book_inputs.json` from real FSR/SFCR/Lloyd's filings → disclosed Exposure/Preparedness.
3. Lock the 57-entity universe, then re-derive median cut-lines (not before).
4. Add asset-specific rubric anchors (S6) before publishing any L3 score.
5. Re-run L0–L8; only publish entities clearing L5 ≥ 60%; everything else stays PROVISIONAL.

> Run order: `score_and_validate.py` → `optimize.py` → `evals.py` → `stress_test.py` →
> `verify_model_spec.py` → `industry_stress.py`. Then review diffs in Cursor.
