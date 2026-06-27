#!/usr/bin/env python3
"""NFRI ingestion adapters — MEASURED data only, from verified primary endpoints.

These adapters pull real records from public registers and compute measured features.
They DISCOVER the dataset schema at runtime rather than hard-coding column names, so no
field is ever assumed/fabricated. Run in your own environment (needs network; Companies
House / FCA need free API keys). Respect each source's licence and rate limits.

Endpoints verified June 2026:
  NESO TEC datastore  resource_id 17becbab-e3e8-473f-b303-3806f43a6a10
  UKPN ECR            ukpowernetworks.opendatasoft.com  (Opendatasoft v2.1)
  SSEN ECR            data.ssen.co.uk
  Northern Powergrid  northernpowergrid.opendatasoft.com  (national ECR combine)
"""
from __future__ import annotations
import time, urllib.parse
try:
    import requests
except ImportError:
    requests = None  # adapters are import-safe even without requests installed

NESO_BASE = "https://api.neso.energy/api/3/action"
TEC_RESOURCE = "17becbab-e3e8-473f-b303-3806f43a6a10"

ODS_PORTALS = {
    "ukpn": "https://ukpowernetworks.opendatasoft.com",
    "npg":  "https://northernpowergrid.opendatasoft.com",
    "ssen": "https://data.ssen.co.uk",
}
ECR_DATASETS = {
    "ukpn": "ukpn-embedded-capacity-register",       # >=1MW (may require ODS API key)
    "npg":  "ecr_manual_combine_test",                # national combine — all DNOs
}
NGED_BASE = "https://connecteddata.nationalgrid.co.uk/api/3/action"
NGED_ECR_RESOURCE = "82a4ae83-77a3-4e7b-9060-8072ed96de9d"

def _get(url, params=None, pause=0.6):
    if requests is None:
        raise RuntimeError("pip install requests to run adapters")
    time.sleep(pause)  # be polite; NESO asks <=1 req/s
    r = requests.get(url, params=params, timeout=30,
                     headers={"User-Agent": "NFRI-harness/0.3 (research)"})
    r.raise_for_status()
    return r.json()

# ---------------- NESO TEC register (transmission generation/storage) ----------------
def neso_tec(limit=100, q=None):
    """Return TEC register rows (list of dicts). The 'Gate' column (Gate 1/Gate 2) is the
    firmness signal under Connections Reform (CMP434/435)."""
    params = {"resource_id": TEC_RESOURCE, "limit": limit}
    if q: params["q"] = q
    data = _get(f"{NESO_BASE}/datastore_search", params)
    return data["result"]["records"]

def neso_tec_fields():
    data = _get(f"{NESO_BASE}/datastore_search", {"resource_id": TEC_RESOURCE, "limit": 0})
    return [f["id"] for f in data["result"]["fields"]]

# ---------------- DNO Embedded Capacity Register (distribution demand/gen/flex) -------
def ods_records(portal_key, dataset, where=None, select=None, limit=100):
    """Generic Opendatasoft Explore v2.1 records query."""
    base = ODS_PORTALS[portal_key]
    params = {"limit": min(limit, 100)}
    if where:  params["where"]  = where
    if select: params["select"] = select
    url = f"{base}/api/explore/v2.1/catalog/datasets/{dataset}/records"
    return _get(url, params).get("results", [])

def ods_fields(portal_key, dataset):
    """Discover the dataset's real field names (no hard-coding)."""
    base = ODS_PORTALS[portal_key]
    url = f"{base}/api/explore/v2.1/catalog/datasets/{dataset}"
    info = _get(url)
    return [f["name"] for f in info.get("dataset", {}).get("fields", [])]

def ukpn_ecr(where=None, limit=100):
    return ods_records("ukpn", ECR_DATASETS["ukpn"], where=where, limit=limit)

def npg_ecr(term, limit=50):
    """Search the NPG national ECR combine (all DNOs)."""
    try:
        where = f'search("{term}")' if term else None
        return ods_records("npg", ECR_DATASETS["npg"], where=where, limit=limit)
    except Exception:
        return []

def nged_ecr(term, limit=50):
    """Search NGED ECR via CKAN datastore (South West / Wales assets)."""
    try:
        params = {"resource_id": NGED_ECR_RESOURCE, "limit": min(limit, 100)}
        if term:
            params["q"] = term
        data = _get(f"{NGED_BASE}/datastore_search", params)
        return data["result"].get("records", [])
    except Exception:
        return []

def _float(val):
    if val is None:
        return 0.0
    s = str(val).strip().lower()
    if s in {"", "none", "data not available", "data not applicable", "n/a"}:
        return 0.0
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return 0.0

def _norm_ecr_row(row: dict, portal: str, source_url: str) -> dict:
    """Normalize ODS / CKAN ECR rows to a common schema."""
    keys = {_k.lower().replace(" ", "").replace("_", ""): _k for _k in row}

    def pick(*candidates):
        for c in candidates:
            ck = c.lower().replace(" ", "").replace("_", "").replace("/", "")
            if ck in keys:
                return row[keys[ck]]
        for c in candidates:
            for k, v in row.items():
                if c.lower() in k.lower():
                    return v
        return None

    flex = str(pick("flexible_connection_yes_no", "flexible connection (yes/no)", "flexible_connection") or "").lower()
    status = str(pick("connection_status", "Connection Status") or "").lower()
    import_mw = _float(pick("maximum_import_capacity_mw", "connected_maximum_import_capacity(mw)",
                            "Maximum Import Capacity (MW)", "accepted_change_to_maximum_import_capacity(mw)"))
    export_mw = _float(pick("maximum_export_capacity_mw", "connected_maximum_export_capacity(mw)",
                            "energy_source_energy_conversion_technology_1_registered_capacity_mw",
                            "energy_source_&_conversion_tech_1_reg_capacity_mw"))
    non_firm = flex in {"yes", "y", "true", "1", "flexible"}
    if "accepted to connect" in status and "connected" not in status:
        non_firm = True
    if "non firm" in status or "curtail" in status:
        non_firm = True
    return {
        "portal": portal,
        "source_url": source_url,
        "customer": pick("customer_name", "Customer Name"),
        "site": pick("customer_site", "customer site", "Site Name"),
        "import_mw": import_mw,
        "export_mw": export_mw,
        "non_firm": non_firm,
        "flex": flex,
        "status": status,
    }

def ecr_search(term: str, limit=50) -> list[dict]:
    """Query NPG national combine + NGED CKAN; return normalized rows."""
    out = []
    npg_url = "https://northernpowergrid.opendatasoft.com/explore/dataset/ecr_manual_combine_test/"
    nged_url = "https://connecteddata.nationalgrid.co.uk/dataset/embedded-capacity-register"
    for row in npg_ecr(term, limit=limit):
        out.append(_norm_ecr_row(row, "npg", npg_url))
    for row in nged_ecr(term, limit=limit):
        out.append(_norm_ecr_row(row, "nged", nged_url))
    return out

def gate_from_tec(row: dict) -> tuple[str, str]:
    """Map a NESO TEC row to asset_link.gate_status + human note."""
    gate = str(row.get("Gate") or "").strip()
    status = str(row.get("Project Status") or "").strip()
    glower = gate.lower()
    if "gate 2" in glower or glower == "2":
        return "gate_2", f"NESO TEC Gate 2 — {row.get('Project Name')} ({row.get('Cumulative Total Capacity (MW)')} MW)"
    if "gate 1" in glower or glower == "1":
        return "gate_1", f"NESO TEC Gate 1 — {row.get('Project Name')}"
    if gate:
        return "non_firm", f"NESO TEC Gate={gate} — {row.get('Project Name')}"
    if status.lower() in {"connected", "operational"}:
        return "firm", f"NESO TEC connected — {row.get('Project Name')}"
    if status:
        return "unknown", f"NESO TEC {status} (Gate unset) — {row.get('Project Name')}"
    return "unknown", f"NESO TEC match — {row.get('Project Name')}"

# ---------------- Measured feature: non-firm intensity --------------------------------
def non_firm_intensity_from_ecr(records, mw_field, flex_field, status_field=None):
    """MEASURED feature. share of MW on flexible/curtailable (non-firm) connections.
    Caller supplies the discovered field names (from ods_fields) so nothing is assumed.
    Returns {value 0..1, mw_total, mw_nonfirm, n, as_of} or None if not computable."""
    tot = nf = 0.0; n = 0
    for r in records:
        try:
            mw = float(r.get(mw_field) or 0)
        except (TypeError, ValueError):
            continue
        if mw <= 0:
            continue
        tot += mw; n += 1
        flex = str(r.get(flex_field, "")).strip().lower()
        is_nonfirm = flex in {"yes", "true", "flexible", "y", "1"}
        if status_field and "non-firm" in str(r.get(status_field, "")).lower():
            is_nonfirm = True
        if is_nonfirm:
            nf += mw
    if tot == 0:
        return None
    return {"value": round(nf / tot, 3), "mw_total": round(tot, 1),
            "mw_nonfirm": round(nf, 1), "n": n, "unit": "MW-share"}

def rating_to_0_4(rating: str) -> int:
    """Disclosed capital feature. AM Best / S&P FSR -> 0..4 (fixed, auditable lookup)."""
    r = (rating or "").upper().replace("+", "").replace("-", "")
    table = {"AAA":4,"AA":4,"A":3,"BBB":2,"BB":1,"B":1,"CCC":0,"CC":0,"C":0,
             "A++":4,"A+":4,"AM_A":3,"B++":2,"B+":2}
    return table.get(r, 0)

if __name__ == "__main__":
    # Smoke test (requires network). Demonstrates schema discovery, no fabricated fields.
    print("NESO TEC fields:", neso_tec_fields()[:12], "…")
    rows = neso_tec(limit=3)
    print("sample TEC row keys:", list(rows[0].keys()) if rows else "n/a")
    print("UKPN ECR fields:", ods_fields("ukpn", ECR_DATASETS["ukpn"])[:12], "…")
