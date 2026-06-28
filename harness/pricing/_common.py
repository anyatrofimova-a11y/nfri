"""Shared paths and helpers for NFRI pricing pipeline."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGES = ROOT / "contract" / "products" / "pricing" / "stages"
LOSS_PAIRS = ROOT / "contract" / "products" / "pricing" / "data" / "loss_pairs.json"
PRICING_MODEL = ROOT / "contract" / "products" / "pricing" / "pricing_model.json"
RECORDS_MEASURED = ROOT / "data" / "records.measured.json"
AUDIT_DIR = ROOT / "data" / "pricing" / "audit"

STAGE1 = STAGES / "01_curtailment_intensity" / "calibration.json"
STAGE2 = STAGES / "02_compound_loss" / "output.json"
STAGE3 = STAGES / "03_expectile_payout" / "calibration.json"
STAGE4 = STAGES / "04_hybrid_tower" / "output.json"
STAGE5 = STAGES / "05_premium_capital" / "output.json"

MODEL_VERSION = "pricing-0.1"
GBP_TO_USD = 1.27
DEFAULT_VOLL_GBP_MWH = 500.0
EXPECTILE_TAU = 0.85
TRAD_CAP_FRACTION = 0.60
EXPENSE_LOAD = 0.12
RISK_MARGIN_BASE = 0.08
SCR_RATE = 0.175


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def inputs_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256-" + hashlib.sha256(blob.encode()).hexdigest()[:16]


def asset_index(payload: dict, key: str = "assets") -> dict[str, dict]:
    return {a["entity_id"]: a for a in payload.get(key, [])}
