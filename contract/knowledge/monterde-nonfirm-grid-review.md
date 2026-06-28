# Monterde et al. — Non-firm grid connections review

**Citation:** `ACAD-NONFIRM-REVIEW`  
**Source:** Monterde, M. R.; Alvarez, E. F.; Valarezo, O. *Non-Firm Grid Connections: A Review of Access Types, Mechanisms, and Regulatory Frameworks.* Current Sustainable/Renewable Energy Reports **12**, 23 (2025). DOI [10.1007/s40518-025-00268-7](https://doi.org/10.1007/s40518-025-00268-7).

## Why NFRI cares

Grid regulators are **standardising interruptibility** faster than insurers are **standardising interruption triggers**. This review is the best single map of how non-firm access is being codified worldwide — and therefore what the placement chain will eventually have to price.

## Four connection models (Section 2)

| Model | Curtailment logic | Predictability | NFRI mapping |
|-------|-------------------|----------------|--------------|
| **Capacity-limited** | Static MW cap | Fixed, known | `non_firm_intensity` from ECR/TEC |
| **Time-limited** | Pre-agreed windows | Scheduled | Off-peak / time-band clauses in connection offer |
| **Dynamic operating envelopes (DOEs)** | Real-time limits, forecast horizon | Foreseen | Parametric index with published envelope |
| **Fully flexible (ANM)** | Real-time dispatch, no prior notice | Unforeseen | Worst `trigger_gap` — BI needs non-damage trigger |

Synonyms in literature: infirm, interruptible, curtailable, conditional, alternative access.

## UK evidence (pioneer jurisdiction)

- **Flexible Plug and Play** (UK Power Networks, 2011–2014): ANM-based fully flexible connections — **up to 87% cost saving**, **57% lead-time reduction** vs firm reinforcement.
- **Ofgem Access SCR** (May 2022): standardised non-firm option for larger users; curtailment limits and end-dates in offers → **DCUSA** contract fields.
- **Curtailment allocation:** LIFO, pro-rata, curtailment indices — maps to `ACT-COMP-LOSS` frequency structure.
- **Energy Exchange** (2019–2021): market-based compensation for flexible customers.

## Other jurisdictions (insurance gloss hooks)

| Jurisdiction | Mechanism | Essay use |
|------------|-----------|-----------|
| **Spain** | CNMC Circular 1/2024; electro-intensive industry focus | Industrial load + curtailment compensation debate |
| **Germany** | EnWG §14a controllable loads >4.2 kW; EnWG §17-2b / EEG §8a flexible Netzanschluss | Demand-side curtailment = tariff discount for interruptibility |
| **Belgium** | Federal flexible-access framework (Walloon since 2016) | Split regulatory readiness |
| **Australia** | AER Export Limits Guidance (Oct 2024); Ergon/Energex DOEs; Tesla VPP API | Site-specific export limits ≈ parametric trigger design |
| **EU** | Directive (EU) 2024/1711 — Member States must offer flexible access where scarce | Firmness becoming **law**, not negotiation |
| **US** | FERC Order 2023 streamlines interconnection; **no** formal non-firm framework yet | Isolated ANM pilots (Avangrid / NY FICS) |

## Reported benefits and open gaps

**Benefits (pilots):** up to **80% connection cost reduction**, **halved lead times**, deferred reinforcement.

**Gaps (insurance-relevant):**

1. **Curtailment predictability** — fixed → scheduled → forecast → real-time; each step changes basis risk for a parametric trigger.
2. **Compensation** — legal uncertainty for curtailed energy; weak alignment with local flexibility markets.
3. **Investor risk** — limited predictability of access conditions → **tenor_mismatch** on multi-year towers.
4. **Harmonisation** — no standard curtailment metrics across DNOs → aggregation harder for reinsurers.

## Insurance parallel (Felix move)

Grid side: regulators + DSOs building **register facts** (gate status, flexible_connection flag, curtailment cap %, end date).

Insurance side (same period): Marsh **Nimbus**, Aon **DCLP**, Parametrix **SLA mirror**, Descartes parametric DC, Swiss Re **sigma** DC+AI — **capacity** stacking on damage-BI forms.

**The gap:** grid literature prices *speed vs interruptibility*; insurance literature prices *TIV vs PML* — neither yet prices *curtailment predictability × SLA penalty* as a first-class variable.

## Graph integration

Anchor node: `acad-nonfirm-review` in `graph.json`. Edges to `ofgem-access-scr`, `neso-gate-reform`, `parametrix-sla-dc`, `sp-hyperscale-pool`.
