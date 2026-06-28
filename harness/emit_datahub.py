#!/usr/bin/env python3
"""Emit NFRI metadata to DataHub (optional catalog mirror).

Maps scored entities to datasets on platform ``nfri``, registers index files and
grid registers, and wires lineage where asset_link points at TEC/ECR.

Default is dry-run (prints summary). Use --emit with acryl-datahub installed and
DATAHUB_GMS_URL pointing at GMS (:8080), not the React UI (:9002).

  python3 harness/emit_datahub.py
  python3 harness/emit_datahub.py --manifest contract/datahub/emit_manifest.json
  DATAHUB_GMS_URL=http://localhost:8080 python3 harness/emit_datahub.py --emit

See contract/DATAHUB_INTEGRATION.md for the full mapping.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING_PATH = os.path.join(ROOT, "contract", "datahub", "mapping.json")
SCORED_PATH = os.path.join(ROOT, "data", "records.scored.json")


def _load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def _dataset_urn(platform: str, name: str, env: str = "PROD") -> str:
    return f"urn:li:dataset:(urn:li:dataPlatform:{platform},{name},{env})"


def _entity_urn(entity_id: str, cfg: dict) -> str:
    return _dataset_urn(cfg["platform"], entity_id, cfg["env"])


def _custom_properties(record: dict) -> Dict[str, str]:
    scores = record.get("scores") or {}
    prov = (record.get("provenance") or {}).get("evidence") or {}
    props = {
        "entity_type": str(record.get("entity_type", "")),
        "layer": str(record.get("layer", "")),
        "parent_group": str(record.get("parent_group") or ""),
        "hq_country": str(record.get("hq_country") or ""),
        "exposure_0_100": _fmt_num(scores.get("exposure_0_100")),
        "preparedness_0_100": _fmt_num(scores.get("preparedness_0_100")),
        "margin_of_safety": _fmt_num(scores.get("margin_of_safety")),
        "quadrant": str(scores.get("quadrant") or ""),
        "overall_confidence": str(scores.get("overall_confidence") or ""),
        "measured_disclosed_subfactors": str(prov.get("measured_disclosed_subfactors", "")),
        "total_subfactors": str(prov.get("total_subfactors", "")),
        "provenance_status": str(prov.get("status") or ""),
        "nfri_entity_id": str(record.get("entity_id", "")),
    }
    return {k: v for k, v in props.items() if v != ""}


def _fmt_num(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.1f}"
    return str(v)


def _tags_for_entity(record: dict, cfg: dict) -> List[str]:
    prefixes = cfg["tag_prefixes"]
    tags: List[str] = []
    layer = record.get("layer")
    if layer is not None:
        tags.append(f"{prefixes['layer']}{layer}")
    quadrant = (record.get("scores") or {}).get("quadrant")
    if quadrant:
        tags.append(f"{prefixes['quadrant']}{quadrant}")
    etype = record.get("entity_type")
    if etype:
        tags.append(f"{prefixes['entity_type']}{etype}")
    return tags


def _citation_tags(record: dict, cfg: dict) -> Set[str]:
    prefix = cfg["tag_prefixes"]["citation"]
    ids: Set[str] = set()
    blend = (record.get("scores") or {}).get("blend") or {}
    for axis in ("exposure_sub_factors", "preparedness_sub_factors"):
        for sf in (blend.get(axis) or {}).values():
            for cid in sf.get("citation_ids") or []:
                ids.add(f"{prefix}{cid}")
    return ids


def _register_urn_for_asset_link(asset_link: dict, cfg: dict) -> Optional[str]:
    if not asset_link:
        return None
    key = (asset_link.get("source") or asset_link.get("register") or "").lower()
    reg_map = cfg.get("asset_link_register_map") or {}
    hit = reg_map.get(key)
    if not hit:
        return None
    return _dataset_urn(hit["platform"], hit["name"], cfg["env"])


def build_plan(
    records: List[dict],
    cfg: dict,
    *,
    with_memory: bool = False,
    with_citation_tags: bool = True,
) -> dict:
    """Build emission plan: entities, index files, registers, lineage edges."""
    entities: List[dict] = []
    lineage: List[dict] = []
    scored_json_urn = _dataset_urn("file", "site/data/records.scored.json", cfg["env"])

    for rec in records:
        eid = rec["entity_id"]
        urn = _entity_urn(eid, cfg)
        tags = _tags_for_entity(rec, cfg)
        if with_citation_tags:
            tags.extend(sorted(_citation_tags(rec, cfg)))

        entry: Dict[str, Any] = {
            "urn": urn,
            "name": rec.get("name", eid),
            "description": (rec.get("notes") or "")[:2000],
            "customProperties": _custom_properties(rec),
            "tags": tags,
        }
        if with_memory:
            urls = _evidence_urls(rec)
            if urls:
                entry["institutionalMemoryUrls"] = urls[:20]
        entities.append(entry)

        lineage.append({"downstream": urn, "upstream": scored_json_urn, "type": "derivation"})

        reg_urn = _register_urn_for_asset_link(rec.get("asset_link"), cfg)
        if reg_urn:
            lineage.append({"downstream": urn, "upstream": reg_urn, "type": "register_measured"})

    index_datasets = []
    for spec in cfg.get("index_datasets") or []:
        path = os.path.join(ROOT, spec["path"])
        index_datasets.append({
            "urn": _dataset_urn(spec["platform"], spec["name"], cfg["env"]),
            "name": spec["name"],
            "description": spec.get("description", ""),
            "path": spec["path"],
            "exists": os.path.isfile(path),
        })

    registers = []
    for spec in cfg.get("register_datasets") or []:
        registers.append({
            "urn": _dataset_urn(spec["platform"], spec["name"], cfg["env"]),
            "name": spec["name"],
            "description": spec.get("description", ""),
            "adapter": spec.get("adapter", ""),
        })

    return {
        "version": cfg.get("version", "0.1"),
        "gms_url": os.environ.get("DATAHUB_GMS_URL", cfg.get("gms_url_default")),
        "entity_count": len(entities),
        "lineage_edge_count": len(lineage),
        "entities": entities,
        "index_datasets": index_datasets,
        "register_datasets": registers,
        "lineage": lineage,
    }


def _evidence_urls(record: dict) -> List[str]:
    urls: List[str] = []
    for block in (record.get("exposure_inputs") or {}).values():
        urls.extend(block.get("sources") or [])
    for block in (record.get("preparedness_inputs") or {}).values():
        urls.extend(block.get("sources") or [])
    seen: Set[str] = set()
    out: List[str] = []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _print_summary(plan: dict) -> None:
    print(f"NFRI → DataHub emission plan (dry-run)")
    print(f"  GMS target:     {plan['gms_url']}")
    print(f"  Entities:       {plan['entity_count']}")
    print(f"  Lineage edges:  {plan['lineage_edge_count']}")
    print(f"  Index files:    {len(plan['index_datasets'])}")
    print(f"  Registers:      {len(plan['register_datasets'])}")
    missing = [d["path"] for d in plan["index_datasets"] if not d["exists"]]
    if missing:
        print(f"  WARN missing:   {', '.join(missing)}")
    reg_lineage = sum(1 for e in plan["lineage"] if e["type"] == "register_measured")
    print(f"  Register links: {reg_lineage}")
    sample = plan["entities"][:3]
    if sample:
        print("  Sample URNs:")
        for e in sample:
            mos = e["customProperties"].get("margin_of_safety", "?")
            print(f"    {e['urn']}  MoS={mos}")


def _emit_to_datahub(plan: dict, server: str) -> Tuple[int, int]:
    """Push plan to GMS. Returns (ok_count, err_count)."""
    try:
        from datahub.emitter.mce_builder import make_dataset_urn
        from datahub.emitter.mcp import MetadataChangeProposalWrapper
        from datahub.emitter.rest_emitter import DatahubRestEmitter
        from datahub.metadata.schema_classes import (
            DatasetPropertiesClass,
            GlobalTagsClass,
            TagAssociationClass,
            TagPropertiesClass,
            UpstreamClass,
            UpstreamLineageClass,
        )
    except ImportError as exc:
        print(
            "ERROR: acryl-datahub not installed. Run:\n"
            "  pip install 'acryl-datahub[datahub-rest]'",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    emitter = DatahubRestEmitter(server)
    ok, err = 0, 0

    def emit_mcp(mcp: MetadataChangeProposalWrapper) -> None:
        nonlocal ok, err
        try:
            emitter.emit_mcp(mcp)
            ok += 1
        except Exception as e:  # noqa: BLE001 — surface per-aspect failures
            err += 1
            print(f"  FAIL {mcp.entityUrn}: {e}", file=sys.stderr)

    def emit_dataset_meta(urn: str, name: str, description: str, custom: dict) -> None:
        props = DatasetPropertiesClass(
            name=name,
            description=description or None,
            customProperties=custom or None,
        )
        emit_mcp(MetadataChangeProposalWrapper(entity_urn=urn, aspect=props))

    def emit_tags(urn: str, tags: Iterable[str]) -> None:
        tag_list = [
            TagAssociationClass(tag=TagPropertiesClass(name=t)) for t in tags if t
        ]
        if tag_list:
            emit_mcp(
                MetadataChangeProposalWrapper(
                    entity_urn=urn, aspect=GlobalTagsClass(tags=tag_list)
                )
            )

    def emit_upstream(downstream: str, upstreams: List[str]) -> None:
        if not upstreams:
            return
        upstream_objs = [UpstreamClass(dataset=u) for u in upstreams]
        emit_mcp(
            MetadataChangeProposalWrapper(
                entity_urn=downstream,
                aspect=UpstreamLineageClass(upstreams=upstream_objs),
            )
        )

    # Index + register stubs (properties only)
    for spec in plan["index_datasets"] + plan["register_datasets"]:
        emit_dataset_meta(
            spec["urn"],
            spec.get("name", spec["urn"]),
            spec.get("description", ""),
            {"nfri_kind": "index" if "path" in spec else "register"},
        )

    # Entities
    upstream_by_down: Dict[str, List[str]] = {}
    for edge in plan["lineage"]:
        upstream_by_down.setdefault(edge["downstream"], []).append(edge["upstream"])

    for ent in plan["entities"]:
        urn = ent["urn"]
        emit_dataset_meta(urn, ent["name"], ent.get("description", ""), ent["customProperties"])
        emit_tags(urn, ent.get("tags") or [])
        emit_upstream(urn, upstream_by_down.get(urn, []))

    emitter.close()
    return ok, err


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--records",
        default=SCORED_PATH,
        help="Path to records.scored.json (default: data/records.scored.json)",
    )
    parser.add_argument(
        "--manifest",
        metavar="PATH",
        help="Write full emission plan JSON to PATH",
    )
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Push aspects to DataHub GMS (requires acryl-datahub)",
    )
    parser.add_argument(
        "--with-memory",
        action="store_true",
        help="Include evidence URLs as institutional memory (emit only)",
    )
    parser.add_argument(
        "--no-citation-tags",
        action="store_true",
        help="Skip nfri:citation:* tags derived from blend citation_ids",
    )
    args = parser.parse_args(argv)

    cfg = _load_json(MAPPING_PATH)
    records = _load_json(args.records)
    if not isinstance(records, list):
        print("ERROR: records file must be a JSON array", file=sys.stderr)
        return 1

    plan = build_plan(
        records,
        cfg,
        with_memory=args.with_memory,
        with_citation_tags=not args.no_citation_tags,
    )

    if args.manifest:
        out_path = args.manifest
        if not os.path.isabs(out_path):
            out_path = os.path.join(ROOT, out_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"Wrote manifest: {out_path}")

    if args.emit:
        server = plan["gms_url"]
        print(f"Emitting to {server} …")
        ok, err = _emit_to_datahub(plan, server)
        print(f"Done: {ok} aspects OK, {err} failed")
        return 1 if err else 0

    _print_summary(plan)
    print("\nNext: pip install 'acryl-datahub[datahub-rest]' && DATAHUB_GMS_URL=… python3 harness/emit_datahub.py --emit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
