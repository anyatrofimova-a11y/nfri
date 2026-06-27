#!/usr/bin/env python3
"""Unified bot deployment manifests — measurement + profile passes.

Prints structured pass manifests and copy-paste subagent prompts for parallel fan-out.

  python3 harness/bot_deploy.py                    # all passes summary
  python3 harness/bot_deploy.py --measurement      # L5 measurement passes
  python3 harness/bot_deploy.py --profiles         # Ciridae profile passes
  python3 harness/bot_deploy.py --prompt sfcr_mining batch1
  python3 harness/bot_deploy.py --prompt entity_analysis batch2
  python3 harness/bot_deploy.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
DATA = os.path.join(ROOT, "data")


def _load(path: str) -> dict:
    if not os.path.isfile(path):
        print(f"Missing {path}", file=sys.stderr)
        sys.exit(1)
    return json.load(open(path))


def _bot_index(spec: dict) -> dict[str, dict]:
    return {b["id"]: b for b in spec.get("bots", [])}


def _batch_manifest(batch_dir: str) -> dict | None:
    path = os.path.join(ROOT, batch_dir, "manifest.json")
    return json.load(open(path)) if os.path.isfile(path) else None


def _batch_done(batch_dir: str, batch_key: str) -> bool:
    path = os.path.join(ROOT, batch_dir, f"{batch_key}.json")
    if not os.path.isfile(path):
        return False
    doc = json.load(open(path))
    if not isinstance(doc, dict):
        return False
    payload = doc.get("inputs") or doc.get("entities")
    if isinstance(payload, dict):
        return len(payload) > 0
    if isinstance(payload, list):
        return len(payload) > 0
    return False


def _pass_manifest_from_writing(spec: dict, label: str) -> dict:
    bots = _bot_index(spec)
    deployment = spec.get("deployment", {})
    passes = []
    for p in deployment.get("parallel_passes", []):
        pass_id = p["pass"]
        batch_dir = p.get("batch_dir", "")
        batches = {}
        if batch_dir:
            bm = _batch_manifest(batch_dir)
            if bm:
                batches = bm.get("batches", {})
        pass_bots = p.get("bots", [])
        passes.append({
            "pass": pass_id,
            "status": p.get("status", "pending"),
            "target": p.get("target", ""),
            "batch_dir": batch_dir,
            "batches": batches,
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
        "gate": spec.get("gate"),
        "workflow": deployment.get("workflow", []),
        "exit_checks": spec.get("exit_checks", []),
        "parallel_passes": passes,
    }


def _prompt_for_pass(pass_id: str, batch_key: str) -> str:
    mw = _load(os.path.join(CT, "measurement_writing.json"))
    pw = _load(os.path.join(CT, "profile_writing.json"))
    passes = {p["pass"]: p for p in mw["deployment"]["parallel_passes"]}
    passes.update({p["pass"]: p for p in pw["deployment"]["parallel_passes"]})

    spec = passes.get(pass_id)
    if not spec:
        print(f"Unknown pass: {pass_id}", file=sys.stderr)
        sys.exit(1)

    batch_dir = spec.get("batch_dir", "")
    bm = _batch_manifest(batch_dir) if batch_dir else None
    if not bm or batch_key not in bm.get("batches", {}):
        print(f"Unknown batch {batch_key} for pass {pass_id}", file=sys.stderr)
        sys.exit(1)

    entities = bm["batches"][batch_key]
    bots = spec.get("bots", bm.get("bots", []))
    bot_id = bots[0] if bots else "researcher"
    all_bots = {**_bot_index(mw), **_bot_index(pw)}
    brief = all_bots.get(bot_id, {})
    target = spec.get("target", bm.get("_doc", ""))
    out_path = os.path.join(ROOT, batch_dir, f"{batch_key}.json")

    if pass_id in ("book_mining", "sfcr_mining"):
        entity_block = ", ".join(entities)
        row_shape = """{
  "entity_id": {
    "total_gwp": number,
    "energy_power_gwp": number,
    "datacentre_tech_gwp": 0,
    "currency": "GBP"|"USD"|"EUR",
    "lines_counted": ["exact class name"],
    "source": "primary URL",
    "as_of": "2024-12-31"
  }
}"""
        source_kind = (
            "Lloyd's Q4 2024 syndicate iXBRL (assets.lloyds.com)"
            if pass_id == "book_mining"
            else "group SFCR / annual report segment tables"
        )
        task = (
            f"For EACH entity below, find DISCLOSED gross written premium from {source_kind}. "
            f"Extract ONLY if a NAMED energy/power class is separately disclosed — NOT broad Fire/Property LoBs."
        )
        omit = "Omit entity entirely if no named energy GWP."
        write_fmt = (
            f'{{"batch":"{batch_key}","researched_by":"{bot_id}","inputs":{{...}}}}'
        )
    elif pass_id == "entity_analysis":
        entity_block = "\n".join(f"  - {e}" for e in entities)
        template = bm.get("template_entity", "nscale-loughton-essex")
        row_shape = f"See contract/entity_analysis.json schema; template entity: {template}"
        task = (
            "For EACH asset, populate grid_posture, risk_manifestation[] (≥2 entries), "
            "cover_stack (evidenced/inferred_typical/absent/gaps), mining block. "
            "Honest placement_status — no synthetic insurer names."
        )
        omit = "Skip fields you cannot source; use unknown/absent tiers."
        write_fmt = f'Merge into contract/entity_analysis.json entities{{}} — do NOT overwrite other entities.'
        out_path = os.path.join(ROOT, "contract", "entity_analysis.json")
    elif pass_id == "trigger_mining":
        entity_block = ", ".join(entities)
        row_shape = '{"entity_id": {"n_nondamage_products": int, "products": [...], "source": "url", "as_of": "2024-12-31"}}'
        task = "Count filed non-damage triggers (availability, parametric, BI without physical damage) from product wordings."
        omit = "Omit if no filing evidence."
        write_fmt = f'{{"batch":"{batch_key}","researched_by":"{bot_id}","inputs":{{...}}}}'
    elif pass_id == "capital_mining":
        entity_block = ", ".join(entities)
        row_shape = '{"entity_id": {"fsr": "AA", "fsr_agency": "sp", "scr_coverage_pct": 200, "source": "url", "as_of": "2024-12-31"}}'
        task = "Pull AM Best / S&P FSR and Solvency II SCR coverage from SFCR or rating agency."
        omit = "Omit SCR if not disclosed; still record FSR if available."
        write_fmt = f'{{"batch":"{batch_key}","researched_by":"{bot_id}","inputs":{{...}}}}'
    else:
        entity_block = ", ".join(entities)
        row_shape = "See pass contract"
        task = brief.get("ask", "Research assigned entities.")
        omit = brief.get("ban", "No synthetic values.")
        write_fmt = out_path

    lines = [
        f"You are a {bot_id} bot for NFRI {pass_id} {batch_key}.",
        "",
        f"Workspace: {ROOT}",
        "",
        task,
        "",
        f"Entities ({len(entities)}):",
        entity_block,
        "",
        f"Output shape per entity (omit entirely if no qualifying disclosure):",
        row_shape,
        "",
        omit,
        "",
        f"NO synthetic values. Primary sources only.",
        "",
        f"Write to: {out_path}",
        write_fmt,
        "",
        f"Bot role: {brief.get('role', bot_id)}",
        f"Banned: {brief.get('ban', 'synthetic data')}",
        "",
        "Return a summary when done: populated count, omitted entities + reason.",
    ]
    if pass_id == "entity_analysis":
        lines.insert(8, f"Read template: contract/entity_analysis.json → entities.{template}")
    return "\n".join(lines)


def _print_manifest(m: dict) -> None:
    print("=" * 72)
    print(f"DEPLOY — {m['contract']}  (v{m.get('version', '?')})")
    if m.get("gate"):
        g = m["gate"]
        print(f"Gate target: {g.get('target', 0.6):.0%} blended measured share")
    print("=" * 72)
    if m.get("workflow"):
        print("Workflow:")
        for step in m["workflow"]:
            print(f"  {step}")
    print("\nParallel passes:")
    for p in m["parallel_passes"]:
        batches = p.get("batches") or {}
        done = sum(1 for bk in batches if _batch_done(p.get("batch_dir", ""), bk)) if batches else 0
        total = len(batches)
        st = p.get("status", "pending")
        prog = f"  batches {done}/{total}" if total else ""
        print(f"\n  [{st:12}] {p['pass']}{prog}")
        if p.get("target"):
            print(f"    target: {p['target']}")
        print(f"    bots: {', '.join(p.get('bots', []))}")
        for bk, ids in batches.items():
            mark = "✓" if _batch_done(p.get("batch_dir", ""), bk) else " "
            print(f"      [{mark}] {bk} ({len(ids)}): {', '.join(ids[:6])}{'…' if len(ids) > 6 else ''}")
        for b in p.get("bot_briefs", [])[:2]:
            print(f"      · {b['id']} — {b['role']}")
    if m.get("exit_checks"):
        print("\nExit checks:")
        for c in m["exit_checks"][:5]:
            print(f"  · {c}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description="Bot deployment manifests")
    ap.add_argument("--measurement", action="store_true", help="measurement_writing.json passes")
    ap.add_argument("--profiles", action="store_true", help="profile_writing.json passes")
    ap.add_argument("--prompt", nargs=2, metavar=("PASS", "BATCH"), help="subagent prompt text")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    if args.prompt:
        print(_prompt_for_pass(args.prompt[0], args.prompt[1]))
        return 0

    both = not args.measurement and not args.profiles
    manifests = []
    if both or args.measurement:
        mw = _load(os.path.join(CT, "measurement_writing.json"))
        manifests.append(_pass_manifest_from_writing(mw, "measurement (L5 gate)"))
    if both or args.profiles:
        pw = _load(os.path.join(CT, "profile_writing.json"))
        manifests.append(_pass_manifest_from_writing(pw, "profiles (Ciridae depth)"))

    if args.json:
        print(json.dumps(manifests if len(manifests) > 1 else manifests[0], indent=2))
        return 0

    for m in manifests:
        _print_manifest(m)

    if both:
        print("Subagent prompts:")
        print("  python3 harness/bot_deploy.py --prompt sfcr_mining batch1")
        print("  python3 harness/bot_deploy.py --prompt entity_analysis batch1")
        print("  python3 harness/bot_deploy.py --prompt book_mining batch4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
