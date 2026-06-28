"""Accumulation graph — scenario propagation for industry stress tests.

RDS acceptance test: correlated curtailment must produce material MoS compression on
cluster-linked entities. Stress overrides measured_value (simulation), not headline ratings.

Graph layer is Phase 2 in BUILD_SEQUENCE.md.
"""
from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Set

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_GRAPH = os.path.join(ROOT, "data", "fixtures", "graph_edges.json")

# Constraint zones in correlated RDS (South Wales + East of England cluster)
RDS_ZONES = frozenset({"east_england", "south_wales", "wiltshire", "oxfordshire"})


def load_graph(path: Optional[str] = None) -> dict:
    p = path or DEFAULT_GRAPH
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _zones_for_record(rec: dict) -> Set[str]:
    agg = rec.get("exposure_inputs", {}).get("aggregation_correlation", {})
    mv = agg.get("measured_value") or {}
    zones: Set[str] = set()
    for key in ("zones", "zone_shares"):
        block = mv.get(key) or {}
        if isinstance(block, dict):
            zones.update(k for k, v in block.items() if v)
    cz = agg.get("constraint_zone") or rec.get("constraint_zone")
    if isinstance(cz, str):
        for z in RDS_ZONES:
            if z.replace("_", " ") in cz.lower() or z in cz.lower():
                zones.add(z)
    return zones


def cluster_entity_ids(
    records: List[dict],
    graph: Optional[dict] = None,
    zones: Iterable[str] = RDS_ZONES,
) -> Set[str]:
    """L3 assets in RDS constraint geography + graph scenario seeds."""
    zone_set = set(zones)
    cluster: Set[str] = set()
    by_id = {r["entity_id"]: r for r in records}

    for rec in records:
        if rec.get("layer") != 3:
            continue
        if _zones_for_record(rec) & zone_set:
            cluster.add(rec["entity_id"])

    graph = graph or load_graph()
    for sc in graph.get("stress_scenarios", []):
        if sc.get("id") != "RDS-CORRELATED-CURTAILMENT":
            continue
        for eid in sc.get("seed_nodes", []):
            if eid in by_id:
                cluster.add(eid)
        for edge in graph.get("edges", []):
            if edge.get("type") != "accumulation_group":
                continue
            gid = edge.get("group_id")
            if any(
                e.get("accumulation_group_id") == gid
                for e in graph.get("nodes", [])
                if e.get("id") in cluster
            ):
                cluster.add(edge.get("from", ""))

    # Propagate to L1/L2 with explicit graph edges
    if graph:
        for edge in graph.get("edges", []):
            et = edge.get("type")
            if et in ("cedant_exposure", "placement") and edge.get("to") in cluster:
                cluster.add(edge.get("from", ""))
            if et == "shared_dependency" and (
                edge.get("from") in cluster or edge.get("to") in cluster
            ):
                cluster.add(edge.get("from", ""))
                cluster.add(edge.get("to", ""))

    return {eid for eid in cluster if eid in by_id}


def _set_measured_share(sf: dict, share: float) -> None:
    mv = sf.get("measured_value")
    if isinstance(mv, dict):
        sf["measured_value"] = {**mv, "share": share}
    else:
        sf["measured_value"] = share
    sf["evidence_tier"] = sf.get("evidence_tier") or "measured"
    sf.pop("deterministic_rating_0_4", None)


def _set_measured_hhi(sf: dict, hhi: float = 1.0) -> None:
    mv = sf.get("measured_value")
    if isinstance(mv, dict):
        sf["measured_value"] = {**mv, "hhi": hhi}
    else:
        sf["measured_value"] = {"hhi": hhi}
    sf["evidence_tier"] = sf.get("evidence_tier") or "derived"
    sf.pop("deterministic_rating_0_4", None)


def apply_rds_stress(
    records: List[dict],
    graph_path: Optional[str] = None,
) -> List[dict]:
    """Apply Lloyd's RDS correlated curtailment via measured-value stress overrides."""
    out = copy.deepcopy(records)
    graph = load_graph(graph_path)
    cluster = cluster_entity_ids(out, graph)

    for rec in out:
        eid = rec["entity_id"]
        layer = rec.get("layer")
        exp = rec.setdefault("exposure_inputs", {})

        # Portfolio-wide aggregation spike under single constraint event
        agg = exp.setdefault("aggregation_correlation", {})
        _set_measured_hhi(agg, 1.0)

        if layer == 3 and eid in cluster:
            nf_key = "non_firm_compute_exposure" if "non_firm_compute_exposure" in exp else "non_firm_intensity"
            nf = exp.setdefault(nf_key, {})
            _set_measured_share(nf, 1.0)
            nf["latent_rating_0_4"] = 4
            nf["rating_0_4"] = 4

        elif layer in (1, 2):
            nf = exp.get("non_firm_intensity")
            if nf and nf.get("measured_value") is not None:
                _set_measured_share(nf, 1.0)
            else:
                nf = exp.setdefault("non_firm_intensity", {})
                nf["latent_rating_0_4"] = 4
                nf["rating_0_4"] = 4
            if eid in cluster:
                bc = exp.setdefault("book_concentration", {})
                bc["latent_rating_0_4"] = max(int(bc.get("latent_rating_0_4", bc.get("rating_0_4", 2))), 3)
                bc["rating_0_4"] = max(int(bc.get("rating_0_4", 2)), 3)

    return out


def propagate_scenario(
    records: List[dict],
    scenario_id: str,
    graph_path: Optional[str] = None,
) -> List[dict]:
    if scenario_id == "RDS-CORRELATED-CURTAILMENT":
        return apply_rds_stress(records, graph_path)
    raise ValueError(f"unknown graph scenario: {scenario_id}")


def enrich_graph_geography(graph: Optional[dict] = None) -> dict:
    """Join L3 node constraint zones from contract/asset_boundary_map.json."""
    graph = copy.deepcopy(graph or load_graph())
    boundary_path = os.path.join(ROOT, "contract", "asset_boundary_map.json")
    if not os.path.isfile(boundary_path):
        return graph
    assets = json.load(open(boundary_path, encoding="utf-8")).get("assets", {})
    for node in graph.get("nodes", []):
        eid = node.get("id")
        if eid in assets:
            node["constraint_zone"] = assets[eid]
    return graph
