#!/usr/bin/env python3
"""Create the CMUI model end-to-end: verify → ingest live feeds → stress → publish.

    python3 harness/create_compute_model.py [--skip-ingest]

Outputs:
  data/compute_records.scored.json   — scored universe
  data/compute_dataset.csv           — download slice
  data/compute_model_verification.txt
  data/compute_stress_report.txt
  site/on-compute-markets.html       — methodology manifesto
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "harness"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CMUI model from contract + live feeds")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip live market ingest (score existing records only)")
    parser.add_argument("--skip-stress", action="store_true", help="Skip industry stress suite")
    parser.add_argument("--skip-manifesto", action="store_true", help="Skip site manifesto rebuild")
    args = parser.parse_args()

    from verify_compute_model_spec import main as verify  # noqa: E402

    print("=== 1/4 Verify model contract ===")
    if verify() != 0:
        print("ABORT: model verification failed")
        return 1

    if not args.skip_ingest:
        print("\n=== 2/4 Ingest live indices + score ===")
        from ingest_compute_indices import main as ingest  # noqa: E402

        ingest()
    else:
        print("\n=== 2/4 Score (ingest skipped) ===")
        import json  # noqa: E402
        from compute_scoring import load_compute_model, load_compute_rubric, score_all  # noqa: E402

        path = os.path.join(ROOT, "data", "compute_records.json")
        records = json.load(open(path))
        rubric = load_compute_rubric()
        model = load_compute_model()
        records, cut_e, cut_p = score_all(records, rubric=rubric, model=model)
        out = os.path.join(ROOT, "data", "compute_records.scored.json")
        json.dump(records, open(out, "w"), indent=2, ensure_ascii=False)
        print(f"scored {len(records)} entities — cuts exposure>={cut_e} prep>={cut_p}")

    if not args.skip_stress:
        print("\n=== 3/4 Industry stress tests ===")
        from compute_industry_stress import run_stress_suite  # noqa: E402

        results, report = run_stress_suite()
        print(report)
        if not all(r["status"] == "PASS" for r in results):
            print("WARN: one or more stress scenarios failed (see compute_stress_report.txt)")
    else:
        print("\n=== 3/4 Stress tests skipped ===")

    if not args.skip_manifesto:
        print("\n=== 4/4 Publish manifesto ===")
        from build_compute_manifesto import main as build_manifesto  # noqa: E402

        build_manifesto()
    else:
        print("\n=== 4/4 Manifesto skipped ===")

    print("\nCMUI model ready.")
    print(f"  spec:     contract/COMPUTE_MODEL_SPEC.md")
    print(f"  machine:  contract/compute_risk_model.json")
    print(f"  scored:   data/compute_records.scored.json")
    print(f"  site:     site/on-compute-markets.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
