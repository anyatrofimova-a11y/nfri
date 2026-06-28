#!/usr/bin/env python3
"""NFRI — Felix-style parallel agent deployment manifests.

Prints structured pass manifests from contract/analysis_writing.json and
contract/findings_writing.json so subagents can be fan-out deployed with
consistent bot assignments, section targets, and exit checks.

Usage:
  python3 harness/agent_deploy.py                 # both manifests
  python3 harness/agent_deploy.py --analysis      # industry essay passes only
  python3 harness/agent_deploy.py --findings      # findings passes only
  python3 harness/agent_deploy.py --transformation  # on-transformation thesis passes
  python3 harness/agent_deploy.py --methodology     # methodology tab + scatter passes
  python3 harness/agent_deploy.py --platform      # phased platform build (BUILD_SEQUENCE.md)
  python3 harness/agent_deploy.py --platform --phase 2
  python3 harness/agent_deploy.py --json          # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")


def _load(name: str) -> dict:
    path = os.path.join(CT, name)
    if not os.path.exists(path):
        print(f"Missing {path}", file=sys.stderr)
        sys.exit(1)
    return json.load(open(path))


def _bot_index(spec: dict) -> dict[str, dict]:
    return {b["id"]: b for b in spec.get("bots", [])}


def _pass_manifest(spec: dict, label: str) -> dict:
    bots = _bot_index(spec)
    deployment = spec.get("deployment", {})
    passes = []
    for p in deployment.get("parallel_passes", []):
        pass_bots = p.get("bots", [])
        passes.append({
            "pass": p["pass"],
            "sections": p.get("sections", []),
            "bots": pass_bots,
            "bot_briefs": [
                {
                    "id": bid,
                    "role": bots[bid]["role"],
                    "ask": bots[bid]["ask"],
                    "output": bots[bid]["output"],
                    "ban": bots[bid]["ban"],
                }
                for bid in pass_bots if bid in bots
            ],
        })
    return {
        "contract": label,
        "version": spec.get("version"),
        "workflow": deployment.get("workflow", []),
        "felix_moves": spec.get("felix_moves", []),
        "parallel_passes": passes,
    }


def _platform_manifest(phase: Optional[int] = None) -> dict:
    spec = _load(os.path.join("platform", "sprints.json"))
    agents_readme = os.path.join(ROOT, "agents", "README.md")
    phases = []
    for p in spec.get("phases", spec.get("sprints", [])):
        pid = p["id"]
        if phase is not None and pid != phase:
            continue
        phases.append({
            "id": pid,
            "name": p["name"],
            "weeks": p.get("weeks"),
            "agents": p["agents"],
            "integration_contracts": p.get("integration_contracts", []),
            "exit": p.get("exit") or p.get("stream_exit"),
            "acceptance_test": p.get("acceptance_test"),
            "blocks": p.get("blocks", []),
        })
    return {
        "contract": "platform phased build",
        "version": spec.get("version"),
        "execution": spec.get("execution"),
        "playbook": spec.get("playbook"),
        "criteria": spec.get("criteria", []),
        "programme_exit": _load(os.path.join("platform", "integration_contracts.json")).get("programme_exit"),
        "agent_briefs_path": agents_readme if os.path.isfile(agents_readme) else None,
        "phases": phases,
    }


def _print_platform(m: dict) -> None:
    print("=" * 72)
    print(f"DEPLOY — PLATFORM PHASED BUILD  (v{m['version']})")
    print("=" * 72)
    print(f"Execution: {m['execution']}")
    print(f"Playbook: {m['playbook']}")
    if m.get("criteria"):
        print("\nCriteria:")
        for c in m["criteria"]:
            print(f"  · {c}")
    print("\nProgramme exit:")
    for k, v in (m.get("programme_exit") or {}).items():
        print(f"  · {k}: {v}")
    print("\nPhases (sequential — do not skip exit gates):")
    for s in m["phases"]:
        print(f"\n  [Phase {s['id']}] {s['name']} ({s.get('weeks', '?')} wk)")
        print(f"    agents: {', '.join(s['agents'])}")
        print(f"    contracts: {', '.join(s.get('integration_contracts') or [])}")
        if s.get("acceptance_test"):
            print(f"    acceptance: {s['acceptance_test']}")
        if s.get("blocks"):
            print(f"    blocks phases: {s['blocks']}")
        print(f"    exit: {s.get('exit')}")
    print("\nGraph acceptance: python3 harness/platform/graph_acceptance.py --strict")
    print("Build guide: BUILD_SEQUENCE.md")
    print()


def main():
    ap = argparse.ArgumentParser(description="Print agent deployment manifests")
    ap.add_argument("--analysis", action="store_true", help="analysis_writing.json only")
    ap.add_argument("--findings", action="store_true", help="findings_writing.json only")
    ap.add_argument("--transformation", action="store_true", help="on_transformation_writing.json only")
    ap.add_argument("--methodology", action="store_true", help="methodology_writing.json only")
    ap.add_argument("--platform", action="store_true", help="phased platform build (contract/platform/sprints.json)")
    ap.add_argument("--phase", type=int, metavar="N", help="with --platform: show phase N only (1-4)")
    ap.add_argument("--profiles", action="store_true", help="profile_writing.json entity analysis passes")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    if args.platform:
        m = _platform_manifest(args.phase)
        if args.json:
            print(json.dumps(m, indent=2))
            return 0
        _print_platform(m)
        return 0

    if args.profiles:
        cmd = [sys.executable, os.path.join(ROOT, "harness", "bot_deploy.py"), "--profiles"]
        if args.json:
            cmd.append("--json")
        return subprocess.run(cmd, cwd=ROOT).returncode

    both = not args.analysis and not args.findings and not args.transformation and not args.methodology and not args.platform

    manifests = []
    if both or args.analysis:
        aw = _load("analysis_writing.json")
        manifests.append(_pass_manifest(aw, "contract/analysis.json"))
    if both or args.findings:
        fw = _load("findings_writing.json")
        manifests.append(_pass_manifest(fw, "contract/findings.json"))
    if both or args.transformation:
        tw = _load("on_transformation_writing.json")
        manifests.append(_pass_manifest(tw, "contract/on_transformation.json"))
    if both or args.methodology:
        mw = _load("methodology_writing.json")
        manifests.append(_pass_manifest(mw, "contract/methodology_tab.json + scatter_methodology.json"))

    if args.json:
        print(json.dumps(manifests if len(manifests) > 1 else manifests[0], indent=2))
        return

    for m in manifests:
        print("=" * 72)
        print(f"DEPLOY — {m['contract']}  (methodology v{m['version']})")
        print("=" * 72)
        print("Felix moves:")
        for move in m["felix_moves"]:
            print(f"  · {move}")
        print("\nWorkflow:")
        for step in m["workflow"]:
            print(f"  {step}")
        print("\nParallel passes:")
        for p in m["parallel_passes"]:
            print(f"\n  [{p['pass']}]")
            if p.get("sections"):
                print(f"    sections: {', '.join(p['sections'])}")
            print(f"    bots: {', '.join(p['bots'])}")
            for b in p["bot_briefs"]:
                print(f"      · {b['id']} — {b['role']}")
                print(f"        ask: {b['ask']}")
                print(f"        ban: {b['ban']}")
        print()


if __name__ == "__main__":
    raise SystemExit(main())
