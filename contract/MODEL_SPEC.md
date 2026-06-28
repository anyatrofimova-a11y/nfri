# NFRI Model Specification (v0.2)

Every calculation in the Non-Firm Power Insurance Risk Index is defined here and in `contract/risk_model.json`. Each formula cites one or more entries in `contract/citations.json`. **No score is produced by an LLM** — agents supply latent inputs; registers and filings supply deterministic inputs; fusion and axis arithmetic run in `harness/scoring.py`.

---

## 1. Design principle: latent × deterministic

| Component | Source | Role |
|---|---|---|
| **Latent rating** `r_lat` | Research agents, broker/market evidence | Qualitative anchor (0–4) when registers are incomplete |
| **Deterministic rating** `r_det` | NESO TEC, DNO ECR, SFCR, FSR, filings | Measured or disclosed quantity → fixed mapping |
| **Effective rating** `r_eff` | Scorer (code) | Credibility-weighted fusion |

**Fusion** follows actuarial credibility theory (Bühlmann & Gisler, 2005 — `ACT-CREDIBILITY`):

\[
r_{\mathrm{eff}} = \mathrm{clamp}_{[0,4]}\bigl(\lambda \cdot r_{\mathrm{det}} + (1-\lambda) \cdot r_{\mathrm{lat}}\bigr)
\]

where \(\lambda = \max(0,\ \lambda_{\mathrm{tier}} + \delta_{\mathrm{confidence}})\):

| Evidence tier | \(\lambda_{\mathrm{tier}}\) | Primary citations |
|---|---|---|
| measured | 0.95 | `ACT-CREDIBILITY`, `NESO-TEC`, `NGED-ECR` |
| derived | 0.85 | `ACT-CREDIBILITY`, `ACT-HHI-EIOPA` |
| disclosed | 0.80 | `ACT-CREDIBILITY`, `PRA-SII-SCR` |
| assessed | 0.00 | latent only — `ACT-CREDIBILITY` |

Confidence adjustment: high +0, medium −0.05, low −0.10 on \(\lambda\).

---

## 2. Axis scores

### 2.1 Exposure \(E\)

\[
E = \frac{100}{4} \sum_{i=1}^{5} w_i \cdot r_{\mathrm{eff},i}
\]

Interpretation: gross exposure to non-firm power risk — compound loss potential before underwriting mitigation (`ACT-COMP-LOSS`, `LLOYDS-RDS`).

| Sub-factor | Weight | Deterministic formula | Citations |
|---|---|---|---|
| **book_concentration** | 0.30 | \(c = \mathrm{GWP}_{\mathrm{energy/DC}} / \mathrm{GWP}_{\mathrm{total}}\) → anchor | `PRA-SII-SCR`, `SII-DELEG-35`, `PRA-PPP` |
| **non_firm_intensity** | 0.25 | \(s_{\mathrm{NF}} = \sum \mathrm{MW}_{\mathrm{nonfirm}} / \sum \mathrm{MW}\) from ECR flex flag + TEC Gate | `NESO-CMP434`, `NESO-TEC`, `DCUSA-ECR` |
| **aggregation_correlation** | 0.20 | \(\mathrm{HHI} = \sum_z (\mathrm{MW}_z / \mathrm{MW})^2\) → anchor | `ACT-HHI-EIOPA`, `ACT-HHI-CAS`, `LLOYDS-RDS` |
| **trigger_gap** | 0.15 | basis gap = 1 − (availability/parametric cover / relevant cover) | `ACAD-BASIS-RISK-ARXIV`, `LMA-BI-GUIDE` |
| **tenor_mismatch** | 0.10 | \(m = \max(0, T_{\mathrm{policy}} - H_{\mathrm{claims}}) / 15\) | `ACT-COMP-LOSS`, `UK-GOV-SII-REFORM` |

#### Non-firm intensity thresholds (register-derived)

Applied to \(s_{\mathrm{NF}}\) from DCUSA-standard ECR fields and NESO TEC Gate column (`NESO-CMP434`, `DCUSA-ECR`):

| \(s_{\mathrm{NF}}\) | Rating | Label |
|---|---|---|
| ≤ 0.05 | 0 | effectively firm |
| ≤ 0.25 | 1 | mostly firm |
| ≤ 0.55 | 2 | mixed |
| ≤ 0.85 | 3 | majority non-firm |
| > 0.85 | 4 | almost entirely non-firm |

#### HHI → aggregation rating

Herfindahl-Hirschman Index per EIOPA diversification study (`ACT-HHI-EIOPA`):

| HHI | Rating |
|---|---|
| ≤ 0.10 | 0 |
| ≤ 0.18 | 1 |
| ≤ 0.28 | 2 |
| ≤ 0.45 | 3 |
| > 0.45 | 4 |

#### Trigger gap — basis risk

Academic framing: basis risk is the payout–loss discrepancy under index/parametric cover (Maier & Scherer, 2025 — `ACAD-BASIS-RISK-EXPECTILES`; arXiv:2505.02607 — `ACAD-BASIS-RISK-ARXIV`). Conventional BI requires physical-damage trigger (`LMA-BI-GUIDE`); curtailment/SLA losses are non-damage (`BROK-LOCKTON-SLA`, `LLOYDS-PARAMETRIC-CYBER`).

---

### 2.2 Preparedness \(P\)

\[
P = \frac{100}{4} \sum_{i=1}^{5} w_i \cdot r_{\mathrm{eff},i}
\]

Interpretation: risk-adjusted capacity to underwrite non-firm exposure (`PRA-SII-SCR`, `LLOYDS-RDS`).

| Sub-factor | Weight | Deterministic formula | Citations |
|---|---|---|---|
| **data_monitoring** | 0.25 | verified telemetry artifact only | `MGA-PARAMETRIX-ANALYTICS` |
| **product_fit** | 0.20 | count of evidenced parametric/availability products | `LLOYDS-PARAMETRIC-CYBER`, `BROK-LOCKTON-SLA` |
| **underwriting_expertise** | 0.20 | FCA approved persons / Lloyd's class permissions | `FCA-PRIN` |
| **capital_reinsurance** | 0.20 | FSR lookup or SCR coverage % | `RATING-AMBEST-FSR`, `PRA-SII-SCR` |
| **pricing_modelling** | 0.15 | \(E[L] = P(\mathrm{curtailment}) \times E[\mathrm{SLA\ breach}]\) when model published | `ACT-COMP-LOSS`, `ACAD-BASIS-RISK-EXPECTILES` |

#### Capital rating from SCR (Solvency II)

| SCR coverage | Rating | Citation |
|---|---|---|
| ≥ 200% | 4 | `PRA-SII-SCR` |
| ≥ 150% | 3 | `PRA-SII-SCR` |
| ≥ 100% | 2 | `SII-DELEG-35` (minimum solvency) |
| < 100% | 1 | `SII-DELEG-35` |

#### FSR → capital rating (AM Best)

| FSR | Rating |
|---|---|
| AAA, AA | 4 |
| A | 3 |
| BBB | 2 |
| BB, B | 1 |

(`RATING-AMBEST-FSR`)

---

### 2.3 Margin of Safety

\[
\mathrm{MoS} = P - E \quad \in [-100, 100]
\]

Negative MoS: exposure exceeds preparedness — analogous to a capital/underwriting deficit (`PRA-SII-SCR`, `ACT-CREDIBILITY`).

**Quadrants** use in-sample **median cut-lines** on \((E, P)\), not fixed 50/50 — avoids quadrant collapse in narrow samples.

---

## 3. Industry practice anchors (brokerage & London Market)

| Market structure | Citation ID | NFRI use |
|---|---|---|
| Marsh Nimbus facility (~$2.7bn, 2026) | `BROK-MARSH-NIMBUS` | product_fit, underwriting_expertise |
| WTW Digital Infrastructure Protector | `BROK-WTW-DIP` | product_fit, broker placement |
| Lockton × Parametrix SLA insurance | `BROK-LOCKTON-SLA` | trigger_gap, data_monitoring |
| Lloyd's parametric cyber/outage BI | `LLOYDS-PARAMETRIC-CYBER` | trigger_gap, product_fit |
| Lloyd's RDS correlated stress | `LLOYDS-RDS` | aggregation_correlation |
| AI × clean energy financial coupling | `ACAD-AI-ENERGY-DCC` | aggregation_correlation, book_concentration |
| Munich Re GenAI / aiSure underwriting | `MUNICHRE-GENAI-WP` | product_fit, pricing_modelling, data_monitoring |
| Grid CRIs → systemic risk (SRIs) | `ACAD-CRI-GRID-SRI` | all sub-factors; register CRIs; aggregation_correlation |

---

## 4. Regulatory & grid register anchors

| Register / rule | Citation ID | Field used |
|---|---|---|
| NESO TEC + Gate column | `NESO-TEC`, `NESO-CMP434` | gate_status, MW, firmness |
| DNO ECR (DCUSA DCP 350) | `DCUSA-ECR`, `NGED-ECR`, `NPG-ECR` | flexible_connection, import MW |
| CMP448 Gate-2 queue fees | `NESO-CMP448` | curtailment cost signal |
| Solvency II SFCR | `PRA-SII-SCR`, `SII-DELEG-35` | SCR ratio, segmental GWP |
| FCA product governance | `FCA-PRIN` | product wordings, approved persons |

---

## 5. Academic literature

| Topic | Citation ID | Application |
|---|---|---|
| Basis risk / parametric expectiles | `ACAD-BASIS-RISK-EXPECTILES`, `ACAD-BASIS-RISK-ARXIV` | trigger_gap; cloud/DC outage parametric design |
| Credibility blending | `ACT-CREDIBILITY` | latent × deterministic fusion |
| Compound loss / frequency-severity | `ACT-COMP-LOSS` | tenor_mismatch; pricing_modelling |
| HHI concentration | `ACT-HHI-EIOPA`, `ACT-HHI-CAS` | aggregation_correlation |
| Data-centre outage drivers | `ACAD-DC-OUTAGE` | exposure thesis (power as leading cause) |

---

## 6. Output contract

Each scored record includes (`entity.schema.json`):

- `scores.exposure_0_100`, `scores.preparedness_0_100` — fused axis scores
- `scores.exposure_latent_0_100`, `scores.exposure_deterministic_0_100` — decomposition
- `scores.blend.exposure_sub_factors.*.citation_ids` — per-sub-factor references
- `scores.citation_ids` — model-level bibliography handles
- `scores.model_spec` → this document

---

## 7. References

Full bibliographic entries: **`contract/citations.json`**.  
Machine-readable formulas: **`contract/risk_model.json`**.  
Implementation: **`harness/scoring.py`**, **`harness/citations.py`**.

---

## 8. Industry stress testing

Catalogue: **`contract/stress_tests.json`**. Runner: **`harness/industry_stress.py`**.

Each scenario perturbs a copy of the scored universe, re-runs the hybrid model with **fixed baseline median cut-lines** (so quadrant moves reflect risk shocks, not re-calibration), and checks pass criteria drawn from market practice and the creative-strategy literature cited below.

| Scenario ID | Industry analogue | Primary citations |
|---|---|---|
| `RDS-CORRELATED-CURTAILMENT` | Lloyd's Realistic Disaster Scenario — one constraint, correlated books | `LLOYDS-RDS`, `ACT-HHI-EIOPA` |
| `MGA-CAPITAL-PULL` | MGA paper withdrawal when reinsurer pulls capacity | `IND-VALUECHAIN`, `MCKINSEY-MGA` |
| `BINDER-FACILITY-EXHAUSTION` | Delegated authority / Nimbus-style facility at premium cap | `IND-VALUECHAIN`, `BROK-MARSH-NIMBUS` |
| `BASIS-RISK-EVENT` | Parametric trigger vs indemnity SLA mismatch under curtailment | `ACAD-BASIS-RISK-*`, `LMA-BI-GUIDE` |
| `GATE-REGIME-SHOCK` | Connections Reform Gate-1 flood — firmness re-pricing | `NESO-CMP434`, `NESO-CMP448` |
| `SHARED-LAYERED-TOWER` | Amazon-scale shared & layered placement (60+ markets) | `IND-VALUECHAIN`, `BROK-WTW-DIP` |
| `PLACEMENT-CHAIN-INTEGRITY` | Retail → wholesale → London chain invariants | `IND-BROKER-CHAIN`, `IND-BROKING` |
| `CLAIMS-HISTORY-IMPORT` | Strata-style: import human baseline; cap latent on high spread | `STRATA-AI-INSURANCE`, `ACT-CREDIBILITY` |
| `SOLVENCY-CAPITAL-FLOOR` | SCR coverage &lt; 100% regulatory intervention | `PRA-SII-SCR`, `SII-DELEG-35` |

### 8.1 Placement & bundling structure (insurance value chain)

**Bundling** (`IND-VALUECHAIN`): risk, distribution, pricing, and balance sheet can unbundle. MGAs price without balance sheet; binders/lineslips bundle pricing with distribution; shared-and-layered towers concentrate aggregation on lead carriers. NFRI maps these to:

- **MGAs** — high `product_fit`, lower `capital_reinsurance` (paper risk externalised)
- **Brokers** — high `product_fit` / facility access, low `capital_reinsurance`
- **Carriers** — inverse; `aggregation_correlation` and `book_concentration` rise under tower stress

**Broking** (`IND-BROKING`): Dunbar-scale relationships; retail vs wholesale vs London. Facility economics (Marsh Nimbus) lift broker `product_fit` without moving balance-sheet risk onto the broker.

**Cannibals** (`IND-BROKER-CHAIN`): three-layer chain; exclusive retail–London deals (Howden/Ardonagh). Structural checks assert layer-appropriate sub-factor ordering rather than perturbing ratings.

### 8.2 Strata pricing discipline

`STRATA-AI-INSURANCE`: MGA path priced against human underwriter baseline and imported claims history; GL/PI exceptions drive new products. NFRI encodes this as the **credibility fusion** rule: when latent and deterministic diverge by more than two anchors without a measured tier, the model must not silently adopt full latent (`CLAIMS-HISTORY-IMPORT` scenario).

### 8.3 Pass criteria semantics

- **MoS drop** — preparedness minus exposure compression under stress (capital or exposure shock).
- **Quadrant movers** — entities crossing median cut-lines; reported per scenario for audit.
- **Structural / fusion checks** — no perturbation; validate invariants on the baseline universe.

Reports: `data/industry_stress_report.txt`, `data/industry_stress_report.json`. Integrated as **L7** in `harness/evals.py`.

**Related:** methodology meta-stress (gate satisfiability, calibration fragility) remains in **`harness/stress_test.py`** — complementary, not duplicate.
