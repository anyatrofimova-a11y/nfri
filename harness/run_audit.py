#!/usr/bin/env python3
"""Data-steward QA pass — source/tier audit at scale.

Reads data/records.scored.json + contract/citations.json; writes per-entity
findings to data/audit/batchN.json.

  python3 harness/run_audit.py --manifest          # write data/audit/manifest.json
  python3 harness/run_audit.py --batch batch1      # audit one batch
  python3 harness/run_audit.py --all               # audit all batches
  python3 harness/run_audit.py --summary           # print rollup from batch files
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDS = os.path.join(ROOT, "data", "records.scored.json")
CITATIONS = os.path.join(ROOT, "contract", "citations.json")
AUDIT_DIR = os.path.join(ROOT, "data", "audit")
MANIFEST = os.path.join(AUDIT_DIR, "manifest.json")

REGISTER = (
    "neso.energy", "api.neso.energy", ".gov.uk", "ofgem.gov.uk", "opendatasoft.com",
    "data.ssen.co.uk", "connecteddata.nationalgrid.co.uk", "elexon",
)
FILING = ("register.fca.org.uk", "data.fca.org.uk", "company-information.service.gov.uk")
RATING = ("ambest.com", "spglobal.com", "moodys.com", "fitchratings.com")
PRESS = (
    "reinsurancene.ws", "insurancetimes.co.uk", "artemis.bm", "datacenterdynamics.com",
    "theregister.com", "insurancebusinessmag.com", "reuters.com", "renews.biz",
    "insurancejournal.com", "computing.co.uk", "itpro.com", "businessinsurance.com",
    "datacentrenews.uk", "insurtechdigital.com", "electricalreview.co.uk", "uktech.news",
    "lifeinsuranceinternational.com", "instech.co", "techhq.com", "downing-renewables.co.uk",
    "colo-x.com", "datacentermap.com",
)
VENDOR = (
    "wikipedia.org", "apexinsurancebrokers.co.uk", "simplywall.st", "prnewswire.com",
    "businesswire.com", "thegpu.ai", "oxfordcalling.co.uk", "bebeez.eu",
    "swnetzerohub.org.uk", "netzerogo.org.uk",
)

TIER_ORDER = {"measured_or_disclosed": 0, "assessed": 1, "unscorable": 2, "fixture_demo": 3}
NUMERIC_SUBFACTORS = {
    "book_concentration", "non_firm_intensity", "aggregation_correlation", "trigger_gap",
    "tenor_mismatch", "capital_reinsurance", "data_monitoring", "non_firm_compute_exposure",
}


def tier_of_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "unscorable"
    if any(h in host for h in REGISTER):
        return "measured_or_disclosed"
    if any(h in host for h in FILING):
        return "measured_or_disclosed"
    if any(h in host for h in RATING):
        return "measured_or_disclosed"
    if any(h in host for h in PRESS):
        return "assessed"
    if any(h in host for h in VENDOR):
        return "unscorable"
    return "unscorable"


def best_source_tier(sources: list) -> str:
    if not sources:
        return "unscorable"
    return min((tier_of_url(s) for s in sources), key=lambda t: TIER_ORDER[t])


def declared_class(evidence_tier: str | None) -> str:
    et = (evidence_tier or "").strip()
    if et in ("measured", "disclosed", "derived"):
        return "measured_or_disclosed"
    if et == "assessed":
        return "assessed"
    if et == "FIXTURE_DEMO":
        return "fixture_demo"
    return "assessed" if et else "unscorable"


def load_records() -> list[dict]:
    return json.load(open(RECORDS))


def load_citation_keys() -> set[str]:
    if not os.path.isfile(CITATIONS):
        return set()
    return set(json.load(open(CITATIONS)).get("references", {}).keys())


def scored_entity_ids(records: list[dict]) -> list[str]:
    return [r["entity_id"] for r in records if r.get("scores")]


def build_manifest(ids: list[str], batch_size: int = 20) -> dict:
    batches = {}
    for i in range(0, len(ids), batch_size):
        n = i // batch_size + 1
        batches[f"batch{n}"] = ids[i:i + batch_size]
    return {
        "_doc": "data_steward source/tier QA — findings in batchN.json (no record patches).",
        "pass": "audit",
        "batch_size": batch_size,
        "parallel_agents": 2,
        "bots": ["data_steward"],
        "inputs": ["data/records.scored.json", "contract/citations.json"],
        "batches": batches,
    }


def audit_sub_factor(
    axis: str,
    sub_factor: str,
    sf: dict,
    cite_keys: set[str],
) -> list[dict]:
    findings = []
    rating = sf.get("rating_0_4", 0)
    rationale = (sf.get("rationale") or "").strip()
    sources = sf.get("sources") or []
    declared = sf.get("evidence_tier")
    src_tier = best_source_tier(sources)
    decl_class = declared_class(declared)

    if len(rationale) < 40:
        findings.append({
            "type": "thin_rationale",
            "severity": "error",
            "chars": len(rationale),
            "action": "Expand to 2–4 sentences with entity-specific facts.",
        })

    if rating >= 1 and not sources:
        findings.append({
            "type": "missing_source",
            "severity": "error",
            "rating": rating,
            "action": "Add primary URL or downgrade rating to 0.",
        })

    for cid in sf.get("citation_ids") or []:
        if cid not in cite_keys:
            findings.append({
                "type": "missing_cite",
                "severity": "error",
                "citation_id": cid,
                "action": f"Add {cid} to contract/citations.json or remove reference.",
            })

    if sources and TIER_ORDER[src_tier] > TIER_ORDER[decl_class]:
        findings.append({
            "type": "tier_mismatch",
            "severity": "warn",
            "declared_tier": declared or "(unset)",
            "declared_class": decl_class,
            "inferred_class": src_tier,
            "primary_source": sources[0],
            "action": "Downgrade evidence_tier to match source domain or replace with filing/register URL.",
        })
    elif sources and TIER_ORDER[src_tier] < TIER_ORDER[decl_class] and decl_class != "fixture_demo":
        findings.append({
            "type": "tier_upgrade_candidate",
            "severity": "info",
            "declared_tier": declared or "(unset)",
            "declared_class": decl_class,
            "inferred_class": src_tier,
            "primary_source": sources[0],
            "action": "Sources support stronger tier — verify and upgrade evidence_tier if appropriate.",
        })

    if declared in ("measured", "disclosed") and sub_factor in NUMERIC_SUBFACTORS:
        if sf.get("measured_value") is None and rating >= 1:
            findings.append({
                "type": "provenance_flag",
                "severity": "warn",
                "flag": "missing_measured_value",
                "declared_tier": declared,
                "action": "Populate measured_value or downgrade evidence_tier.",
            })

    if rating >= 2 and src_tier == "unscorable" and sources:
        findings.append({
            "type": "provenance_flag",
            "severity": "warn",
            "flag": "high_rating_unscorable_source",
            "rating": rating,
            "primary_source": sources[0],
            "action": "Rating ≥2 on vendor/unknown domain — replace source or cap rating.",
        })

    if sf.get("confidence") == "high" and src_tier == "assessed" and decl_class != "measured_or_disclosed":
        findings.append({
            "type": "provenance_flag",
            "severity": "info",
            "flag": "confidence_source_gap",
            "confidence": "high",
            "inferred_class": src_tier,
            "action": "High confidence with press-only sources — review or lower confidence.",
        })

    latent = sf.get("latent_rating_0_4")
    if latent is not None and abs(latent - rating) >= 2:
        findings.append({
            "type": "provenance_flag",
            "severity": "info",
            "flag": "latent_rating_divergence",
            "rating": rating,
            "latent_rating_0_4": latent,
            "action": "Large latent vs fused gap — confirm fusion λ and rationale.",
        })

    for f in findings:
        f["axis"] = axis
        f["sub_factor"] = sub_factor
    return findings


def audit_entity(rec: dict, cite_keys: set[str]) -> dict:
    all_findings = []
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for sub_factor, sf in (rec.get(axis) or {}).items():
            all_findings.extend(audit_sub_factor(axis, sub_factor, sf, cite_keys))

    counts = Counter(f["type"] for f in all_findings)
    severity_counts = Counter(f["severity"] for f in all_findings)
    status = "clean"
    if any(f["severity"] == "error" for f in all_findings):
        status = "errors"
    elif any(f["severity"] == "warn" for f in all_findings):
        status = "flags"
    elif all_findings:
        status = "info"

    return {
        "entity_id": rec["entity_id"],
        "layer": rec.get("layer"),
        "entity_type": rec.get("entity_type"),
        "status": status,
        "sub_factors_audited": sum(
            len(rec.get(ax) or {}) for ax in ("exposure_inputs", "preparedness_inputs")
        ),
        "findings": all_findings,
        "counts": dict(counts),
        "severity": dict(severity_counts),
    }


def write_batch(batch_key: str, entity_ids: list[str], records_by_id: dict, cite_keys: set[str]) -> dict:
    entities = {}
    rollup = Counter()
    status_counts = Counter()
    for eid in entity_ids:
        rec = records_by_id.get(eid)
        if not rec:
            continue
        report = audit_entity(rec, cite_keys)
        entities[eid] = report
        status_counts[report["status"]] += 1
        for k, v in report["counts"].items():
            rollup[k] += v

    doc = {
        "batch": batch_key,
        "researched_by": "data_steward",
        "as_of": date.today().isoformat(),
        "pass": "audit",
        "summary": {
            "entities": len(entities),
            "clean": status_counts.get("clean", 0),
            "flags": status_counts.get("flags", 0),
            "errors": status_counts.get("errors", 0),
            "info_only": status_counts.get("info", 0),
            "findings_total": sum(len(e["findings"]) for e in entities.values()),
            "by_type": dict(rollup),
        },
        "entities": entities,
    }
    out_path = os.path.join(AUDIT_DIR, f"{batch_key}.json")
    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return doc


def cmd_manifest(batch_size: int) -> int:
    records = load_records()
    ids = scored_entity_ids(records)
    doc = build_manifest(ids, batch_size)
    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print(f"Wrote {MANIFEST} — {len(ids)} entities in {len(doc['batches'])} batches")
    return 0


def cmd_batch(batch_key: str) -> int:
    if not os.path.isfile(MANIFEST):
        cmd_manifest(20)
    manifest = json.load(open(MANIFEST))
    ids = manifest.get("batches", {}).get(batch_key)
    if not ids:
        print(f"Unknown batch: {batch_key}", file=sys.stderr)
        return 1
    records = load_records()
    by_id = {r["entity_id"]: r for r in records}
    cite_keys = load_citation_keys()
    doc = write_batch(batch_key, ids, by_id, cite_keys)
    s = doc["summary"]
    print(f"Wrote data/audit/{batch_key}.json — {s['entities']} entities, "
          f"{s['findings_total']} findings ({s['clean']} clean, {s['flags']} flags, {s['errors']} errors)")
    return 0


def cmd_all() -> int:
    if not os.path.isfile(MANIFEST):
        cmd_manifest(20)
    manifest = json.load(open(MANIFEST))
    rc = 0
    for bk in sorted(manifest.get("batches", {})):
        if cmd_batch(bk):
            rc = 1
    return rc


def cmd_summary() -> int:
    import glob
    files = sorted(glob.glob(os.path.join(AUDIT_DIR, "batch*.json")))
    if not files:
        print("No audit batches found.", file=sys.stderr)
        return 1
    total_e = 0
    total_f = 0
    by_type = Counter()
    by_status = Counter()
    for path in files:
        doc = json.load(open(path))
        s = doc.get("summary", {})
        total_e += s.get("entities", 0)
        total_f += s.get("findings_total", 0)
        for k, v in (s.get("by_type") or {}).items():
            by_type[k] += v
        for eid, ent in (doc.get("entities") or {}).items():
            by_status[ent.get("status", "?")] += 1
    print("AUDIT ROLLUP")
    print("=" * 52)
    print(f"  batches: {len(files)}")
    print(f"  entities: {total_e}")
    print(f"  findings: {total_f}")
    print(f"  status: {dict(by_status)}")
    print(f"  by_type: {dict(by_type)}")
    print("=" * 52)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Data-steward audit pass")
    ap.add_argument("--manifest", action="store_true", help="Write data/audit/manifest.json")
    ap.add_argument("--batch", metavar="KEY", help="Audit one batch (e.g. batch1)")
    ap.add_argument("--all", action="store_true", help="Audit all batches in manifest")
    ap.add_argument("--summary", action="store_true", help="Print rollup from batch files")
    ap.add_argument("--batch-size", type=int, default=20)
    args = ap.parse_args()
    if args.manifest:
        return cmd_manifest(args.batch_size)
    if args.batch:
        return cmd_batch(args.batch)
    if args.all:
        return cmd_all()
    if args.summary:
        return cmd_summary()
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
