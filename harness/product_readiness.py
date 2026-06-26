#!/usr/bin/env python3
"""Commercial offering readiness harness — holds gaps for filed parametric, curtailment at scale,
market alternative, and IOSCO-grade benchmark until evidence artifacts pass.

  python3 harness/product_readiness.py           # report; exit 0 (informational)
  python3 harness/product_readiness.py --strict  # exit 1 if any offering 0% ready

Reads: contract/products/commercial_offerings.json
Writes: data/product_readiness_report.txt, data/product_readiness_report.json
"""

from __future__ import annotations

import fnmatch
import json
import os
import statistics as st
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "contract" / "products" / "commercial_offerings.json"
REPORT_TXT = ROOT / "data" / "product_readiness_report.txt"
REPORT_JSON = ROOT / "data" / "product_readiness_report.json"

REGISTER = ("neso.energy", "api.neso.energy", ".gov.uk", "ofgem.gov.uk", "opendatasoft.com",
            "data.ssen.co.uk", "connecteddata.nationalgrid.co.uk", "elexon")
FILING = ("register.fca.org.uk", "data.fca.org.uk", "company-information.service.gov.uk")
RATING = ("ambest.com", "spglobal.com", "moodys.com", "fitchratings.com")


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def tier_of_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "unscorable"
    if any(h in host for h in REGISTER + FILING + RATING):
        return "measured_or_disclosed"
    return "assessed"


def eff_tier(sf: dict) -> str:
    et = sf.get("evidence_tier")
    if et in ("measured", "disclosed", "derived"):
        return "measured_or_disclosed"
    if et == "assessed":
        return "assessed"
    sources = sf.get("sources") or []
    if not sources:
        return "unscorable"
    order = {"measured_or_disclosed": 0, "assessed": 1, "unscorable": 2}
    return min((tier_of_url(s) for s in sources), key=lambda t: order[t])


def blended_measured_share(records_path: Path) -> float:
    if not records_path.exists():
        return 0.0
    rubric = load_json(ROOT / "contract" / "rubric.json")
    records = load_json(records_path)
    if not rubric or not records:
        return 0.0

    def axis_share(axis_name: str) -> float:
        cfg = rubric[axis_name]
        inputs_key = f"{axis_name}_inputs"
        md = 0.0
        for rec in records:
            for k, c in cfg.items():
                sf = rec.get(inputs_key, {}).get(k, {})
                if eff_tier(sf) == "measured_or_disclosed":
                    md += c["weight"]
        return md / len(records) if records else 0.0

    return st.mean([axis_share("exposure"), axis_share("preparedness")])


def check_criterion(crit: dict) -> tuple[str, str, str]:
    """Return (status, detail, blocker). status: PASS | FAIL | WARN"""
    kind = crit["check"]

    if kind == "json_array_min":
        path = ROOT / crit["artifact"]
        data = load_json(path)
        if data is None:
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        arr = data
        for key in crit.get("path", "").split("."):
            if key:
                arr = arr.get(key, [])
        n = len(arr) if isinstance(arr, list) else 0
        need = crit.get("min_count", 1)
        if n >= need:
            return "PASS", f"{n}/{need} entries", ""
        return "FAIL", f"{n}/{need} entries — populate {crit['artifact']}", crit.get("label", crit["id"])

    if kind == "file_exists_json":
        path = ROOT / crit["artifact"]
        data = load_json(path)
        if data is None:
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        missing = [f for f in crit.get("required_fields", []) if not _field_populated(data, f)]
        if missing:
            return "FAIL", f"null fields: {', '.join(missing)}", crit.get("label", crit["id"])
        return "PASS", "all required fields populated", ""

    if kind == "json_field_true":
        path = ROOT / crit["artifact"]
        data = load_json(path)
        if data is None:
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        val = _get_nested(data, crit.get("path", ""))
        if val is True:
            return "PASS", "signed=true", ""
        return "FAIL", f"{crit.get('path')}={val!r}", crit.get("label", crit["id"])

    if kind == "json_field_nonempty":
        path = ROOT / crit["artifact"]
        data = load_json(path)
        if data is None:
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        val = _get_nested(data, crit.get("path", ""))
        if val not in (None, "", [], {}):
            return "PASS", str(val)[:60], ""
        return "FAIL", "empty", crit.get("label", crit["id"])

    if kind == "json_nested_required":
        path = ROOT / crit["artifact"]
        data = load_json(path)
        if data is None:
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        nested = data
        for key in crit.get("path", "").split("."):
            if key:
                nested = nested.get(key) if isinstance(nested, dict) else None
        if not isinstance(nested, dict):
            return "FAIL", f"missing nested {crit.get('path')}", crit.get("label", crit["id"])
        missing = [f for f in crit.get("required_fields", []) if not _field_populated(nested, f)]
        if missing:
            return "FAIL", f"null: {', '.join(missing)}", crit.get("label", crit["id"])
        return "PASS", "nested fields populated", ""

    if kind == "directory_min_files":
        d = ROOT / crit["artifact"]
        if not d.is_dir():
            return "FAIL", f"missing directory {crit['artifact']}", crit.get("label", crit["id"])
        pattern = crit.get("pattern", "*")
        files = [f for f in d.iterdir() if fnmatch.fnmatch(f.name, pattern)]
        need = crit.get("min_files", 1)
        if len(files) >= need:
            return "PASS", f"{len(files)}/{need} files", ""
        return "FAIL", f"{len(files)}/{need} files in {crit['artifact']}", crit.get("label", crit["id"])

    if kind == "files_exist":
        missing = [a for a in crit.get("artifacts", []) if not (ROOT / a).exists()]
        if missing:
            return "FAIL", f"missing: {', '.join(missing)}", crit.get("label", crit["id"])
        return "PASS", f"{len(crit['artifacts'])} artifacts present", ""

    if kind == "file_contains":
        path = ROOT / crit["artifact"]
        if not path.exists():
            return "FAIL", f"missing {crit['artifact']}", crit.get("label", crit["id"])
        text = path.read_text().lower()
        needle = crit.get("must_contain", "").lower()
        if needle in text:
            return "PASS", f"contains '{needle}'", ""
        return "FAIL", f"no '{needle}' in {crit['artifact']}", crit.get("label", crit["id"])

    if kind == "records_measured_subfactor":
        path = ROOT / crit.get("records", "data/records.measured.json")
        records = load_json(path)
        if not records:
            return "FAIL", f"missing {path.relative_to(ROOT)}", crit.get("label", crit["id"])
        layer = crit.get("layer")
        sf = crit.get("sub_factor")
        min_tier = crit.get("min_tier", "measured")
        tier_ok = {"measured": {"measured"}, "disclosed": {"measured", "disclosed", "derived"},
                   "derived": {"measured", "disclosed", "derived"}}
        allowed = tier_ok.get(min_tier, {min_tier})
        subset = [r for r in records if r.get("layer") == layer]
        if not subset:
            return "FAIL", f"no layer={layer} records", crit.get("label", crit["id"])
        good = 0
        for r in subset:
            et = r.get("exposure_inputs", {}).get(sf, {}).get("evidence_tier")
            if et in allowed:
                good += 1
        pct = good / len(subset)
        need = crit.get("min_coverage_pct", 1.0)
        if pct >= need:
            return "PASS", f"{good}/{len(subset)} L{layer} @ {sf} tier>={min_tier}", ""
        return "FAIL", f"{good}/{len(subset)} L{layer} measured (need {need:.0%})", crit.get("label", crit["id"])

    if kind == "eval_l5_min":
        records = crit.get("records", "data/records.measured.json")
        share = blended_measured_share(ROOT / records)
        need = crit.get("min_blended_pct", 0.60)
        if share >= need:
            return "PASS", f"blended {share:.0%} >= {need:.0%}", ""
        return "FAIL", f"blended {share:.0%} < {need:.0%}", crit.get("label", crit["id"])

    return "WARN", f"unknown check {kind}", crit.get("label", crit["id"])


def _field_populated(data: dict, field: str) -> bool:
    val = data.get(field)
    return val not in (None, "", [], {})


def _get_nested(data: Any, path: str) -> Any:
    val = data
    for key in path.split("."):
        if not key:
            continue
        val = val.get(key) if isinstance(val, dict) else None
    return val


def main() -> int:
    strict = "--strict" in sys.argv
    catalog = load_json(CATALOG)
    if not catalog:
        print(f"ERROR: missing {CATALOG}")
        return 1

    lines: list[str] = []
    lines.append("NFRI COMMERCIAL OFFERING READINESS")
    lines.append("=" * 72)
    lines.append(f"catalog: {CATALOG.relative_to(ROOT)}")
    lines.append("")

    report_offerings = []
    any_zero = False

    for off in catalog["offerings"]:
        oid = off["id"]
        label = off["label"]
        criteria_results = []
        pass_n = 0
        blockers = []

        lines.append(f"## {oid}")
        lines.append(f"   {label}")
        lines.append(f"   layer: {off.get('layer')} | target: {off.get('readiness_target')}")
        lines.append("")

        for crit in off["criteria"]:
            status, detail, blocker = check_criterion(crit)
            if status == "PASS":
                pass_n += 1
            if blocker:
                blockers.append(blocker)
            flag = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}[status]
            lines.append(f"  [{flag:4}] {crit['id']} — {crit['label']}")
            lines.append(f"         {detail}")
            criteria_results.append({
                "id": crit["id"],
                "label": crit["label"],
                "status": status,
                "detail": detail,
                "artifact": crit.get("artifact"),
                "citation_ids": crit.get("citation_ids", []),
            })

        total = len(off["criteria"])
        pct = pass_n / total if total else 0
        readiness = "READY" if pass_n == total else ("PARTIAL" if pass_n > 0 else "NOT_READY")
        if pass_n == 0:
            any_zero = True
        lines.append("")
        lines.append(f"  READINESS: {readiness} ({pass_n}/{total} criteria, {pct:.0%})")
        if blockers:
            lines.append(f"  Blockers: {'; '.join(blockers[:3])}")
        lines.append("")

        report_offerings.append({
            "id": oid,
            "label": label,
            "readiness": readiness,
            "pass_count": pass_n,
            "total_count": total,
            "pass_pct": round(pct, 4),
            "criteria": criteria_results,
        })

    lines.append("=" * 72)
    lines.append("SUMMARY")
    for ro in report_offerings:
        lines.append(f"  {ro['id']}: {ro['readiness']} ({ro['pass_count']}/{ro['total_count']})")
    lines.append("")
    lines.append("Populate contract/products/commercial/* and governance/* to advance readiness.")
    lines.append("Pricing pipeline: contract/products/pricing/stages/*")

    text = "\n".join(lines) + "\n"
    REPORT_TXT.write_text(text)
    REPORT_JSON.write_text(json.dumps({
        "version": "0.1",
        "offerings": report_offerings,
    }, indent=2) + "\n")

    print(text, end="")
    if strict and any_zero:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
