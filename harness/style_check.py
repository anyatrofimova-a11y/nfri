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
FACT_RE = re.compile(r"\{\{fact:([a-z0-9_]+)\}\}")


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


def lint(name, contract, voice, analysis_writing=None, argument_writing=None, findings_writing=None):
    prose = prose_of(contract)
    plain = re.sub(r"<[^>]+>", " ", prose)
    findings = []
    for ap in voice["anti_patterns"]:
        for m in re.finditer(ap["regex"], plain):
            snippet = plain[max(0, m.start() - 20):m.start() + 30].strip()
            findings.append(f"anti-pattern [{ap['id']}] — {ap['why']}: …{snippet}…")
    meta_spec = (
        analysis_writing if name == "analysis"
        else argument_writing if name == "argument"
        else findings_writing if name == "findings"
        else None
    )
    if meta_spec:
        for ap in meta_spec.get("anti_meta", []):
            for m in re.finditer(ap["regex"], plain):
                snippet = plain[max(0, m.start() - 20):m.start() + 30].strip()
                tag = {"analysis": "analysis-meta", "argument": "argument-meta", "findings": "findings-meta"}.get(name, "meta")
                findings.append(f"{tag} [{ap['id']}] — {ap['why']}: …{snippet}…")
    raw = json.dumps(contract)
    n_nums = len(NUM_RE.findall(plain)) + len(FACT_RE.findall(raw))
    cited = set()
    for m in CITE_RE.finditer(raw):
        cited.update(k.strip() for k in m.group(1).split(","))
    frames = [f["id"] for f in voice["concept_frames"]
              if f.get("anchor") and (set(f["anchor"]) & cited)]
    words = len(plain.split())
    density = round((n_nums + len(cited)) / max(words, 1) * 100, 1)
    ok = (not findings) and n_nums >= 2 and density >= 1.0
    if name in ("analysis", "argument") and meta_spec:
        untagged = [b for b in contract.get("blocks", [])
                    if b.get("type") in ("p", "lead", "pull") and not b.get("bot")]
        if untagged:
            ok = False
    if name == "findings" and findings_writing:
        used_facts = set(FACT_RE.findall(raw))
        unknown = used_facts - set(findings_writing.get("fact_catalog", {}).get("keys", []))
        if unknown:
            findings.append(f"findings-fact unknown keys: {', '.join(sorted(unknown))}")
            ok = False
        if len(used_facts) < 8:
            findings.append(f"findings-fact density low ({len(used_facts)} distinct {{fact:}} keys; target ≥8)")
            ok = False
    return {"name": name, "words": words, "nums": n_nums, "cites": len(cited),
            "frames": frames, "density": density, "findings": findings, "ok": ok}


def section_report(contract, spec):
    """Map contract kickers to methodology sections and expected bots."""
    kickers = [b.get("text", "").lower() for b in contract.get("blocks", []) if b.get("type") == "kicker"]
    spec_k = {s["kicker"].lower(): s for s in spec.get("sections", []) if s.get("kicker")}
    present, missing, bots = [], [], set()
    for k in spec_k:
        if k in kickers:
            present.append(k)
            bots.update(spec_k[k].get("bots", []))
        else:
            missing.append(k)
    return {"present": present, "missing": missing, "bots": sorted(bots)}


def bot_report(contract, spec):
    """Verify paragraph bot tags and parallel editorial passes."""
    passes = {p["pass"]: set(p["bots"]) for p in spec.get("deployment", {}).get("parallel_passes", [])}
    section_bots = {}
    current = None
    tagged, untagged = [], []
    for b in contract.get("blocks", []):
        t = b.get("type")
        if t == "kicker":
            current = b.get("text", "").lower()
            section_bots[current] = []
        elif t in ("p", "lead", "pull"):
            bot = b.get("bot")
            if bot:
                tagged.append(bot)
                if current:
                    section_bots.setdefault(current, []).append(bot)
            else:
                untagged.append(f"{current or '?'}:{t}")
    tagged_set = set(tagged)
    pass_cov = {
        name: {"hit": len(tagged_set & bots), "total": len(bots), "missing": sorted(bots - tagged_set)}
        for name, bots in passes.items()
    }
    return {"tagged": tagged, "untagged": untagged, "section_bots": section_bots, "passes": pass_cov}


def analysis_bot_report(contract, spec):
    return bot_report(contract, spec)


def thesis_combined_report(contracts, analysis_writing):
    """Bot coverage across argument + analysis read as one essay."""
    combined = []
    for c in contracts:
        for b in c.get("blocks", []):
            if b.get("type") in ("p", "lead", "pull") and b.get("bot"):
                combined.append(b["bot"])
    tagged_set = set(combined)
    passes = (analysis_writing or {}).get("deployment", {}).get("thesis_combined_passes") or {}
    out = {}
    for name, bots in passes.items():
        if name.startswith("_"):
            continue
        bot_set = set(bots)
        out[name] = {
            "hit": len(tagged_set & bot_set),
            "total": len(bot_set),
            "missing": sorted(bot_set - tagged_set),
        }
    return out


def analysis_section_report(contract, spec):
    return section_report(contract, spec)


def main():
    voice = json.load(open(os.path.join(CT, "voice.json")))
    aw_path = os.path.join(CT, "analysis_writing.json")
    argw_path = os.path.join(CT, "argument_writing.json")
    fw_path = os.path.join(CT, "findings_writing.json")
    analysis_writing = json.load(open(aw_path)) if os.path.exists(aw_path) else None
    argument_writing = json.load(open(argw_path)) if os.path.exists(argw_path) else None
    findings_writing = json.load(open(fw_path)) if os.path.exists(fw_path) else None
    strict = "--strict" in sys.argv
    print(f"REGISTER LINT — voice spec v{voice.get('version')}  "
          f"({len(voice['voice_rules'])} rules, {len(voice['anti_patterns'])} anti-patterns, "
          f"{len(voice['concept_frames'])} frames)")
    if analysis_writing:
        print(f"ANALYSIS METH — v{analysis_writing.get('version')}  "
              f"({len(analysis_writing.get('bots', []))} bots, "
              f"{len(analysis_writing.get('sections', []))} sections)")
    if argument_writing:
        print(f"ARGUMENT METH — v{argument_writing.get('version')}  "
              f"({len(argument_writing.get('bots', []))} bots, "
              f"{len(argument_writing.get('sections', []))} sections)")
    if findings_writing:
        print(f"FINDINGS METH — v{findings_writing.get('version')}  "
              f"({len(findings_writing.get('bots', []))} bots, "
              f"{len(findings_writing.get('sections', []))} sections, "
              f"{len(findings_writing.get('fact_catalog', {}).get('keys', []))} fact keys)")
    print("=" * 74)
    any_fail = False
    thesis_contracts = []
    for name in ESSAYS:
        path = os.path.join(CT, f"{name}.json")
        if not os.path.exists(path):
            continue
        contract = json.load(open(path))
        if name in ("argument", "analysis"):
            thesis_contracts.append(contract)
        r = lint(name, contract, voice, analysis_writing, argument_writing, findings_writing)
        flag = "OK " if r["ok"] else "WARN"
        if not r["ok"]:
            any_fail = True
        print(f"[{flag}] {name:<12} {r['words']:>4}w · {r['nums']:>2} nums · "
              f"{r['cites']:>2} cites · density {r['density']:>4} · frames: "
              + (", ".join(r["frames"]) or "none"))
        if name == "analysis" and analysis_writing:
            rep = section_report(contract, analysis_writing)
            bot_rep = analysis_bot_report(contract, analysis_writing)
            print(f"        sections {len(rep['present'])}/{len(rep['present']) + len(rep['missing'])} · "
                  f"paragraphs tagged: {len(bot_rep['tagged'])} · "
                  f"unique bots: {len(set(bot_rep['tagged']))}")
            for pname, cov in bot_rep["passes"].items():
                print(f"        pass {pname}: {cov['hit']}/{cov['total']} bots")
                if cov["missing"]:
                    print(f"          missing: {', '.join(cov['missing'])}")
            if bot_rep["untagged"]:
                print("        ⚠ untagged blocks:", ", ".join(bot_rep["untagged"]))
            if rep["missing"]:
                print("        ⚠ missing kickers:", ", ".join(rep["missing"]))
        if name == "argument" and argument_writing:
            rep = section_report(contract, argument_writing)
            bot_rep = bot_report(contract, argument_writing)
            print(f"        sections {len(rep['present'])}/{len(rep['present']) + len(rep['missing'])} · "
                  f"paragraphs tagged: {len(bot_rep['tagged'])} · "
                  f"unique bots: {len(set(bot_rep['tagged']))}")
            for pname, cov in bot_rep["passes"].items():
                print(f"        pass {pname}: {cov['hit']}/{cov['total']} bots")
                if cov["missing"]:
                    print(f"          missing: {', '.join(cov['missing'])}")
            if bot_rep["untagged"]:
                print("        ⚠ untagged blocks:", ", ".join(bot_rep["untagged"]))
            if rep["missing"]:
                print("        ⚠ missing kickers:", ", ".join(rep["missing"]))
        if name == "findings" and findings_writing:
            rep = section_report(contract, findings_writing)
            used = len(set(FACT_RE.findall(json.dumps(contract))))
            print(f"        sections {len(rep['present'])}/{len(rep['present']) + len(rep['missing'])} · "
                  f"{used} fact tokens · bots: {', '.join(rep['bots'][:6])}{'…' if len(rep['bots']) > 6 else ''}")
            if rep["missing"]:
                print("        ⚠ missing kickers:", ", ".join(rep["missing"]))
        for f in r["findings"]:
            print("        ⚠ " + f)
    if thesis_contracts and analysis_writing:
        combined = thesis_combined_report(thesis_contracts, analysis_writing)
        if combined:
            print("THESIS COMBINED — argument + analysis")
            for pname, cov in combined.items():
                print(f"        pass {pname}: {cov['hit']}/{cov['total']} bots")
                if cov["missing"]:
                    print(f"          missing: {', '.join(cov['missing'])}")
                    any_fail = True
    print("=" * 74)
    print("Frames available:", ", ".join(f["id"] for f in voice["concept_frames"]))
    if strict and any_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
