#!/usr/bin/env python3
"""Phase 1 index API — static export + optional local server (IC-04).

  python3 harness/platform/index_api.py --export     # site/api/v1/
  python3 harness/platform/index_api.py --serve      # localhost:8787
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
API_ROOT = os.path.join(ROOT, "site", "api", "v1")
sys.path.insert(0, os.path.join(ROOT, "harness", "platform"))
from graph import enrich_graph_geography, propagate_scenario  # noqa: E402


def _load_records() -> list:
    for name in ("records.measured.json", "records.scored.json", "records.json"):
        path = os.path.join(ROOT, "data", name)
        if os.path.isfile(path):
            return json.load(open(path, encoding="utf-8"))
    return []


def _provenance_headers(data_source: str = "live") -> dict:
    return {
        "X-Data-Source": data_source,
        "X-Snapshot-As-Of": date.today().isoformat(),
        "X-Evidence-Tier": "mixed",
        "X-Model-Version": "risk_model-0.2",
    }


def _strip_scores(records: list) -> list:
    out = []
    for r in records:
        rec = dict(r)
        rec.pop("scores", None)
        out.append(rec)
    return out


def run_propagation(scenario_id: str) -> dict:
    harness_dir = os.path.join(ROOT, "harness")
    if harness_dir not in sys.path:
        sys.path.insert(0, harness_dir)
    from scoring import load_rubric, load_risk_model, median_cut_lines, score_all
    recs = _strip_scores(_load_records())
    perturbed = propagate_scenario(recs, scenario_id)
    cut_exp, cut_prep = median_cut_lines(recs)
    rubric = load_rubric()
    model = load_risk_model()
    base_scored, _, _ = score_all(recs, cut_exp, cut_prep, rubric, model)
    stress_scored, _, _ = score_all(perturbed, cut_exp, cut_prep, rubric, model)
    base_by = {r["entity_id"]: r.get("scores", {}) for r in base_scored}
    stress_by = {r["entity_id"]: r.get("scores", {}) for r in stress_scored}
    movers = []
    for eid in base_by:
        bq = base_by[eid].get("quadrant")
        sq = stress_by[eid].get("quadrant")
        if bq != sq:
            movers.append({
                "entity_id": eid,
                "from": bq,
                "to": sq,
                "mos_delta": round(stress_by[eid].get("margin_of_safety", 0) - base_by[eid].get("margin_of_safety", 0), 1),
            })
    max_drop = max(
        (base_by[eid].get("margin_of_safety", 0) - stress_by[eid].get("margin_of_safety", 0) for eid in base_by),
        default=0,
    )
    exposed = sum(1 for s in stress_by.values() if s.get("quadrant") == "exposed")
    return {
        "scenario_id": scenario_id,
        "generated": date.today().isoformat(),
        "entity_count": len(recs),
        "exposed_count": exposed,
        "max_mos_drop": round(max_drop, 1),
        "quadrant_movers": sorted(movers, key=lambda m: m["mos_delta"])[:20],
        "graph_module": "harness/platform/graph.py",
    }


def export_static() -> None:
    os.makedirs(API_ROOT, exist_ok=True)
    recs = _load_records()
    graph = enrich_graph_geography()
    in_force = os.path.join(ROOT, "data", "l5_in_force.json")

    meta = {
        "generated": date.today().isoformat(),
        "provenance": _provenance_headers(),
        "entity_count": len(recs),
    }
    json.dump(meta, open(os.path.join(API_ROOT, "meta.json"), "w"), indent=2)

    scored = [r for r in recs if r.get("scores")]
    json.dump(scored, open(os.path.join(API_ROOT, "entities.json"), "w"), indent=2)

    # CSV dataset
    if scored:
        import csv
        rows = []
        for r in scored:
            s = r.get("scores") or {}
            rows.append({
                "entity_id": r["entity_id"],
                "name": r["name"],
                "layer": r["layer"],
                "entity_type": r["entity_type"],
                "value_chain_seat": r.get("value_chain_seat", ""),
                "exposure_0_100": s.get("exposure_0_100"),
                "preparedness_0_100": s.get("preparedness_0_100"),
                "margin_of_safety": s.get("margin_of_safety"),
                "quadrant": s.get("quadrant"),
            })
        with open(os.path.join(API_ROOT, "dataset.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    json.dump(graph, open(os.path.join(API_ROOT, "graph.json"), "w"), indent=2)
    json.dump(
        run_propagation("RDS-CORRELATED-CURTAILMENT"),
        open(os.path.join(API_ROOT, "graph_propagate.example.json"), "w"),
        indent=2,
    )
    if os.path.isfile(in_force):
        shutil.copy(in_force, os.path.join(API_ROOT, "l5_in_force.json"))

    open(os.path.join(API_ROOT, "openapi.yaml"), "w").write(
        open(os.path.join(ROOT, "contract", "platform", "openapi.index.yaml"), encoding="utf-8").read()
    )
    print(f"exported index API → {API_ROOT}/ ({len(scored)} entities, graph + propagate)")


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj: dict, code: int = 200) -> None:
        body = json.dumps(obj, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for k, v in _provenance_headers().items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in ("/api/v1/entities", "/entities"):
            recs = _load_records()
            self._json({"entities": recs, "count": len(recs)})
        elif path in ("/api/v1/dataset", "/dataset"):
            self._json({"path": "site/api/v1/dataset.csv"})
        elif path in ("/api/v1/graph", "/graph"):
            self._json(enrich_graph_geography())
        else:
            self._json({"routes": ["/entities", "/dataset", "/graph", "/graph/propagate"]})

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        if path not in ("/api/v1/graph/propagate", "/graph/propagate"):
            self._json({"error": "not found"}, 404)
            return
        body = self._read_json_body()
        scenario_id = body.get("scenario_id")
        if not scenario_id:
            self._json({"error": "scenario_id required"}, 400)
            return
        try:
            self._json(run_propagation(scenario_id))
        except ValueError as exc:
            self._json({"error": str(exc)}, 400)


def serve(port: int = 8787) -> None:
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main() -> int:
    if "--export" in sys.argv:
        export_static()
        return 0
    if "--serve" in sys.argv:
        print("serving index API on http://127.0.0.1:8787/api/v1/entities")
        serve()
        return 0
    print("Usage: index_api.py --export | --serve")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
