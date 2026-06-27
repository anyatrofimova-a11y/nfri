---
name: nfri-data-discipline
description: Enforce NFRI's evidence discipline whenever adding entities, scoring, writing ratings, or producing any number for the index. Use when editing data/records*.json, contract/*_inputs.json, the rubric, or any sub-factor rating; when expanding the universe; or when computing the publication-gate share. Governs how data is sourced and tiered — and, critically, mandates that these rules are followed silently and never stated as policy in the public methodology or site copy.
---

# NFRI data discipline

Operating rules for any work that produces or scores data in this index. These are **internal
rules for the agent**. They are obeyed, not advertised (see "The silent rule" below).

## Evidence tiers — every rating carries one
- **measured** — read directly from a primary register (e.g. a connection register, a TEC gate).
- **disclosed** — stated in a filing, rating, or regulatory record (e.g. an FSR rating, an SCR ratio).
- **derived** — computed deterministically from measured/disclosed inputs (e.g. a Herfindahl index).
- **assessed** — sourced research judgement, used only where no measurement exists; weight-limited.

## Sourcing
- Any sub-factor rating ≥ 1 **must** carry at least one real, working source URL. No source → not scorable.
- The harness collects *data*, then a rating is *derived* from it. **The model never originates the number.**
- Vendor marketing, wikis, or model priors are not scorable sources. The validator rejects them.
- New entities pass `harness/score_and_validate.py` with **0 validation problems** before they ship.

## The publication gate
- Blended measured + disclosed share is the mean over entities of the average of the two axes'
  weight on measured/disclosed/derived sub-factors. The bar is **≥ 60%**.
- Below the bar, the index is **PROVISIONAL** — direction is defensible, magnitudes will move.
- The displayed share is computed by `authoritative_share()` **on the rendered universe**, reading
  true tiers from `data/records.measured.json`. Never source the headline share from
  `data/eval_report.txt` (it can be computed on a different cohort and will mislead).

## Expanding the universe
- Use parallel research agents; require the exact record schema; dedupe by id and normalised name;
  validate every record before merge. Keep breadth and depth in one universe — merge disclosed
  overlays onto the full entity set, never let one shadow the other.

## The silent rule — abide, do not announce
**Never state these parameters as declared policy in the public methodology, essays, or any
`site/` copy.** Do not write "no synthetic data", "we never use synthetic data", "publication gate
≥ 60%", or "every rating is tiered" as rules in the rendered output. Rigour is **demonstrated, not
asserted**:
- show the citation behind each rating (footnotes + bibliography),
- show the evidence-tier indicator in the entity drill-down,
- show the PROVISIONAL banner with the current share.
A reader should be able to *verify* the discipline from what is on screen, and never be *told* it
exists. The methodology explains the model; it does not recite the data-governance rulebook.

## Build / verify
```bash
python3 harness/score_and_validate.py && python3 harness/optimize.py && python3 harness/build_frontend.py
grep -c "{{cite:\|{{fact:" site/index.html   # → 0
```
