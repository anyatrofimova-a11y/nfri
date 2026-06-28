"""Resolve canonical PRINCEPS brand asset paths from contract/brand_assets.json."""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "contract", "brand_assets.json")


def load_brand_manifest(path: str | None = None) -> dict:
    with open(path or MANIFEST_PATH) as f:
        return json.load(f)


def _asset(manifest: dict, key: str) -> dict | None:
    return (manifest.get("assets") or {}).get(key)


def asset_path(manifest: dict, key: str) -> str | None:
    entry = _asset(manifest, key)
    if not entry:
        return None
    return entry.get("file")


def asset_ready(manifest: dict, key: str) -> bool:
    entry = _asset(manifest, key)
    return bool(entry and entry.get("status") == "ready")


def resolve_brand_paths(ds: dict, manifest: dict | None = None) -> dict:
    """Merge design_system brand block with manifest paths and readiness."""
    manifest = manifest or load_brand_manifest()
    b = dict(ds.get("brand") or {})
    assets = manifest.get("assets") or {}

    glyph = b.get("glyph") or asset_path(manifest, "glyph") or b.get(
        "triquetra", "assets/brand/princeps-glyph.png"
    )
    b["glyph"] = glyph
    b["triquetra"] = glyph

    for key in assets:
        file_path = asset_path(manifest, key)
        if file_path:
            b[key] = file_path
        b[f"{key}_ready"] = asset_ready(manifest, key)

    header = (manifest.get("lockup") or {}).get("header_light") or {}
    splash = (manifest.get("lockup") or {}).get("splash") or {}
    b["header_wordmark_key"] = header.get("wordmark")
    b["splash_wordmark_key"] = splash.get("wordmark")
    b["image_policy"] = manifest.get("policy", "use_unchanged")
    return b
