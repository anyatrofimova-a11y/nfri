# Munich Re — Insuring Generative AI (extract)

**Citation:** `MUNICHRE-GENAI-WP`  
**Source:** Munich Re whitepaper, © 2024, 18 pp.  
**NFRI entity:** `munich-re` (L1 reinsurer)

---

## Why it matters for NFRI

DC/AI load growth is both an **exposure driver** (non-firm power, curtailment) and an **underwriting subject** (who insures model failure, SLA breach, discrimination). Munich Re is one of the few carriers with a published GenAI insurance framework — directly relevant to scoring Munich Re on `product_fit`, `pricing_modelling`, `data_monitoring`, and `capital_reinsurance`.

---

## Product suite (aiSure™)

| Product | Who | What is insured | NFRI sub-factor |
|---|---|---|---|
| **Contractual Liabilities** | AI vendors | Performance guarantee backed by Munich Re if model misses SLA (e.g. fraud model catches &lt;99%) | `product_fit`, `capital_reinsurance` |
| **Own Damages** | Enterprise users | Self-built ML underperformance in critical ops (e.g. QC drift) | `trigger_gap` (non-damage operational loss) |
| **General Liabilities** | Enterprise users | Discrimination / disparate-impact class actions from AI decisions | `underwriting_expertise`, legal tail |

**Track record:** first AI risk 2018; first LLM 2019.

---

## GenAI risk taxonomy (vs traditional ML)

| Risk | Mechanism | Insurability (Munich Re view) |
|---|---|---|
| Hallucinations / false information | Output deviates from expected; no single ground truth | **Insurable** if task-scoped, metrics defined, testing regime in place |
| Bias / fairness | Fairness metrics ≠ legal discrimination; class-action scale | **Partially insurable** with fairness testing + legal alignment |
| Privacy / IP | Training data provenance, derivative works | **Critical uncertainty** — limited loss data, legal flux |
| Harmful content | Offensive / illegal generation | Bundled with performance / content moderation |
| **Environmental** | Parameter count → training energy | Listed as "other risk"; links DC power thesis |

**Structural difference from ML:** GenAI is unsupervised/semi-supervised; outputs are subjective; foundation-model updates cause **performance drift over time** (GPT-4 degradation cited).

---

## Underwriting recipe (juice for modellers)

1. **Scope to one task** — indiscriminate multi-use GenAI cannot hold a constant performance threshold.
2. **Define input space** — topic restrictions, format constraints.
3. **Define failure abstractly** — hallucination / false info / harmful content = underperformance vs encoded latent-space expectation (not single ground-truth label).
4. **Testing regime** — representative input-space sample; continuous human-feedback loop where data is sensitive (legal, medical, insurance).
5. **Transform to classical ML problem** — if damage occurs AND metrics breach threshold → payout.
6. **Foundation-model API users** — require provider continuous monitoring; policy tools:
   - **Pause guarantee** on detected degradation
   - **Adjust threshold** to hold risk constant
   - **Adjust premium** to match fluctuating exposure

Premium ∝ **robustness** from technical due diligence (see "De-Risking AI Ventures" companion paper).

---

## Implications for NFRI scoring

- **`pricing_modelling`** — Munich Re explicitly prices from model robustness quantification, not checkbox underwriting. Supports high preparedness rating when evidenced.
- **`data_monitoring`** — continuous monitoring is **required** for GenAI policies, not optional. Aligns with Parametrix/telemetry narrative for DC SLA cover.
- **`tenor_mismatch`** — foundation-model update cadence vs policy tenor is an explicit gap; policies must be **regularly updated**.
- **`trigger_gap`** — performance guarantees cover **non-damage financial loss** from model failure — analogous to parametric SLA insurance for curtailment (different trigger, same structure).
- **`aggregation_correlation`** — Munich Re flags **systematic, geographic spread** of GenAI class actions — supports correlated tail on large AI-exposed books.
- **Environmental link** — training energy consumption acknowledged; reinforces why AI DC assets sit on **non-firm** connections (power intensity × grid constraint).

---

## Quotes worth keeping

> "Insurance will become vital for a smooth and widespread adoption of GenAI."

> "Even the most accurate AI will produce wrong or misleading results from time to time."

> Pooling GenAI failure risk "enables active innovation … without worrying about the residual financial risks" and helps develop **industry standards** without overregulation.

---

## Gaps / not useful for NFRI (skip)

- Consumer GenAI hype stats (GDP %, occupation %)
- Detailed fairness metric taxonomy
- US case-law catalogue (Mata v. Avianca etc.) — background only
