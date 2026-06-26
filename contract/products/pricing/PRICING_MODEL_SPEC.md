# NFRI Pricing Model Specification (v0.1 — scaffold)

Distinct from the **Index** (`contract/MODEL_SPEC.md`). The index ranks underwriting capacity; this spec defines **fair premium, triggers, and payouts** for non-firm / curtailment / NDBI risk.

**Status:** scaffold — fill each section as research lands. Machine-readable mirror: `pricing_model.json`.

---

## 0. Design principles

| Principle | Meaning |
|-----------|---------|
| **Register-anchored exposure** | Curtailment frequency/severity start from TEC Gate + ECR flex, not expert guess |
| **Basis risk explicit** | Every parametric design states downside risk \(r = P(\text{loss} \land \text{no payout})\) |
| **Heavy-tail aware** | SLA/curtailment tails use compound + hybrid tower, not Gaussian shortcuts |
| **Index selects, pricing prices** | NFRI MoS picks *who* to offer; this pipeline prices *what* to offer |
| **Cite everything** | Each formula → `contract/citations.json` ID |

---

## Stage 1 — Curtailment intensity process

**Question:** What is the stochastic curtailment exposure for asset \(a\) in zone \(z\)?

### Inputs (measured)
- `TEC.Gate`, `ECR.flexible_connection`, `import_mw` — see `feature_dictionary.md`
- Optional: `curtailment_rule` (ProRata / LIFO) — `ACAD-DESANTI-FCA-QUEUE`

### Model slot (fill in)

```
TODO: state process — e.g. semi-Markov curtailment hours / year
TODO: link to D'Amico joint generation–price template (ACAD-DAMICO-WIND)
TODO: OPF simulation parameters (ACAD-BOEHME-NONFIRM)
```

### Outputs
| Symbol | Definition | Unit |
|--------|------------|------|
| \(\lambda_a\) | Event rate | events/year |
| \(\mu_a\) | Mean curtailed MWh \| event | MWh |
| \(T_a\) | Mean duration \| event | hours |

### Research drop zone
`stages/01_curtailment_intensity/research.md`

---

## Stage 2 — Compound loss \(N \times S\)

**Question:** What is aggregate loss \(L = \sum N_i S_i\) for revenue / SLA shortfall?

### Frequency–severity (Klugman — `ACT-COMP-LOSS`)

\[
E[L] = E[N] \cdot E[S], \quad \mathrm{Var}(L) \text{ via independence or copula}
\]

### Severity slot
- DC/SLA: Exponential body + Pareto tail — `ACAD-EXPONENTIAL-PARETO-SLA-PREMIUM`
- Curtailment: \(S = \text{MWh shortfall} \times \text{VoLL or PPA strike}\)

### Outputs
`E[L]`, `VaR_99`, `TVaR_99`, loss distribution sample

### Research drop zone
`stages/02_compound_loss/research.md`

---

## Stage 3 — Expectile-optimal payout \(g^*(\theta)\)

**Question:** Given index \(\theta\) (e.g. curtailment hours, MWh shortfall, grid constraint flag), what payout minimises basis risk?

### Maier & Scherer (`ACAD-BASIS-RISK-EXPECTILES`)

\[
g^*(\theta) = e_\gamma(S \mid \theta)
\]

### Index design checklist (Teh–Woolnough — `ACAD-TEH-WOOLNOUGH-TRIGGER`)
- [ ] Downside basis risk \(r\) estimated
- [ ] Upside basis risk \(q\) estimated
- [ ] Multiscale nested triggers considered (`ACAD-ELABED-MULTISCALE`)
- [ ] Geographic aggregation vs exposure location (`ACAD-WOODARD-BASIS`)

### Outputs
Payout schedule (step/linear), `MSE(S, g(θ))`, monitoring ratio

### Research drop zone
`stages/03_expectile_payout/research.md`

---

## Stage 4 — Hybrid tower

**Question:** How to combine damage-triggered BI with parametric curtailment tail?

### Lopez (`ACAD-LOPEZ-HYBRID`)
\[
\text{Cover} = \min(L, L_{\mathrm{trad}}) + g_{\mathrm{param}}(\theta)
\]

### Product precedents
- Property/BI layer: `LMA-BI-GUIDE`
- Parametric SLA: `MGA-PARAMETRIX-SLA`, `DESCARTES-DC-PARAMETRIC`

### Outputs
Tower diagram, limits, triggers per layer, residual `trigger_gap`

### Research drop zone
`stages/04_hybrid_tower/research.md`

---

## Stage 5 — Premium + capital load

**Question:** What premium and capital support the structure?

### Pure premium slot
```
TODO: actuarial premium principle (variance / Esscher / TVaR) — Bahl SLA paper
TODO: expense + risk margin
```

### Capital (`PRA-SII-SCR`, `ACT-CREDIBILITY`)
- SCR charge from tail loss
- Credibility blend when experience thin

### Outputs
`pure_premium`, `gross_premium`, `SCR_pct`, `reinsurance_need`

### Research drop zone
`stages/05_premium_capital/research.md`

---

## Data requirements (shared)

| Dataset | Schema | Status |
|---------|--------|--------|
| Historical (index, loss) pairs | `data/loss_pairs.schema.json` | empty |
| Register time series | TEC/ECR pulls | adapter ready |
| Filed wordings | per-carrier trigger_gap | assessed |

---

## Verification gates (pricing)

| Gate | Check |
|------|-------|
| P1 | Every stage formula cites `citations.json` |
| P2 | `loss_pairs` validates when populated |
| P3 | Payout is elicitable / coherent |
| P4 | Premium mean ≈ compound loss (sanity) |
| P5 | Portfolio traceable to NFRI MoS |

Runner: `python3 harness/pricing/verify_pricing_spec.py`

---

## Build log

| Date | Stage | Change |
|------|-------|--------|
| 2026-06-26 | all | Scaffold created |
