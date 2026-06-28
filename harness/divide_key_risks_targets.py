#!/usr/bin/env python3
"""Divide scored universe into key_risks_mining batches (one entity → substantiated cards).

  python3 harness/divide_key_risks_targets.py status
  python3 harness/divide_key_risks_targets.py divide --write
  python3 harness/divide_key_risks_targets.py deploy   # print bot_deploy hints
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
SCORED = os.path.join(ROOT, "data", "records.scored.json")
BATCH_DIR = os.path.join(ROOT, "data", "key_risks")
MANIFEST = os.path.join(BATCH_DIR, "manifest.json")
BATCH_SIZE = 12
LAYER_ORDER = {2: 0, 1: 1, 3: 2, 4: 3}


def _load_scored() -> list[dict]:
    return json.load(open(SCORED))


def _batch_done(batch_key: str) -> bool:
    path = os.path.join(BATCH_DIR, f"{batch_key}.json")
    if not os.path.isfile(path):
        return False
    doc = json.load(open(path))
    ents = doc.get("entities") or {}
    return bool(doc.get("researched_by") and len(ents) >= 1)


def _ordered_ids(records: list[dict]) -> list[str]:
    rows = [r for r in records if r.get("scores")]
    rows.sort(key=lambda r: (
        LAYER_ORDER.get(r.get("layer") or 9, 9),
        (r.get("display_name") or r.get("entity_id") or "").lower(),
    ))
    return [r["entity_id"] for r in rows]


def _chunk(ids: list[str], size: int) -> list[list[str]]:
    return [ids[i : i + size] for i in range(0, len(ids), size)]


def divide(write: bool) -> dict:
    records = _load_scored()
    ids = _ordered_ids(records)
    existing: dict[str, list[str]] = {}
    if os.path.isdir(BATCH_DIR):
        for path in sorted(glob.glob(os.path.join(BATCH_DIR, "batch*.json"))):
            bk = os.path.splitext(os.path.basename(path))[0]
            doc = json.load(open(path))
            if doc.get("researched_by") and (doc.get("entities") or {}):
                existing[bk] = sorted((doc.get("entities") or {}).keys())
    assigned = {eid for chunk in existing.values() for eid in chunk}
    pending = [eid for eid in ids if eid not in assigned]
    chunks = _chunk(pending, BATCH_SIZE)
    batches = dict(existing)
    n = max([int(b.replace("batch", "")) for b in batches], default=0)
    for chunk in chunks:
        n += 1
        batches[f"batch{n}"] = chunk
    manifest = {
        "_doc": "Key risks mining — entity-specific Ciridae cards. Output via apply_key_risks.py --all",
        "pass": "key_risks_mining",
        "batch_size": BATCH_SIZE,
        "parallel_agents": 4,
        "bots": ["risk_analyst"],
        "template": "contract/key_risks_framework.json",
        "batches": batches,
    }
    if write:
        os.makedirs(BATCH_DIR, exist_ok=True)
        json.dump(manifest, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
        print(f"wrote {MANIFEST} — {len(ids)} entities in {len(batches)} batches")
    return manifest


def status() -> None:
    manifest = json.load(open(MANIFEST)) if os.path.isfile(MANIFEST) else divide(False)
    batches = manifest.get("batches") or {}
    done = sum(1 for bk in batches if _batch_done(bk))
    total = len(batches)
    pending = [bk for bk in batches if not _batch_done(bk)]
    print(f"key_risks_mining: {done}/{total} batches complete")
    for bk, ids in batches.items():
        mark = "✓" if _batch_done(bk) else " "
        print(f"  [{mark}] {bk} ({len(ids)}): {', '.join(ids[:5])}{'…' if len(ids) > 5 else ''}")
    if pending:
        print("\nNext prompts:")
        for bk in pending[:4]:
            print(f"  python3 harness/bot_deploy.py --prompt key_risks_mining {bk}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Divide key_risks mining targets")
    ap.add_argument("command", choices=("status", "divide", "deploy"), nargs="?", default="status")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.command == "divide":
        divide(write=args.write or True)
    elif args.command == "deploy":
        status()
    else:
        status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
