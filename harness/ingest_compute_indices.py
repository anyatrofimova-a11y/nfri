#!/usr/bin/env python3
"""Live compute-market index ingestion + CMUI re-score.

Pulls public multi-provider GPU pricing feeds (default: GridStackHub — no auth),
optionally GPUs.io when GPUS_IO_API_KEY is set, or a local snapshot file.

Does NOT depend on any single vendor index (Squaretower or otherwise). Feeds are
pluggable via FEED_SOURCES below.

Updates market-derived sub-factors on entities with market_link.apply_market_derived,
propagates NFRI grid coupling from data/records.scored.json, re-scores, exports.
"""
from __future__ import annotations

import csv
import json
import math
import os
import statistics as st
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))

from compute_scoring import (  # noqa: E402
    load_compute_model,
    load_compute_rubric,
    score_all,
)

TODAY = date.today().isoformat()
DATA = os.path.join(ROOT, "data")
INDICES_DIR = os.path.join(DATA, "compute_indices")
HISTORY_DIR = os.path.join(INDICES_DIR, "history")
RECORDS_PATH = os.path.join(DATA, "compute_records.json")
NFRI_SCORED_PATH = os.path.join(DATA, "records.scored.json")

DEFAULT_CHIP = "H100"
USER_AGENT = "nfri-cmui-ingest/0.1 (+https://github.com/anyatrofimova-a11y/nfri)"


def _http_get_json(url: str, headers: Optional[dict] = None, timeout: int = 30) -> dict:
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_gridstackhub(chip: str = DEFAULT_CHIP) -> dict:
    """Public multi-provider GPU pricing — no API key."""
    chip_q = urllib.parse.quote(chip)
    pricing_url = f"https://gridstackhub.ai/api/gpu-pricing?gpu_model={chip_q}"
    pulse_url = "https://gridstackhub.ai/api/pulse-stack"
    pricing = _http_get_json(pricing_url)
    pulse = _http_get_json(pulse_url)
    rows = pricing.get("data") or []
    pulse_index = None
    for row in pulse.get("full_gpu_index") or []:
        if chip.upper() in str(row.get("gpu_model", "")).upper():
            pulse_index = row
            break
    return {
        "source": "gridstackhub",
        "citation_id": "FEED-GRIDSTACKHUB",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "chip_model": chip,
        "pricing_rows": rows,
        "pulse_index": pulse_index,
        "pulse_meta": {
            "generated_at": pulse.get("generated_at"),
            "providers_tracked": pulse.get("providers_tracked"),
            "total_pricing_records": pulse.get("total_pricing_records"),
        },
    }


def fetch_gpus_io(chip: str = DEFAULT_CHIP) -> Optional[dict]:
    api_key = os.environ.get("GPUS_IO_API_KEY", "").strip()
    if not api_key:
        return None
    params = urllib.parse.urlencode({"gpu": chip.lower(), "rentalType": "on_demand", "limit": 500})
    url = f"https://api.gpus.io/v1/prices?{params}"
    payload = _http_get_json(url, headers={"Authorization": f"Bearer {api_key}"})
    rows = []
    for item in payload.get("data") or []:
        gpu = item.get("gpu") or {}
        provider = item.get("provider") or {}
        rows.append({
            "provider": provider.get("name") or provider.get("id"),
            "gpu_model": gpu.get("name") or chip,
            "price_per_hour": item.get("pricePerGpuHourUsd"),
            "pricing_type": item.get("rentalType", "on_demand"),
            "region": (item.get("regions") or ["global"])[0],
            "source_url": provider.get("website"),
        })
    return {
        "source": "gpus.io",
        "citation_id": "FEED-GPUS-IO",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "chip_model": chip,
        "pricing_rows": [r for r in rows if r.get("price_per_hour")],
    }


def load_snapshot_file(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    data.setdefault("source", "snapshot_file")
    return data


def collect_feeds(chip: str = DEFAULT_CHIP) -> Tuple[dict, List[str]]:
    """Merge available feeds; primary cross-section from first successful source."""
    warnings: List[str] = []
    feeds: List[dict] = []

    snap_path = os.environ.get("COMPUTE_INDEX_SNAPSHOT_PATH", "").strip()
    if snap_path and os.path.isfile(snap_path):
        feeds.append(load_snapshot_file(snap_path))
    else:
        try:
            feeds.append(fetch_gridstackhub(chip))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            warnings.append(f"gridstackhub failed: {exc}")

        gpus = fetch_gpus_io(chip)
        if gpus:
            feeds.append(gpus)

    if not feeds:
        raise RuntimeError("No compute index feeds available — set COMPUTE_INDEX_SNAPSHOT_PATH for offline mode.")

    primary = feeds[0]
    rows = list(primary.get("pricing_rows") or [])
    for extra in feeds[1:]:
        rows.extend(extra.get("pricing_rows") or [])

    return {
        "primary_source": primary.get("source"),
        "citation_ids": list(dict.fromkeys(f.get("citation_id") for f in feeds if f.get("citation_id"))),
        "chip_model": chip,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "feeds": feeds,
        "pricing_rows": rows,
        "pulse_index": primary.get("pulse_index"),
    }, warnings


def _price(row: dict) -> Optional[float]:
    for key in ("price_per_hour", "price_per_gpu_hour", "per_gpu_rate", "pricePerGpuHourUsd"):
        val = row.get(key)
        if val is not None:
            try:
                p = float(val)
                if p > 0:
                    return p
            except (TypeError, ValueError):
                pass
    hr = row.get("hourly_rate")
    cnt = row.get("gpu_count") or 1
    if hr is not None:
        try:
            return float(hr) / max(1, float(cnt))
        except (TypeError, ValueError):
            pass
    return None


def summarize_market(bundle: dict) -> dict:
    """Derive index statistics from cross-sectional provider prices."""
    chip = bundle.get("chip_model", DEFAULT_CHIP)
    prices: List[float] = []
    on_demand: List[float] = []
    spot: List[float] = []

    for row in bundle.get("pricing_rows") or []:
        p = _price(row)
        if p is None:
            continue
        prices.append(p)
        ptype = str(row.get("pricing_type", "on_demand")).lower()
        if "spot" in ptype or "preempt" in ptype:
            spot.append(p)
        else:
            on_demand.append(p)

    pulse = bundle.get("pulse_index") or {}
    spot_median = st.median(prices) if prices else pulse.get("avg_per_gpu_hourly")
    spot_mean = st.mean(prices) if prices else spot_median
    spot_min = min(prices) if prices else pulse.get("min_per_gpu_hourly")
    spot_max = max(prices) if prices else pulse.get("max_per_gpu_hourly")

    if spot_median is None:
        raise RuntimeError(f"No {chip} prices in feed bundle.")

    spot_median = float(spot_median)
    spot_mean = float(spot_mean or spot_median)
    spot_min = float(spot_min or spot_median)
    spot_max = float(spot_max or spot_median)

    cv_cross = (st.pstdev(prices) / spot_mean) if len(prices) > 1 else 0.0
    spread_ratio = (spot_max - spot_min) / spot_median if spot_median > 0 else 0.0
    # scarcity / elasticity proxy (wider cross-section = tighter market)
    tightness_proxy = min(1.0, spread_ratio / 2.0)

    return {
        "chip_model": chip,
        "as_of": TODAY,
        "n_quotes": len(prices),
        "n_on_demand": len(on_demand),
        "n_spot": len(spot),
        "spot_median_usd": round(spot_median, 4),
        "spot_mean_usd": round(spot_mean, 4),
        "spot_min_usd": round(spot_min, 4),
        "spot_max_usd": round(spot_max, 4),
        "cv_cross_section": round(cv_cross, 4),
        "spread_ratio": round(spread_ratio, 4),
        "tightness_proxy": round(tightness_proxy, 4),
        "pulse_avg_usd": pulse.get("avg_per_gpu_hourly"),
        "pulse_wow_pct": pulse.get("wow_change_pct"),
        "primary_source": bundle.get("primary_source"),
        "citation_ids": bundle.get("citation_ids", []),
    }


def append_history(summary: dict) -> str:
    os.makedirs(HISTORY_DIR, exist_ok=True)
    path = os.path.join(HISTORY_DIR, f"{TODAY}.json")
    history: List[dict] = []
    if os.path.isfile(path):
        history = json.load(open(path))
    history.append({**summary, "recorded_at": datetime.now(timezone.utc).isoformat()})
    json.dump(history, open(path, "w"), indent=2)
    return path


def rolling_cv(chip: str = DEFAULT_CHIP, window: int = 30) -> Optional[float]:
    """Coefficient of variation from stored daily median snapshots."""
    if not os.path.isdir(HISTORY_DIR):
        return None
    medians: List[float] = []
    for name in sorted(os.listdir(HISTORY_DIR))[-window:]:
        if not name.endswith(".json"):
            continue
        for entry in json.load(open(os.path.join(HISTORY_DIR, name))):
            if entry.get("chip_model", chip).upper() == chip.upper():
                medians.append(float(entry["spot_median_usd"]))
    if len(medians) < 2:
        return None
    return st.pstdev(medians) / st.mean(medians)


def load_nfri_interaction_index() -> Dict[str, float]:
    """entity_id -> grid coupling index for grid_compute_coupling."""
    if not os.path.isfile(NFRI_SCORED_PATH):
        return {}
    records = json.load(open(NFRI_SCORED_PATH))
    out: Dict[str, float] = {}
    for rec in records:
        eid = rec.get("entity_id")
        exp = rec.get("exposure_inputs") or {}
        comp = exp.get("non_firm_compute_exposure")
        if not comp:
            continue
        mv = comp.get("measured_value")
        if isinstance(mv, dict):
            if "interaction_index" in mv:
                out[eid] = float(mv["interaction_index"])
            elif "share" in mv:
                # Register-only non-firm share — conservative proxy until full I is derived
                out[eid] = float(mv["share"])
        elif isinstance(mv, (int, float)):
            out[eid] = float(mv)
    return out


def basis_gap(contract: float, index: float) -> float:
    if contract <= 0 or index <= 0:
        return 0.0
    return abs(math.log(contract / index))


def apply_market_to_record(rec: dict, market: dict, nfri_idx: Dict[str, float]) -> List[str]:
    """Update deterministic fields from live market; return log lines."""
    log: List[str] = []
    link = rec.get("market_link") or {}
    if not link.get("apply_market_derived"):
        pass
    else:
        chip = link.get("chip_model", market["chip_model"])
        if chip.upper() != market["chip_model"].upper():
            log.append(f"skip market (chip mismatch {chip} vs {market['chip_model']})")
        else:
            spot = market["spot_median_usd"]
            contract = float(link.get("contract_rate_usd", spot))
            gap = basis_gap(contract, spot)

            bg = rec["exposure_inputs"]["price_basis_gap"]
            bg.update({
                "measured_value": {"r_contract": contract, "r_index": spot, "g_basis": round(gap, 4)},
                "evidence_tier": "measured",
                "confidence": "high",
                "source_type": "market_index",
                "as_of": market["as_of"],
                "citation_ids": market.get("citation_ids", ["FEED-GRIDSTACKHUB"]),
                "rationale": (
                    f"Live feed ({market['primary_source']}): |ln(contract/index)| = {gap:.3f} "
                    f"(contract ${contract:.2f}/hr vs index ${spot:.2f}/hr)."
                ),
                "sources": ["https://gridstackhub.ai/developers"],
            })
            log.append(f"basis_gap={gap:.3f}")

            exp = rec["exposure_inputs"]
            ts = exp.get("tightness_sensitivity") or {}
            f_short = 0.0
            mv = ts.get("measured_value")
            if isinstance(mv, dict):
                f_short = float(mv.get("f_short", 0))
            beta_t = market["tightness_proxy"] * f_short if f_short else market["tightness_proxy"] * 0.3
            ts.update({
                "measured_value": {**(mv if isinstance(mv, dict) else {}), "beta_t": round(beta_t, 4),
                                   "tightness_proxy": market["tightness_proxy"]},
                "evidence_tier": "derived",
                "confidence": "medium",
                "source_type": "market_index",
                "as_of": market["as_of"],
                "citation_ids": market.get("citation_ids", []),
                "rationale": (
                    f"tightness_proxy={market['tightness_proxy']:.3f} (spread/median) × f_short={f_short:.2f}."
                ),
            })
            log.append(f"beta_t={beta_t:.3f}")

            pve = exp["price_volatility_exposure"]
            p_mv = pve.get("measured_value")
            p_unhedged = float(p_mv.get("p_unhedged", 0.5)) if isinstance(p_mv, dict) else 0.5
            cv = market.get("cv_90") or market["cv_cross_section"]
            v = p_unhedged * cv
            pve.update({
                "measured_value": {"p_unhedged": p_unhedged, "cv_90": cv, "v": round(v, 4)},
                "evidence_tier": "derived",
                "confidence": "medium",
                "source_type": "market_index",
                "as_of": market["as_of"],
                "citation_ids": market.get("citation_ids", []),
                "rationale": f"v = p_unhedged({p_unhedged:.2f}) × cv({cv:.3f}).",
            })
            log.append(f"vol_exposure v={v:.3f}")

    nfri_link = rec.get("nfri_link") or {}
    asset_id = nfri_link.get("asset_id")
    if asset_id and asset_id in nfri_idx:
        gcc = rec["exposure_inputs"]["grid_compute_coupling"]
        idx = nfri_idx[asset_id]
        gcc.update({
            "measured_value": {"interaction_index": idx},
            "evidence_tier": "derived",
            "confidence": "medium",
            "source_type": "nfri_link",
            "as_of": TODAY,
            "citation_ids": ["CMUI-NFRI-BRIDGE"],
            "rationale": f"NFRI link {asset_id}: interaction_index={idx:.4f}.",
        })
        log.append(f"nfri I_grid={idx:.4f}")

    rec.setdefault("market_context", {}).update({
        "last_ingest": market["as_of"],
        "spot_median_usd": market["spot_median_usd"],
        "tightness_proxy": market["tightness_proxy"],
        "primary_source": market["primary_source"],
    })
    return log


def export_csv(records: List[dict], path: str) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "entity_id", "name", "layer", "entity_type", "stratum",
            "exposure", "preparedness", "margin_of_safety", "quadrant", "confidence",
        ])
        for r in records:
            s = r.get("scores") or {}
            w.writerow([
                r.get("entity_id"), r.get("name"), r.get("layer"), r.get("entity_type"),
                r.get("stratum", ""),
                s.get("exposure_0_100"), s.get("preparedness_0_100"),
                s.get("margin_of_safety"), s.get("quadrant"), s.get("overall_confidence"),
            ])


def main() -> None:
    os.makedirs(INDICES_DIR, exist_ok=True)
    chip = os.environ.get("CMUI_CHIP_MODEL", DEFAULT_CHIP)

    bundle, warnings = collect_feeds(chip)
    summary = summarize_market(bundle)
    cv90 = rolling_cv(chip)
    if cv90 is not None:
        summary["cv_90"] = round(cv90, 4)
    else:
        summary["cv_90"] = summary["cv_cross_section"]

    snapshot_path = os.path.join(INDICES_DIR, "snapshot.json")
    json.dump({"bundle": bundle, "summary": summary}, open(snapshot_path, "w"), indent=2)
    hist_path = append_history(summary)

    records = json.load(open(RECORDS_PATH))
    nfri_idx = load_nfri_interaction_index()
    ingest_log: List[str] = []

    for rec in records:
        lines = apply_market_to_record(rec, summary, nfri_idx)
        if lines:
            ingest_log.append(f"  {rec['entity_id']}: " + "; ".join(lines))

    rubric = load_compute_rubric()
    model = load_compute_model()
    nfri_scores = {k: {"interaction_index": v} for k, v in nfri_idx.items()}
    records, cut_exp, cut_prep = score_all(records, rubric=rubric, model=model, nfri_scores=nfri_scores)

    scored_path = os.path.join(DATA, "compute_records.scored.json")
    json.dump(records, open(scored_path, "w"), indent=2, ensure_ascii=False)
    # also refresh source records with market-enriched inputs
    json.dump(records, open(RECORDS_PATH, "w"), indent=2, ensure_ascii=False)

    csv_path = os.path.join(DATA, "compute_dataset.csv")
    export_csv(records, csv_path)

    report_lines = [
        "CMUI LIVE INGEST REPORT",
        "=" * 60,
        f"snapshot: {TODAY}",
        f"chip: {chip}",
        f"primary_source: {summary['primary_source']}",
        f"spot_median: ${summary['spot_median_usd']}/hr  (n={summary['n_quotes']} quotes)",
        f"spread_ratio: {summary['spread_ratio']}  tightness_proxy: {summary['tightness_proxy']}",
        f"cv_cross: {summary['cv_cross_section']}  cv_90: {summary.get('cv_90')}",
        f"median cut-lines: exposure>={cut_exp}  preparedness>={cut_prep}",
        "",
    ]
    if warnings:
        report_lines.append("WARNINGS:")
        report_lines.extend(f"  - {w}" for w in warnings)
        report_lines.append("")
    report_lines.append("ENTITY UPDATES:")
    report_lines.extend(ingest_log or ["  (none)"])
    report_lines.append("")
    report_lines.append("RANKED BY MARGIN OF SAFETY:")
    for r in sorted(records, key=lambda x: x["scores"]["margin_of_safety"], reverse=True):
        s = r["scores"]
        report_lines.append(
            f"  {s['margin_of_safety']:>6}  [{s['quadrant']:<10}] L{r['layer']} {r['name']}"
        )

    report_path = os.path.join(DATA, "compute_ingest_report.txt")
    open(report_path, "w").write("\n".join(report_lines))
    print("\n".join(report_lines))
    print(f"\nWROTE: {snapshot_path}, {hist_path}, {scored_path}, {csv_path}, {report_path}")

    try:
        from build_compute_manifesto import main as build_manifesto  # noqa: E402

        build_manifesto()
    except Exception as exc:
        print(f"WARN: manifesto rebuild skipped: {exc}")


if __name__ == "__main__":
    main()
