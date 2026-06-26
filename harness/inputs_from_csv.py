#!/usr/bin/env python3
"""Turn the filled collection worksheet into the two live measured-input files.

Workflow:  fill contract/inputs_worksheet.csv from real filings (see DATA_COLLECTION_CHECKLIST.md)
        -> python3 harness/inputs_from_csv.py
        -> writes contract/capital_inputs.json + contract/book_inputs.json (only rows with real
           values; blanks are skipped, never invented)
        -> python3 harness/measure_capital.py --live ; python3 harness/measure_book.py --live
        -> re-score (ingest_live.py or score_and_validate.py) ; L5 moves as disclosed evidence lands.

No synthetic data: a row contributes to capital only if fsr_rating is filled, and to book only if
both total_gwp and energy_power_gwp are filled. Everything else is left out.
"""
from __future__ import annotations
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "contract", "inputs_worksheet.csv")
CAP_PATH = os.path.join(ROOT, "contract", "capital_inputs.json")
BOOK_PATH = os.path.join(ROOT, "contract", "book_inputs.json")


def num(v):
    v = (v or "").strip().replace(",", "")
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def nonempty(v):
    return (v or "").strip() != ""


def load_template(path):
    return json.load(open(path)) if os.path.exists(path) else {"inputs": {}}


def main():
    if not os.path.exists(CSV_PATH):
        sys.exit(f"missing {CSV_PATH} — see DATA_COLLECTION_CHECKLIST.md")
    rows = list(csv.DictReader(open(CSV_PATH)))

    capital, book, warnings = {}, {}, []
    for r in rows:
        eid = (r.get("entity_id") or "").strip()
        if not eid or eid.startswith("#"):
            continue
        as_of = (r.get("as_of") or "").strip() or None

        # --- capital_inputs: needs at least an FSR rating ---
        if nonempty(r.get("fsr_rating")):
            scale = (r.get("fsr_scale") or "").strip().lower()
            if scale not in ("ambest", "sp"):
                warnings.append(f"{eid}: fsr_scale '{scale}' not in (ambest, sp) — skipped capital")
            else:
                capital[eid] = {
                    "fsr_rating": r["fsr_rating"].strip(),
                    "fsr_scale": scale,
                    "scr_coverage_pct": num(r.get("scr_coverage_pct")),
                    "fsr_source": (r.get("fsr_source") or "").strip() or None,
                    "scr_source": (r.get("scr_source") or "").strip() or None,
                    "as_of": as_of,
                }

        # --- book_inputs: needs total + energy/power premium (else book stays assessed) ---
        tot, en = num(r.get("total_gwp")), num(r.get("energy_power_gwp"))
        if tot and en is not None:
            book[eid] = {
                "total_gwp": tot,
                "energy_power_gwp": en,
                "datacentre_tech_gwp": num(r.get("datacentre_tech_gwp")) or 0,
                "currency": (r.get("currency") or "GBP").strip(),
                "lines_counted": [s.strip() for s in (r.get("lines_counted") or "").split(";") if s.strip()],
                "source": (r.get("book_source") or "").strip() or None,
                "as_of": as_of,
            }
        elif nonempty(r.get("total_gwp")) and not nonempty(r.get("energy_power_gwp")):
            warnings.append(f"{eid}: total_gwp without a named energy/power figure — book stays assessed (by design)")

    # MERGE into existing inputs — never clobber rows populated directly in the JSON (the files
    # are co-edited in a shared folder). CSV rows add/override only their own entity_ids; a blank
    # worksheet is a no-op. This makes the converter safe to run alongside hand-population.
    cap = load_template(CAP_PATH); cap.setdefault("inputs", {}).update(capital)
    bk = load_template(BOOK_PATH); bk.setdefault("inputs", {}).update(book)
    json.dump(cap, open(CAP_PATH, "w"), indent=2, ensure_ascii=False)
    json.dump(bk, open(BOOK_PATH, "w"), indent=2, ensure_ascii=False)
    capital, book = cap["inputs"], bk["inputs"]  # report the merged totals

    print("=== inputs_from_csv ===")
    print(f"worksheet rows: {len(rows)}")
    print(f"capital_inputs.json: {len(capital)} carriers populated -> {sorted(capital)}")
    print(f"book_inputs.json:    {len(book)} carriers populated -> {sorted(book)}")
    for w in warnings:
        print("  warn:", w)
    print("\nnext: python3 harness/measure_capital.py --live ; python3 harness/measure_book.py --live")
    print("      then re-score (ingest_live.py) and re-run evals.")


if __name__ == "__main__":
    main()
