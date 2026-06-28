# Infirm connection — comprehensive risk profile (literature synthesis)

**Purpose:** NFRI thesis claim that infirm/non-firm grid access is **not** reducible to “being switched off.” This note maps academic and industry literature to eight assessable loss channels integrated in `contract/infirm_connection_risk.json` and `entity_analysis.infirm_risk_profile`.

---

## 1. Why “switch-off” is too narrow

Grid regulators and DSOs standardise **interruptibility** as a connection attribute (`ACAD-NONFIRM-REVIEW`, Monterde et al. 2025). Insurance still prices **damage** and occasional **cyber outage**. The gap is structural:

| Grid fact | Insurance instrument | Mismatch |
|-----------|---------------------|----------|
| Lawful curtailment order | Physical-damage BI | No proximate damage |
| Partial MW cap (capacity-limited) | Property TIV limit | Loss is utilisation, not asset |
| Workload deferral / migration | Cyber service outage | Correlation is geography not vendor |
| Low-notice ANM dispatch | Weather parametric | Trigger ≠ gate status |

---

## 2. Literature map → NFRI dimensions

### Monterde et al. — four access models (`ACAD-NONFIRM-REVIEW`)

1. **Capacity-limited** — static MW cap → **capacity_derating** (not always zero).
2. **Time-limited** — scheduled windows → **predictability**, **frequency_duration**.
3. **Dynamic operating envelopes (DOEs)** — forecast limits → **capacity_derating** + **basis_mismatch**.
4. **Fully flexible / ANM** — real-time → **interruption** + **utilisation_compute** + worst **predictability**.

UK: Ofgem Access SCR, DCUSA fields, Gate 1/2 register facts (`NESO-CMP434`).

### Flexible connection hosting capacity (`ACAD-FLEX-CONN-HCA`, arXiv:2510.11476)

- Modest flexibility (few interventions, small depth) unlocks large hosting capacity on **distribution** feeders.
- Loss is **infrequent but contractual** — maps to **frequency_duration** with low N, non-zero S.
- **connection_stage**: planning assumes historical profiles; operational risk if observability lags.

### Princeton ZERO — conditional firm service (`INDUSTRY-DC-FLEX-PRINCETON`)

- Distinguishes **transmission constraint** events from **generation curtailment** (balancing shortage).
- Conditional firm service: portion of load curtailed under stress; remainder firm — **capacity_derating** + **utilisation_compute**.
- On-site BESS/generators may cover transmission events but leave **basis_mismatch** if index ≠ accredited capacity test.

### DC siting & flexibility envelopes (`ACAD-DC-SITING-FLEX`, Nat Commun 2026)

- **Firm / pause / shift** envelopes expand siting frontier 9–21% vs firm-only.
- **utilisation_compute**: “shift” attenuates price peaks without full off — SLA risk is throughput not binary.
- **connection_stage**: pre-certified envelopes shorten energisation — shifts risk from queue to operational envelope compliance.

### Spatio-temporal DC flexibility (`ACAD-DC-STCU-FLEX`)

- Load floor vs ceiling within day — **capacity_derating** and geographic **utilisation_compute**.
- Curtailment reduction via temporal/spatial shift ≠ insurance “off” event; compound **frequency_duration**.

### Compound loss & basis risk (`ACT-COMP-LOSS`, `ACAD-BASIS-RISK-ARXIV`)

- Availability peril is **E[N]·E[S]** with rising N from queue depth (`NESO-CONSTRAINT-COSTS`).
- Parametric relief carries **basis_mismatch** when index ≠ SLA metric.

---

## 3. Eight-dimension assessment (operational)

| ID | Loss channel (plain) | Primary measure in NFRI |
|----|----------------------|-------------------------|
| interruption | Full lawful off | connection + boundary curtailment_prob |
| capacity_derating | Partial MW cap | mw_phase1 / mw_max, overplanting |
| utilisation_compute | SLA / job deferral | DC tag + load_norm + flex envelope |
| predictability | Notice horizon | predictability_class from connection/gate |
| frequency_duration | Chronic compound | boundary prob × constraint series |
| constraint_class | Transmission vs gen vs DNO | asset type + zone text |
| connection_stage | Queue / pre-COD | connection=queue, mining stage |
| basis_mismatch | Index ≠ loss metric | cover_stack absent parametric |

**Composite:** weighted mean → `infirm_severity_index` ∈ [0,1]; feeds L3 **non_firm_compute_exposure** interpretation and key-risk cards.

---

## 4. Insurance integration (Felix move)

1. **Exposure axis** — `non_firm_intensity` captures firmness share; **non_firm_compute_exposure** prices load × firmness × boundary likelihood; infirm profile explains *which channel* dominates.
2. **Trigger gap** — each dimension names the wording gap (damage BI, weather parametric, occurrence limits).
3. **Entity profiles** — `infirm_risk_profile.dimensions[]` rendered in drawer; agents extend `risk_manifestation[]` per channel.
4. **Analysis essay** — Act III mechanics: “Infirm connection is not a binary switch-off” table + prose.

---

## Graph edges

`infirm-risk-profile` → `acad-nonfirm-review`, `acad-flex-conn-hca`, `industry-dc-flex-princeton`, `act-comp-loss`, `acad-basis-risk-arxiv`.
