#!/usr/bin/env python3
"""Thesis research — five Ciridae-framed investigations (deterministic reports).

  python3 harness/thesis_research.py           # all five
  python3 harness/thesis_research.py --t1      # single thesis

Writes:
  data/thesis/T1_measurement_lift.json + .md
  data/thesis/T2_trigger_gap.json + .md
  data/thesis/T3_grid_constraint.json + .md
  data/thesis/T4_portfolio_divergence.json + .md
  data/thesis/T5_whitespace_evidence.json + .md
  data/thesis/THESIS_SUMMARY.md
"""
from __future__ import annotations

import copy
import json
import os
import statistics as st
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "thesis")
RECORDS = os.path.join(ROOT, "data", "records.scored.json")
BOOK = os.path.join(ROOT, "contract", "book_inputs.json")
TRIGGER = os.path.join(ROOT, "contract", "trigger_inputs.json")
GEO = os.path.join(ROOT, "contract", "asset_geo_tags.json")
COPY = os.path.join(ROOT, "contract", "entity_copy.json")
PROFILES = os.path.join(ROOT, "site", "data", "profiles.json")
COVERAGE = os.path.join(ROOT, "contract", "entity_links.json")

import sys

sys.path.insert(0, os.path.join(ROOT, "harness"))
from scoring import load_rubric, score_record, score_all  # noqa: E402


def _load(path: str):
    return json.load(open(path))


def _save(name: str, data: dict, md: str) -> None:
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, name + ".json"), "w"), indent=2, ensure_ascii=False)
    with open(os.path.join(OUT, name + ".md"), "w") as f:
        f.write(md)


def _measured_pct(rec: dict) -> int:
    ev = (rec.get("provenance") or {}).get("evidence") or {}
    total = ev.get("total_subfactors") or 10
    disclosed = ev.get("measured_disclosed_subfactors") or 0
    return round(100 * disclosed / total) if total else 0


def _share_to_rating(share: float) -> int:
    return 0 if share < 0.02 else 1 if share < 0.06 else 2 if share < 0.15 else 3 if share < 0.30 else 4


def _research_book_anchors() -> dict[str, int]:
    """Pre-disclosure book_concentration ratings from l1_research patches."""
    anchors: dict[str, int] = {}
    import glob

    for path in glob.glob(os.path.join(ROOT, "data", "l1_research", "batch*.json")):
        data = json.load(open(path))
        items = data if isinstance(data, list) else data.get("entities", [])
        for row in items:
            if not isinstance(row, dict):
                continue
            eid = row.get("entity_id")
            bc = (row.get("exposure_inputs") or {}).get("book_concentration") or {}
            if eid and "rating_0_4" in bc:
                anchors[eid] = bc["rating_0_4"]
    return anchors


def _assessed_book_rating(bc: dict, eid: str, anchors: dict[str, int]) -> int:
    latent = bc.get("latent_rating_0_4")
    rating = bc.get("rating_0_4", 0)
    if latent is not None and latent != rating:
        return latent
    if eid in anchors and anchors[eid] != rating:
        return anchors[eid]
    return latent if latent is not None else rating


def _book_subfactor_at_rating(sf: dict, rating: int) -> dict:
    """Force book_concentration to a single effective rating (latent path)."""
    out = copy.deepcopy(sf)
    out["rating_0_4"] = rating
    out["latent_rating_0_4"] = rating
    out["evidence_tier"] = "assessed"
    out.pop("measured_value", None)
    out.pop("deterministic_rating_0_4", None)
    return out


def t1_measurement_lift(records: list) -> None:
    rubric = load_rubric()
    _, cut_exp, cut_prep = score_all(copy.deepcopy(records))
    book_ids = set(_load(BOOK).get("inputs", {}))
    anchors = _research_book_anchors()
    rows = []
    for rec in records:
        if rec.get("layer") != 1 or not rec.get("scores"):
            continue
        eid = rec["entity_id"]
        bc = rec["exposure_inputs"].get("book_concentration", {})
        if bc.get("evidence_tier") != "disclosed":
            if eid in book_ids:
                rows.append({"entity_id": eid, "name": rec["name"], "status": "book_inputs_ready_not_applied"})
            continue
        assessed_anchor = _assessed_book_rating(bc, eid, anchors)
        disclosed_rating = int(bc.get("rating_0_4", 0))
        cf = copy.deepcopy(rec)
        cf["exposure_inputs"]["book_concentration"] = _book_subfactor_at_rating(bc, assessed_anchor)
        assessed_scores = score_record(cf, cut_exp, cut_prep, rubric)
        df = copy.deepcopy(rec)
        df["exposure_inputs"]["book_concentration"] = _book_subfactor_at_rating(bc, disclosed_rating)
        disclosed_scores = score_record(df, cut_exp, cut_prep, rubric)
        d_mos = round(disclosed_scores["margin_of_safety"] - assessed_scores["margin_of_safety"], 1)
        d_exp = round(disclosed_scores["exposure_0_100"] - assessed_scores["exposure_0_100"], 1)
        share = (bc.get("measured_value") or {}).get("share")
        rows.append({
            "entity_id": eid,
            "name": rec["name"],
            "assessed_book_rating": assessed_anchor,
            "disclosed_book_rating": disclosed_rating,
            "energy_share": share,
            "mos_disclosed": disclosed_scores["margin_of_safety"],
            "mos_assessed_book": assessed_scores["margin_of_safety"],
            "delta_mos": d_mos,
            "delta_exposure": d_exp,
            "quad_disclosed": disclosed_scores["quadrant"],
            "quad_counterfactual": assessed_scores["quadrant"],
            "quad_flip": disclosed_scores["quadrant"] != assessed_scores["quadrant"],
        })
    deltas = [r["delta_mos"] for r in rows if "delta_mos" in r]
    flips = sum(1 for r in rows if r.get("quad_flip"))
    summary = {
        "thesis": "T1_measurement_lift",
        "question": "How much does MoS move when assessed book is replaced by disclosed GWP?",
        "as_of": date.today().isoformat(),
        "n_disclosed_book": len(rows),
        "mean_delta_mos": round(st.mean(deltas), 2) if deltas else None,
        "median_delta_mos": round(st.median(deltas), 2) if deltas else None,
        "max_abs_delta_mos": round(max(abs(d) for d in deltas), 1) if deltas else None,
        "quadrant_flips": flips,
        "entities": sorted(rows, key=lambda x: abs(x.get("delta_mos", 0)), reverse=True),
    }
    md = f"""# T1 — Measurement lift (disclosed GWP → book_concentration)

**Question:** How much does MoS move when we replace assessed book with disclosed energy/power GWP?

**Method:** Fixed median cut-lines (exp≥{cut_exp}, prep≥{cut_prep}). Per L1 carrier with `evidence_tier=disclosed` on book_concentration, rescore with book reverted to latent-only anchor.

## Headline
- Carriers with disclosed book: **{summary['n_disclosed_book']}**
- Mean ΔMoS (disclosed − assessed-book): **{summary['mean_delta_mos']}**
- Median ΔMoS: **{summary['median_delta_mos']}**
- Quadrant flips: **{flips}**

## Interpretation
Negative ΔMoS means disclosed GWP **lowers** exposure vs research anchor (carrier looks less concentrated). Positive ΔMoS means disclosed share **raises** exposure vs latent guess.

## Top movers
"""
    for r in summary["entities"][:12]:
        if "delta_mos" not in r:
            continue
        md += f"- **{r['name']}** ({r.get('energy_share', 0):.1%} share): assessed={r.get('assessed_book_rating')} disclosed={r.get('disclosed_book_rating')} ΔMoS {r['delta_mos']:+.1f}, ΔExp {r['delta_exposure']:+.1f}"
        if r["quad_flip"]:
            md += f" — quad {r['quad_disclosed']}→{r['quad_counterfactual']}"
        md += "\n"
    _save("T1_measurement_lift", summary, md)


def t2_trigger_gap(records: list) -> None:
    trigger = _load(TRIGGER).get("inputs", {})
    l1 = [r for r in records if r.get("layer") == 1 and r.get("scores")]
    rows = []
    for rec in l1:
        eid = rec["entity_id"]
        exp = rec["exposure_inputs"]
        prep = rec["preparedness_inputs"]
        tri = exp.get("trigger_gap", {})
        pf = prep.get("product_fit", {})
        disc = trigger.get(eid, {})
        n = disc.get("n_nondamage_products")
        rows.append({
            "entity_id": eid,
            "name": rec["name"],
            "mos": rec["scores"]["margin_of_safety"],
            "quad": rec["scores"]["quadrant"],
            "trigger_gap": tri.get("rating_0_4"),
            "trigger_tier": tri.get("evidence_tier"),
            "product_fit": pf.get("rating_0_4"),
            "n_nondamage_products": n,
            "closes_basis_risk": (tri.get("rating_0_4", 4) <= 2) if tri.get("rating_0_4") is not None else None,
        })
    closers = [r for r in rows if r.get("closes_basis_risk")]
    wide_gap = [r for r in rows if r.get("trigger_gap", 4) >= 3]
    summary = {
        "thesis": "T2_trigger_gap",
        "question": "Who closes non-damage basis risk (parametric) vs who doesn't among L1?",
        "n_l1": len(rows),
        "n_closes_gap_rated_0_2": len(closers),
        "n_wide_gap_rated_3_4": len(wide_gap),
        "n_in_trigger_inputs": sum(1 for r in rows if r["n_nondamage_products"] is not None),
        "closes_basis_risk": sorted(closers, key=lambda x: x["trigger_gap"]),
        "wide_trigger_gap": sorted(wide_gap, key=lambda x: -x["trigger_gap"]),
        "all": sorted(rows, key=lambda x: (x.get("trigger_gap") or 9, -x["mos"])),
    }
    md = f"""# T2 — Trigger gap (parametric vs indemnity)

**Question:** Which L1 carriers close the non-damage basis-risk gap?

**Rule:** `trigger_gap` ≤2 = partial/full match; ≥3 = legacy physical-damage reliance. `n_nondamage_products` from `trigger_inputs.json` where disclosed.

## Headline
- L1 carriers: **{len(rows)}**
- Close gap (trigger≤2): **{len(closers)}** — {', '.join(r['name'].split()[0] for r in closers[:8])}{'…' if len(closers)>8 else ''}
- Wide gap (trigger≥3): **{len(wide_gap)}**

## Closers (parametric/availability evidenced)
"""
    for r in closers:
        md += f"- {r['name']}: trigger_gap={r['trigger_gap']}, product_fit={r['product_fit']}, n_products={r['n_nondamage_products']}\n"
    md += "\n## Wide gap (damage-led)\n"
    for r in wide_gap[:15]:
        md += f"- {r['name']}: trigger_gap={r['trigger_gap']}, n_products={r['n_nondamage_products']}\n"
    _save("T2_trigger_gap", summary, md)


def t3_grid_constraint(records: list) -> None:
    geo = _load(GEO).get("entities", {}) if os.path.isfile(GEO) else {}
    l3 = [r for r in records if r.get("layer") == 3 and r.get("scores")]
    rows = []
    for rec in l3:
        eid = rec["entity_id"]
        g = geo.get(eid, {})
        zone = g.get("constraint_zone", "unclassified")
        dno = g.get("dno", "unknown")
        nf_key = "non_firm_compute_exposure" if "non_firm_compute_exposure" in rec.get("exposure_inputs", {}) else "non_firm_intensity"
        nf = rec["exposure_inputs"].get(nf_key, {})
        rows.append({
            "entity_id": eid,
            "name": rec["name"],
            "dno": dno,
            "constraint_zone": zone,
            "constraint_hotspot": zone in ("ssen_west_london", "nged_midlands", "scotland_wind"),
            "non_firm_eff": nf.get("rating_0_4"),
            "non_firm_tier": nf.get("evidence_tier"),
            "mos": rec["scores"]["margin_of_safety"],
            "exp": rec["scores"]["exposure_0_100"],
        })
    hot = [r for r in rows if r["constraint_hotspot"]]
    cool = [r for r in rows if not r["constraint_hotspot"] and r["constraint_zone"] != "unclassified"]
    uncl = [r for r in rows if r["constraint_zone"] == "unclassified"]

    def _mean_nf(group):
        vals = [r["non_firm_eff"] for r in group if r["non_firm_eff"] is not None]
        return round(st.mean(vals), 2) if vals else None

    summary = {
        "thesis": "T3_grid_constraint",
        "question": "Do L3 assets in SSEN/NGED constraint zones score worse on non_firm_compute?",
        "n_l3": len(rows),
        "mean_nf_hotspot": _mean_nf(hot),
        "mean_nf_other_tagged": _mean_nf(cool),
        "mean_nf_unclassified": _mean_nf(uncl),
        "hotspot_assets": sorted(hot, key=lambda x: -(x["non_firm_eff"] or 0)),
        "entities": rows,
    }
    md = f"""# T3 — Grid constraint × non-firm exposure

**Question:** Do assets in SSEN/NGED constraint hotspots score higher on non-firm compute exposure?

**Tags:** `contract/asset_geo_tags.json` (DNO + constraint_zone per L3 asset).

## Headline
- L3 assets tagged: **{len(rows) - len(uncl)}** / {len(rows)}
- Mean non-firm eff (hotspot): **{summary['mean_nf_hotspot']}**
- Mean non-firm eff (other tagged): **{summary['mean_nf_other_tagged']}**
- Mean non-firm eff (unclassified): **{summary['mean_nf_unclassified']}**

## Hotspot assets
"""
    for r in hot:
        md += f"- **{r['name']}** [{r['dno']}/{r['constraint_zone']}]: nf={r['non_firm_eff']}, MoS={r['mos']:+.1f}\n"
    _save("T3_grid_constraint", summary, md)


def t4_portfolio_divergence(records: list, profiles: dict) -> None:
    coverage = _load(COVERAGE).get("links", {}) if os.path.isfile(COVERAGE) else {}
    rows = []
    for rec in records:
        if rec.get("layer") != 1 or not rec.get("scores"):
            continue
        eid = rec["entity_id"]
        p = profiles.get(eid, {})
        port = p.get("portfolio") or {}
        if not port.get("n"):
            continue
        cm = rec["scores"]["margin_of_safety"]
        avg = port.get("mosAvg", cm)
        gap = round(cm - avg, 1)
        named = coverage.get(eid, {}).get("covered_assets", [])
        explanation = "book_vs_prototype"
        if abs(gap) < 5:
            explanation = "aligned"
        elif gap > 10:
            explanation = "carrier_safer_than_linked_assets"
        elif gap < -10:
            explanation = "linked_assets_safer_than_carrier"
        rows.append({
            "entity_id": eid,
            "name": rec["name"],
            "carrier_mos": cm,
            "portfolio_mos_avg": avg,
            "portfolio_mos_min": port.get("mosMin"),
            "portfolio_mos_max": port.get("mosMax"),
            "gap": gap,
            "explanation": explanation,
            "named_asset_links": len(named),
            "n_linked": port.get("n"),
        })
    big_gap = sorted([r for r in rows if abs(r["gap"]) >= 10], key=lambda x: -abs(x["gap"]))
    summary = {
        "thesis": "T4_portfolio_divergence",
        "question": "When carrier MoS ≠ linked-asset mean, what explains it?",
        "n_l1_with_portfolio": len(rows),
        "mean_abs_gap": round(st.mean(abs(r["gap"]) for r in rows), 1) if rows else None,
        "n_large_divergence": len(big_gap),
        "large_divergences": big_gap,
        "entities": sorted(rows, key=lambda x: -abs(x["gap"])),
    }
    md = f"""# T4 — Portfolio divergence (carrier vs linked L3 slice)

**Question:** When headline carrier MoS diverges from linked-asset mean, is it book shape vs prototype slice?

## Headline
- L1 with portfolio: **{len(rows)}**
- Mean |carrier − portfolio avg|: **{summary['mean_abs_gap']}** pts
- Large divergence (≥10 pts): **{len(big_gap)}**

## Largest gaps
"""
    for r in big_gap[:15]:
        md += f"- **{r['name']}**: carrier MoS {r['carrier_mos']:+.1f} vs portfolio avg {r['portfolio_mos_avg']:+.1f} (Δ{r['gap']:+.1f}) — {r['explanation']}, named links={r['named_asset_links']}\n"
    _save("T4_portfolio_divergence", summary, md)


def t5_whitespace_evidence(records: list) -> None:
    copy = _load(COPY).get("entities", {})
    by_quad: dict[str, list] = {}
    for rec in records:
        if not rec.get("scores"):
            continue
        q = rec["scores"]["quadrant"]
        meas = _measured_pct(rec)
        synth = copy.get(rec["entity_id"], {})
        exec_w = len((synth.get("executive_summary") or "").split())
        by_quad.setdefault(q, []).append({
            "entity_id": rec["entity_id"],
            "name": rec["name"],
            "layer": rec.get("layer"),
            "mos": rec["scores"]["margin_of_safety"],
            "measured_pct": meas,
            "exec_words": exec_w,
            "prep": rec["scores"]["preparedness_0_100"],
            "exp": rec["scores"]["exposure_0_100"],
        })
    ws = by_quad.get("whitespace", [])
    thin = [r for r in ws if r["measured_pct"] < 20]
    summary = {
        "thesis": "T5_whitespace_evidence",
        "question": "Is whitespace real underwriting optionality or thin evidence?",
        "n_whitespace": len(ws),
        "whitespace_mean_measured_pct": round(st.mean(r["measured_pct"] for r in ws), 1) if ws else None,
        "whitespace_mean_prep": round(st.mean(r["prep"] for r in ws), 1) if ws else None,
        "whitespace_mean_exp": round(st.mean(r["exp"] for r in ws), 1) if ws else None,
        "whitespace_thin_evidence": thin,
        "by_quadrant_measured": {
            q: round(st.mean(item["measured_pct"] for item in items), 1)
            for q, items in by_quad.items()
        },
        "by_quadrant_count": {q: len(r) for q, r in by_quad.items()},
        "whitespace_l1": [r for r in ws if r["layer"] == 1],
    }
    md = f"""# T5 — Whitespace: optionality vs thin evidence

**Question:** Whitespace quadrant — genuine prep>exp optionality or assessed-heavy noise?

## Headline
- Whitespace entities: **{len(ws)}**
- Mean measured share in whitespace: **{summary['whitespace_mean_measured_pct']}%**
- Mean prep / exp in whitespace: **{summary['whitespace_mean_prep']}** / **{summary['whitespace_mean_exp']}**
- Whitespace with <20% measured: **{len(thin)}** ({100*len(thin)/len(ws):.0f}%)

## Measured share by quadrant
"""
    for q, pct in summary["by_quadrant_measured"].items():
        md += f"- {q}: {pct}% measured (n={summary['by_quadrant_count'][q]})\n"
    md += "\n## Verdict (provisional)\n"
    if summary["whitespace_mean_measured_pct"] is not None and summary["whitespace_mean_measured_pct"] < 25:
        md += "Whitespace skews **assessed-heavy** — reads as underwriting *hypothesis* until registers/disclosures lift measured share. Prep scores are directionally useful but magnitudes are provisional.\n"
    else:
        md += "Whitespace has moderate measured backing — optionality claims are partially register-backed.\n"
    _save("T5_whitespace_evidence", summary, md)


def write_summary() -> None:
    parts = []
    for stem in ("T1_measurement_lift", "T2_trigger_gap", "T3_grid_constraint", "T4_portfolio_divergence", "T5_whitespace_evidence"):
        p = os.path.join(OUT, stem + ".md")
        if os.path.isfile(p):
            parts.append(open(p).read())
    with open(os.path.join(OUT, "THESIS_SUMMARY.md"), "w") as f:
        f.write(f"# NFRI thesis research — {date.today().isoformat()}\n\n")
        f.write("\n---\n\n".join(parts))


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--t1", action="store_true")
    ap.add_argument("--t2", action="store_true")
    ap.add_argument("--t3", action="store_true")
    ap.add_argument("--t4", action="store_true")
    ap.add_argument("--t5", action="store_true")
    args = ap.parse_args()
    all_t = not any([args.t1, args.t2, args.t3, args.t4, args.t5])

    records = _load(RECORDS)
    profiles = _load(PROFILES) if os.path.isfile(PROFILES) else {}

    if all_t or args.t1:
        t1_measurement_lift(records)
        print("wrote T1_measurement_lift")
    if all_t or args.t2:
        t2_trigger_gap(records)
        print("wrote T2_trigger_gap")
    if all_t or args.t3:
        t3_grid_constraint(records)
        print("wrote T3_grid_constraint")
    if all_t or args.t4:
        t4_portfolio_divergence(records, profiles)
        print("wrote T4_portfolio_divergence")
    if all_t or args.t5:
        t5_whitespace_evidence(records)
        print("wrote T5_whitespace_evidence")
    if all_t:
        write_summary()
        print("wrote THESIS_SUMMARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
