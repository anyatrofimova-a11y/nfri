#!/usr/bin/env python3
"""Divide gate cohort carriers missing book_inputs into SFCR mining batches + deploy prompts.

  python3 harness/divide_book_gap_targets.py status
  python3 harness/divide_book_gap_targets.py deploy
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, "contract", "book_inputs.json")
SCORED = os.path.join(ROOT, "data", "records.measured.json")
SFCR_DIR = os.path.join(ROOT, "data", "sfcr_mining")
MANIFEST = os.path.join(SFCR_DIR, "manifest.json")

BATCHES = {
    "batch4": [
        "everest-re",
        "axis-re",
        "transre",
        "mapfre-re",
        "ms-reinsurance",
        "antares-re",
        "axa-xl-re",
        "renaissance-re",
    ],
    "batch5": [
        "zurich",
        "allianz-agcs",
        "munich-re",
        "rsa-intact",
        "convex",
        "hannover-re",
        "hdi-global-uk",
        "sompo-intl-energy-uk",
    ],
    "batch6": [
        "bhsi-uk",
        "sompo-re",
        "swiss-re-corso",
        "lloyds-market",
        "fidelis-novagen",
        "inigo-1301",
    ],
}


def missing_carriers() -> list[str]:
    book = json.load(open(BOOK)).get("inputs", {})
    carriers = [
        r for r in json.load(open(SCORED))
        if r.get("entity_type") in ("insurer", "lloyds_syndicate", "reinsurer")
    ]
    return sorted(
        r["entity_id"] for r in carriers
        if r["entity_id"] not in book or not book.get(r["entity_id"], {}).get("total_gwp")
    )


def _batch_done(bk: str) -> bool:
    path = os.path.join(SFCR_DIR, f"{bk}.json")
    if not os.path.isfile(path):
        return False
    doc = json.load(open(path))
    return bool(doc.get("inputs")) or bool(doc.get("blockers"))


def cmd_status() -> int:
    miss = missing_carriers()
    print(f"book_inputs gap: {len(miss)} carriers without total_gwp")
    for e in miss:
        print(f"  · {e}")
    print("\nSFCR gate-gap batches:")
    for bk, ids in BATCHES.items():
        done = _batch_done(bk)
        print(f"  [{'✓' if done else '○'}] {bk} ({len(ids)})")
    return 0


def cmd_deploy() -> int:
    print("NFRI BOOK GAP — parallel SFCR / filing analyst deploy")
    print("=" * 60)
    for bk, ids in BATCHES.items():
        print(f"\n--- {bk} ({len(ids)} carriers) ---")
        print(f"  python3 harness/bot_deploy.py --prompt sfcr_mining {bk}")
        for eid in ids:
            print(f"    · {eid}")
    print("\nAfter agents finish:")
    print("  python3 harness/verify_mining_batch.py --pass sfcr_mining --all")
    print("  python3 harness/data_orchestrator.py apply measure")
    print("  python3 harness/data_orchestrator.py cycle --measure")
    print("\nAutomated Lloyd's pass (syndicates in URL bank):")
    print("  python3 harness/mine_syndicate_book.py --write-batches")
    return 0


def cmd_write_manifest() -> int:
    manifest = json.load(open(MANIFEST))
    batches = dict(manifest.get("batches", {}))
    for bk, ids in BATCHES.items():
        batches[bk] = ids
        path = os.path.join(SFCR_DIR, f"{bk}.json")
        if not os.path.isfile(path):
            json.dump(
                {
                    "batch": bk,
                    "researched_by": "filing_analyst",
                    "inputs": {},
                    "blockers": {},
                },
                open(path, "w"),
                indent=2,
            )
            print(f"created {path}")
    manifest["batches"] = batches
    json.dump(manifest, open(MANIFEST, "w"), indent=2, ensure_ascii=False)
    print(f"updated {MANIFEST}")
    return 0


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["status", "deploy", "write"], default="status", nargs="?")
    args = ap.parse_args()
    if args.command == "status":
        return cmd_status()
    if args.command == "deploy":
        return cmd_deploy()
    if args.command == "write":
        return cmd_write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
