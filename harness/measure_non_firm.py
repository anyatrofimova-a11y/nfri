#!/usr/bin/env python3
"""Measured non_firm_intensity for Layer-3 assets — end to end.

Pipeline:  DNO Embedded Capacity Register rows
        -> resolve real field names (no hard-coding)
        -> MW-weighted share of capacity on FLEXIBLE / non-firm connections
        -> 0-4 rating mapped to the rubric anchors
        -> write a MEASURED-tier non_firm_intensity sub-factor with full provenance
           (measured_value, unit, as_of, source_type=register, evidence_tier=measured)

Modes:
  --live     query the live DNO ECR APIs via adapters.py (needs network + free ODS account)
  --fixture  run against harness/fixtures/ecr_fixture.json to UNIT-TEST the computation.
             Fixture rows are placeholder test data, clearly flagged, and the output is
             written to data/records.measured_demo.json — NEVER into the index dataset.

This honours the no-synthetic rule: live mode produces measured values; fixture mode is a
labelled test of the maths, quarantined from the published records.
"""
from __future__ import annotations
import json, os, sys, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()

# ---------- field resolver (matches real ECR columns by keyword) ----------
def _norm(s): return re.sub(r"[^a-z0-9]", " ", str(s).lower()).strip()

def resolve_fields(rows):
    """Find the import/export-capacity, flexibility and connection-status columns by
    keyword so we never assume an exact column name."""
    keys = list(rows[0].keys()) if rows else []
    def find(*must, prefer=None):
        cand = [k for k in keys if all(m in _norm(k) for m in must)]
        if prefer:
            cand.sort(key=lambda k: 0 if prefer in _norm(k) else 1)
        return cand[0] if cand else None
    mw = (find("import", "capacity") or find("export", "capacity")
          or find("maximum", "capacity") or find("capacity"))
    flex = find("flexible") or find("flexibility")
    status = find("connection", "status")
    return mw, flex, status

# ---------- measured feature ----------
def _is_nonfirm(row, flex_field, status_field):
    if flex_field:
        v = _norm(row.get(flex_field, ""))
        if v in {"yes", "y", "true", "1", "flexible"}:
            return True
    if status_field:
        s = _norm(row.get(status_field, ""))
        # "accepted to connect" (queue, not yet firm) and explicit non-firm/curtailable
        if "non firm" in s or "curtail" in s or "accepted to connect" in s:
            return True
    return False

def compute(rows):
    mw_f, flex_f, status_f = resolve_fields(rows)
    if not mw_f:
        return None
    tot = nf = 0.0; n = 0
    for r in rows:
        try: mw = float(str(r.get(mw_f, "")).replace(",", ""))
        except (TypeError, ValueError): continue
        if mw <= 0: continue
        tot += mw; n += 1
        if _is_nonfirm(r, flex_f, status_f): nf += mw
    if tot == 0: return None
    share = nf / tot
    return {"share": round(share, 3), "mw_total": round(tot, 1), "mw_nonfirm": round(nf, 1),
            "n": n, "fields": {"mw": mw_f, "flex": flex_f, "status": status_f}}

def share_to_rating(s):
    return 0 if s < 0.05 else 1 if s < 0.25 else 2 if s < 0.55 else 3 if s < 0.85 else 4

def conf_from_n(n):
    return "high" if n >= 5 else "medium" if n >= 2 else "low"

def build_subfactor(m, source_url, method):
    r = share_to_rating(m["share"])
    return {
        "rating_0_4": r,
        "measured_value": m["share"], "unit": "MW-share-non-firm",
        "as_of": TODAY,
        "evidence_tier": "measured" if method == "live" else "FIXTURE_DEMO",
        "source_type": "register",
        "rationale": (f"MW-weighted share of capacity on flexible/non-firm connections "
                      f"= {m['mw_nonfirm']}/{m['mw_total']} MW ({m['share']:.0%}) across "
                      f"{m['n']} ECR rows; columns {m['fields']}."),
        "sources": [source_url],
        "confidence": conf_from_n(m["n"]) if method == "live" else "low",
    }

# ---------- asset -> DNO routing ----------
ASSET_ROUTE = {  # entity_id -> (portal_key, ods search term)  [used in --live]
    "asset-kao-harlow":     ("ukpn", "Harlow"),
    "asset-nscale-loughton":("ukpn", "Loughton"),
    "asset-yondr-slough":   ("ssen", "Slough"),
    "asset-ark":            ("nged", "Corsham"),
    "asset-ark-corsham":    ("nged", "Corsham"),
}

def live_rows(entity_id):
    import adapters
    portal, term = ASSET_ROUTE.get(entity_id, (None, None))
    if not portal: return []
    where = f'search("{term}")'
    if portal == "ukpn":
        return adapters.ukpn_ecr(where=where, limit=100)
    return adapters.ods_records(portal, "embedded-capacity-register", where=where, limit=100)

# ---------- main ----------
def main():
    mode = "fixture" if "--fixture" in sys.argv else "live" if "--live" in sys.argv else "fixture"
    recs = json.load(open(os.path.join(ROOT, "data", "records.optimized.json")))
    by_id = {r["entity_id"]: r for r in recs}

    if mode == "fixture":
        fx = json.load(open(os.path.join(ROOT, "harness", "fixtures", "ecr_fixture.json")))
        src_label = "FIXTURE (placeholder test data — not live ECR)"
        groups = fx["rows_by_entity"]; out_name = "records.measured_demo.json"
        source_url = fx["source_note"]
    else:
        groups = None; out_name = "records.measured.json"
        source_url = "https://ukpowernetworks.opendatasoft.com/explore/dataset/ukpn-embedded-capacity-register/"

    changed = []
    targets = [r for r in recs if r["layer"] == 3 and r["entity_type"] == "data_centre"]
    for r in targets:
        eid = r["entity_id"]
        rows = groups.get(eid, []) if mode == "fixture" else live_rows(eid)
        if not rows:
            continue
        m = compute(rows)
        if not m:
            continue
        old = r["exposure_inputs"]["non_firm_intensity"]["rating_0_4"]
        r["exposure_inputs"]["non_firm_intensity"] = build_subfactor(m, source_url, mode)
        if mode == "fixture":
            r.setdefault("provenance", {})["method"] = "FIXTURE_DEMO"
        changed.append((eid, old, r["exposure_inputs"]["non_firm_intensity"]["rating_0_4"], m))

    out_path = os.path.join(ROOT, "data", out_name)
    json.dump(recs, open(out_path, "w"), indent=2, ensure_ascii=False)

    print(f"=== MEASURE non_firm_intensity ({mode}) ===")
    print(f"source: {src_label if mode=='fixture' else source_url}\n")
    for eid, old, new, m in changed:
        print(f"  {eid:<26} rating {old} -> {new}   share={m['share']:.0%} "
              f"({m['mw_nonfirm']}/{m['mw_total']} MW, n={m['n']})  cols={m['fields']}")
    print(f"\nassets measured: {len(changed)}/{len(targets)}")
    print(f"wrote: data/{out_name}")
    if mode == "fixture":
        print("\nNOTE: fixture mode is a UNIT TEST of the computation. Values are placeholder")
        print("test data and are NOT entered into the index. Run with --live for real ECR data.")

if __name__ == "__main__":
    main()
