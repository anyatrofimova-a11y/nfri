#!/usr/bin/env python3
"""Measurement-mining orchestrator — coordinate register pulls + disclosed banking.

Unlike profile orchestration (narrative overlays), this drives L5 measured share:
  book_mining → bank disclosed inputs → measure_all --live → score → rebuild

  python3 harness/measure_orchestrator.py status
  python3 harness/measure_orchestrator.py batches book_mining
  python3 harness/measure_orchestrator.py deploy              # all measurement passes
  python3 harness/measure_orchestrator.py deploy sfcr_mining batch1
  python3 harness/measure_orchestrator.py apply bank
  python3 harness/measure_orchestrator.py apply measure
  python3 harness/measure_orchestrator.py apply all
  python3 harness/measure_orchestrator.py gate
  python3 harness/measure_orchestrator.py rebuild
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data", "profile_passes", "manifest.json")
PY = sys.executable


def _load_manifest() -> dict:
    return json.load(open(MANIFEST))


def _book_coverage() -> tuple[int, int]:
    book = json.load(open(os.path.join(ROOT, "contract", "book_inputs.json"))).get("inputs", {})
    scored = os.path.join(ROOT, "data", "records.scored.json")
    carriers = [
        r for r in json.load(open(scored))
        if r.get("entity_type") in ("insurer", "lloyds_syndicate", "reinsurer")
    ]
    book_n = sum(1 for r in carriers if r["entity_id"] in book and book[r["entity_id"]].get("total_gwp"))
    return book_n, len(carriers)


def _gate_book_gap() -> list[str]:
    book = json.load(open(os.path.join(ROOT, "contract", "book_inputs.json"))).get("inputs", {})
    gate = [
        r for r in json.load(open(os.path.join(ROOT, "data", "records.measured.json")))
        if r.get("entity_type") in ("insurer", "lloyds_syndicate", "reinsurer")
    ]
    return sorted(
        r["entity_id"] for r in gate
        if r["entity_id"] not in book or not book.get(r["entity_id"], {}).get("total_gwp")
    )


def _l3_measured() -> tuple[int, int]:
    scored = json.load(open(os.path.join(ROOT, "data", "records.scored.json")))
    l3 = [r for r in scored if r.get("layer") == 3]
    m = sum(
        1 for r in l3
        if r["exposure_inputs"].get("non_firm_intensity", {}).get("evidence_tier") == "measured"
    )
    return m, len(l3)


def _entity_analysis_done() -> tuple[int, int]:
    ea = json.load(open(os.path.join(ROOT, "contract", "entity_analysis.json"))).get("entities", {})
    l3 = [r for r in json.load(open(os.path.join(ROOT, "data", "records.scored.json"))) if r.get("layer") == 3]
    return len(ea), len(l3)


def _share() -> float:
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    from build_frontend import authoritative_share, load_records

    recs, _ = load_records()
    mp = os.path.join(ROOT, "data", "records.measured.json")
    if os.path.isfile(mp):
        recs = json.load(open(mp))
    return authoritative_share(recs)


def _batch_has_output(doc: dict) -> bool:
    if not isinstance(doc, dict):
        return False
    payload = doc.get("inputs") or doc.get("entities")
    if isinstance(payload, dict):
        return len(payload) > 0
    if isinstance(payload, list):
        return len(payload) > 0
    return False


def _batch_progress(pass_id: str) -> tuple[int, int]:
    spec = (_load_manifest().get("measurement_passes") or {}).get(pass_id, {})
    batch_dir = os.path.join(ROOT, spec.get("batch_dir", ""))
    manifest_path = os.path.join(batch_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        return 0, 0
    batches = json.load(open(manifest_path)).get("batches", {})
    done = 0
    for bk in batches:
        path = os.path.join(batch_dir, f"{bk}.json")
        if os.path.isfile(path) and _batch_has_output(json.load(open(path))):
            done += 1
    return done, len(batches)


def cmd_status() -> int:
    m = _load_manifest()
    meas = m.get("measurement_passes") or {}
    book_n, book_total = _book_coverage()
    l3_m, l3_n = _l3_measured()
    ea_done, ea_total = _entity_analysis_done()
    share = _share()
    gap = _gate_book_gap()
    print("MEASUREMENT MINING (L5 gate ≥60%)")
    print("=" * 56)
    print(f"  blended measured share (gate cohort): {share:.0%}  {'PASS' if share >= 0.6 else 'PROVISIONAL'}")
    print(f"  book_concentration disclosed: {book_n}/{book_total} carriers")
    print(f"  gate cohort missing book:       {len(gap)}  ({', '.join(gap[:5])}{'…' if len(gap) > 5 else ''})")
    print(f"  non_firm_intensity measured:    {l3_m}/{l3_n} L3 assets")
    print(f"  entity_analysis depth:          {ea_done}/{ea_total} L3 assets")
    print("-" * 56)
    for pid, spec in meas.items():
        st = spec.get("status", "pending")
        done, total = _batch_progress(pid)
        prog = f"  {done}/{total} batches" if total else ""
        print(f"  [{st:12}] {pid:18}{prog}  bots={spec.get('bots', [])}")
    print("-" * 56)
    print("Deploy: python3 harness/bot_deploy.py --measurement")
    print("Prompt: python3 harness/bot_deploy.py --prompt sfcr_mining batch1")
    print("=" * 56)
    return 0


def cmd_batches(pass_id: str) -> int:
    m = _load_manifest()
    spec = (m.get("measurement_passes") or {}).get(pass_id)
    if not spec:
        print(f"Unknown measurement pass: {pass_id}", file=sys.stderr)
        return 1
    batch_dir = os.path.join(ROOT, spec["batch_dir"])
    manifest_path = os.path.join(batch_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        batches = json.load(open(manifest_path)).get("batches", {})
        for bk, ids in batches.items():
            path = os.path.join(batch_dir, f"{bk}.json")
            mark = "✓" if os.path.isfile(path) else " "
            print(f"\n[{mark}] {bk} ({len(ids)})")
            print("  " + ", ".join(ids))
        return 0
    for f in sorted(glob.glob(os.path.join(batch_dir, "*.json"))):
        print(f"  {os.path.basename(f)}")
    return 0


def cmd_deploy(pass_id: str | None, batch_key: str | None) -> int:
    cmd = [PY, os.path.join(ROOT, "harness", "bot_deploy.py"), "--measurement"]
    if pass_id and batch_key:
        return subprocess.run(
            [PY, os.path.join(ROOT, "harness", "bot_deploy.py"), "--prompt", pass_id, batch_key],
            cwd=ROOT,
        ).returncode
    return subprocess.run(cmd, cwd=ROOT).returncode


def _run(cmd: str) -> int:
    print(f"→ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


def cmd_rebuild() -> int:
    steps = [
        f"{PY} harness/score_and_validate.py",
        f"{PY} harness/optimize.py",
        f"{PY} harness/build_frontend.py",
    ]
    for cmd in steps:
        if _run(cmd):
            return 1
    return 0


def cmd_gate() -> int:
    return _run(f"{PY} harness/publication_gate.py --check-only")


def cmd_apply(pass_id: str) -> int:
    if pass_id == "all":
        for pid in ("extract_book", "bank", "measure", "score"):
            rc = cmd_apply(pid)
            if rc:
                return rc
        return cmd_rebuild()

    steps = {
        "extract_book": (
            f"{PY} harness/verify_mining_batch.py --pass book_mining --all && "
            f"{PY} harness/verify_mining_batch.py --pass sfcr_mining --all ; "
            f"{PY} harness/extract_book_inputs.py --merge"
        ),
        "bank": f"{PY} harness/integrate_entities.py",
        "measure": f"{PY} harness/measure_all.py --live",
        "score": f"{PY} harness/score_and_validate.py && {PY} harness/optimize.py",
    }
    cmd = steps.get(pass_id)
    if not cmd:
        print(f"Unknown apply step: {pass_id}", file=sys.stderr)
        return 1
    return _run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["status", "batches", "deploy", "apply", "gate", "rebuild"])
    ap.add_argument("arg", nargs="?", help="pass id for batches/apply/deploy")
    ap.add_argument("batch", nargs="?", help="batch key for deploy prompt")
    args = ap.parse_args()

    if args.command == "status":
        return cmd_status()
    if args.command == "batches":
        return cmd_batches(args.arg or "book_mining")
    if args.command == "deploy":
        return cmd_deploy(args.arg, args.batch)
    if args.command == "apply":
        return cmd_apply(args.arg or "all")
    if args.command == "gate":
        return cmd_gate()
    if args.command == "rebuild":
        return cmd_rebuild()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
