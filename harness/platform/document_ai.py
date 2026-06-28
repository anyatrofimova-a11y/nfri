#!/usr/bin/env python3
"""Document-AI layer — validate extractions, apply to scoring inputs only (ADR-003).

Reads contract/trigger_inputs.json + data/fixtures/extraction_*.json as templates.
Never writes scores.* on records.

  python3 harness/platform/document_ai.py --apply
  python3 harness/platform/document_ai.py --verify
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEASURED = os.path.join(ROOT, "data", "records.measured.json")
SCHEMA = os.path.join(ROOT, "contract", "platform", "schemas", "extraction", "sub_factor_extraction.schema.json")
FIXTURES = os.path.join(ROOT, "data", "fixtures")


def validate_extraction(obj: dict) -> list[str]:
    issues = []
    for key in ("entity_id", "sub_factor", "rating_0_4", "evidence_tier", "confidence", "source_text", "sources"):
        if key not in obj:
            issues.append(f"missing {key}")
    if not obj.get("source_text", "").strip():
        issues.append("empty source_text")
    if obj.get("confidence", 0) < 0.7 and not obj.get("human_reviewed"):
        issues.append("confidence < 0.7 without human_reviewed")
    return issues


def apply_trigger_bank(records: list) -> int:
    """Delegate to measure_trigger/product via trigger_inputs — already disclosed tier."""
    trigger_path = os.path.join(ROOT, "contract", "trigger_inputs.json")
    if not os.path.isfile(trigger_path):
        return 0
    inputs = json.load(open(trigger_path, encoding="utf-8")).get("inputs", {})
    by_id = {r["entity_id"]: r for r in records}
    n = 0
    for eid in inputs:
        if eid in by_id and "scores" in by_id[eid]:
            issues = ["scores block must not be set by document-ai"]
            raise RuntimeError(f"ADR-003 violation on {eid}: {issues}")
    return len(inputs)


def verify_no_llm_scores(records: list) -> list[str]:
    violations = []
    for r in records:
        prov = r.get("provenance", {})
        if prov.get("method") == "llm_scored":
            violations.append(f"{r['entity_id']}: llm_scored provenance forbidden")
    return violations


def main() -> int:
    if not os.path.isfile(MEASURED):
        print(f"missing {MEASURED} — run measure_all --live first")
        return 1

    recs = json.load(open(MEASURED, encoding="utf-8"))

    if "--apply" in sys.argv:
        import subprocess
        py = sys.executable
        subprocess.run([py, os.path.join(ROOT, "harness", "measure_trigger.py"), "--live"], cwd=ROOT, check=False)
        subprocess.run([py, os.path.join(ROOT, "harness", "measure_product.py"), "--live"], cwd=ROOT, check=False)
        recs = json.load(open(MEASURED, encoding="utf-8"))
        n = apply_trigger_bank(recs)
        print(f"document_ai --apply: trigger bank covers {n} entities; scores untouched")

    # Validate fixture extractions
    issues_all = []
    for name in os.listdir(FIXTURES):
        if not name.startswith("extraction_") or not name.endswith(".json"):
            continue
        obj = json.load(open(os.path.join(FIXTURES, name), encoding="utf-8"))
        issues = validate_extraction(obj)
        if issues:
            issues_all.append(f"{name}: {', '.join(issues)}")

    violations = verify_no_llm_scores(recs)
    if violations:
        issues_all.extend(violations)

    if not os.path.isfile(SCHEMA):
        issues_all.append("missing extraction schema")

    if issues_all:
        print("document_ai --verify FAIL:")
        for i in issues_all:
            print(f"  · {i}")
        return 1

    print("document_ai --verify PASS (ADR-003: extract/cite only, no LLM scores)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
