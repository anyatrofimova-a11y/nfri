#!/usr/bin/env python3
"""NFRI — research bank mining manifest and merge.

Reads contract/research_mining.json and contract/knowledge/research_bank.json.
Prints parallel pass manifests for subagents; merges agent JSON output into the bank.

Usage:
  python3 harness/research_mining.py --manifest
  python3 harness/research_mining.py --manifest --json
  python3 harness/research_mining.py --sources
  python3 harness/research_mining.py --bank-summary
  python3 harness/research_mining.py --merge path/to/snippets.json
  python3 harness/research_mining.py --prompt grid_evidence
"
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
BANK_PATH = os.path.join(CT, "knowledge", "research_bank.json")


def _load(name: str) -> dict:
    path = os.path.join(CT, name)
    if not os.path.exists(path):
        print(f"Missing {path}", file=sys.stderr)
        sys.exit(1)
    return json.load(open(path))


def _load_bank() -> dict:
    if not os.path.exists(BANK_PATH):
        return {"version": "1.0", "snippets": [], "style_notes": [], "argument_moves": []}
    return json.load(open(BANK_PATH))


def _save_bank(bank: dict) -> None:
    bank["as_of"] = date.today().isoformat()
    os.makedirs(os.path.dirname(BANK_PATH), exist_ok=True)
    with open(BANK_PATH, "w") as f:
        json.dump(bank, f, indent=2)
        f.write("\n")


def _bot_index(spec: dict) -> dict[str, dict]:
    return {b["id"]: b for b in spec.get("bots", [])}


def _source_index(spec: dict) -> dict[str, dict]:
    return {s["id"]: s for s in spec.get("source_catalog", [])}


def manifest(spec: dict) -> dict:
    bots = _bot_index(spec)
    sources = _source_index(spec)
    passes = []
    for p in spec.get("deployment", {}).get("parallel_passes", []):
        pass_sources = p.get("sources", [])
        pass_bots = p.get("bots", [])
        passes.append({
            "pass": p["pass"],
            "deliver": p.get("deliver", ""),
            "sources": [
                {
                    "id": sid,
                    "tier": sources[sid].get("tier"),
                    "urls": sources[sid].get("urls", []),
                    "cite_keys": sources[sid].get("cite_keys", []),
                    "mine_for": sources[sid].get("mine_for", []),
                }
                for sid in pass_sources if sid in sources
            ],
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
        "contract": spec.get("output", {}).get("bank", "contract/knowledge/research_bank.json"),
        "version": spec.get("version"),
        "essay_style_ref": spec.get("essay_style_ref"),
        "essay_moves": spec.get("essay_moves", []),
        "snippet_schema": spec.get("snippet_schema", {}),
        "workflow": spec.get("deployment", {}).get("workflow", []),
        "parallel_passes": passes,
    }


def pass_prompt(spec: dict, pass_name: str) -> str:
    m = manifest(spec)
    for p in m["parallel_passes"]:
        if p["pass"] == pass_name:
            lines = [
                f"# Research pass: {pass_name}",
                f"Deliver: {p['deliver']}"
                "Return JSON: {\"snippets\": [...]} matching snippet_schema.",
                f"Schema required fields: {spec.get('snippet_schema', {}).get('required', [])}"
                "Sources:"]
            for s in p["sources"]:
                lines.append(f"- {s['id']} ({s['tier']})")
                for u in s.get("urls", []):
                    lines.append(f"  {u}")
                if s.get("cite_keys"):
                    lines.append(f"  cite_keys: {', '.join(s['cite_keys'])}")
            lines.append("\nBot briefs:")
            for b in p["bot_briefs"]:
                lines.append(f"- {b['id']}: {b['ask']}")
                lines.append(f"  ban: {b['ban']}")
            lines.append("\nEssay moves to tag where applicable:")
            for move in m["essay_moves"]:
                lines.append(f"- {move}")
            lines.append("\nNever include external blog author names in claim text.")
            return "\n".join(lines)
    print(f"Unknown pass: {pass_name}", file=sys.stderr)
    sys.exit(1)


def merge_snippets(path: str) -> None:
    spec = _load("research_mining.json")
    bank = _load_bank()
    incoming = json.load(open(path))
    new_items = incoming if isinstance(incoming, list) else incoming.get("snippets", [])
    required = set(spec.get("snippet_schema", {}).get("required", []))
    existing_ids = {s["id"] for s in bank.get("snippets", [])}
    added = 0
    skipped = 0
    for item in new_items:
        if not required.issubset(item.keys()):
            print(f"Skip (missing fields): {item.get('id', '?')}", file=sys.stderr)
            skipped += 1
            continue
        if item["id"] in existing_ids:
            print(f"Skip (duplicate id): {item['id']}", file=sys.stderr)
            skipped += 1
            continue
        item.setdefault("status", "candidate")
        bank.setdefault("snippets", []).append(item)
        existing_ids.add(item["id"])
        added += 1
    for key in ("style_notes", "argument_moves"):
        if key in incoming and isinstance(incoming[key], list):
            bank.setdefault(key, []).extend(incoming[key])
    _save_bank(bank)
    print(f"Merged {added} snippets ({skipped} skipped) → {BANK_PATH}")


def bank_summary() -> None:
    bank = _load_bank()
    snippets = bank.get("snippets", [])
    by_use: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for s in snippets:
        by_status[s.get("status", "unknown")] = by_status.get(s.get("status", "unknown"), 0) + 1
        for u in s.get("use_in", []):
            by_use[u] = by_use.get(u, 0) + 1
    print(f"Research bank: {len(snippets)} snippets")
    print(f"  style_notes: {len(bank.get('style_notes', []))}")
    print(f"  argument_moves: {len(bank.get('argument_moves', []))}")
    if by_status:
        print("  by status:", ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())))
    if by_use:
        print("  by use_in:")
        for k, v in sorted(by_use.items(), key=lambda x: -x[1])[:12]:
            print(f"    {k}: {v}")


def print_manifest(spec: dict, as_json: bool) -> None:
    m = manifest(spec)
    if as_json:
        print(json.dumps(m, indent=2))
        return
    print("=" * 72)
    print(f"RESEARCH MINING — {m['contract']}  (v{m['version']})")
    print("=" * 72)
    print(f"Essay style ref: {m.get('essay_style_ref')}")
    print("\nEssay moves:")
    for move in m["essay_moves"]:
        print(f"  · {move}")
    print("\nWorkflow:")
    for step in m["workflow"]:
        print(f"  {step}")
    print("\nParallel passes:")
    for p in m["parallel_passes"]:
        print(f"\n  [{p['pass']}]")
        print(f"    deliver: {p['deliver']}")
        print(f"    bots: {', '.join(p['bots'])}")
        for s in p["sources"]:
            print(f"    source: {s['id']} — {', '.join(s.get('cite_keys', []) or ['no cite_keys'])}")
        for b in p["bot_briefs"]:
            print(f"      · {b['id']} — {b['role']}")


def print_sources(spec: dict) -> None:
    for s in spec.get("source_catalog", []):
        print(f"{s['id']} [{s['tier']}]")
        for u in s.get("urls", []):
            print(f"  {u}")
        if s.get("cite_keys"):
            print(f"  cites: {', '.join(s['cite_keys'])}")
        print(f"  mine: {', '.join(s.get('mine_for', []))}")
        print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Research mining manifest and merge")
    ap.add_argument("--manifest", action="store_true", help="Print parallel pass manifest")
    ap.add_argument("--sources", action="store_true", help="List source catalog")
    ap.add_argument("--bank-summary", action="store_true", help="Summarize research_bank.json")
    ap.add_argument("--merge", metavar="FILE", help="Merge snippets JSON into research bank")
    ap.add_argument("--prompt", metavar="PASS", help="Print subagent prompt for one pass")
    ap.add_argument("--json", action="store_true", help="JSON output for --manifest")
    args = ap.parse_args()

    if not any([args.manifest, args.sources, args.bank_summary, args.merge, args.prompt]):
        args.manifest = True

    spec = _load("research_mining.json")
    if args.merge:
        merge_snippets(args.merge)
    if args.bank_summary:
        bank_summary()
    if args.sources:
        print_sources(spec)
    if args.prompt:
        print(pass_prompt(spec, args.prompt))
    if args.manifest:
        print_manifest(spec, args.json)


if __name__ == "__main__":
    main()
