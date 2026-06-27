#!/usr/bin/env python3
"""Profile pass orchestrator — status, gaps, fan-out, apply + rebuild.

  python3 harness/profile_orchestrator.py status
  python3 harness/profile_orchestrator.py gaps
  python3 harness/profile_orchestrator.py fanout          # pending batches + agent count
  python3 harness/profile_orchestrator.py prompt entity_analysis batch1
  python3 harness/profile_orchestrator.py apply entity_analysis
  python3 harness/profile_orchestrator.py apply all
  python3 harness/profile_orchestrator.py rebuild
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
COPY = os.path.join(ROOT, "contract", "entity_copy.json")
RECORDS = os.path.join(ROOT, "data", "records.scored.json")
ANALYSIS = os.path.join(ROOT, "contract", "entity_analysis.json")
PY = sys.executable


def _load_manifest() -> dict:
    return json.load(open(MANIFEST))


def _copy_entities() -> dict:
    if not os.path.isfile(COPY):
        return {}
    return json.load(open(COPY)).get("entities", {})


def _records() -> list:
    return json.load(open(RECORDS))


def _batch_done(batch_dir: str, batch_key: str) -> bool:
    path = os.path.join(ROOT, batch_dir, f"{batch_key}.json")
    if not os.path.isfile(path):
        return False
    doc = json.load(open(path))
    if isinstance(doc, list):
        return len(doc) > 0
    payload = doc.get("inputs") or doc.get("entities") or doc
    if isinstance(payload, dict):
        return len([k for k in payload if not str(k).startswith("_")]) > 0
    if isinstance(payload, list):
        return len(payload) > 0
    return False


def pass_coverage(pass_id: str, spec: dict) -> tuple[int, int]:
    entities = _copy_entities()
    recs = _records()
    if pass_id == "l1_research":
        total = sum(1 for r in recs if r.get("layer") == 1 and r.get("scores"))
        return total, total
    if pass_id == "synthesis":
        total = sum(1 for r in recs if r.get("scores"))
        done = sum(1 for r in recs if r.get("scores") and entities.get(r["entity_id"], {}).get("executive_summary"))
        return done, total
    if pass_id == "portfolio":
        total = sum(1 for r in recs if r.get("layer") == 1 and r.get("scores"))
        done = sum(
            1 for r in recs
            if r.get("layer") == 1 and r.get("scores")
            and entities.get(r["entity_id"], {}).get("portfolio_narrative")
        )
        return done, total
    if pass_id == "l3_research":
        total = sum(1 for r in recs if r.get("layer") == 3 and r.get("scores"))
        return total, total
    if pass_id == "l4_research":
        total = sum(1 for r in recs if r.get("layer") == 4 and r.get("scores"))
        batch_dir = spec.get("batch_dir", "data/l4_research")
        bm = os.path.join(ROOT, batch_dir, "manifest.json")
        if os.path.isfile(bm):
            batches = json.load(open(bm)).get("batches", {})
            done_batches = sum(1 for bk in batches if _batch_done(batch_dir, bk))
            if done_batches == len(batches) and batches:
                return total, total
        return 0, total
    if pass_id == "entity_analysis":
        ea = json.load(open(ANALYSIS)).get("entities", {}) if os.path.isfile(ANALYSIS) else {}
        total = sum(1 for r in recs if r.get("layer") == 3 and r.get("scores"))
        return len(ea), total
    if pass_id == "audit":
        return 0, spec.get("entities", len(recs))
    total = spec.get("entities", 0)
    return 0, total


def cmd_status() -> int:
    m = _load_manifest()
    print("PROFILE PASSES")
    print("=" * 56)
    for pid, spec in m["passes"].items():
        done, total = pass_coverage(pid, spec)
        st = spec.get("status", "pending")
        bar = f"{done}/{total}" if total else "—"
        print(f"  [{st:12}] {pid:16} {bar:8}  {spec.get('bots', [])}")
    print("=" * 56)
    print("Gaps:  python3 harness/profile_orchestrator.py gaps")
    print("Fanout: python3 harness/profile_orchestrator.py fanout")
    return 0


def cmd_gaps() -> int:
    return subprocess.run([PY, os.path.join(ROOT, "harness", "profile_gap_report.py")], cwd=ROOT).returncode


def _pending_fanout() -> list[dict]:
    """Return list of {pass, batch, entities, done, priority} for parallel deploy."""
    m = _load_manifest()
    out = []
    ladder = {item["pass"]: item["priority"] for item in m.get("optimization_ladder", [])}

    fanout_passes = [
        ("entity_analysis", "data/entity_analysis", "data/entity_analysis/manifest.json"),
        ("l4_research", "data/l4_research", "data/l4_research/manifest.json"),
    ]
    for pass_id, batch_dir, manifest_path in fanout_passes:
        if not os.path.isfile(os.path.join(ROOT, manifest_path)):
            continue
        batches = json.load(open(os.path.join(ROOT, manifest_path))).get("batches", {})
        for bk, ids in batches.items():
            done = _batch_done(batch_dir, bk)
            if not done:
                out.append({
                    "pass": pass_id,
                    "batch": bk,
                    "entities": ids,
                    "n": len(ids),
                    "priority": ladder.get(pass_id, "P1"),
                    "prompt_cmd": f"python3 harness/bot_deploy.py --prompt {pass_id} {bk}",
                })

    meas = m.get("measurement_passes") or {}
    for pass_id in ("sfcr_mining", "book_mining", "trigger_mining", "capital_mining"):
        spec = meas.get(pass_id, {})
        batch_dir = spec.get("batch_dir", "")
        mp = os.path.join(ROOT, batch_dir, "manifest.json")
        if not os.path.isfile(mp):
            continue
        for bk in json.load(open(mp)).get("batches", {}):
            if not _batch_done(batch_dir, bk):
                out.append({
                    "pass": pass_id,
                    "batch": bk,
                    "entities": json.load(open(mp))["batches"][bk],
                    "n": len(json.load(open(mp))["batches"][bk]),
                    "priority": ladder.get(pass_id, "P2"),
                    "prompt_cmd": f"python3 harness/bot_deploy.py --prompt {pass_id} {bk}",
                })

    # thin rationales — single batch
    recs = _records()
    thin_ids = set()
    for r in recs:
        if not r.get("scores"):
            continue
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for k, sf in (r.get(ax) or {}).items():
                if len((sf.get("rationale") or "").strip()) < 40:
                    thin_ids.add(r["entity_id"])
    if thin_ids:
        out.append({
            "pass": "thin_rationales",
            "batch": "all",
            "entities": sorted(thin_ids),
            "n": len(thin_ids),
            "priority": "P1",
            "prompt_cmd": "python3 harness/profile_orchestrator.py prompt thin_rationales all",
        })

    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    out.sort(key=lambda x: (prio_order.get(x["priority"], 9), x["pass"], x["batch"]))
    return out


def cmd_fanout() -> int:
    pending = _pending_fanout()
    print("PARALLEL FAN-OUT — pending batches")
    print("=" * 56)
    if not pending:
        print("  All profile batches complete.")
        return 0
    agents = 0
    for item in pending:
        mark = " "
        print(f"\n  [{item['priority']}] {item['pass']} / {item['batch']} ({item['n']} entities)")
        print(f"      {item['prompt_cmd']}")
        print(f"      ids: {', '.join(item['entities'][:5])}{'…' if item['n'] > 5 else ''}")
        agents += 1
    print("\n" + "=" * 56)
    print(f"  {agents} parallel subagents recommended")
    print("  After batches land: python3 harness/profile_orchestrator.py apply all")
    print("                      python3 harness/profile_orchestrator.py rebuild")
    return 0


def cmd_prompt(pass_id: str, batch_key: str) -> int:
    if pass_id == "thin_rationales":
        recs = _records()
        lines = [
            "You are a profile depth bot for NFRI thin_rationales pass.",
            f"Workspace: {ROOT}",
            "",
            "For each entity below, expand sub-factors with rationale < 40 chars to 2–4 sentences.",
            "Entity-specific facts + underwriting implication. Keep rating unchanged unless evidence demands it.",
            "Patch data/records.scored.json in place (exposure_inputs / preparedness_inputs rationale fields).",
            "",
            "Entities with thin lines:",
        ]
        for r in recs:
            if not r.get("scores"):
                continue
            eid = r["entity_id"]
            thin = []
            for ax in ("exposure_inputs", "preparedness_inputs"):
                for k, sf in (r.get(ax) or {}).items():
                    if len((sf.get("rationale") or "").strip()) < 40:
                        thin.append(f"{ax}.{k}: {(sf.get('rationale') or '')!r}")
            if thin:
                lines.append(f"\n{eid}:")
                lines.extend(f"  - {t}" for t in thin)
        lines += ["", "Exit: python3 harness/profile_harness.py --strict (0 thin warnings target)"]
        print("\n".join(lines))
        return 0
    return subprocess.run(
        [PY, os.path.join(ROOT, "harness", "bot_deploy.py"), "--prompt", pass_id, batch_key],
        cwd=ROOT,
    ).returncode


def cmd_apply(pass_id: str) -> int:
    if pass_id == "all":
        order = ("entity_analysis", "l4_research", "l1_research", "l3_research", "synthesis", "portfolio")
        for pid in order:
            rc = cmd_apply(pid)
            if rc:
                return rc
        return cmd_rebuild()

    m = _load_manifest()
    spec = m["passes"].get(pass_id)
    if pass_id == "l4_research":
        cmd = f"{PY} harness/apply_l1_patches.py --all-l4"
        print(f"→ {cmd}")
        rc = subprocess.run(cmd, shell=True, cwd=ROOT).returncode
        if rc:
            return rc
        return subprocess.run([PY, os.path.join(ROOT, "harness", "score_and_validate.py")], cwd=ROOT).returncode

    if pass_id == "entity_analysis":
        cmd = f"{PY} harness/apply_entity_analysis.py --all"
        print(f"→ {cmd}")
        rc = subprocess.run(cmd, shell=True, cwd=ROOT).returncode
        if rc:
            return rc
        return subprocess.run([PY, os.path.join(ROOT, "harness", "build_frontend.py")], cwd=ROOT).returncode

    if not spec or "apply" not in spec:
        print(f"No apply command for {pass_id}", file=sys.stderr)
        return 1
    cmd = spec["apply"].replace("python3", PY, 1)
    print(f"→ {cmd}")
    rc = subprocess.run(cmd, shell=True, cwd=ROOT).returncode
    if rc:
        return rc
    then = spec.get("then")
    if then:
        cmd2 = then.replace("python3", PY, 1)
        print(f"→ {cmd2}")
        return subprocess.run(cmd2, shell=True, cwd=ROOT).returncode
    return 0


def cmd_batches(pass_id: str) -> int:
    m = _load_manifest()
    spec = m["passes"].get(pass_id)
    if not spec:
        print(f"Unknown pass: {pass_id}", file=sys.stderr)
        return 1
    batch_dir = os.path.join(ROOT, spec["batch_dir"])
    manifest_path = os.path.join(batch_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        batches = json.load(open(manifest_path)).get("batches", {})
        for bk, ids in batches.items():
            mark = "✓" if _batch_done(spec["batch_dir"], bk) else " "
            print(f"\n[{mark}] {bk} ({len(ids)})")
            print("  " + ", ".join(ids))
        return 0
    files = sorted(glob.glob(os.path.join(batch_dir, "batch*.json")))
    for f in files:
        print(f"  {os.path.basename(f)}")
    return 0


def cmd_rebuild() -> int:
    for script in ("score_and_validate.py", "build_frontend.py"):
        path = os.path.join(ROOT, "harness", script)
        print(f"→ {PY} {path}")
        rc = subprocess.run([PY, path], cwd=ROOT).returncode
        if rc:
            return rc
    return subprocess.run([PY, os.path.join(ROOT, "harness", "profile_harness.py"), "--strict"], cwd=ROOT).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Profile pass orchestrator")
    ap.add_argument("command", choices=["status", "gaps", "fanout", "batches", "prompt", "apply", "rebuild"])
    ap.add_argument("pass_id", nargs="?", help="pass name or 'all' for apply")
    ap.add_argument("batch_key", nargs="?", help="batch key for prompt")
    args = ap.parse_args()
    if args.command == "status":
        return cmd_status()
    if args.command == "gaps":
        return cmd_gaps()
    if args.command == "fanout":
        return cmd_fanout()
    if args.command == "batches":
        if not args.pass_id:
            print("Usage: profile_orchestrator.py batches <pass>", file=sys.stderr)
            return 1
        return cmd_batches(args.pass_id)
    if args.command == "prompt":
        if not args.pass_id or not args.batch_key:
            print("Usage: profile_orchestrator.py prompt <pass> <batch>", file=sys.stderr)
            return 1
        return cmd_prompt(args.pass_id, args.batch_key)
    if args.command == "apply":
        if not args.pass_id:
            print("Usage: profile_orchestrator.py apply <pass|all>", file=sys.stderr)
            return 1
        return cmd_apply(args.pass_id)
    if args.command == "rebuild":
        return cmd_rebuild()
    return 1


if __name__ == "__main__":
    sys.exit(main())
