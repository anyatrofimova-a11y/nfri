#!/usr/bin/env python3
"""Integrate expansion entities + bank disclosed evidence INTO records.json (durable).

Two recurring problems this fixes:
  (1) The pipeline re-scores from records.json (research/assessed tier). The measured/disclosed
      passes (measure_capital --live, ECR ingest) wrote to records.optimized AFTER scoring, so
      every re-score / universe expansion DROPPED them. Fix: bank disclosed values into records.json
      itself, so re-scoring preserves them.
  (2) New researched entities arrive as JSON arrays and must be merged without duplicating.

It also stamps each record with a `provenance.evidence` summary (measured / disclosed / assessed
counts + axis measured-share) — the schema the frontend uses to show a PER-ENTITY provenance badge
instead of one blanket PROVISIONAL banner.

Idempotent: re-running banks the same disclosed values and skips already-present entity_ids.

  python3 harness/integrate_entities.py [new_entities1.json new_entities2.json ...]
       --no-bank   skip the disclosed-capital banking step
"""
from __future__ import annotations
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))
RECORDS = os.path.join(ROOT, "data", "records.json")
CAPITAL = os.path.join(ROOT, "contract", "capital_inputs.json")
BOOK = os.path.join(ROOT, "contract", "book_inputs.json")
TRIGGER = os.path.join(ROOT, "contract", "trigger_inputs.json")
TENOR = os.path.join(ROOT, "contract", "tenor_inputs.json")
MEASURED = os.path.join(ROOT, "data", "records.measured.json")

EXP_KEYS = ["book_concentration", "non_firm_intensity", "aggregation_correlation", "trigger_gap", "tenor_mismatch"]
PREP_KEYS = ["data_monitoring", "product_fit", "underwriting_expertise", "capital_reinsurance", "pricing_modelling"]
MD = {"measured", "disclosed", "derived"}
BANKED_TIERS = {"measured", "disclosed", "derived"}


def load(p): return json.load(open(p))
def dump(obj, p): json.dump(obj, open(p, "w"), indent=2, ensure_ascii=False)


# ---------- (1) bank disclosed capital + book INTO records.json ----------
def bank_disclosed(records):
    import measure_capital as mc
    import measure_book as mb
    import measure_trigger as mt
    import measure_tenor as mten
    by_id = {r["entity_id"]: r for r in records}
    banked = {"capital": [], "book": [], "trigger": [], "tenor": []}

    cap_inputs = load(CAPITAL).get("inputs", {})
    for eid, row in cap_inputs.items():
        rec = by_id.get(eid)
        if not rec:
            continue
        sf = mc.build_subfactor(row, "live")  # evidence_tier=disclosed, measured_value, source, as_of
        sf.setdefault("latent_rating_0_4", rec["preparedness_inputs"]["capital_reinsurance"].get("rating_0_4"))
        rec["preparedness_inputs"]["capital_reinsurance"] = sf
        banked["capital"].append(eid)

    book_inputs = load(BOOK).get("inputs", {}) if os.path.exists(BOOK) else {}
    for eid, row in book_inputs.items():
        rec = by_id.get(eid)
        if not rec or not row.get("total_gwp") or row.get("energy_power_gwp") is None:
            continue
        sf = mb.build_subfactor(row, "live")
        prev = rec["exposure_inputs"]["book_concentration"]
        if prev.get("latent_rating_0_4") is None and prev.get("evidence_tier") != "disclosed":
            sf["latent_rating_0_4"] = prev.get("rating_0_4")
        elif prev.get("latent_rating_0_4") is not None:
            sf["latent_rating_0_4"] = prev["latent_rating_0_4"]
        rec["exposure_inputs"]["book_concentration"] = sf
        banked["book"].append(eid)

    trigger_inputs = load(TRIGGER).get("inputs", {}) if os.path.exists(TRIGGER) else {}
    for eid, row in trigger_inputs.items():
        rec = by_id.get(eid)
        if not rec:
            continue
        sf = mt.build_subfactor(row, "live")
        sf.setdefault("latent_rating_0_4", rec["exposure_inputs"]["trigger_gap"].get("rating_0_4"))
        rec["exposure_inputs"]["trigger_gap"] = sf
        banked["trigger"].append(eid)

    tenor_inputs = load(TENOR).get("inputs", {}) if os.path.exists(TENOR) else {}
    for eid, row in tenor_inputs.items():
        rec = by_id.get(eid)
        if not rec or row.get("max_cover_tenor_years") is None or row.get("claims_history_years") is None:
            continue
        sf = mten.build_subfactor(row, "live")
        prev = rec["exposure_inputs"]["tenor_mismatch"]
        if prev.get("latent_rating_0_4") is None and prev.get("evidence_tier") != "disclosed":
            sf["latent_rating_0_4"] = prev.get("rating_0_4")
        elif prev.get("latent_rating_0_4") is not None:
            sf["latent_rating_0_4"] = prev["latent_rating_0_4"]
        rec["exposure_inputs"]["tenor_mismatch"] = sf
        banked["tenor"].append(eid)
    return banked


def bank_measured(records):
    """Bank register/disclosure tiers from records.measured.json into records.json."""
    if not os.path.exists(MEASURED):
        return []
    from apply_l1_patches import _merge_sf

    measured = {r["entity_id"]: r for r in load(MEASURED)}
    by_id = {r["entity_id"]: r for r in records}
    banked = []
    for eid, mrec in measured.items():
        rec = by_id.get(eid)
        if not rec:
            continue
        touched = False
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for k, sf in (mrec.get(ax) or {}).items():
                if k not in rec.get(ax, {}):
                    continue
                tier = sf.get("evidence_tier") or "assessed"
                if tier not in BANKED_TIERS:
                    continue
                _merge_sf(rec[ax][k], sf)
                if tier == "measured":
                    touched = True
        if touched:
            banked.append(eid)
    return banked


# ---------- (2) merge new entities (dedupe by entity_id) ----------
def _valid(e):
    if not isinstance(e, dict) or "entity_id" not in e:
        return False, "missing entity_id"
    for ax, keys in (("exposure_inputs", EXP_KEYS), ("preparedness_inputs", PREP_KEYS)):
        if ax not in e:
            return False, f"missing {ax}"
        for k in keys:
            sf = e[ax].get(k)
            if not isinstance(sf, dict) or "rating_0_4" not in sf:
                return False, f"{ax}.{k} missing/invalid"
            # contract rule: rating>=1 must carry a source
            if sf.get("rating_0_4", 0) >= 1 and not sf.get("sources"):
                return False, f"{ax}.{k} rating>=1 with no source (no-synthetic)"
    return True, ""


def _entities_from_doc(doc):
    """Accept entity arrays or batch wrappers {\"batch\", \"inputs\": {eid: record}}."""
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict) and isinstance(doc.get("inputs"), dict):
        out = []
        for eid, row in doc["inputs"].items():
            if not isinstance(row, dict):
                continue
            rec = dict(row)
            rec.setdefault("entity_id", eid)
            out.append(rec)
        return out
    return [doc] if isinstance(doc, dict) else []


def merge_new(records, paths):
    existing = {r["entity_id"] for r in records}
    added, skipped, rejected = [], [], []
    for p in paths:
        try:
            arr = _entities_from_doc(load(p))
        except Exception as e:
            rejected.append((p, f"unreadable: {e}"))
            continue
        for e in arr:
            eid = e.get("entity_id") if isinstance(e, dict) else None
            if eid in existing:
                skipped.append(eid)
                continue
            ok, why = _valid(e)
            if not ok:
                rejected.append((eid or "?", why))
                continue
            e.pop("scores", None)  # raw record; scorer computes scores
            records.append(e)
            existing.add(eid)
            added.append(eid)
    return added, skipped, rejected


# ---------- (3) per-entity provenance schema (drives the granular frontend badge) ----------
def stamp_provenance(records):
    """Write rec['provenance']['evidence'] = {measured, disclosed, assessed, exposure_md, prep_md}.
    Tier is read from each sub-factor's evidence_tier (explicit) — the honest, banked signal."""
    for r in records:
        counts = {"measured": 0, "disclosed": 0, "derived": 0, "assessed": 0}
        for ax in ("exposure_inputs", "preparedness_inputs"):
            for sf in r[ax].values():
                t = sf.get("evidence_tier") or "assessed"
                counts[t if t in counts else "assessed"] += 1
        md = counts["measured"] + counts["disclosed"] + counts["derived"]
        r.setdefault("provenance", {})["evidence"] = {
            "measured": counts["measured"], "disclosed": counts["disclosed"],
            "derived": counts["derived"], "assessed": counts["assessed"],
            "measured_disclosed_subfactors": md,
            "total_subfactors": 10,
            # per-entity status used by the frontend instead of a blanket banner:
            "status": "measured" if md >= 6 else "partial" if md >= 1 else "assessed",
        }


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_bank = "--no-bank" not in sys.argv
    records = load(RECORDS)
    before = len(records)

    banked = bank_disclosed(records) if do_bank else {"capital": [], "book": [], "trigger": [], "tenor": []}
    measured_banked = bank_measured(records) if do_bank else []
    added, skipped, rejected = merge_new(records, paths) if paths else ([], [], [])
    stamp_provenance(records)
    dump(records, RECORDS)

    print("=== integrate_entities ===")
    print(f"records.json: {before} -> {len(records)}")
    if do_bank:
        print(f"banked disclosed capital into {len(banked['capital'])} records: {banked['capital']}")
        print(f"banked disclosed book into {len(banked['book'])} records: {banked['book']}")
        print(f"banked disclosed trigger into {len(banked['trigger'])} records")
        print(f"banked disclosed tenor into {len(banked['tenor'])} records: {banked['tenor'][:8]}{'…' if len(banked['tenor']) > 8 else ''}")
    if measured_banked:
        print(f"banked measured register tiers into {len(measured_banked)} records")
    if paths:
        print(f"merged new entities: +{len(added)} ({added})")
        if skipped:
            print(f"skipped (already present): {len(skipped)}")
        if rejected:
            print(f"REJECTED (invalid / no-synthetic violation): {len(rejected)}")
            for eid, why in rejected[:20]:
                print(f"   - {eid}: {why}")
    n_md = sum(1 for r in records if r["provenance"]["evidence"]["status"] != "assessed")
    print(f"per-entity provenance stamped; {n_md}/{len(records)} now carry >=1 measured/disclosed sub-factor")
    print("\nnext: re-score + rebuild — python3 harness/score_and_validate.py ; python3 harness/build_frontend.py")
    print("      then python3 harness/evals.py data/records.optimized.json  (watch L5)")


if __name__ == "__main__":
    main()
