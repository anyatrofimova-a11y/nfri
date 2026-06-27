---
name: reconcile-and-bank
description: >
  Consolidate the NFRI pipeline into a consistent, gate-passing state — reconcile the dormant
  non_firm_compute_exposure rubric factor (the recurring harness-crash root cause), bank disclosed
  FSR/SCR durably INTO records.json so re-scoring can't drop it, stamp per-entity provenance, and
  verify the gate suite. Use after a universe expansion, when evals.py / optimize.py / stress_test.py
  crash with `KeyError: 'non_firm_compute_exposure'`, when banked disclosed evidence keeps disappearing
  from records.optimized, or to bring a clobbered/concurrently-edited tree back to green. Enforces the
  no-synthetic-data policy.
---

# Reconcile & Bank — NFRI pipeline consolidation

A single-writer pass that fixes the two structural problems that recur every time the universe is
expanded or the tree is edited by multiple writers at once.

## When to use
- `evals.py` / `optimize.py` / `harness/stress_test.py` crash with `KeyError: 'non_firm_compute_exposure'`.
- The publication-gate eval (L5) shows banked disclosed evidence vanishing after a re-score.
- After adding entities (universe expansion) — the new carriers' disclosed FSR/SCR are not yet banked.
- To consolidate after parallel writers clobbered each other (run this as the **sole writer**).

> **Process note (learned the hard way):** these fixes only stick if ONE actor edits the tree at a
> time. If multiple agents/Cursor are writing concurrently, code fixes get reverted within minutes
> (data in `records.json` survives because it's idempotent; harness code does not). Freeze the tree —
> pause other agents — before running this skill.

---

## Problem 1 — the dormant L3 factor that crashes the harness

`contract/rubric.json` lists a 6th exposure sub-factor **`non_firm_compute_exposure`** (weight 0.25,
`include_layers:[3]`) that is meant to *replace* `non_firm_intensity` at Layer 3. But **no record
carries it** (it is dormant), so:
- the exposure weights sum to **1.25**, not 1.0, and
- every naive `for k in RUBRIC["exposure"]: inp[k]` does a **KeyError** on records that lack the key.

### Fix: make every harness rubric-iteration layer-aware (skip absent / `include_layers` keys)

Apply this guard pattern everywhere a harness sums or indexes rubric keys. The base axis then sums to
1.0 and nothing crashes (the L3 compute factor 1:1 replaces non_firm_intensity at its own layer):

```python
# weighted axis — skip sub-factors absent on this record
def axis(inp, cfg):
    return round(sum(c["weight"]*(inp[k]["rating_0_4"]/4) for k, c in cfg.items() if k in inp)*100, 1)

# gate / tier loop — skip absent sub-factor before indexing
for k, c in cfg.items():
    if k not in r[ax]:        # layer-conditional factor absent
        continue
    ...

# golden-math fixture / weight-ceiling math — iterate BASE keys only
BASE_EXP = {k: c for k, c in RUBRIC["exposure"].items() if not c.get("include_layers")}

# completeness check — require the BASE keys, not all keys
keys_e = {k for k, c in RUBRIC["exposure"].items() if not c.get("include_layers")}
```

**Checklist of files that have crashed on this** (guard each; some may already be fixed upstream):
- `harness/evals.py` — L2 `keys_e`, L3 `axis()`, L5 tier loop (`r[ax][k]`), L6 golden fixture `gx`.
- `harness/optimize.py` — `axis()` (or normalise weight over present keys).
- `harness/stress_test.py` — `EXP_W`/`PREP_W` derivation, S4 `axis_score()`.
- `harness/industry_stress.py` — any structural-check rubric iteration.

> **Alternative (cleaner, if you own the rubric):** decide what `non_firm_compute_exposure` *is*.
> Either (a) remove it from the base exposure block (it is unused) so the sum is 1.0 and no guards are
> needed, or (b) actually wire it into L3 records (derived from `non_firm` × compute load) and give the
> scorer a proper layer-aware weight swap. Until one of those lands, the guards above are required.

---

## Problem 2 — disclosed evidence keeps getting dropped on re-score

`measure_capital.py --live` / ECR ingest historically wrote disclosed tiers to `records.optimized`
*after* scoring, so every re-score and every universe expansion dropped them. The durable fix is to
bank disclosed values **into `records.json` itself** (the source the scorer reads), where re-scoring
preserves them.

### Fix: run the banking harness

```bash
python3 harness/integrate_entities.py           # bank disclosed capital/book INTO records.json
# optionally merge new sourced entities at the same time:
python3 harness/integrate_entities.py path/to/new_entities1.json path/to/new_entities2.json
```

`harness/integrate_entities.py` (idempotent, no-synthetic-enforcing):
1. Banks disclosed FSR/SCR from `contract/capital_inputs.json` (and book from `contract/book_inputs.json`)
   into each record's `capital_reinsurance` / `book_concentration` as `evidence_tier:disclosed` — so the
   tier survives re-scoring.
2. Merges new entity JSON arrays, deduping by `entity_id`, rejecting any record that violates the
   no-synthetic rule (a rating ≥1 with no source).
3. Stamps each record with **`provenance.evidence`** = `{measured, disclosed, assessed, status}` — the
   per-entity provenance schema (status ∈ measured / partial / assessed).

---

## Per-entity provenance → replace the blanket PROVISIONAL banner

The blanket "⚠ PROVISIONAL — assessed-tier prototype" banner is dishonest at the blanket level and
alarmist. Use the per-entity `provenance.evidence.status` instead: each entity shows its own evidence
tier; the global banner becomes a neutral factual line. The gate banner renders from **three** places —
change all three or the old text persists:
- `harness/frontend/client.py` — the JS `#banner` block.
- `harness/frontend/chrome.py` — `render_hero_gate` (server-side hero gate).
- `harness/frontend/template.py` — any "PROVISIONAL until …" prose.

Then rebuild: `cd harness && python3 -m frontend.assemble`.

---

## The consolidation run (do these in order, as the sole writer)

```bash
cd ~/Developer/nfri
git pull origin framework                       # start from the latest

# 1. guard / reconcile the dormant factor (Problem 1) — edit the files in the checklist
# 2. bank disclosed + stamp provenance (Problem 2)
python3 harness/integrate_entities.py
# 3. re-score from the banked source
python3 harness/score_and_validate.py
python3 harness/optimize.py
# 4. (optional) reconcile the banner across the 3 frontend modules, then rebuild
cd harness && python3 -m frontend.assemble && cd ..
# 5. verify — gate must at least RUN (L5 stays an honest FAIL until measured share ≥ 60%)
python3 harness/run_loop.py
python3 harness/evals.py data/records.optimized.json

git add -A && git commit -m "Reconcile pipeline + bank disclosed (single-writer pass)" && git push origin framework
```

## Acceptance / what "done" looks like
- `evals.py` **runs** (no KeyError); L0–L4, L6 PASS; L6 golden = 100/0 (base axis sums to 1.0).
- `records.optimized.json` carries the banked `evidence_tier:disclosed` carriers (count matches
  `contract/capital_inputs.json`); the count survives a second re-score.
- L5 reports the honest blended measured/disclosed share. **L5 staying FAIL is correct** — the 60%
  publication gate cannot clear without live registers/filings; never delete the provenance signal to
  force a pass (no-synthetic rule).
- The site banner reflects per-entity provenance, not a blanket warning.

## Invariants (never violate)
- **No synthetic data** — never invent a rating or a measured value; a rating ≥1 must carry a real
  source; disclosed tiers must trace to a filing/rating (`contract/DATA_POLICY.md`).
- **Bank into the source** (`records.json`), not into derived files — derived files are regenerated.
- **L5 is honest** — the gate is allowed to fail; that failure is the product telling the truth.
