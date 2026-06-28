#!/usr/bin/env python3
"""Sync disclosed book_concentration rows into contract/book_inputs.json.

Sources (no synthetic values):
  1. measured_value on records.scored.json where evidence_tier == disclosed
  2. SYNDICATE_BANK — Lloyd's class-of-business figures banked from filings
  3. data/book_mining/batch*.json — parallel miner output

  python3 harness/extract_book_inputs.py           # dry-run summary
  python3 harness/extract_book_inputs.py --merge   # write book_inputs.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_PATH = os.path.join(ROOT, "contract", "book_inputs.json")
SCORED = os.path.join(ROOT, "data", "records.scored.json")

# Gate-cohort entity_id when mining keyed the Lloyd's syndicate parent slug.
BOOK_ID_ALIASES: dict[str, str] = {
    "scor-2015": "scor",
}

SYNDICATE_BANK: dict[str, dict] = {
    "chaucer-1084": {
        "total_gwp": 2384.759,
        "energy_power_gwp": 22.353,
        "datacentre_tech_gwp": 0,
        "currency": "USD",
        "lines_counted": ["Energy"],
        "source": "https://media.chaucergroup.com/documents/Syndicate_1084-2024.pdf",
        "as_of": "2024-12-31",
    },
    "liberty-specialty": {
        "total_gwp": 1753.0,
        "energy_power_gwp": 5.7,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Energy"],
        "source": (
            "https://assets.lloyds.com/media/cd38206b-d105-410e-a77f-8a537d59d6f3/"
            "4472%20Liberty%20Syndicate%20-%204472%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
    "ms-amlin": {
        "total_gwp": 2128.0,
        "energy_power_gwp": 72.0,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Energy (Specialities + liability energy)"],
        "source": "https://global.msamlin.com/media/1c4fjxwy/msamlin_annualreport_2025-final-web.pdf",
        "as_of": "2024-12-31",
    },
    "tokio-marine-kiln": {
        "total_gwp": 1817.0,
        "energy_power_gwp": 107.0,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Marine & Energy"],
        "source": (
            "https://assets.lloyds.com/media/8a6cb2ca-536c-44fd-925f-67c6b8d9028f/"
            "0510%20Tokio%20Marine%20Combined%20Syndicate%20-%200510%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
    "beat-4242": {
        "total_gwp": 390.0,
        "energy_power_gwp": 29.0,
        "datacentre_tech_gwp": 0,
        "currency": "USD",
        "lines_counted": ["Energy"],
        "source": (
            "https://assets.lloyds.com/media/6e3cdb67-2bcc-412c-8941-ddc303a62362/"
            "4242%20Beat%20Syndicate%20-%204242%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
    "aegis-london-1225": {
        "total_gwp": 1010.0,
        "energy_power_gwp": 24.0,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Energy"],
        "source": (
            "https://assets.lloyds.com/media/4c27add6-228f-4022-aa0a-44d0a62d6dac/"
            "1225%20Aegis%20London%20Syndicate%20-%201225%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
    "allied-world-2232": {
        "total_gwp": 472.0,
        "energy_power_gwp": 4.4,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Energy"],
        "source": (
            "https://assets.lloyds.com/media/e28f76fd-0d97-404f-b670-7f9574217a32/"
            "2232%20Allied%20World%20Syndicate%20-%202232%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
    "ark-4020": {
        "total_gwp": 758.0,
        "energy_power_gwp": 136.0,
        "datacentre_tech_gwp": 0,
        "currency": "GBP",
        "lines_counted": ["Marine & Energy"],
        "source": (
            "https://assets.lloyds.com/media/8865c6d6-d827-43f9-a62f-de5af166d90e/"
            "4020%20Ark%20Syndicate%20-%204020%20-%20Q4%202024%20Syndicate%20Accounts%20"
            "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
        ),
        "as_of": "2024-12-31",
    },
}


def _from_scored() -> dict[str, dict]:
    if not os.path.isfile(SCORED):
        return {}
    out = {}
    for rec in json.load(open(SCORED)):
        sf = rec.get("exposure_inputs", {}).get("book_concentration", {})
        if sf.get("evidence_tier") != "disclosed":
            continue
        mv = sf.get("measured_value")
        if not isinstance(mv, dict) or not mv.get("total_gwp"):
            continue
        srcs = sf.get("sources") or []
        out[rec["entity_id"]] = {
            "total_gwp": mv["total_gwp"],
            "energy_power_gwp": mv.get("relevant_gwp") or mv.get("energy_power_gwp"),
            "datacentre_tech_gwp": mv.get("datacentre_tech_gwp", 0) or 0,
            "currency": mv.get("currency", "GBP"),
            "lines_counted": mv.get("lines_counted") or [],
            "source": srcs[0] if srcs else None,
            "as_of": sf.get("as_of"),
        }
    return out


def _from_book_mining() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for subdir in ("book_mining", "sfcr_mining"):
        mining_dir = os.path.join(ROOT, "data", subdir)
        patterns = ("batch*.json", "gate_gap*.json") if subdir == "sfcr_mining" else ("batch*.json",)
        paths = []
        for pat in patterns:
            paths.extend(glob.glob(os.path.join(mining_dir, pat)))
        for path in sorted(paths):
            doc = json.load(open(path))
            for eid, row in (doc.get("inputs") or {}).items():
                if row.get("total_gwp") and row.get("energy_power_gwp") is not None:
                    out[eid] = row
    return out


def merge_book_inputs() -> tuple[dict, list[str], list[str]]:
    doc = json.load(open(BOOK_PATH))
    inputs = dict(doc.get("inputs") or {})
    added: list[str] = []
    updated: list[str] = []
    mining = _from_book_mining()
    for eid, row in {**SYNDICATE_BANK, **_from_scored()}.items():
        if not row.get("total_gwp") or row.get("energy_power_gwp") is None:
            continue
        if eid in inputs and inputs[eid].get("total_gwp"):
            continue
        inputs[eid] = row
        added.append(eid)
    for eid, row in mining.items():
        if not row.get("total_gwp") or row.get("energy_power_gwp") is None:
            continue
        if eid in inputs and inputs[eid].get("total_gwp"):
            if inputs[eid] != row:
                updated.append(eid)
        else:
            added.append(eid)
        inputs[eid] = row
    for alias_id, source_id in BOOK_ID_ALIASES.items():
        src = inputs.get(source_id)
        if not src or not src.get("total_gwp") or src.get("energy_power_gwp") is None:
            continue
        if alias_id in inputs and inputs[alias_id].get("total_gwp"):
            continue
        inputs[alias_id] = dict(src)
        added.append(alias_id)
    doc["inputs"] = inputs
    return doc, added, updated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--merge", action="store_true", help="write contract/book_inputs.json")
    args = ap.parse_args()
    doc, added, updated = merge_book_inputs()
    print(f"book_inputs: {len(doc['inputs'])} carriers  (+{len(added)} new, ~{len(updated)} updated)")
    for eid in sorted(added):
        row = doc["inputs"][eid]
        sh = float(row["energy_power_gwp"]) / float(row["total_gwp"])
        print(f"  + {eid:<22} energy {sh:.1%}  ({row['energy_power_gwp']}/{row['total_gwp']} {row.get('currency','GBP')}m)")
    for eid in sorted(updated):
        row = doc["inputs"][eid]
        sh = float(row["energy_power_gwp"]) / float(row["total_gwp"])
        print(f"  ~ {eid:<22} energy {sh:.1%}  ({row['energy_power_gwp']}/{row['total_gwp']} {row.get('currency','GBP')}m)")
    if args.merge:
        json.dump(doc, open(BOOK_PATH, "w"), indent=2, ensure_ascii=False)
        print("\nwrote: contract/book_inputs.json")
    else:
        print("\n(dry-run — pass --merge to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
