#!/usr/bin/env python3
"""Continuous data expansion orchestrator — one entry point to expand and refine the index.

Coordinates the two planes from contract/BOT_ORCHESTRATION.md:
  • Measurement (L5 gate) — register pulls, disclosed banking, scored inputs
  • Profile (narrative depth) — entity copy, analysis, placements, rationales

Typical weekly loop:
  1. python3 harness/data_orchestrator.py status      # what's blocking publish
  2. python3 harness/data_orchestrator.py fanout      # pending parallel agent batches
  3. Deploy N agents (bot_deploy.py --prompt …)
  4. python3 harness/data_orchestrator.py apply all   # merge batches + rebuild
  5. python3 harness/data_orchestrator.py cycle --measure  # register refresh + gate

  python3 harness/data_orchestrator.py status
  python3 harness/data_orchestrator.py next [--limit 5]
  python3 harness/data_orchestrator.py fanout
  python3 harness/data_orchestrator.py apply [profile|measure|all]
  python3 harness/data_orchestrator.py expand data/new_entities.json …
  python3 harness/data_orchestrator.py cycle [--measure]
  python3 harness/data_orchestrator.py rebuild [--measure] [--qa]
  python3 harness/data_orchestrator.py swarm [--write]  # L3 cross-industry bot batches
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.path.join(ROOT, "harness")
MANIFEST = os.path.join(ROOT, "data", "profile_passes", "manifest.json")
STATUS_OUT = os.path.join(ROOT, "data", "expansion_status.json")
PY = sys.executable


def _import_pipeline():
    sys.path.insert(0, HARNESS)
    from publish_pipeline import publish_metrics, rebuild

    return publish_metrics, rebuild


def _run_orchestrator(script: str, *args: str) -> int:
    path = os.path.join(HARNESS, script)
    return subprocess.run([PY, path, *args], cwd=ROOT).returncode


def _load_manifest() -> dict:
    return json.load(open(MANIFEST))


def _pass_status(manifest: dict, pass_id: str) -> str:
    for section in ("passes", "measurement_passes"):
        spec = (manifest.get(section) or {}).get(pass_id)
        if spec:
            return spec.get("status", "pending")
    return "pending"


def _pass_complete(manifest: dict, pass_id: str) -> bool:
    return _pass_status(manifest, pass_id) == "complete"


def _pending_from_profile_orchestrator() -> list[dict]:
    """Reuse profile_orchestrator fanout logic."""
    sys.path.insert(0, HARNESS)
    from profile_orchestrator import _pending_fanout

    return _pending_fanout()


def cmd_status() -> int:
    publish_metrics, _ = _import_pipeline()
    m = publish_metrics()
    g_path = os.path.join(ROOT, "data", "profile_gap_report.txt")
    print("NFRI DATA EXPANSION — STATUS")
    print("=" * 60)
    print(f"  Universe:     {m['entities']} entities ({m['records_source']})")
    print(f"  L5 gate:        {m['gate_share']:.0%} → {m['gate_status']}  (target ≥60%)")
    print(f"  Tier coverage:  {m['measured_entities']}/{m['entities']} entities with measured share > 0")
    print(f"  Quadrants:      {m['quadrants']}")
    if m.get("calibration"):
        print(f"  Calibration:    {m['calibration']}")
    print("-" * 60)
    _run_orchestrator("measure_orchestrator.py", "status")
    print("-" * 60)
    _run_orchestrator("profile_orchestrator.py", "status")
    if os.path.isfile(g_path):
        print("-" * 60)
        print(f"  Gap report:     data/profile_gap_report.txt")
    print("=" * 60)
    print("Next:  python3 harness/data_orchestrator.py next")
    print("Cycle: python3 harness/data_orchestrator.py cycle [--measure]")
    return 0


def _pending_measurement_batches() -> list[dict]:
    manifest = _load_manifest()
    ladder = {item["pass"]: item["priority"] for item in manifest.get("optimization_ladder", [])}
    out = []
    sys.path.insert(0, HARNESS)
    from measure_orchestrator import _batch_has_output

    for pass_id, spec in (manifest.get("measurement_passes") or {}).items():
        if _pass_complete(manifest, pass_id):
            continue
        batch_dir = spec.get("batch_dir", "")
        if not batch_dir:
            continue
        mp = os.path.join(ROOT, batch_dir, "manifest.json")
        if not os.path.isfile(mp):
            continue
        for bk, ids in json.load(open(mp)).get("batches", {}).items():
            path = os.path.join(ROOT, batch_dir, f"{bk}.json")
            if os.path.isfile(path) and _batch_has_output(json.load(open(path))):
                continue
            out.append({
                "pass": pass_id,
                "batch": bk,
                "n": len(ids),
                "priority": ladder.get(pass_id, "P2"),
                "prompt_cmd": f"python3 harness/bot_deploy.py --prompt {pass_id} {bk}",
                "why": spec.get("target", spec.get("apply", "")),
            })
    return out


def cmd_next(limit: int) -> int:
    manifest = _load_manifest()
    publish_metrics, _ = _import_pipeline()
    m = publish_metrics()
    gate_passed = m["gate_share"] >= 0.6

    pending = _pending_from_profile_orchestrator()
    pending += _pending_measurement_batches()
    seen: set[tuple[str, str]] = set()
    deduped = []
    for p in pending:
        key = (p["pass"], p["batch"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    pending = deduped
    ladder = manifest.get("optimization_ladder", [])
    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    pending.sort(key=lambda x: (prio_order.get(x.get("priority", "P9"), 9), x["pass"], x["batch"]))
    print("RECOMMENDED NEXT ACTIONS (priority order)")
    print("=" * 60)
    if gate_passed:
        print(f"  L5 gate PASSED at {m['gate_share']:.0%} — focus shifts to profile depth and refresh.")
        print("-" * 60)
    shown = 0
    seen_passes: set[str] = set()
    for p in pending:
        if shown >= limit:
            break
        why = next((i["why"] for i in ladder if i["pass"] == p["pass"]), p.get("why", ""))
        print(f"\n  [{p.get('priority', 'P?')}] {p['pass']} / {p['batch']} ({p['n']} entities)")
        if why:
            print(f"      Why: {why}")
        print(f"      Run: {p['prompt_cmd']}")
        shown += 1
        seen_passes.add(p["pass"])
    for item in ladder:
        if shown >= limit:
            break
        pid = item["pass"]
        if pid in seen_passes or _pass_complete(manifest, pid):
            continue
        if item["priority"] in ("P0", "P1", "P2"):
            print(f"\n  [{item['priority']}] {pid} — {item['why']}")
            print(f"      Check: python3 harness/measure_orchestrator.py batches {pid}"
                  if pid in (manifest.get("measurement_passes") or {})
                  else f"      Check: python3 harness/profile_orchestrator.py batches {pid}")
            shown += 1
    if shown == 0:
        if gate_passed:
            print("  Gate passed — no pending batches. Run cycle --measure to refresh registers, or expand universe.")
        else:
            print("  No pending batches — run cycle --measure to refresh registers, or expand universe.")
    print("\nAfter batches: python3 harness/data_orchestrator.py apply all")
    if not gate_passed:
        print("Book gap deploy: python3 harness/divide_book_gap_targets.py deploy")
    return 0


def cmd_fanout() -> int:
    return _run_orchestrator("profile_orchestrator.py", "fanout")


def cmd_apply(plane: str) -> int:
    if plane in ("all", "measure"):
        rc = _run_orchestrator("measure_orchestrator.py", "apply", "all")
        if rc:
            return rc
    if plane in ("all", "profile"):
        rc = _run_orchestrator("profile_orchestrator.py", "apply", "all")
        if rc:
            return rc
    if plane == "all":
        _, rebuild = _import_pipeline()
        return rebuild()
    return 0


def cmd_expand(paths: list[str]) -> int:
    if not paths:
        print("Usage: data_orchestrator.py expand data/new_entities.json …", file=sys.stderr)
        return 1
    cmd = [PY, os.path.join(HARNESS, "integrate_entities.py"), *paths]
    print(f"→ {' '.join(cmd)}")
    if subprocess.run(cmd, cwd=ROOT).returncode:
        return 1
    _, rebuild = _import_pipeline()
    return rebuild(bank=False)


def cmd_cycle(measure: bool) -> int:
    """One refinement cycle: merge mining → bank → optional live measure → score → site."""
    print("NFRI REFINEMENT CYCLE")
    print("=" * 60)
    rc = cmd_apply("measure")
    if rc:
        print("WARN: measurement apply had errors; continuing rebuild")
    _, rebuild = _import_pipeline()
    rc = rebuild(measure=measure, bank=True, qa=False)
    if rc:
        return rc
    _run_orchestrator("publication_gate.py", "--check-only")
    cmd_report()
    publish_metrics, _ = _import_pipeline()
    m = publish_metrics()
    print("=" * 60)
    print(f"Cycle complete — gate {m['gate_share']:.0%} ({m['gate_status']})")
    return 0


def cmd_rebuild(measure: bool, qa: bool) -> int:
    _, rebuild = _import_pipeline()
    return rebuild(measure=measure, bank=True, qa=qa)


def cmd_report() -> int:
    publish_metrics, _ = _import_pipeline()
    sys.path.insert(0, HARNESS)
    from profile_gap_report import compute_gaps

    m = publish_metrics()
    gaps = compute_gaps()
    gaps["publish"] = m
    gaps["continuous_cycle"] = _load_manifest().get("continuous_cycle", {})
    os.makedirs(os.path.dirname(STATUS_OUT), exist_ok=True)
    json.dump(gaps, open(STATUS_OUT, "w"), indent=2)
    _run_orchestrator("profile_gap_report.py", "--write", os.path.join(ROOT, "data", "profile_gap_report.txt"))
    print(f"wrote {STATUS_OUT}")
    print(f"gate {m['gate_share']:.0%} · {m['entities']} entities · "
          f"{gaps['narrative']['thin_rationales']} thin rationales")
    return 0


def _run_py(script: str, *args: str) -> int:
    cmd = [PY, os.path.join(HARNESS, script), *args]
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_swarm(write: bool) -> int:
    """Divide L3 expansion queue cross-industry and print swarm deploy prompts."""
    args = ["--write"] if write else []
    rc = _run_py("divide_swarm_targets.py", "divide", *args)
    if rc:
        return rc
    _run_py("divide_swarm_targets.py", "status")
    print("\n--- SWARM DEPLOY (parallel subagents) ---")
    return _run_py("divide_swarm_targets.py", "deploy")


def cmd_priority(measure: bool) -> int:
    """Run P0 sfcr + P2 book_mining + P3 register_pull harness passes (no manual agent deploy)."""
    print("NFRI PRIORITY PASSES — sfcr_mining · book_mining · register_pull")
    print("=" * 60)

    steps = [
        ("P2 Lloyd's syndicate auto-miner", "mine_syndicate_book.py", ["--write-batches"]),
        ("P3 L3 register search map", "build_l3_register_map.py", ["--write"]),
        ("P3 L3 boundary map (all assets)", "build_asset_boundary_map.py", ["--write"]),
        ("Validate sfcr_mining batches", "verify_mining_batch.py", ["--pass", "sfcr_mining", "--all"]),
        ("Validate book_mining batches", "verify_mining_batch.py", ["--pass", "book_mining", "--all"]),
        ("Merge mining batches → contract inputs", "apply_mining_batches.py", ["--apply"]),
        ("Merge → book_inputs.json", "extract_book_inputs.py", ["--merge"]),
        ("Bank disclosed into records.json", "integrate_entities.py", []),
    ]
    for label, script, args in steps:
        print(f"\n--- {label} ---")
        rc = _run_py(script, *args)
        if rc and script != "verify_mining_batch.py":
            print(f"WARN: {script} exited {rc}")

    if measure:
        print("\n--- P3 register_pull: bootstrap full L3 universe ---")
        _run_py("bootstrap_measured_universe.py", "--force", "--register-pull")
        print("\n--- P3 register_pull: non_firm_intensity (ECR/TEC) ---")
        _run_py("measure_non_firm.py", "--live")
        print("\n--- Full live measurement chain ---")
        _run_py("measure_all.py", "--live")

    print("\n--- Publish rebuild ---")
    _, rebuild = _import_pipeline()
    rc = rebuild(bank=False, measure=False, qa=False)
    _run_orchestrator("publication_gate.py", "--check-only")
    cmd_report()
    publish_metrics, _ = _import_pipeline()
    m = publish_metrics()
    print("=" * 60)
    print(f"Priority passes complete — gate {m['gate_share']:.0%} ({m['gate_status']})")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="Continuous data expansion orchestrator")
    ap.add_argument(
        "command",
        choices=["status", "next", "fanout", "apply", "expand", "cycle", "rebuild", "report", "priority", "swarm"],
    )
    ap.add_argument("arg", nargs="?", help="apply plane: profile|measure|all")
    ap.add_argument("extra", nargs="*", help="expand: entity JSON paths")
    ap.add_argument("--limit", type=int, default=5, help="next: max actions")
    ap.add_argument("--measure", action="store_true", help="cycle/rebuild: live register pulls")
    ap.add_argument("--write", action="store_true", help="swarm: write cross-industry batch manifest")
    ap.add_argument("--qa", action="store_true", help="rebuild: run profile_harness --strict")
    args = ap.parse_args()

    if args.command == "status":
        return cmd_status()
    if args.command == "next":
        return cmd_next(args.limit)
    if args.command == "fanout":
        return cmd_fanout()
    if args.command == "apply":
        return cmd_apply(args.arg or "all")
    if args.command == "expand":
        paths = list(args.extra)
        if args.arg:
            paths = [args.arg, *paths]
        return cmd_expand(paths)
    if args.command == "cycle":
        return cmd_cycle(args.measure)
    if args.command == "rebuild":
        return cmd_rebuild(args.measure, args.qa)
    if args.command == "report":
        return cmd_report()
    if args.command == "priority":
        return cmd_priority(args.measure)
    if args.command == "swarm":
        return cmd_swarm(write=args.write)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
