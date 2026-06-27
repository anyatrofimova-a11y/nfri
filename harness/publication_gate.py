#!/usr/bin/env python3
"""Publication gate pipeline — measure, score, eval, and report L5 progress.

Runs the live measurement chain on the gate cohort (trigger + capital carriers +
mapped L3 assets), scores records.measured.json, evaluates L5, and writes a gap
report when the ≥60% blended gate is not yet met.

  python3 harness/publication_gate.py              # measure + score + eval + gap
  python3 harness/publication_gate.py --check-only # eval + gap (no network)
  python3 harness/publication_gate.py --promote    # copy measured → records.publishable.json

See RUNBOOK_LIVE.md and contract/DATA_POLICY.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
DATA = os.path.join(ROOT, "data")
MEASURED = os.path.join(DATA, "records.measured.json")
PUBLISHABLE = os.path.join(DATA, "records.publishable.json")
GATE = 0.60

sys.path.insert(0, os.path.join(ROOT, "harness"))
from scoring import score_all  # noqa: E402

REGISTER = (
    "neso.energy", "api.neso.energy", ".gov.uk", "ofgem.gov.uk", "opendatasoft.com",
    "data.ssen.co.uk", "connecteddata.nationalgrid.co.uk", "elexon",
)
FILING = ("register.fca.org.uk", "data.fca.org.uk", "company-information.service.gov.uk", "lloyds.com")
RATING = ("ambest.com", "spglobal.com", "moodys.com", "fitchratings.com")


def tier_of_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "unscorable"
    if any(h in host for h in REGISTER + FILING + RATING):
        return "md"
    return "unscorable"


def eff_tier(sf: dict) -> str:
    et = sf.get("evidence_tier")
    if et in ("measured", "disclosed", "derived"):
        return "md"
    if et == "FIXTURE_DEMO":
        return "fixture"
    src = sf.get("sources") or []
    if not src:
        return "unscorable"
    return "md" if any(tier_of_url(s) == "md" for s in src) else "unscorable"


def entity_l5_share(rec: dict, rubric: dict) -> float:
    md = 0.0
    for ax, cfg in (("exposure_inputs", rubric["exposure"]), ("preparedness_inputs", rubric["preparedness"])):
        for k, c in cfg.items():
            if k not in rec[ax]:
                continue
            if eff_tier(rec[ax][k]) == "md":
                md += c["weight"]
    return md / 2.0


def gap_analysis(records: list, rubric: dict) -> list[str]:
    lines = ["GAP ANALYSIS (L5 publication gate)", "-" * 56]
    shares = [(entity_l5_share(r, rubric), r) for r in records]
    mean = sum(s for s, _ in shares) / len(shares) if shares else 0.0
    lines.append(f"blended share: {mean:.0%}  (gate ≥{GATE:.0%})  gap: {max(0, GATE - mean):.0%}")
    lines.append(f"entities: {len(records)}")
    lines.append("")

    unmet = Counter()
    for r in records:
        for ax, cfg in (("exposure_inputs", rubric["exposure"]), ("preparedness_inputs", rubric["preparedness"])):
            for k, c in cfg.items():
                if k not in r[ax]:
                    continue
                if eff_tier(r[ax][k]) != "md":
                    unmet[k] += c["weight"]
    lines.append("Top unmet sub-factor weight (summed across entities):")
    for k, w in unmet.most_common(8):
        lines.append(f"  {k:<28} {w:.1f}")
    lines.append("")

    low = sorted(shares, key=lambda x: x[0])[:5]
    high = sorted(shares, key=lambda x: x[0], reverse=True)[:5]
    lines.append("Lowest entity shares:")
    for s, r in low:
        lines.append(f"  {s:.0%}  {r['entity_id']}  L{r['layer']} {r['entity_type']}")
    lines.append("Highest entity shares:")
    for s, r in high:
        lines.append(f"  {s:.0%}  {r['entity_id']}  L{r['layer']} {r['entity_type']}")
    lines.append("")

    book_n = sum(1 for r in records if r["exposure_inputs"].get("book_concentration", {}).get("evidence_tier") == "disclosed")
    cap_n = len(json.load(open(os.path.join(ROOT, "contract", "capital_inputs.json"))).get("inputs", {}))
    l3 = [r for r in records if r.get("layer") == 3]
    l3_m = sum(1 for r in l3 if r["exposure_inputs"].get("non_firm_intensity", {}).get("evidence_tier") == "measured")
    lines.append(f"book_concentration disclosed: {book_n}/{cap_n} carriers")
    lines.append(f"non_firm_intensity measured: {l3_m}/{len(l3)} L3 assets")
    lines.append("")
    if mean < GATE:
        lines.append("Next levers (no synthetic data):")
        lines.append("  1. Populate contract/book_inputs.json — named energy/power GWP from Lloyd's class tables / SFCR")
        lines.append("  2. Extend ASSET_ROUTE + asset_boundary_map.json; re-run measure_non_firm.py --live")
        lines.append("  3. Broaden trigger_inputs + capital_inputs coverage across gate cohort")
    else:
        lines.append("Gate PASSED — run: python3 harness/build_frontend.py --publishable")
    return lines


def run_measure_live() -> int:
    p = subprocess.run([PY, os.path.join(ROOT, "harness", "measure_all.py"), "--live"], cwd=ROOT)
    return p.returncode


def score_measured() -> None:
    records = json.load(open(MEASURED))
    for r in records:
        r.pop("scores", None)
    records, cut_exp, cut_prep = score_all(records)
    for r in records:
        if r.get("scores"):
            r["scores"]["calibration"] = f"median exp>={cut_exp} prep>={cut_prep}"
    json.dump(records, open(MEASURED, "w"), indent=2, ensure_ascii=False)


def run_evals() -> int:
    p = subprocess.run([PY, os.path.join(ROOT, "harness", "evals.py"), MEASURED], cwd=ROOT)
    return p.returncode


def read_l5_share() -> tuple[float, str]:
    path = os.path.join(DATA, "eval_report.txt")
    if not os.path.exists(path):
        return 0.0, "FAIL"
    text = open(path).read()
    import re
    m = re.search(r"BLENDED measured\+disclosed share = (\d+)%", text)
    share = int(m.group(1)) / 100 if m else 0.0
    status = "PASS" if "L5  [PASS]" in text or share >= GATE else "FAIL"
    return share, status


def main() -> int:
    check_only = "--check-only" in sys.argv
    promote = "--promote" in sys.argv

    if not check_only:
        print("=== PUBLICATION GATE: live measurement ===")
        if run_measure_live() != 0:
            print("FAIL: measure_all --live")
            return 1
        print("\n=== PUBLICATION GATE: score measured universe ===")
        score_measured()

    if not os.path.exists(MEASURED):
        print(f"missing {MEASURED}")
        return 1

    print("\n=== PUBLICATION GATE: eval L5 ===")
    run_evals()

    rubric = json.load(open(os.path.join(ROOT, "contract", "rubric.json")))
    records = json.load(open(MEASURED))
    gap = gap_analysis(records, rubric)
    gap_path = os.path.join(DATA, "publication_gap_report.txt")
    open(gap_path, "w").write("\n".join(gap))
    print("\n".join(gap))
    print(f"\nwrote: data/publication_gap_report.txt")

    share, status = read_l5_share()
    print(f"\nL5: {share:.0%} → {status}")

    if status == "PASS":
        import shutil
        shutil.copy2(MEASURED, PUBLISHABLE)
        print(f"promoted: data/records.publishable.json ({len(records)} entities)")
    elif promote:
        print("WARN: --promote requested but L5 gate has not passed")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
