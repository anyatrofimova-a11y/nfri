# Fixtures — parallel sprint stubs

Committed stub data for **all parallel streams**. Same schemas as production; tagged
`data_source: fixture`.

| File | Contract | Used by |
|------|----------|---------|
| `register_snapshot.json` | IC-02 | Ingestion, API, graph, pricing, active |
| `graph_edges.json` | IC-05 | Graph sprint, frontend explorer, stress |
| `pricing_request.json` | IC-06 | Pricing sprint, API |
| `pricing_response.json` | IC-06 | Pricing sprint, API |
| `curtailment_alert.json` | IC-07 | Active Availability sprint |
| `extraction_trigger_gap.json` | IC-03 | Document-AI golden set |

Validate:

```bash
python3 harness/platform/fixtures_check.py
python3 harness/platform/fixtures_check.py --strict
```

**Day 5 rule:** Sprint 1 freezes `register_snapshot.json` for the wave (patch versions only).
Live pulls replace fixture content in-place without schema changes.

See `PARALLEL_EXECUTION.md`.
