#!/usr/bin/env python3
"""NFRI — register/voice linter.

Lints the narrative essay contracts against contract/voice.json: flags off-register
anti-patterns, requires concrete substantiation (numbers / citations), and reports
which conceptual frames each section actually deploys (by the citation anchors in
the voice spec). This is the harness that keeps the prose at the target standard —
the conceptual register of the field, not generic whitepaper filler.

Usage:
  python3 harness/style_check.py            # lint all essay contracts, print scorecard
  python3 harness/style_check.py --strict   # non-zero exit if any section fails
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = os.path.join(ROOT, "contract")
ESSAYS = ("argument", "analysis", "findings", "methodology", "data")
NUM_RE = re.compile(r"(?<![A-Za-z])(\d[\d,.]*\s?(%|GW|MW|MWh|MVA|kV|bn|m|x|×)?)")
CITE_RE = re.compile(r"\{\{cite:([A-Za-z0-9_,\-]+)\}\}")
FACT_RE = re.compile(r"\{\{fact:[a-z0-9_]+\}\}")


def prose_of(contract):
    """Concatenate the human-readable prose fields of a contract (skip _meta)."""
    out = []

    def walk(v, key=None):
        if isinstance(v, str) and key in ("text", "note", "caption", "lead", "role"):
            out.append(v)
        elif isinstance(v, dict):
            for k, vv in v.items():
                if not k.startswith("_"):
                    walk(vv, k)
        elif isinstance(v, list):
            for vv in v:
                walk(vv, key)
    for b in contract.get("blocks", []):
        walk(b)
    return "\n".join(out)


def lint(name, contract, voice):
    prose = prose_of(contract)
    plain = re.sub(r"<[^>]+>", " ", prose)
    findings = []
    for ap in voice["anti_patterns"]:
        for m in re.finditer(ap["regex"], plain):
            snippet = plain[max(0, m.start() - 20):m.start() + 30].strip()
            findings.append(f"anti-pattern [{ap['id']}] — {ap['why']}: …{snippet}…")
    # numbers in prose, plus {{fact:}} tokens (which render as live figures)
    n_nums = len(NUM_RE.findall(plain)) + len(FACT_RE.findall(json.dumps(contract)))
    cited = set()
    for m in CITE_RE.finditer(json.dumps(contract)):
        cited.update(k.strip() for k in m.group(1).split(","))
    frames = [f["id"] for f in voice["concept_frames"]
              if f.get("anchor") and (set(f["anchor"]) & cited)]
    words = len(plain.split())
    # substantiation density: numbers + citations per 100 words
    density = round((n_nums + len(cited)) / max(words, 1) * 100, 1)
    ok = (not findings) and n_nums >= 2 and density >= 1.0
    return {"name": name, "words": words, "nums": n_nums, "cites": len(cited),
            "frames": frames, "density": density, "findings": findings, "ok": ok}


def main():
    voice = json.load(open(os.path.join(CT, "voice.json")))
    strict = "--strict" in sys.argv
    print(f"REGISTER LINT — voice spec v{voice.get('version')}  "
          f"({len(voice['voice_rules'])} rules, {len(voice['anti_patterns'])} anti-patterns, "
          f"{len(voice['concept_frames'])} frames)")
    print("=" * 74)
    any_fail = False
    for name in ESSAYS:
        path = os.path.join(CT, f"{name}.json")
        if not os.path.exists(path):
            continue
        r = lint(name, json.load(open(path)), voice)
        flag = "OK " if r["ok"] else "WARN"
        if not r["ok"]:
            any_fail = True
        print(f"[{flag}] {name:<12} {r['words']:>4}w · {r['nums']:>2} nums · "
              f"{r['cites']:>2} cites · density {r['density']:>4} · frames: "
              + (", ".join(r["frames"]) or "none"))
        for f in r["findings"]:
            print("        ⚠ " + f)
    print("=" * 74)
    print("Frames available:", ", ".join(f["id"] for f in voice["concept_frames"]))
    if strict and any_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
