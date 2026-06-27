#!/usr/bin/env python3
"""Verify index narrative redesign (Phases 1–4) and Ciridae parity checklist.

Checks structural IA, chart_copy contract, and feature presence against
contract/CIRIDAE_GAP.md implemented items.

  python3 harness/verify_index_narrative.py
  python3 harness/verify_index_narrative.py --strict   # exit 1 on failure
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site", "index.html")
CHART_COPY = os.path.join(ROOT, "contract", "chart_copy.json")
GAP = os.path.join(ROOT, "contract", "CIRIDAE_GAP.md")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _pos(html: str, needle: str) -> int:
    i = html.find(needle)
    return i if i >= 0 else 10**9


def check_ia_order(html: str) -> list[str]:
    errors = []
    order = [
        ("argument", "industry act"),
        ("landscape", "landscape act"),
        ("mechanics", "mechanics act"),
        ("analysis", "proposal act"),
        ("index", "universe scatter"),
        ("findings", "findings"),
        ("rankings", "rankings table"),
        ("benchmark", "benchmark (deep analytics)")]
    positions = {name: _pos(html, f'id="{name}"') for name, _ in order}
    for i in range(len(order) - 1):
        a, la = order[i]
        b, lb = order[i + 1]
        if positions[a] >= positions[b]:
            errors.append(f"IA order: #{a} ({la}) should precede #{b} ({lb})")
    if _pos(html, 'id="terminal"') < _pos(html, 'id="argument"'):
        errors.append("terminal appears before thesis")
    if 'id="analytics-deep"' not in html:
        errors.append("missing collapsed analytics-deep accordion")
    if 'class="term-view-tabs"' not in html:
        errors.append("missing tabbed terminal (Phase 3)")
    if 'class="viz-block"' not in html:
        errors.append("missing viz-block narrative wrappers (Phase 2)")
    if 'id="section-tabs"' not in html:
        errors.append("missing section-tabs in sticky header")
    if 'data-viz="scatter_hero"' not in html:
        errors.append("missing scatter_hero chart copy slot")
    if 'id="hero-layer-chart"' not in html:
        errors.append("missing MoS-by-layer hero chart")
    if 'class="intro-pillar-grid"' in html:
        pass  # optional — thesis TOC replaces pillar grid
    if 'id="reference"' not in html:
        errors.append("missing reference disclosure (objections + sources)")
    if 'class="viz-bento"' not in html:
        errors.append("missing viz bento layout")
    if 'term-grid-bento' not in html:
        errors.append("missing terminal bento grid")
    if 'index-thesis-shell' not in html:
        errors.append("missing sticky thesis TOC shell")
    if 'class="faq-item"' not in html:
        errors.append("missing objection FAQ band")
    return errors


def check_chart_copy() -> list[str]:
    errors = []
    if not os.path.exists(CHART_COPY):
        return ["contract/chart_copy.json missing"]
    data = json.load(open(CHART_COPY))
    charts = data.get("charts") or {}
    required = (
        "scatter_hero", "mos_by_layer", "table_rankings",
        "term_regression", "term_scoreboard", "term_strategy",
        "term_swarm", "term_quad_stack", "term_alpha", "term_compare",
        "terminal_hub",
    )
    for k in required:
        if k not in charts:
            errors.append(f"chart_copy missing key: {k}")
        else:
            c = charts[k]
            if c.get("density") == "compact":
                for field in ("title", "stats"):
                    if not c.get(field):
                        errors.append(f"chart_copy.{k} missing {field}")
            else:
                for field in ("lede", "stats", "so_what"):
                    if k == "terminal_hub" and field in ("stats", "so_what"):
                        continue
                    if not c.get(field):
                        errors.append(f"chart_copy.{k} missing {field}")
    return errors


def check_terminal_viz(html: str) -> list[str]:
    errors = []
    term_charts = (
        "term_regression", "term_strategy", "term_scoreboard",
        "term_swarm", "term_quad_stack", "term_alpha", "term_compare",
    )
    for cid in term_charts:
        if f'data-viz="{cid}"' not in html:
            errors.append(f"built index missing terminal viz block: {cid}")
    if 'term-viz-card' not in html:
        errors.append("terminal panels missing term-viz-card structure")
    if 'class="term-chart-shell"' not in html:
        errors.append("terminal panels missing term-chart-shell wrapper")
    if "<!--__TERM_REGRESSION__-->" in html:
        errors.append("unresolved TERM_REGRESSION placeholder in built index")
    if 'term-panel-title">MoS vs measured share' in html:
        errors.append("duplicate hardcoded terminal titles still present")
    return errors


def check_built_payload(html: str) -> list[str]:
    errors = []
    if '"chartCopy"' not in html:
        errors.append("built index missing chartCopy in payload")
    if '"indexCharts"' not in html:
        errors.append("built index missing indexCharts in payload")
    if '"profileIds"' not in html:
        errors.append("built index missing profileIds (entity profiles)")
    m = re.search(r'"chartCopy"\s*:\s*\{', html)
    if m and "scatter_hero" not in html[m.start(): m.start() + 800]:
        errors.append("chartCopy.scatter_hero not in payload")
    return errors


def check_ciridae_parity(html: str) -> tuple[list[str], list[str]]:
    """Implemented vs deferred from CIRIDAE_GAP.md."""
    implemented = {
        "Fund-style entity cards": 'class="fund-card"' in html or 'id="card-list"' in html,
        "Portfolio swarm": 'id="term-swarm"' in html,
        "MoS vs outcome regression": 'id="term-regression"' in html,
        "Sector/layer scoreboards": 'id="term-scoreboard"' in html,
        "Full sub-factor profiles": '"profileIds"' in html,
        "Compare / alpha views": 'id="term-compare"' in html and 'id="term-alpha"' in html,
        "Carrier quad stack": 'id="term-quad-stack"' in html,
        "Thesis-first narrative": _pos(html, 'id="argument"') < _pos(html, 'id="index"')
            and _pos(html, 'id="mechanics"') < _pos(html, 'id="index"'),
        "Chart narrative copy": '"chartCopy"' in html,
        "Progressive disclosure": 'id="analytics-deep"' in html,
    }
    deferred = {
        "NL query layer": 'id="nl-query"' not in html,
        "Dark Bloomberg terminal skin": 'bench-section' in html,  # still light theme
        "L5 measured gate pass": "PROVISIONAL" in html or "Measured" in html,
    }
    errors = [f"Ciridae parity missing: {k}" for k, ok in implemented.items() if not ok]
    warnings = []
    if not deferred["NL query layer"]:
        warnings.append("NL query not expected yet")
    return errors, warnings


def main() -> int:
    strict = "--strict" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []

    if not os.path.exists(SITE):
        print(f"FAIL — run harness/build_frontend.py first ({SITE} missing)")
        return 1

    html = _read(SITE)
    errors.extend(check_ia_order(html))
    errors.extend(check_chart_copy())
    errors.extend(check_terminal_viz(html))
    errors.extend(check_built_payload(html))
    cir_errors, cir_warn = check_ciridae_parity(html)
    errors.extend(cir_errors)
    warnings.extend(cir_warn)

    print("INDEX NARRATIVE VERIFY — Phases 1–4 + Ciridae parity")
    print("=" * 56)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("  ✓ IA order, chart_copy, payload, Ciridae implemented items")
    if warnings:
        for w in warnings:
            print(f"  · {w}")
    print("=" * 56)
    if errors:
        print(f"FAIL — {len(errors)} error(s)")
        return 1 if strict else 0
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
