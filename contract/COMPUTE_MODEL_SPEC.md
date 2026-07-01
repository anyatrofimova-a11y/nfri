# Compute Market Underwriting Index — Model Specification (v0.1)

**CMUI** — insurance-grade scoring for compute-market risk across buyers, clouds, brokers/MGAs, carriers, and reinsurers.

Every calculation in the Compute Market Underwriting Index is defined here and in `contract/compute_risk_model.json`. Each formula cites one or more entries in `contract/compute_citations.json` and may cross-reference NFRI handles in `contract/citations.json` where grid coupling applies. **No axis score is produced by an LLM** — research agents supply latent inputs; market indices, filings, and contract disclosures supply deterministic inputs; fusion and axis arithmetic run in `harness/compute_scoring.py`.

**Sibling index:** NFRI (`contract/MODEL_SPEC.md`) prices **grid availability** (non-firm power). CMUI prices **silicon-market** risk (GPU-hour price, capacity delivery, economic depreciation, demand shocks). The bridge sub-factor `grid_compute_coupling` imports NFRI L3 exposure where an entity has linked grid assets.

**Thesis grounding:** Squaretower Research — GPU depreciation (`ST-GPU-DEPRECIATION`), H100 rental volatility (`ST-H100-VOLATILITY`), open-weight compute shocks (`ST-OPEN-WEIGHTS-RISK`), and Injective H100 market design (`ST-H100-PERP`).

---

## 0. Scope and peril stack

### 0.1 What CMUI measures

CMUI scores each entity on:

| Axis | Question |
|------|----------|
| **Exposure** \(E\) | How much compute-market loss potential sits on this balance sheet, book, or procurement plan **before** hedges and insurance? |
| **Preparedness** \(P\) | How much capacity does the entity have — instruments, data, products, capital, modelling — to **carry or transfer** that exposure? |
| **Margin of Safety** | \(\mathrm{MoS} = P - E\) — surplus or deficit of preparedness over exposure |

The scatter is a **posture map**, not a hazard league table. Two clouds with identical GPU inventory can diverge on stratum (value-trader vs long-tail industrialist), hedge ratio, and basis gap.

### 0.2 Peril prioritization (product sequencing)

| Priority | Peril | Primary index / trigger | Insurance product |
|----------|-------|-------------------------|-------------------|
| 1 | **Availability / tightness** | Squaretower tightness; hours-delivered vs contracted | Parametric capacity cover |
| 2 | **Price volatility** | H100 spot; 1-month forward | Cost band / overrun cover |
| 3 | **Demand shocks** | Release calendar + joint tightness/price spike | Event reinstatement overlay |
| 4 | **Economic depreciation** | Forward-implied residual; survival probability | Residual / economic-life shortfall (institutional) |
| 5 | **Grid coupling** | NFRI `non_firm_compute_exposure` on linked L3 | Bundled grid–compute joint trigger |

Sub-factor weights in §2 reflect this stack: availability and price dominate exposure; depreciation and grid coupling are material but secondary in v0.1.

### 0.3 Entity layers

| Layer | Segment | Role in value chain |
|-------|---------|---------------------|
| **L1** | Carriers, Lloyd's syndicates | Balance-sheet risk; facultative/treaty on compute parametric |
| **L2** | MGAs, brokers, compute-finance intermediaries | Structure triggers, place capacity, run facilities |
| **L3** | AI labs, enterprises, neoclouds, hyperscaler-adjacent buyers, GPU cloud operators | Originate exposure; procure, own, or resell GPU-hours |
| **L4** | Reinsurers, ILS, GPU-backed ABS investors | Tail and correlation bearer |

**L3 strata** (Squaretower cloud taxonomy — `ST-GPU-DEPRECIATION`):

| Stratum | Label | Risk profile | Depreciation / tenor bias |
|---------|-------|--------------|---------------------------|
| **S1** | Value trader | Short-cycle, frontier-chasing, spot-heavy | High `price_volatility_sensitivity`; fast margin decay |
| **S2** | Mid-market operator | Mixed reserved + on-demand | Balanced; basis gap often largest here |
| **S3** | Long-tail industrialist | Multi-tenant, re-tiering, concentrated whales | High `customer_concentration`; slower survival decay |
| **S4** | Reseller / broker-cloud | Hardware not owned; margin on resale | Low depreciation exposure; high tightness pass-through |

Stratum is an **entity tag**, not a score. It modulates interpretation of `depreciation_tenor_mismatch` and stress scenarios (§8).

---

## 1. Design principle: latent × deterministic fusion

Identical machinery to NFRI (`ACT-CREDIBILITY`):

| Component | Source | Role |
|-----------|--------|------|
| **Latent rating** `r_lat` | Research agents, broker terms, public disclosures | Qualitative anchor (0–4) when market data incomplete |
| **Deterministic rating** `r_det` | Squaretower indices, filings, contract extracts, NFRI link | Measured or disclosed quantity → fixed mapping |
| **Effective rating** `r_eff` | Scorer (code) | Credibility-weighted fusion |

\[
r_{\mathrm{eff}} = \mathrm{clamp}_{[0,4]}\bigl(\lambda \cdot r_{\mathrm{det}} + (1-\lambda) \cdot r_{\mathrm{lat}}\bigr)
\]

\[
\lambda = \max(0,\ \lambda_{\mathrm{tier}} + \delta_{\mathrm{confidence}})
\]

| Evidence tier | \(\lambda_{\mathrm{tier}}\) | CMUI primary sources |
|---------------|------------------------------|----------------------|
| **measured** | 0.95 | Published index print; exchange settlement price; verified SLA telemetry |
| **derived** | 0.85 | Computed from measured inputs (volatility, HHI, hedge ratio, NFRI link) |
| **disclosed** | 0.80 | SEC/Companies House capex, debt covenants, facility limits, GWP splits |
| **assessed** | 0.00 | Research only — no deterministic anchor |
| **unknown** | 0.00 | Missing; falls back to latent |

Confidence adjustment: high +0, medium −0.05, low −0.10 on \(\lambda\).

**Publication discipline:** A sub-factor with tier `assessed` may not drive a **positive** preparedness rating above 2 without a second independent source (`DATA-POLICY` analogue for CMUI).

---

## 2. Axis scores

### 2.1 Exposure \(E\)

\[
E = \frac{100}{4} \sum_{i=1}^{7} w_i \cdot r_{\mathrm{eff},i}
\]

**Interpretation:** Gross exposure to compute-market loss — unhedged GPU-hour spend at risk, capacity shortfall, basis mismatch, and economic-life uncertainty — before insurance and derivatives mitigation (`ACT-COMP-LOSS`, `ST-H100-VOLATILITY`).

| Sub-factor | Weight | Deterministic kernel | Citations |
|------------|--------|----------------------|-----------|
| **capacity_at_risk** | 0.22 | Unhedged GPU-hour notional | `ST-H100-PERP`, `ST-OPEN-WEIGHTS-RISK` |
| **tightness_sensitivity** | 0.20 | On-demand / short-tenor share × tightness beta | `ST-H100-VOLATILITY`, `ST-OPEN-WEIGHTS-RISK` |
| **price_basis_gap** | 0.16 | Contract rate vs index mismatch | `ACAD-BASIS-RISK-ARXIV`, `ST-H100-VOLATILITY` |
| **price_volatility_exposure** | 0.14 | Budget unhedged against spot/forward vol | `ST-H100-VOLATILITY`, `ST-GPU-DEPRECIATION` |
| **shock_calendar_exposure** | 0.10 | Open-weight / post-training workload dependency | `ST-OPEN-WEIGHTS-RISK` |
| **depreciation_tenor_mismatch** | 0.10 | Accounting life vs forward-implied economic life | `ST-GPU-DEPRECIATION`, `IND-GPU-ABS` |
| **grid_compute_coupling** | 0.08 | NFRI link on shared L3 assets | `INDUSTRY-DC-COMPUTE-DEMAND`, NFRI `ACAD-CCM-NF-LOAD` |

Weights sum to 1.00. At **L1/L2/L4**, `capacity_at_risk` uses book or facility notional; at **L3**, uses entity procurement/owned inventory.

---

#### 2.1.1 capacity_at_risk

**Question:** How many GPU-hours (or $ notional) can this entity lose if the market moves against them?

**Deterministic (L3 buyer/cloud):**

\[
N_{\mathrm{risk}} = H_{\mathrm{annual}} \times p_{\mathrm{unhedged}}
\]

\[
p_{\mathrm{unhedged}} = 1 - \frac{H_{\mathrm{hedged}}}{H_{\mathrm{annual}}}
\]

where \(H_{\mathrm{hedged}}\) counts hours covered by forwards, swaps, reserved contracts with fixed rate, or exchange positions (`ST-H100-PERP`, `IND-GPU-SWAP`).

Normalize to rating:

\[
n_{\mathrm{norm}} = \min\left(1,\ \frac{N_{\mathrm{risk}}}{N_{\mathrm{ref}}}\right), \quad N_{\mathrm{ref}} = 10^7\ \text{GPU-hours/year}
\]

**Deterministic (L1 carrier / L2 MGA):**

\[
c_{\mathrm{book}} = \frac{\mathrm{GWP}_{\mathrm{compute/parametric}}}{\mathrm{GWP}_{\mathrm{total}}}
\]

**Rating:** `threshold_map(n_norm or c_book, capacity_at_risk_thresholds)`.

| Input | ≤ 0.05 | ≤ 0.15 | ≤ 0.35 | ≤ 0.60 | > 0.60 |
|-------|--------|--------|--------|--------|--------|
| Rating | 0 | 1 | 2 | 3 | 4 |
| Label | de minimis | modest | material | large | dominant |

**Latent:** Research on undisclosed procurement (funding runway × implied burn, press releases on cluster size).

---

#### 2.1.2 tightness_sensitivity

**Question:** If the market tightens, does this entity feel it first?

Squaretower: on-demand H100 pricing embeds an **elasticity premium**; tightness reprices before spot stabilizes (`ST-H100-VOLATILITY`). DeepSeek V4: tightness index +200% overnight (`ST-OPEN-WEIGHTS-RISK`).

**Deterministic:**

\[
\beta_T = \sigma_{30}(\mathrm{TightnessIndex}) \times f_{\mathrm{short}}
\]

\[
f_{\mathrm{short}} = \frac{H_{\mathrm{on\_demand}} + H_{\mathrm{spot}} + H_{\mathrm{<\,90d}}}{H_{\mathrm{annual}}}
\]

\(\sigma_{30}\) = 30-day rolling std of tightness index, normalized by in-sample median across universe snapshot.

**Rating:** `threshold_map(β_T, tightness_sensitivity_thresholds)`.

| \(\beta_T\) | Rating | Label |
|-------------|--------|-------|
| ≤ 0.10 | 0 | reserved-heavy; tightness-insulated |
| ≤ 0.25 | 1 | low pass-through |
| ≤ 0.45 | 2 | mixed tenure |
| ≤ 0.70 | 3 | on-demand heavy |
| > 0.70 | 4 | burst / serverless / uncontracted |

**Latent:** Workload burstiness (inference autoscale, fine-tuning sprints) when contract shape undisclosed.

---

#### 2.1.3 price_basis_gap

**Question:** Does the insured's economic loss match the index trigger?

Basis risk = payout − true loss under parametric cover (`ACAD-BASIS-RISK-EXPECTILES`, `ACAD-BASIS-RISK-ARXIV`). CMUI: gap between **contracted GPU-hour rate** and **index the policy would use**.

**Deterministic:**

\[
g_{\mathrm{basis}} = \left| \ln\left(\frac{r_{\mathrm{contract}}}{r_{\mathrm{index}}}\right) \right|
\]

\(r_{\mathrm{contract}}\) = volume-weighted average rate on in-force compute contracts.  
\(r_{\mathrm{index}}\) = Squaretower H100 spot (or chip-matched index: A100, B200) over same window.

If entity has **no** parametric/index cover in force, use structural gap vs market:

\[
g_{\mathrm{basis}} = \left| \ln\left(\frac{r_{\mathrm{contract}}}{r_{\mathrm{spot}}}\right) \right|
\]

**Rating:**

| \(g_{\mathrm{basis}}\) | Rating | Label |
|------------------------|--------|-------|
| ≤ 0.05 | 0 | indexed / aligned |
| ≤ 0.15 | 1 | minor basis |
| ≤ 0.30 | 2 | moderate mismatch |
| ≤ 0.50 | 3 | reserved vs on-demand gap |
| > 0.50 | 4 | severe basis; trigger likely wrong |

---

#### 2.1.4 price_volatility_exposure

**Question:** How much annual spend is exposed to spot/forward repricing?

**Deterministic:**

\[
v = p_{\mathrm{unhedged}} \times \frac{\sigma_{90}(r_{\mathrm{spot}})}{\bar{r}_{\mathrm{spot}}}
\]

Coefficient of variation of H100 (or chip-matched) spot over 90 days, times unhedged share (`ST-H100-VOLATILITY`).

**Rating:**

| \(v\) | Rating | Label |
|-------|--------|-------|
| ≤ 0.05 | 0 | hedged or fixed |
| ≤ 0.12 | 1 | low vol pass-through |
| ≤ 0.25 | 2 | moderate |
| ≤ 0.45 | 3 | high |
| > 0.45 | 4 | extreme budget risk |

---

#### 2.1.5 shock_calendar_exposure

**Question:** Does this entity externalize demand on open-weight adoption?

Closed frontier models internalize procurement; open weights hit fragmented supply immediately (`ST-OPEN-WEIGHTS-RISK`).

**Deterministic (when workload disclosed):**

\[
s_{\mathrm{ow}} = w_{\mathrm{finetune}} + w_{\mathrm{post\_train}} + \mathbf{1}_{\mathrm{open\_weights\_in\_prod}}
\]

each weight ∈ [0,1] on GPU-hour mix.

**Proxy (derived):** public statements on in-house RL/post-training; downloads-served of open models × inference share.

**Rating:**

| \(s_{\mathrm{ow}}\) | Rating | Label |
|---------------------|--------|-------|
| ≤ 0.10 | 0 | closed-stack |
| ≤ 0.25 | 1 | peripheral |
| ≤ 0.45 | 2 | mixed |
| ≤ 0.65 | 3 | open-weight dependent |
| > 0.65 | 4 | release-calendar exposed |

**Event overlay (pricing, not scoring):** Named peril schedule on frontier open-weight releases; 48h joint trigger if \(\Delta \mathrm{tightness} > \tau_T\) AND \(\Delta r_{\mathrm{spot}} > \tau_p\) (`ST-OPEN-WEIGHTS-RISK`).

---

#### 2.1.6 depreciation_tenor_mismatch

**Question:** Is accounting life aligned with market-implied economic life?

Squaretower asset value (`ST-GPU-DEPRECIATION`):

\[
V_0 = \sum_{t=1}^{T} \frac{m_t \cdot u_t \cdot \pi_t}{(1 + \delta)^t} + \frac{S_T}{(1 + \delta)^T}
\]

| Symbol | Meaning |
|--------|---------|
| \(m_t\) | expected GPU-hour margin in period \(t\) |
| \(u_t\) | utilization |
| \(\pi_t\) | survival probability (not economically obsolesced) |
| \(\delta\) | cost of capital |
| \(S_T\) | salvage / resale |

Forward GPU-hour curve + utilization assumptions **imply** \(\bar{T}_{\mathrm{econ}}\) where \(V_0\) falls below replacement threshold.

**Deterministic:**

\[
\Delta T = T_{\mathrm{account}} - T_{\mathrm{econ\_implied}}
\]

\[
T_{\mathrm{econ\_implied}} = \inf\left\{ T : \frac{F_{12m}}{F_{0}} < \theta_{\mathrm{obs}} \right\}
\]

\(F_{\tau}\) = forward GPU-hour rate at tenor \(\tau\) from index or disclosed curve (`IND-GPU-FORWARD-CURVE`).  
\(\theta_{\mathrm{obs}} = 0.50\) = obsolescence threshold (configurable in `compute_risk_model.json`).

\[
m_{\mathrm{tenor}} = \max\left(0,\ \frac{\Delta T}{6\ \mathrm{years}}\right)
\]

**Rating:**

| \(m_{\mathrm{tenor}}\) | Rating | Label |
|-------------------------|--------|-------|
| ≤ 0.05 | 0 | aligned |
| ≤ 0.20 | 1 | minor drift |
| ≤ 0.40 | 2 | GAAP vs market gap |
| ≤ 0.65 | 3 | material mismatch |
| > 0.65 | 4 | balance-sheet fiction risk |

**Stratum note:** S1 value-traders expect high ratings; S3 long-tail with 6-year accounting may rate lower on this factor despite whale concentration elsewhere.

---

#### 2.1.7 grid_compute_coupling

**Question:** Is silicon risk independent of grid risk on the same asset?

NFRI (`contract/MODEL_SPEC.md` §2.1, `non_firm_compute_exposure`):

\[
I_{\mathrm{grid}} = \mathrm{load\_norm}(\mathrm{import\_MW}) \times s_{\mathrm{NF}} \times p_{\mathrm{curtail}}(\mathrm{boundary})
\]

**Deterministic (L3 with NFRI link):**

\[
r_{\mathrm{det}} = \mathrm{threshold\_map}(I_{\mathrm{grid}},\ \mathrm{non\_firm\_compute\_exposure\_index})
\]

Reuse NFRI thresholds from `contract/risk_model.json` → `non_firm_compute_exposure_index`.

**Deterministic (L1/L2 with linked L3 book):** exposure-weighted mean of linked assets' \(I_{\mathrm{grid}}\).

**Latent (no link):** assessed only; capped at medium confidence.

**Joint product trigger (out of score, in product spec):** pay if curtailment hours > attachment AND tightness > percentile 90.

---

#### 2.1.8 customer_concentration (aggregation modifier)

Not a separate exposure weight in v0.1 — enters as **correlation uplift** on portfolio stress (§8) and L3 S3 interpretation.

\[
\mathrm{HHI}_{\mathrm{cust}} = \sum_j \left(\frac{\mathrm{rev}_j}{\mathrm{rev}_{\mathrm{total}}}\right)^2
\]

Squaretower: whale tenants subsidize tail demand (`ST-GPU-DEPRECIATION`). High HHI → single cancellation reprices entire fleet.

Stored on record as `scores.aggregation.customer_hhi`; stresses apply +0.5 exposure anchor uplift when HHI > 0.28.

---

### 2.2 Preparedness \(P\)

\[
P = \frac{100}{4} \sum_{i=1}^{6} w_i \cdot r_{\mathrm{eff},i}
\]

**Interpretation:** Capacity to underwrite, hedge, or structurally absorb compute-market exposure (`PRA-SII-SCR`, `ST-H100-PERP`).

| Sub-factor | Weight | Deterministic kernel | Citations |
|------------|--------|----------------------|-----------|
| **index_hedge_coverage** | 0.22 | Forwards, swaps, perps vs at-risk hours | `ST-H100-PERP`, `IND-GPU-SWAP` |
| **data_monitoring** | 0.20 | Index subscriptions, internal telemetry | `ST-H100-VOLATILITY`, `MGA-PARAMETRIX-ANALYTICS` |
| **product_fit** | 0.18 | Parametric compute / SLA / availability products | `LLOYDS-PARAMETRIC-CYBER`, `MGA-PARAMETRIX-SLA` |
| **pricing_modelling** | 0.18 | Forward curve + survival model published | `ST-GPU-DEPRECIATION`, `ACAD-BASIS-RISK-EXPECTILES` |
| **underwriting_expertise** | 0.12 | Named compute-finance + insurance talent | `FCA-PRIN`, `BROK-MARSH-NIMBUS` |
| **capital_reinsurance** | 0.10 | FSR / SCR / GPU-backed facility depth | `PRA-SII-SCR`, `IND-GPU-ABS` |

---

#### 2.2.1 index_hedge_coverage

**Deterministic:**

\[
h = \frac{H_{\mathrm{hedged}}}{H_{\mathrm{annual}}}
\]

Hedge instruments: reserved fixed-rate contracts, CME/OTC compute swaps (`IND-GPU-SWAP`), on-chain perps (`ST-H100-PERP`), internal transfer pricing at locked rate.

**Rating:**

| \(h\) | Rating | Label |
|-------|--------|-------|
| ≥ 0.85 | 4 | largely transferred |
| ≥ 0.65 | 3 | substantial hedge |
| ≥ 0.40 | 2 | partial |
| ≥ 0.15 | 1 | token hedge |
| < 0.15 | 0 | unhedged |

---

#### 2.2.2 data_monitoring

**Deterministic:** verified subscription or API artifact to ≥1 financial-grade index (Squaretower H100, Silicon Data SDH100RT, Ornn OCPI — `IND-GPU-INDICES`).

| Evidence | Rating |
|----------|--------|
| ≥2 indices + internal utilization dashboard (verified) | 4 |
| 1 financial-grade index + utilization | 3 |
| 1 index only | 2 |
| Spot scraping / ad hoc | 1 |
| None cited | 0 (assessed latent only) |

---

#### 2.2.3 product_fit

**Deterministic:**

\[
n = \#\{\text{evidenced parametric compute / SLA / availability products}\}
\]

Products: Parametrix SLA (`MGA-PARAMETRIX-SLA`), Descartes DC parametric (`DESCARTES-DC-PARAMETRIC`), Lloyd's parametric cyber/outage (`LLOYDS-PARAMETRIC-CYBER`), compute cost parametric pilots (`IND-COMPUTE-PARAMETRIC`).

**Rating:** \(\min(4,\ n)\).

---

#### 2.2.4 pricing_modelling

**Deterministic:** entity publishes or files a model with:

1. forward curve input (≥2 tenors), and  
2. either survival probability \(\pi_t\) or explicit \(E[L]\) for compute availability/price.

**Rating:**

| Evidence | Rating |
|----------|--------|
| Full Squaretower-style \(V_0\) or internal equiv. in filing | 4 |
| Forward curve + \(E[L]\) for compute | 3 |
| Spot VaR / budget model only | 2 |
| Vendor model (unverified) | 1 |
| None | 0 |

Kernel (`ACT-COMP-LOSS`):

\[
E[L] = P(\mathrm{event}) \times E[S \mid \mathrm{event}]
\]

Events: tightness breach, index attachment, joint grid–compute trigger.

---

#### 2.2.5 underwriting_expertise

Same machinery as NFRI: FCA approved persons, Lloyd's class permissions, named compute-finance desk (`FCA-PRIN`). Latent: research on specialist teams (Marsh Nimbus, compute MGAs).

---

#### 2.2.6 capital_reinsurance

Reuse NFRI FSR / SCR maps (`RATING-AMBEST-FSR`, `PRA-SII-SCR`). **Add** GPU-collateralized facility depth where disclosed (`IND-GPU-ABS`):

| Evidence | Rating bump (cap 4) |
|----------|---------------------|
| Investment-grade GPU ABS / bankruptcy-remote SPV with perfected security | +1 vs SCR-only rating |
| Covenant-linked to compute index | +0.5 |

---

### 2.3 Margin of Safety

\[
\mathrm{MoS} = P - E \quad \in [-100, 100]
\]

**Interpretation:** Negative MoS = exposure exceeds instruments and capacity to carry compute-market risk — analogous to underwriting deficit (`PRA-SII-SCR`, `ACT-CREDIBILITY`).

**Quadrants:** median cut-lines on \((E, P)\) within snapshot (same rule as NFRI — avoids collapse in narrow samples).

| Quadrant | Condition | Label |
|----------|-----------|-------|
| **exposed** | \(E > \mathrm{median}(E)\), \(P \leq \mathrm{median}(P)\) | Danger zone |
| **earning_it** | \(E > \mathrm{median}(E)\), \(P > \mathrm{median}(P)\) | Carrying risk with instruments |
| **whitespace** | \(E \leq \mathrm{median}(E)\), \(P > \mathrm{median}(P)\) | Capacity seeking risk |
| **sidelined** | \(E \leq \mathrm{median}(E)\), \(P \leq \mathrm{median}(P)\) | Low relevance |

---

## 3. Insurance products (index as pricing OS)

CMUI is the **operating system** for placing cover; the products are parametric overlays on market indices.

### 3.1 Parametric capacity cover (priority 1)

| Element | Specification |
|---------|---------------|
| **Trigger** | Delivered GPU-hours < contracted in window \(T\) |
| **Index** | Squaretower tightness OR provider SLA feed |
| **Payout** | \(\mathrm{indemnity\_rate} \times \max(0,\ H_{\mathrm{contract}} - H_{\mathrm{delivered}})\) |
| **Basis** | Contract must reference same chip class as index |
| **CMUI inputs** | `tightness_sensitivity`, `capacity_at_risk`, `price_basis_gap` |

### 3.2 Cost band / overrun cover (priority 2)

| Element | Specification |
|---------|---------------|
| **Trigger** | 30-day rolling index mean > attachment \(A\) |
| **Index** | H100 spot or 1-month forward (`IND-GPU-FORWARD-CURVE`) |
| **Payout** | \(\min(\mathrm{limit},\ \sum_t \max(0,\ r_t - A) \times H_t)\) |
| **CMUI inputs** | `price_volatility_exposure`, `price_basis_gap`, `index_hedge_coverage` |

### 3.3 Release-event reinstatement (priority 3)

| Element | Specification |
|---------|---------------|
| **Trigger** | Named open-weight release + \(\Delta \mathrm{tightness} > \tau_T\) within 48h |
| **Payout** | Reinstatement of 3.1/3.2 limits once per policy year |
| **CMUI inputs** | `shock_calendar_exposure` |

### 3.4 Economic-life shortfall (priority 4, institutional)

| Element | Specification |
|---------|---------------|
| **Trigger** | \(F_{12m}/F_0 < \theta_{\mathrm{obs}}\) on policy chip class |
| **Payout** | Indemnity on leveraged fleet mark-down vs policy schedule |
| **CMUI inputs** | `depreciation_tenor_mismatch`, stratum S1/S3 |

### 3.5 Grid–compute bundle (priority 5)

| Element | Specification |
|---------|---------------|
| **Trigger** | NFRI curtailment hours > attachment AND tightness > p90 |
| **Payout** | Joint formula on lost availability × cost overrun |
| **CMUI inputs** | `grid_compute_coupling`, NFRI link |

**Pricing rule:** rate scales with \(\max(0,\ - \mathrm{MoS})\) and sub-factor spread on `price_basis_gap` + `tightness_sensitivity`.

---

## 4. Market data & index anchors

| Source | Citation ID | Fields |
|--------|-------------|--------|
| Squaretower H100 spot | `ST-H100-INDEX` | \(r_{\mathrm{spot}}\), \(\sigma_{30}\), \(\sigma_{90}\) |
| Squaretower tightness | `ST-TIGHTNESS-INDEX` | level, \(\Delta\) day-over-day |
| Squaretower forward curve | `ST-FORWARD-CURVE` | \(F_{1m}, F_{12m}\) |
| Injective H100 perp | `ST-H100-PERP` | settlement, open interest |
| Silicon Data SDH100RT | `IND-SILICON-H100` | cross-check spot |
| Ornn OCPI | `IND-ORNN-OCPI` | multi-chip spot |
| GPU forward curve (industry) | `IND-GPU-FORWARD-CURVE` | term structure |
| NFRI L3 link | NFRI `NESO-TEC` etc. | \(I_{\mathrm{grid}}\) |

**Ingestion cadence:** index feeds daily; filings on event; contract extracts on placement.

**Quality gate (L5):** ≥60% of L3 entities must have ≥1 measured tier on `capacity_at_risk` OR `tightness_sensitivity` before publication.

---

## 5. Academic & industry anchors

| Topic | Citation ID | CMUI use |
|-------|-------------|----------|
| GPU depreciation economics | `ST-GPU-DEPRECIATION` | `depreciation_tenor_mismatch`, pricing_modelling |
| H100 volatility & elasticity premium | `ST-H100-VOLATILITY` | `price_volatility_exposure`, `tightness_sensitivity` |
| Open-weight demand externalization | `ST-OPEN-WEIGHTS-RISK` | `shock_calendar_exposure`, stress |
| Basis risk / expectiles | `ACAD-BASIS-RISK-*` | `price_basis_gap`, product design |
| Credibility fusion | `ACT-CREDIBILITY` | all sub-factors |
| Compound loss | `ACT-COMP-LOSS` | pricing_modelling |
| HHI concentration | `ACT-HHI-*` | customer concentration stress |
| Parametric SLA (DC) | `MGA-PARAMETRIX-SLA` | product_fit |
| GPU ABS / collateral | `IND-GPU-ABS` | capital_reinsurance, depreciation |
| AI × energy coupling | `INDUSTRY-DC-COMPUTE-DEMAND` | grid_compute_coupling |
| NFRI non-firm compute | `ACAD-CCM-NF-LOAD` | grid_compute_coupling |

---

## 6. Output contract

Each scored record (`compute_entity.schema.json` — to be added):

```json
{
  "id": "example-neocloud",
  "layer": 3,
  "stratum": "S2",
  "scores": {
    "exposure_0_100": 62.5,
    "preparedness_0_100": 41.0,
    "margin_of_safety": -21.5,
    "quadrant": "exposed",
    "exposure_latent_0_100": 58.0,
    "exposure_deterministic_0_100": 67.0,
    "blend": {
      "exposure_sub_factors": {
        "tightness_sensitivity": {
          "r_lat": 3, "r_det": 3, "r_eff": 3.0,
          "lambda": 0.85, "tier": "derived", "confidence": "high",
          "citation_ids": ["ST-H100-VOLATILITY", "ST-TIGHTNESS-INDEX"]
        }
      }
    },
    "aggregation": {
      "customer_hhi": 0.31
    },
    "nfri_link": {
      "asset_id": "example-dc-uk",
      "grid_coupling_index": 0.22
    },
    "citation_ids": ["ST-GPU-DEPRECIATION", "ACT-CREDIBILITY"],
    "model_spec": "contract/COMPUTE_MODEL_SPEC.md"
  }
}
```

---

## 7. Industry stress testing

Catalogue: `contract/compute_stress_tests.json`. Runner: `harness/compute_industry_stress.py`.

Fixed baseline median cut-lines; perturb copy universe; report MoS compression and quadrant movers.

| Scenario ID | Analogue | Perturbation | Citations |
|-------------|----------|--------------|-----------|
| `ST-OPEN-WEIGHT-SHOCK` | DeepSeek V4 | tightness ×2.0; spot +7.5%; 48h window | `ST-OPEN-WEIGHTS-RISK` |
| `ST-TIGHTNESS-SPIKE` | Capacity shortfall | tightness +150%; delivered hours −20% | `ST-H100-VOLATILITY` |
| `ST-SPOT-CRASH` | H100 $8→$2 replay | spot −60%; unhedged exposure stressed | `ST-H100-VOLATILITY` |
| `ST-FORWARD-INVERSION` | Obsolescence repricing | \(F_{12m}/F_0 < 0.5\) | `ST-GPU-DEPRECIATION` |
| `ST-WHALE-EXIT` | Customer concentration | top customer rev → 0; HHI shock | `ST-GPU-DEPRECIATION` |
| `ST-BASIS-MISMATCH` | Wrong index trigger | basis gap +0.30 on all parametric | `ACAD-BASIS-RISK-ARXIV` |
| `ST-GRID-COMPUTE-JOINT` | UK curtailment + tightness | NFRI \(I_{\mathrm{grid}}\) ×1.5 AND tightness ×1.5 | NFRI + CMUI |
| `ST-HEDGE-FAILURE` | Hedge ineffectiveness | \(h \rightarrow 0.1\) on all L3 | `ST-H100-PERP` |
| `ST-MGA-CAPACITY-PULL` | Reinsurer exit | preparedness −15 on L2/L1 | `IND-VALUECHAIN` |

**Pass criteria:**

- **MoS drop** — median ΔMoS < −10 under severity-1 scenarios
- **Quadrant movers** — logged per entity; no silent fusion violations
- **Basis check** — parametric product attachment must not improve MoS without `index_hedge_coverage` increase

---

## 8. NFRI integration

| Mode | Behavior |
|------|----------|
| **Linked L3** | `grid_compute_coupling` uses NFRI `non_firm_compute_exposure` at measured/derived tier |
| **Carrier book** | L1 exposure-weighted roll-up of linked assets |
| **Joint product** | §3.5 trigger requires NFRI curtailment probability > entity attachment |
| **Shared harness** | Credibility fusion, quadrant logic, eval gates reuse NFRI `harness/scoring.py` patterns |

NFRI remains authoritative for **grid registers**; CMUI remains authoritative for **compute indices**. Neither score replaces underwriting judgement.

---

## 9. Versioning & implementation map

| Artifact | Status | Path |
|----------|--------|------|
| Model spec (this document) | **v0.1** | `contract/COMPUTE_MODEL_SPEC.md` |
| Machine-readable model | **shipped** | `contract/compute_risk_model.json` |
| Citations registry | **shipped** | `contract/compute_citations.json` |
| Rubric anchors | **shipped** | `contract/compute_rubric.json` |
| Stress catalogue | **shipped** | `contract/compute_stress_tests.json` |
| Scoring implementation | **shipped** | `harness/compute_scoring.py` |
| Index ingest | **shipped** | `harness/ingest_compute_indices.py` |
| Model builder | **shipped** | `harness/create_compute_model.py` |
| Stress runner | **shipped** | `harness/compute_industry_stress.py` |
| Spec verifier | **shipped** | `harness/verify_compute_model_spec.py` |
| Manifesto page | **shipped** | `site/on-compute-markets.html` |

**Changelog v0.1:** initial spec — seven exposure sub-factors, six preparedness sub-factors, Squaretower peril stack, NFRI bridge, product catalogue, stress scenarios.

---

## 10. References

Bibliographic entries: **`contract/compute_citations.json`**.

Cross-index handles: **`contract/citations.json`** (NFRI shared literature).

Squaretower Research (primary thesis sources):

- [We need new markets to assess GPU depreciation](https://squaretower.substack.com/p/we-need-new-markets-to-assess-gpu) → `ST-GPU-DEPRECIATION`
- [What's happening to H100 rental prices?](https://squaretower.substack.com/p/whats-happening-to-h100-rental-prices) → `ST-H100-VOLATILITY`
- [On open weights and compute market risk](https://squaretower.substack.com/p/on-open-weights-and-compute-market) → `ST-OPEN-WEIGHTS-RISK`
- [Injective H100 Market spotlight](https://injective.com/blog/injective-ecosystem-spotlight-squaretower) → `ST-H100-PERP`
