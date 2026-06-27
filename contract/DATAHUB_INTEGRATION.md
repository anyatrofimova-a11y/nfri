# NFRI ↔ DataHub integration

How to publish NFRI index metadata into [DataHub](https://github.com/datahub-project/datahub) so it sits alongside warehouse/catalog assets — queryable via GraphQL, MCP, and the analytics agent.

NFRI remains the **source of truth** for scoring. DataHub is a **read-side catalog** for discovery, lineage, and AI context.

## Architecture

```
NESO TEC / DNO ECR          harness/scoring.py
        │                            │
        ▼                            ▼
  register datasets            NFRI entity datasets
  (platform: neso, ukpn)       (platform: nfri)
        │                            │
        └──────── lineage ───────────┘
                     │
                     ▼
              DataHub GMS (:8080)
                     │
         GraphQL / MCP / analytics-agent
```

## Entity mapping

NFRI entities are **not** native DataHub types (no `Insurer` PDL entity). Map each scored record to a **dataset** on custom platform `nfri`:

| NFRI field | DataHub aspect | Notes |
|---|---|---|
| `entity_id` | URN name segment | `urn:li:dataset:(urn:li:dataPlatform:nfri,{entity_id},PROD)` |
| `name` | `datasetProperties.name` | Display name |
| `entity_type`, `layer`, `parent_group` | `datasetProperties.customProperties` | Filterable key/value |
| `scores.*` | `customProperties` | `exposure_0_100`, `preparedness_0_100`, `margin_of_safety`, `quadrant` |
| `provenance.evidence` | `customProperties` | measured/disclosed counts |
| `notes` | `datasetProperties.description` | Executive one-liner |
| `layer` | Global tag `nfri:layer-{n}` | |
| `quadrant` | Global tag `nfri:quadrant-{name}` | whitespace / exposed / … |
| `entity_type` | Global tag `nfri:type-{type}` | insurer, data_centre, … |
| Source URLs | `institutionalMemory` | Evidence links (optional `--with-memory`) |
| `asset_link.register_ref` | `upstreamLineage` | L3 asset ← TEC/ECR register row |

### Index artifacts (file datasets)

| Artifact | URN |
|---|---|
| Public CSV | `urn:li:dataset:(urn:li:dataPlatform:file,site/data/dataset.csv,PROD)` |
| Scored JSON | `urn:li:dataset:(urn:li:dataPlatform:file,site/data/records.scored.json,PROD)` |
| Knowledge graph | `urn:li:dataset:(urn:li:dataPlatform:file,contract/knowledge/graph.json,PROD)` |

Emit **lineage**: `records.scored.json` → each `nfri` entity dataset (derivation).

### Register sources (upstream)

| Register | URN | NFRI adapter |
|---|---|---|
| NESO TEC | `urn:li:dataset:(urn:li:dataPlatform:neso,tec-register,PROD)` | `harness/adapters.py::neso_tec` |
| UKPN ECR | `urn:li:dataset:(urn:li:dataPlatform:ukpn,embedded-capacity-register,PROD)` | `ukpn_ecr` |
| NPG national ECR | `urn:li:dataset:(urn:li:dataPlatform:npg,ecr-national-combine,PROD)` | `npg_ecr` |

Lineage rule: when `asset_link.source` is `neso_tec` or `ecr`, emit `register URN → nfri entity URN`.

### Knowledge graph citations

Citation nodes in `contract/knowledge/graph.json` map to **tags** on entity datasets when `scores.blend.*.citation_ids` overlap:

- Tag format: `nfri:citation:{CITATION_ID}` (e.g. `nfri:citation:NESO-CMP434`)

Full graph remains in NFRI; DataHub carries only the entity↔citation edges needed for search.

## Harness

```bash
# Preview emission plan (no DataHub required)
python3 harness/emit_datahub.py

# Write manifest JSON for review
python3 harness/emit_datahub.py --manifest contract/datahub/emit_manifest.json

# Push to local GMS (requires acryl-datahub)
pip install 'acryl-datahub[datahub-rest]'
export DATAHUB_GMS_URL=http://localhost:8080   # GMS, not :9002 UI
python3 harness/emit_datahub.py --emit
```

Dry-run is the default. `--emit` never runs inside `run_loop.py` (external catalog is opt-in).

## GraphQL examples (post-ingest)

**Worst MoS carriers (layer 1):**

```graphql
{
  search(input: {
    type: DATASET,
    query: "*",
    filters: [
      { field: "platform", values: ["nfri"] },
      { field: "tags", values: ["nfri:layer-1"] }
    ]
  }) {
    searchResults {
      entity {
        urn
        ... on Dataset {
          name
          properties { customProperties }
        }
      }
    }
  }
}
```

Sort/filter on `customProperties.margin_of_safety` in application code or analytics-agent.

**Lineage for a data centre asset:**

```graphql
query AssetLineage {
  dataset(urn: "urn:li:dataset:(urn:li:dataPlatform:nfri,asset-kao-harlow,PROD)") {
    upstream: lineage(input: { direction: UPSTREAM, maxHops: 2 }) {
      entities { urn ... on Dataset { name platform { name } } }
    }
  }
}
```

## MCP + analytics agent

After ingest:

```bash
npx -y @acryldata/mcp-server-datahub init   # point at same GMS
```

Analytics agent (`datahub-project/analytics-agent`) can then answer questions grounded in NFRI custom properties **if** the index CSV is also registered with column schema.

## What stays in NFRI only

| Concern | Why not DataHub |
|---|---|
| Scoring / fusion math | Deterministic harness; not catalog metadata |
| Publication gate (L5) | NFRI policy in `contract/DATA_POLICY.md` |
| Full knowledge graph edges | 58 typed edges; export tags only |
| Live register pulls | NFRI adapters own freshness; DataHub mirrors lineage |

## Future: native custom entity

If NFRI grows beyond ~500 entities with rich cross-entity relationships, consider a **custom PDL entity** (`NfriEntity`) in a forked metadata-models patch. Until then, `nfri` platform datasets keep integration cost low and work with stock DataHub.
