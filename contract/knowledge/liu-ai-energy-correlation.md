# Liu et al. — AI assets × energy markets (extract)

**Citation:** `ACAD-AI-ENERGY-DCC`  
**Source:** Liu, M.; Huang, J.; Liu, S. *Artificial intelligence assets and energy markets: Risk correlation dynamics and determinants.* **Utilities Policy** 98 (2026) 102118.  
**DOI:** [10.1016/j.pup.2025.102118](https://doi.org/10.1016/j.pup.2025.102118)  
**Sample:** Mar 2018 – Dec 2023 (COVID, 2022 energy crisis included)

---

## Why it matters for NFRI

Hyperscale AI and clean energy are **financially coupled**, not just physically (grid connection). When climate or dollar volatility rises, AI and energy books move together — directly relevant to `aggregation_correlation`, portfolio stress (RDS), and why DC insurers cannot treat "tech" and "power" as independent lines.

---

## Headline findings

| Relationship | Mean short-run DCC | NFRI role |
|---|---|---|
| **AI ↔ clean energy** | **~0.67** (persistent, long-run b≈0.9) | Strong co-movement — limited diversification within AI+renewables portfolio |
| **AI ↔ WTI / Brent** | ~0.23 / ~0.24 | Moderate diversifier |
| **AI ↔ natural gas** | ~negligible | AI as **hedge** vs gas |
| **AI ↔ INE (China crude)** | **0.06** (76% below Brent) | Regional insulation — Asia policy-driven decoupling |
| **AI ↔ DME (Middle East)** | ~0.11 | Intermediate |

**Regional heterogeneity (crude):** Western benchmarks (WTI, Brent) show 2×+ AI linkage vs INE/DME. Cross-regional energy books reduce AI-driven spillover 50–75%.

---

## Correlation drivers (DCC-MIDAS-X)

**Strengthen AI–energy correlation (significant):**

| Driver | Index | Mechanism |
|---|---|---|
| Dollar volatility | DRV | Global portfolio rebalancing, commodity pricing |
| **Climate policy uncertainty** | CPU | Shared decarbonisation / ESG capital flows |
| Economic policy uncertainty | EPU | Investment expectations, innovation + energy demand |
| Financial stress | FSI | Liquidity, risk appetite |

**Weak / insignificant:** trade policy uncertainty (TPU), general geopolitical risk (GPR) — do **not** tighten AI–energy link.

**Safe-haven caveat:** paper does not prove Baur–Lucey safe-haven in tails; associations not causality.

---

## Hypotheses tested

- **H1:** AI weak/negative vs traditional energy → **partially confirmed** (hedge for gas/INE; diversifier for WTI/Brent/gasoline/gas oil).
- **H2:** AI strong positive vs clean energy → **confirmed** (tech co-dependence: grid optimisation, renewables forecasting, smart grids, shared ESG narrative).

---

## NFRI sub-factor mapping

| Sub-factor | Use |
|---|---|
| **`aggregation_correlation`** | CPU/DRV/EPU shocks increase AI–energy DCC — correlated curtailment + tech drawdown scenarios (feeds `RDS-CORRELATED-CURTAILMENT` stress test) |
| **`book_concentration`** | Insurers writing both renewable parametric and DC/AI property accumulate **0.67+ correlated** exposure |
| **`non_firm_intensity`** | AI optimises renewables but **increases load** on constrained grids — physical + financial linkage |
| **`pricing_modelling`** | DCC-MIDAS as precedent for time-varying correlation in internal models |
| **`tenor_mismatch`** | Long-run persistence (b≈0.9) — short-horizon diversification understates multi-year policy risk |

---

## Actionable numbers for stress / calibration

- Treat **AI + clean energy** as **one cluster** for HHI / RDS (correlation &gt; 0.6).
- Under **climate policy uncertainty** shock, widen `aggregation_correlation` rating +1 for carriers with renewable + digital infrastructure books.
- **UK/Western DC assets** on Brent-linked portfolios inherit higher AI–energy spillover than yuan-denominated or regional Asian exposure.
- **Natural gas** books: AI assets provide genuine hedge — don't double-count gas + AI as independent diversifiers.

---

## Limitations (author-stated)

- Sample ends 2023 — pre-latest GenAI capex wave.
- No AI subsector split (hardware vs software vs services).
- Correlation ≠ causality; no tail-specific safe-haven proof.

---

## Skip / low value for NFRI

- Full GARCH-MIDAS equation notation
- China-specific funding acknowledgements
- Generic MPT introduction
