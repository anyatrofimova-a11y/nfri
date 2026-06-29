#!/usr/bin/env python3
"""Build site/explore.html — browsable card grid with insurer logos."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_essays import ESSAY_CSS  # noqa: E402
from design_system import load_design_system  # noqa: E402
from frontend.explore_assemble import assemble_explore_page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_explore_page(*, payload: dict) -> str:
    ds = load_design_system(os.path.join(ROOT, "contract", "design_system.json"))
    slim = {
        "pts": payload.get("pts", []),
        "cal": payload.get("cal", {}),
        "n": payload.get("n", 0),
        "share": payload.get("share", 0),
        "cites": payload.get("cites", {}),
        "sfLabels": payload.get("sfLabels", {}),
        "profileIds": payload.get("profileIds", []),
    }
    return assemble_explore_page(
        ds=ds,
        payload=slim,
        prose_css=ESSAY_CSS,
        fonts_url=ds["fonts"]["google_url"],
    )


def main():
    from build_frontend import (  # noqa: WPS433
        SF_LABEL,
        authoritative_share,
        build_points,
        load_records,
        parse_calibration,
    )

    records, _ = load_records()
    pts = build_points(records)
    cut_exp, cut_prep = parse_calibration((records[0].get("scores") or {}).get("calibration"))
    share = authoritative_share(records)
    import json

    cites_full = json.load(open(os.path.join(ROOT, "contract", "citations.json")))["references"]
    cites = {
        k: {
            "t": v.get("title", ""),
            "a": v.get("authors", ""),
            "y": v.get("year", ""),
            "u": v.get("url", ""),
            "use": v.get("use", ""),
        }
        for k, v in cites_full.items()
    }
    profiles_path = os.path.join(ROOT, "site", "data", "profiles.json")
    profile_ids = list(json.load(open(profiles_path)).keys()) if os.path.exists(profiles_path) else []
    payload = {
        "pts": pts,
        "cal": {"cutExp": cut_exp, "cutPrep": cut_prep},
        "share": share,
        "n": len(pts),
        "cites": cites,
        "sfLabels": SF_LABEL,
        "profileIds": profile_ids,
    }
    html = build_explore_page(payload=payload)
    out = os.path.join(ROOT, "site", "explore.html")
    open(out, "w").write(html)
    print(f"wrote {out}  ({len(html)//1024} KB, {len(pts)} entity cards)")


if __name__ == "__main__":
    main()
