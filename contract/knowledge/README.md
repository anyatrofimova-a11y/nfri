# NFRI knowledge base

Curated extracts and a **structured knowledge graph** for data-centre exposure, non-firm grid connection, pricing models, and placement.

| Artifact | Purpose |
|---|---|
| [`graph.json`](graph.json) | Nodes (sources, CRIs, products, registers, models) + typed edges |
| [`graph.schema.json`](graph.schema.json) | JSON schema for graph extensions |
| [`che-castaldo-grid-cri-sri.md`](che-castaldo-grid-cri-sri.md) | Anchor extract + graph integration (CRI→SRI framework) |
| [`sources/`](sources/) | Per-source juice extracts |

## Query the graph

```bash
python3 harness/knowledge_graph.py topics
python3 harness/knowledge_graph.py topic dc_exposure
python3 harness/knowledge_graph.py path register-ecr parametrix-sla-dc
python3 harness/knowledge_graph.py neighbours che-castaldo-grid-cri-sri
```

## Topic clusters

| ID | Focus |
|---|---|
| `systemic_risk` | Che-Castaldo CRIs → SRIs, Lloyd's RDS stress |
| `grid_firmness` | NESO Gate reform, TEC/ECR registers, reserve margin |
| `dc_exposure` | SLA/NDBI, Parametrix, Descartes, Marsh Nimbus, EPIC |
| `pricing_models` | Basis risk, compound loss, credibility fusion, parametric |
| `placement` | Facilities, value-chain bundling, broker chain |
| `correlation` | Liu AI–energy DCC, finance–grid CRIs |

## Extract index

| Note | Graph node | Citation ID |
|---|---|---|
| [che-castaldo-grid-cri-sri.md](che-castaldo-grid-cri-sri.md) | `che-castaldo-grid-cri-sri` | `ACAD-CRI-GRID-SRI` |
| [monterde-nonfirm-grid-review.md](monterde-nonfirm-grid-review.md) | `acad-nonfirm-review` | `ACAD-NONFIRM-REVIEW` |
| [liu-ai-energy-correlation.md](liu-ai-energy-correlation.md) | `liu-ai-energy-dcc` | `ACAD-AI-ENERGY-DCC` |
| [munichre-genai-insurance.md](munichre-genai-insurance.md) | `munichre-genai` | `MUNICHRE-GENAI-WP` |
| [sources/instech-ndbi-parametric.md](sources/instech-ndbi-parametric.md) | `instech-ndbi-parametric` | `INSTECH-NDBI-PARAMETRIC` |
| [sources/epic-dc-energy-risk.md](sources/epic-dc-energy-risk.md) | `epic-dc-energy-risk` | `EPIC-DC-ENERGY-RISK` |
| [sources/descartes-dc-parametric.md](sources/descartes-dc-parametric.md) | `descartes-dc-parametric` | `DESCARTES-DC-PARAMETRIC` |
| [sources/parametrix-sla-dc.md](sources/parametrix-sla-dc.md) | `parametrix-sla-dc` | `MGA-PARAMETRIX-SLA` |

All nodes with `citation_id` resolve to [`../citations.json`](../citations.json) (66 entries as of v0.2).

## Adding a source

1. Add entry to `contract/citations.json`
2. Add node + edges to `graph.json` (validate against `graph.schema.json`)
3. Optional extract under `sources/<slug>.md`
4. Link from relevant anchor extract (e.g. `che-castaldo-grid-cri-sri.md`)
