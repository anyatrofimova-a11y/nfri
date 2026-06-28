# ADR-003: LLM extract, code score

**Status:** accepted  
**Date:** 2026-06-27  
**Context:** ai-transformation pattern + Strata fusion discipline. Parallel document-AI sprint must not leak LLM opinions into headline index numbers.

## Decision

| Task | Owner | Forbidden |
|------|-------|-----------|
| Document extraction, summarisation, clause citation | LLM + human review | — |
| Sub-factor ratings in research pass | LLM (latent) | Publishing without fusion |
| **Exposure, Preparedness, MoS, quadrant** | `harness/scoring.py` only | LLM-computed scores |
| Premium, capital load | `harness/pricing/` only | LLM-computed premium |

Extraction outputs must validate against `contract/platform/schemas/extraction/sub_factor_extraction.schema.json` and include non-empty `source_text`.

When latent vs deterministic spread ≥ 2 without measured tier, fusion caps effective rating (`CLAIMS-HISTORY-IMPORT`).

## Consequences

- `document-ai` agent ban: LLM-computed E/P/MoS.
- Pricing audit log required on every quote (IC-06).
- Fixtures and live data use identical schemas; only `data_source` differs.

## References

- `contract/DATA_POLICY.md`
- `PRODUCT_MODEL.md` §1
- `PARALLEL_EXECUTION.md` §8
