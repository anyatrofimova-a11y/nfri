#!/usr/bin/env python3
"""Divide L3 expansion targets by industry segment and deploy swarm bot batches.

Cross-industry fan-out: data_centre · energy_asset · storage_asset each get their own
parallel subagent batch so asset_researcher bots stay focused.

  python3 harness/divide_swarm_targets.py status
  python3 harness/divide_swarm_targets.py divide --write
  python3 harness/divide_swarm_targets.py deploy          # print bot prompts
  python3 harness/divide_swarm_targets.py integrate       # merge net-new → records.json
  python3 harness/divide_swarm_targets.py cycle --write   # divide + integrate + rebuild hint

Sources:
  data/expansion_nonfirm_assets.json  — researched queue (primary)
  data/l3_expansion/targets_pending.json — seed IDs for future bot runs (optional)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPANSION = os.path.join(ROOT, "data", "expansion_nonfirm_assets.json")
PENDING = os.path.join(ROOT, "data", "l3_expansion", "targets_pending.json")
BATCH_DIR = os.path.join(ROOT, "data", "l3_expansion")
MANIFEST = os.path.join(BATCH_DIR, "manifest.json")
RECORDS = os.path.join(ROOT, "data", "records.json")
PY = sys.executable

PASS = "l3_expansion"
BATCH_SIZE = 8

# Expansion entity_id → canonical id already in records.json (skip duplicate research)
ALIASES: dict[str, str] = {
    "asset-ntt-london1-dagenham": "ntt-london1-dagenham",
    "asset-virtus-london": "virtus-stockley-park-hayes",
    "asset-equinix-london-ld": "equinix-london-ld-series",
    "asset-global-switch-london": "global-switch-london-docklands",
    "asset-yondr-slough-london": "yondr-slough-london",
    "asset-cyrusone-london-slough": "cyrusone-lon6-iver-heath",
    "asset-stellium-newcastle": "stellium-newcastle",
    "asset-harmony-pillswood-bess": "harmony-energy-pillswood-hull",
    "asset-zenobe-capenhurst-bess": "zenobe-capenhurst-chester",
    "asset-statera-thurrock-storage-bess": "statera-thurrock-storage-essex",
    "asset-cleve-hill-solar-park": "cleve-hill-solar-park-kent",
    "asset-seagreen-offshore-wind": "seagreen-offshore-wind-farm-angus",
    "asset-blackstone-qts-cambois-blyth": "qts-blackstone-cambois-blyth",
    "asset-vantage-newport-cardiff": "vantage-cwl1-newport",
}

INDUSTRY_ORDER = ("data_centre", "energy_asset", "storage_asset")
INDUSTRY_LABEL = {
    "data_centre": "Hyperscale & colocation DC",
    "energy_asset": "Generation & solar/wind",
    "storage_asset": "BESS & grid storage",
}


def _load_json(path: str, default):
    if not os.path.isfile(path):
        return default
    return json.load(open(path))


def _record_ids() -> set[str]:
    return {r["entity_id"] for r in _load_json(RECORDS, [])}


def _canonical_id(eid: str) -> str:
    return ALIASES.get(eid, eid)


def _is_covered(eid: str, in_records: set[str]) -> bool:
    canon = _canonical_id(eid)
    return eid in in_records or canon in in_records


def load_queue() -> list[dict]:
    """Researched entities + pending seed stubs not yet in records."""
    out: list[dict] = []
    seen: set[str] = set()
    in_rec = _record_ids()

    for row in _load_json(EXPANSION, []):
        eid = row["entity_id"]
        if _is_covered(eid, in_rec):
            continue
        if eid in seen:
            continue
        seen.add(eid)
        out.append(row)

    pending = _load_json(PENDING, {})
    for seg, stubs in (pending.get("segments") or {}).items():
        for stub in stubs:
            eid = stub if isinstance(stub, str) else stub.get("entity_id", "")
            if not eid or eid in seen or _is_covered(eid, in_rec):
                continue
            seen.add(eid)
            out.append({
                "entity_id": eid,
                "name": stub.get("name", eid) if isinstance(stub, dict) else eid,
                "layer": 3,
                "entity_type": seg,
                "hint": stub.get("hint", "") if isinstance(stub, dict) else "",
                "_pending": True,
            })
    return out


def divide_targets(
    entities: list[dict],
    *,
    by: str = "entity_type",
    batch_size: int = BATCH_SIZE,
) -> dict[str, list[list[str]]]:
    """Split entity list into cross-industry batches.

    Returns {segment: [[batch1_ids], [batch2_ids], ...]}.
    """
    buckets: dict[str, list[str]] = defaultdict(list)
    for e in entities:
        seg = e.get(by) or e.get("entity_type") or "other"
        buckets[seg].append(e["entity_id"])

    out: dict[str, list[list[str]]] = {}
    batch_n = 0
    for seg in INDUSTRY_ORDER + tuple(k for k in buckets if k not in INDUSTRY_ORDER):
        ids = buckets.get(seg, [])
        if not ids:
            continue
        batches = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]
        out[seg] = batches
        batch_n += len(batches)
    return out


def flatten_batches(by_segment: dict[str, list[list[str]]]) -> dict[str, list[str]]:
    """Flat batch keys: batch_dc1, batch_energy1, batch_storage1, …"""
    flat: dict[str, list[str]] = {}
    prefix = {"data_centre": "dc", "energy_asset": "energy", "storage_asset": "storage"}
    for seg, batches in by_segment.items():
        p = prefix.get(seg, seg[:6])
        for i, ids in enumerate(batches, 1):
            flat[f"batch_{p}{i}"] = ids
    return flat


def write_manifest(by_segment: dict[str, list[list[str]]]) -> str:
    os.makedirs(BATCH_DIR, exist_ok=True)
    flat = flatten_batches(by_segment)
    doc = {
        "_doc": "L3 expansion swarm — cross-industry asset_researcher batches. "
                "Output: data/l3_expansion/batch_*.json → integrate_entities.py",
        "pass": PASS,
        "batch_size": BATCH_SIZE,
        "parallel_agents": len(flat),
        "bots": ["asset_researcher"],
        "segments": {
            seg: {"label": INDUSTRY_LABEL.get(seg, seg), "batches": len(batches)}
            for seg, batches in by_segment.items()
        },
        "batches": flat,
    }
    json.dump(doc, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
    for bk, ids in flat.items():
        path = os.path.join(BATCH_DIR, f"{bk}.json")
        if not os.path.isfile(path):
            json.dump({"batch": bk, "inputs": {}}, open(path, "w"), indent=2)
    return MANIFEST


def cmd_status() -> int:
    in_rec = _record_ids()
    l3 = sum(1 for r in _load_json(RECORDS, []) if r.get("layer") == 3)
    queue = load_queue()
    by_seg: dict[str, int] = defaultdict(int)
    researched = 0
    pending = 0
    for e in queue:
        by_seg[e.get("entity_type", "other")] += 1
        if e.get("_pending"):
            pending += 1
        else:
            researched += 1

    print("L3 SWARM EXPANSION — STATUS")
    print("=" * 60)
    print(f"  In index (L3):     {l3}")
    print(f"  Queue total:       {len(queue)}  ({researched} researched · {pending} seed stubs)")
    for seg in INDUSTRY_ORDER:
        if by_seg.get(seg):
            print(f"    {INDUSTRY_LABEL.get(seg, seg):32} {by_seg[seg]}")
    if os.path.isfile(MANIFEST):
        m = _load_json(MANIFEST, {})
        print(f"  Manifest batches:  {len(m.get('batches', {}))}")
    print("=" * 60)
    print("Next: python3 harness/divide_swarm_targets.py divide --write")
    print("      python3 harness/divide_swarm_targets.py deploy")
    return 0


def cmd_divide(write: bool) -> int:
    queue = load_queue()
    if not queue:
        print("Queue empty — all expansion targets already in records.json")
        return 0
    by_seg = divide_targets(queue)
    flat = flatten_batches(by_seg)
    print("CROSS-INDUSTRY BATCH PLAN")
    print("=" * 60)
    for seg, batches in by_seg.items():
        print(f"\n  [{INDUSTRY_LABEL.get(seg, seg)}] — {sum(len(b) for b in batches)} entities, {len(batches)} batch(es)")
        for i, ids in enumerate(batches, 1):
            print(f"    batch {i}: {', '.join(ids[:4])}{'…' if len(ids) > 4 else ''}")
    print(f"\n  → {len(flat)} parallel swarm bots")
    if write:
        path = write_manifest(by_seg)
        print(f"\nwrote {path}")
    return 0


def _prompt_for_batch(batch_key: str) -> str:
    m = _load_json(MANIFEST, {})
    ids = m.get("batches", {}).get(batch_key, [])
    if not ids:
        print(f"Unknown batch: {batch_key}", file=sys.stderr)
        sys.exit(1)
    seg = "mixed"
    for s, spec in (m.get("segments") or {}).items():
        if batch_key.startswith(f"batch_{s[:2]}" if s == "data_centre" else ""):
            pass
    if batch_key.startswith("batch_dc"):
        seg = INDUSTRY_LABEL["data_centre"]
    elif batch_key.startswith("batch_energy"):
        seg = INDUSTRY_LABEL["energy_asset"]
    elif batch_key.startswith("batch_storage"):
        seg = INDUSTRY_LABEL["storage_asset"]

    out_path = os.path.join(BATCH_DIR, f"{batch_key}.json")
    return "\n".join([
        f"You are an asset_researcher bot for NFRI {PASS} {batch_key}.",
        "",
        f"Workspace: {ROOT}",
        f"Industry slice: {seg}",
        "",
        "For EACH entity below, produce a full L3 record matching contract/entity.schema.json.",
        "Include exposure_inputs + preparedness_inputs (all sub-factors), asset_link, provenance.",
        "NO synthetic values — omit entity if you cannot source a rating ≥1.",
        "",
        f"Entities ({len(ids)}):",
        ", ".join(ids),
        "",
        "Read skill: .claude/skills/expand-layer3-assets/SKILL.md",
        "",
        f'Write: {{"batch":"{batch_key}","researched_by":"asset_researcher","inputs":{{...}}}}',
        f"To: {out_path}",
        "",
        "After batch lands: python3 harness/divide_swarm_targets.py integrate",
    ])


def cmd_deploy(batch_key: str | None) -> int:
    if not os.path.isfile(MANIFEST):
        print("Run: python3 harness/divide_swarm_targets.py divide --write", file=sys.stderr)
        return 1
    m = _load_json(MANIFEST, {})
    batches = m.get("batches", {})
    if batch_key:
        print(_prompt_for_batch(batch_key))
        return 0
    print("SWARM DEPLOY — parallel subagent prompts")
    print("=" * 60)
    for bk in sorted(batches):
        n = len(batches[bk])
        print(f"\n  [{bk}] ({n} entities)")
        print(f"      python3 harness/bot_deploy.py --prompt {PASS} {bk}")
    print("\n" + "=" * 60)
    print(f"  {len(batches)} bots — one per batch, run in parallel")
    return 0


def cmd_integrate() -> int:
    """Merge researched expansion records (full JSON rows) into records.json."""
    queue = load_queue()
    researched = [e for e in queue if not e.get("_pending") and e.get("exposure_inputs")]
    if not researched:
        print("No researched net-new entities to integrate.")
        return 0
    staging = os.path.join(BATCH_DIR, "_integrate_staging.json")
    json.dump(researched, open(staging, "w"), indent=2, ensure_ascii=False)
    cmd = [PY, os.path.join(ROOT, "harness", "integrate_entities.py"), staging]
    print(f"→ {' '.join(cmd)}")
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc:
        return rc
    print(f"Integrated {len(researched)} entities. Rebuild: python3 harness/publish_pipeline.py rebuild")
    return 0


def cmd_cycle(write: bool) -> int:
    rc = cmd_divide(write=write)
    if rc:
        return rc
    rc = cmd_integrate()
    if rc:
        return rc
    subprocess.run([PY, os.path.join(ROOT, "harness", "publish_pipeline.py"), "rebuild"], cwd=ROOT)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Divide L3 targets cross-industry and deploy swarm bots")
    ap.add_argument("command", choices=["status", "divide", "deploy", "integrate", "cycle"])
    ap.add_argument("batch", nargs="?", help="deploy: single batch key")
    ap.add_argument("--write", action="store_true", help="divide/cycle: write manifest + stub batches")
    args = ap.parse_args()

    if args.command == "status":
        return cmd_status()
    if args.command == "divide":
        return cmd_divide(args.write)
    if args.command == "deploy":
        return cmd_deploy(args.batch)
    if args.command == "integrate":
        return cmd_integrate()
    if args.command == "cycle":
        return cmd_cycle(args.write)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
