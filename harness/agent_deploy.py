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
  python3 harness/agent_deploy.py --json          # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import sys

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


def main():
    ap = argparse.ArgumentParser(description="Print agent deployment manifests")
    ap.add_argument("--analysis", action="store_true", help="analysis_writing.json only")
    ap.add_argument("--findings", action="store_true", help="findings_writing.json only")
    ap.add_argument("--transformation", action="store_true", help="on_transformation_writing.json only")
    ap.add_argument("--methodology", action="store_true", help="methodology_writing.json only")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()
    both = not args.analysis and not args.findings and not args.transformation and not args.methodology

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
    main()
