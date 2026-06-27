#!/usr/bin/env python3
"""Profile depth gap report — what is done vs pending for Ciridae parity.

  python3 harness/profile_gap_report.py
  python3 harness/profile_gap_report.py --json
  python3 harness/profile_gap_report.py --write data/profile_gap_report.txt
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CT = os.path.join(ROOT, "contract")
SITE = os.path.join(ROOT, "site", "data")


def _load(path: str, default=None):
    if not os.path.isfile(path):
        return default if default is not None else {}
    return json.load(open(path))


def _batch_done(batch_dir: str, batch_key: str) -> bool:
    path = os.path.join(ROOT, batch_dir, f"{batch_key}.json")
    if not os.path.isfile(path):
        return False
    doc = json.load(open(path))
    payload = doc.get("inputs") or doc.get("entities") or doc
    if isinstance(payload, dict):
        return len([k for k in payload if not k.startswith("_")]) > 0
    if isinstance(payload, list):
        return len(payload) > 0
    return False


def compute_gaps() -> dict:
    records = _load(os.path.join(DATA, "records.scored.json"), [])
    copy = _load(os.path.join(CT, "entity_copy.json"), {}).get("entities", {})
    analysis = _load(os.path.join(CT, "entity_analysis.json"), {}).get("entities", {})
    profiles = _load(os.path.join(SITE, "profiles.json"), {})
    manifest = _load(os.path.join(DATA, "profile_passes", "manifest.json"), {})

    scored = [r for r in records if r.get("scores")]
    l1 = [r for r in scored if r.get("layer") == 1]
    l3 = [r for r in scored if r.get("layer") == 3]
    l4 = [r for r in scored if r.get("layer") == 4]

    thin = []
    for r in scored:
        eid = r["entity_id"]
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for k, sf in (r.get(ax) or {}).items():
                rat = (sf.get("rationale") or "").strip()
                if len(rat) < 40:
                    thin.append({"entity_id": eid, "subfactor": k, "len": len(rat), "text": rat})

    no_placements = [r["entity_id"] for r in scored if not (copy.get(r["entity_id"]) or {}).get("placements")]
    l3_no_analysis = [r["entity_id"] for r in l3 if r["entity_id"] not in analysis]

    passes = {}
    for pid, spec in manifest.get("passes", {}).items():
        batch_dir = spec.get("batch_dir", "")
        bm_path = os.path.join(ROOT, batch_dir, "manifest.json")
        batches = {}
        if os.path.isfile(bm_path):
            for bk, ids in json.load(open(bm_path)).get("batches", {}).items():
                batches[bk] = {"entities": ids, "done": _batch_done(batch_dir, bk)}
        elif pid == "entity_analysis":
            ea_m = _load(os.path.join(DATA, "entity_analysis", "manifest.json"), {})
            for bk, ids in ea_m.get("batches", {}).items():
                batches[bk] = {"entities": ids, "done": _batch_done("data/entity_analysis", bk)}
        done_b = sum(1 for b in batches.values() if b["done"])
        passes[pid] = {
            "status": spec.get("status", "pending"),
            "batches_done": done_b,
            "batches_total": len(batches),
            "batches": batches,
        }

    meas = {}
    for pid, spec in manifest.get("measurement_passes", {}).items():
        batch_dir = spec.get("batch_dir", "")
        bm_path = os.path.join(ROOT, batch_dir, "manifest.json")
        batches = {}
        if os.path.isfile(bm_path):
            for bk in json.load(open(bm_path)).get("batches", {}):
                batches[bk] = _batch_done(batch_dir, bk)
        meas[pid] = {
            "status": spec.get("status", "pending"),
            "batches_done": sum(1 for v in batches.values() if v),
            "batches_total": len(batches),
        }

    sys.path.insert(0, os.path.join(ROOT, "harness"))
    try:
        from build_frontend import authoritative_share, load_records
        mp = os.path.join(DATA, "records.measured.json")
        tier_src = json.load(open(mp)) if os.path.isfile(mp) else records
        gate_share = authoritative_share(tier_src)
    except Exception:
        gate_share = 0.0

    return {
        "as_of": manifest.get("passes", {}).get("synthesis", {}).get("status"),
        "universe": {"scored": len(scored), "l1": len(l1), "l3": len(l3), "l4": len(l4)},
        "narrative": {
            "executive_summary": sum(1 for r in scored if copy.get(r["entity_id"], {}).get("executive_summary")),
            "axis_rationale": sum(1 for r in scored if copy.get(r["entity_id"], {}).get("axis_rationale")),
            "portfolio_narrative_l1": sum(1 for r in l1 if copy.get(r["entity_id"], {}).get("portfolio_narrative")),
            "placements": len(scored) - len(no_placements),
            "profiles_with_exec": sum(1 for p in profiles.values() if p.get("executive_summary")),
            "entity_analysis_l3": len(analysis),
            "thin_rationales": len(thin),
        },
        "gate_share": round(gate_share, 3),
        "pending": {
            "thin_rationales": thin,
            "l3_missing_entity_analysis": l3_no_analysis,
            "missing_placements": no_placements[:20],
            "missing_placements_count": len(no_placements),
        },
        "passes": passes,
        "measurement": meas,
        "optimization_ladder": [
            {"priority": "P0", "pass": "entity_analysis", "why": "23/24 L3 assets lack grid/cover-stack depth — biggest Ciridae gap on click"},
            {"priority": "P0", "pass": "sfcr_mining", "why": "Raises L5 gate — disclosed GWP on gate cohort carriers"},
            {"priority": "P1", "pass": "l4_research", "why": "17 reinsurers unscored on aggregation subs"},
            {"priority": "P1", "pass": "thin_rationales", "why": f"{len(thin)} sub-factors under 40 chars"},
            {"priority": "P2", "pass": "placements", "why": f"{len(no_placements)} entities without product chips"},
            {"priority": "P2", "pass": "book_mining", "why": "Lloyd's class GWP for book_concentration measured tier"},
            {"priority": "P3", "pass": "register_pull", "why": "ECR/TEC live pull for non_firm_intensity measured"},
            {"priority": "P3", "pass": "audit", "why": "data_steward tier/source QA at scale"},
        ],
    }


def format_report(g: dict) -> str:
    u = g["universe"]
    n = g["narrative"]
    lines = [
        "NFRI PROFILE DEPTH — GAP REPORT",
        "=" * 56,
        f"Universe: {u['scored']} scored ({u['l1']} L1 · {u['l3']} L3 · {u['l4']} L4)",
        f"L5 gate share: {g['gate_share']:.0%}  ({'PASS' if g['gate_share'] >= 0.6 else 'PROVISIONAL'})",
        "",
        "NARRATIVE (Ciridae layer)",
        f"  executive_summary     {n['executive_summary']}/{u['scored']}",
        f"  axis_rationale        {n['axis_rationale']}/{u['scored']}",
        f"  portfolio_narrative   {n['portfolio_narrative_l1']}/{u['l1']} L1",
        f"  placements            {n['placements']}/{u['scored']}",
        f"  entity_analysis (L3)  {n['entity_analysis_l3']}/{u['l3']}",
        f"  thin rationales       {n['thin_rationales']} sub-factors",
        "",
        "PROFILE PASSES",
    ]
    for pid, p in g["passes"].items():
        prog = f"{p['batches_done']}/{p['batches_total']} batches" if p["batches_total"] else p["status"]
        lines.append(f"  [{p['status']:12}] {pid:18} {prog}")
        for bk, bd in (p.get("batches") or {}).items():
            mark = "✓" if bd["done"] else " "
            lines.append(f"      [{mark}] {bk} ({len(bd['entities'])})")
    lines += ["", "MEASUREMENT PASSES"]
    for pid, p in g["measurement"].items():
        prog = f"{p['batches_done']}/{p['batches_total']} batches" if p["batches_total"] else p["status"]
        lines.append(f"  [{p['status']:12}] {pid:18} {prog}")
    lines += ["", "OPTIMIZATION LADDER (run in order)"]
    for item in g["optimization_ladder"]:
        lines.append(f"  {item['priority']} {item['pass']:20} — {item['why']}")
    if g["pending"]["thin_rationales"]:
        lines += ["", "THIN RATIONALES (fix first)"]
        for t in g["pending"]["thin_rationales"][:20]:
            lines.append(f"  {t['entity_id']}.{t['subfactor']} ({t['len']} chars)")
    if g["pending"]["l3_missing_entity_analysis"]:
        lines += ["", f"L3 MISSING entity_analysis ({len(g['pending']['l3_missing_entity_analysis'])})"]
        lines.append("  " + ", ".join(g["pending"]["l3_missing_entity_analysis"][:12]))
        if len(g["pending"]["l3_missing_entity_analysis"]) > 12:
            lines.append(f"  … +{len(g['pending']['l3_missing_entity_analysis']) - 12} more")
    lines.append("=" * 56)
    lines.append("Fan out: python3 harness/profile_orchestrator.py fanout")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", metavar="PATH")
    args = ap.parse_args()
    g = compute_gaps()
    if args.json:
        print(json.dumps(g, indent=2))
        return 0
    text = format_report(g)
    print(text)
    if args.write:
        os.makedirs(os.path.dirname(args.write) or ".", exist_ok=True)
        open(args.write, "w").write(text + "\n")
        print(f"\nWrote {args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
