# Che-Castaldo et al. — Critical Risk Indicators for the electric power grid (extract)

**Citation:** `ACAD-CRI-GRID-SRI`  
**Source:** Che-Castaldo, J. P. et al. *Critical Risk Indicators (CRIs) for the electric power grid: a survey and discussion of interconnected effects.* **Environment Systems and Decisions** 41, 594–615 (2021).  
**DOI:** [10.1007/s10669-021-09822-2](https://doi.org/10.1007/s10669-021-09822-2)  
**Local PDF:** `Downloads/10669_2021_Article_9822-2.pdf`

---

## Why it matters for NFRI

This is the closest **academic framing** for what NFRI does: multi-domain **Critical Risk Indicators** feeding **Systemic Risk Indicators (SRIs)** on grid reliability. It legitimises cross-domain scoring (climate, finance, hydrology, ecology → electric energy) and treats **power supply interruption** — not asset damage — as the primary risk realisation. Direct precedent for `aggregation_correlation`, register-based CRIs, and industry stress tests.

---

## Core definitions

| Term | Definition | NFRI mapping |
|---|---|---|
| **CRI** | Domain-specific quantifiable indicator of stress on (or from) the grid | Measured/disclosed sub-factor inputs (ECR, TEC, SAIDI analogues) |
| **Risk realisation** | **Power supply interruption** to customers (IEEE; excludes sags/swells/harmonics) | Non-firm curtailment / SLA breach — **not** physical damage |
| **Outage** | Loss of component ability to deliver power; may or may not cause interruption | Distinction matters for `trigger_gap` (equipment up, power not firm) |
| **Systemic risk** | Holistic risk from **cross-domain CRI interconnections** | `RDS-CORRELATED-CURTAILMENT`, Felix bundling, Liu AI–energy DCC |
| **SRI** | Trans-domain systemic risk measure from CRI network dynamics | Future: VAR/Granger layer on top of entity scores |

> "The electrical grid as an infrastructure is shaped by human activity and public policy in terms of demand and supply requirements."

Renewables, EVs, and climate stress increase variability — same thesis as NESO Gate reform / non-firm connections.

---

## Electric-energy CRIs (Section 3)

| CRI | What it measures | NFRI use |
|---|---|---|
| **SAIDI** | Average customer interruption **duration** (>5 min) | Severity axis for L3 assets / DNO performance |
| **SAIFI** | Average interruption **frequency** | Frequency leg of compound loss (`ACT-COMP-LOSS`) |
| **Reserve margin** | `(G_avail − D_peak) / D_peak` — adequacy **before** failure | **Leading** indicator; NERC default 15% thermal / 10% hydro |
| **EENS** | Expected energy not supplied (+ customer interruption cost) | Economic loss from curtailment without damage |

**Empirical link (ISO New England 2016–18):** reserve margin turned negative → external imports needed → **SAIDI and SAIFI spiked** (Jan 2017). Same logic as Gate-1 firmness shock: adequacy collapses before reliability indices move.

**Data sources cited:** EIA SAIDI/SAIFI (2013–18), DOE OE-417 major disturbances, state/utility outage feeds.

---

## Cross-domain CRI catalogue (Section 2.7 summary)

Domains surveyed: **climate, hydrology, agriculture, ecology, space weather, finance**, plus electric energy.

| Domain | Top CRIs | Affects grid? | Affected by grid? |
|---|---|---|---|
| Climate | Temp/precip anomalies, SPI, cooling/heating degree days | Yes | No |
| Hydrology | Streamflow, drought indices, groundwater | Yes | Yes |
| Agriculture | Irrigation demand, biomass, EVI | Yes | Yes |
| Ecology | LPI, bird abundance (BBS), Shannon/Simpson diversity | Yes | Yes |
| Space weather | Kp, SuperMAG, **GICs on transformers** | Yes | No |
| Finance | **VIX**, public utility index, oil/gas/coal/**electricity** prices | **Yes** | **Yes** |
| Electric | SAIDI, SAIFI, reserve margin | — | — |

**Key insight:** many CRIs are **bidirectional** (finance, hydrology, agriculture). Finance is **affected by** grid shocks but in the Granger example **does not propagate outward** — space weather is **exogenous** (affects all, affected by none). Electric energy, climate, agriculture, ecology sit in the **dense core** where shocks propagate.

---

## Finance ↔ grid (Section 2.6) — insurance-relevant

- **US sustained interruption cost:** ~$44B/year (2015), +25% since 2002.
- **Sector interruption costs (1994–2002 basis):** agriculture peak demand **$1.94/kW**; food industry spoilage **$50.52/kW**; industrial **$3,253/customer-hour** vs residential **$2.70**.
- **PG&E:** ~$30B wildfire losses → equipment-caused interruptions → **Chapter 11 (2019)**.
- **SCE:** $650k settlement for 2011 blackout.
- Finance CRIs: **VIX** (systemic stress), equal-weight **public utility stock index**, CME crude/natgas/coal/**electricity futures**.

Maps to carrier `capital_reinsurance` (utility credit events), `book_concentration` (utility exposure), and `aggregation_correlation` (VIX co-movement).

---

## Systemic Risk Indicators — methodology (Section 4)

**Proposal:** stack domain CRIs → **VAR(1)** on aligned time series → **Granger-causality network** → network summaries as SRIs:

- **Eigenvector centrality** — which CRI is most connected in the nexus
- **Degree of Granger causality (DGC)** — fraction of significant pairwise causal links

**Illustrative result (8 CRIs, monthly 2006–2018):** 15 significant links → **DGC 26.8%** (moderate connectivity). Space weather exogenous; finance sink; climate/agriculture/ecology/electric energy **mutually propagating**.

**Alternatives cited:** cosine similarity (portfolio joint fire-sales after Harvey/Rita), MES, SRISK (Bisias et al. 2012 survey).

**NFRI parallel:** entity sub-factors = CRIs; hybrid fusion = compositional weighting; industry stress tests = shock propagation through the nexus; future work = explicit VAR/SRI layer on register time series.

---

## UK / NFRI register mapping

Paper is US-centric but CRI **logic transfers**:

| Che-Castaldo CRI | UK NFRI register analogue |
|---|---|
| Reserve margin / adequacy | NESO TEC margin, capacity market, **Gate status** (CMP434/448) |
| SAIDI / SAIFI | DNO **Customer Minutes Lost** (RIIO), ofgem reliability |
| Non-firm / interruption | DNO **ECR** flexible connection flags |
| Finance / utility stress | SFCR, listed utility equity, **Lloyd's RDS** correlated scenarios |
| Climate / drought → hydro | Relevant for UK pumped storage / Scottish hydro mix |
| Renewable variability | Embedded generation, **non-firm DC load** |

---

## Quotes worth keeping

> "Power supply interruption in the power grid [is] the realization of risk in the context for CRI development."

> "Individual CRIs may only be important during specified scenarios or time frames."

> "Many CRIs do not conveniently fit in siloed domains."

> Systemic risk "threatens the stability of our society and natural world" via the **power grid system at large**.

---

## Skip / low value for NFRI

- US-specific datasets (gridMET, GAGES II, BBS routes) — cite as methodology only
- Space weather GIC chain detail (unless scoring transmission RE assets)
- Jupyter notebook supplementary — not needed in repo
- Full VAR matrix algebra

---

## Industry reference framing (for later citations)

Use this paper when arguing:

1. **NFRI is a CRI→SRI stack**, not ad-hoc ESG scoring.
2. **Curtailment / non-firm** = interruption-type risk realisation (damage-based BI gap).
3. **Multi-domain stress tests** (Felix, Lloyd's RDS, Liu AI–energy) have academic precedent in Che-Castaldo SRI framework.
4. **Leading vs lagging:** reserve margin / gate status **before** SAIDI; preparedness **before** exposure in MoS framing.
5. **Finance–grid coupling** supports correlated stress on insurers with utility + energy + tech books.

---

## Knowledge graph integration

**Graph:** [`graph.json`](graph.json) · **Schema:** [`graph.schema.json`](graph.schema.json)

This extract is the **anchor node** `che-castaldo-grid-cri-sri` in the NFRI knowledge graph. The graph links sources → CRIs → products → registers → pricing models with typed edges (`supports_cri`, `prices`, `exposes`, `maps_register`, `hedges`, `stress_analogue`, etc.).

### Topic clusters (from graph)

| Topic ID | Scope | Key nodes |
|---|---|---|
| `systemic_risk` | CRI/SRI framework | `che-castaldo-grid-cri-sri`, `sri-var-granger`, `lloyds-rds`, `stress-rds-curtailment` |
| `grid_firmness` | Non-firm / Gate / registers | `neso-gate-reform`, `register-tec`, `register-ecr`, `cri-reserve-margin`, `stress-gate-shock` |
| `dc_exposure` | Data centre insurance gap | `parametrix-sla-dc`, `descartes-dc-parametric`, `marsh-nimbus`, `epic-dc-energy-risk`, `uptime-dc-outage` |
| `pricing_models` | Actuarial / parametric / fusion | `basis-risk-expectiles`, `act-comp-loss`, `act-credibility`, `model-hybrid-fusion` |
| `placement` | Facilities & bundling | `marsh-nimbus`, `felix-bundling`, `wtw-dip`, `lockton-sla-placement` |
| `correlation` | Cross-asset spillover | `liu-ai-energy-dcc`, `cri-finance-vix` |

Query from repo root:

```bash
python3 harness/knowledge_graph.py topics
python3 harness/knowledge_graph.py node parametrix-sla-dc
python3 harness/knowledge_graph.py topic dc_exposure
python3 harness/knowledge_graph.py path cri-interruption-realisation parametrix-sla-dc
```

### DC + non-firm extension of Che-Castaldo CRIs

Che-Castaldo predates the UK DC queue crisis and parametric SLA market. The graph extends their framework:

| Che-Castaldo CRI | DC / non-firm extension | Graph node |
|---|---|---|
| Reserve margin (leading) | **Gate status**, TEC margin, flexible-connection flag | `cri-reserve-margin` → `neso-gate-reform`, `register-ecr` |
| SAIDI / SAIFI (lagging) | DNO CML; **SLA breach frequency** (Parametrix telemetry) | `cri-saidi-saifi` → `parametrix-sla-dc` |
| EENS + interruption cost | **SLA credits**, colo rent abatement, hyperscale penalties | `cri-interruption-realisation` → `instech-ndbi-parametric` |
| Finance: electricity price CRI | **Non-firm curtailment** as NDBI without price spike | `epic-dc-energy-risk` |
| Systemic risk (VAR/Granger) | **AI–clean energy DCC ~0.67** + correlated DC/re/newable books | `liu-ai-energy-dcc` → `sri-var-granger` |

**Risk realisation chain (graph path):**

```
register-ecr (flexible_connection=Yes)
  → neso-gate-reform (Gate 1 / non-firm offer)
    → cri-interruption-realisation (curtailment ≠ damage)
      → lma-bi-guide (conventional BI gap)
        → instech-ndbi-parametric
          → parametrix-sla-dc | descartes-dc-parametric (hedge)
            → basis-risk-expectiles (index vs true SLA loss)
              → model-hybrid-fusion (λ·register + (1−λ)·research)
```

### Pricing model nodes linked to this paper

| Model | Citation | Role in CRI→SRI stack |
|---|---|---|
| VAR(1) + Granger SRI | `ACAD-CRI-GRID-SRI` | Dynamic cross-domain propagation (Che-Castaldo §4) |
| DCC-MIDAS correlation | `ACAD-AI-ENERGY-DCC` | Static correlation special case for AI+energy+DC cluster |
| Expectile basis-risk optimal | `ACAD-BASIS-RISK-EXPECTILES` | Minimise trigger_gap under parametric SLA |
| Compound loss E[N]·E[S] | `ACT-COMP-LOSS` | SAIFI-analogue curtailment frequency × SLA severity |
| Credibility fusion | `ACT-CREDIBILITY` | Register CRI (measured) × research CRI (assessed) |
| Parametric SLA mirror | `MGA-PARAMETRIX-SLA` | Prices **interruption realisation** directly |

### Sources mined (graph nodes with extracts)

| Node | Extract |
|---|---|
| `instech-ndbi-parametric` | [`sources/instech-ndbi-parametric.md`](sources/instech-ndbi-parametric.md) |
| `epic-dc-energy-risk` | [`sources/epic-dc-energy-risk.md`](sources/epic-dc-energy-risk.md) |
| `descartes-dc-parametric` | [`sources/descartes-dc-parametric.md`](sources/descartes-dc-parametric.md) |
| `parametrix-sla-dc` | [`sources/parametrix-sla-dc.md`](sources/parametrix-sla-dc.md) |
| `liu-ai-energy-dcc` | [`liu-ai-energy-correlation.md`](liu-ai-energy-correlation.md) |
| `munichre-genai` | [`munichre-genai-insurance.md`](munichre-genai-insurance.md) |

*Graph is extensible — add nodes to `graph.json`, citations to `contract/citations.json`, extracts under `sources/`.*

