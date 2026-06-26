#!/usr/bin/env python3
"""NFRI loop orchestrator — runs the METHODOLOGY §6 loops as one reproducible harness.

The pipeline is a set of named loops over the shared contract. This ties the discrete scripts
into one runnable sequence with explicit pass/fail gating, so either side of the Cowork⇄Cursor
bridge can run the whole thing with one command and review the result.

  python3 harness/run_loop.py            # --check : NON-DESTRUCTIVE (evals + all verifiers only)
  python3 harness/run_loop.py --full     # full loop: ingest → score → optimize → eval → build
  python3 harness/run_loop.py --list     # show the loop → script mapping and exit

--check never rewrites records/site files (safe to run while the other side edits); it runs every
gate that only READS the current data. --full runs the data-regenerating stages too. Exit code is
nonzero if any GATE stage fails.
"""
from __future__ import annotations
import os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

# (loop name, script, args, destructive?, gate?)  — order matters within each mode
STAGES = [
    # METHODOLOGY §6 loop          script                       args                          destr  gate
    ("Ingestion",                  "ingest_live.py",            [],                            True,  False),
    ("Scoring + Linking + Valid.", "score_and_validate.py",     [],                            True,  True),
    ("Optimization",               "optimize.py",               [],                            True,  False),
    ("Eval / drift (L0-L8)",       "evals.py",                  ["data/records.optimized.json"], False, True),
    ("Validation / adversary",     "industry_stress.py",        [],                            False, True),
    ("Methodology meta-stress",    "stress_test.py",            [],                            False, False),
    ("Model-spec ↔ knowledge",     "verify_model_spec.py",      [],                            False, True),
    ("Frontend build",             "build_frontend.py",         [],                            True,  False),
]
CHECK_ONLY = {"evals.py", "industry_stress.py", "stress_test.py", "verify_model_spec.py"}


def summarise(out: str) -> str:
    """Pull the most informative one-line summary from a stage's stdout."""
    for key in ("SUMMARY", "VERDICT", "scenarios pass", "wrote:", "checks pass"):
        hits = [ln.strip() for ln in out.splitlines() if key in ln]
        if hits:
            return hits[-1][:100]
    tail = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return tail[-1][:100] if tail else "(no output)"


def run_stage(script: str, args: list) -> tuple:
    path = os.path.join(ROOT, "harness", script)
    if not os.path.exists(path):
        return 127, f"(missing: harness/{script})"
    try:
        p = subprocess.run([PY, path, *args], cwd=ROOT, capture_output=True, text=True, timeout=600)
        return p.returncode, summarise(p.stdout + "\n" + p.stderr)
    except Exception as e:
        return 1, f"(runner error: {e})"


def main() -> int:
    mode = "full" if "--full" in sys.argv else "check"
    if "--list" in sys.argv:
        print("NFRI loops → harness scripts:")
        for loop, script, args, destr, gate in STAGES:
            tags = " ".join(t for t, f in (("[destructive]", destr), ("[GATE]", gate)) if f)
            print(f"  {loop:<28} harness/{script:<24} {tags}")
        return 0

    stages = STAGES if mode == "full" else [s for s in STAGES if s[1] in CHECK_ONLY]
    print(f"NFRI LOOP ORCHESTRATOR — mode: {mode}"
          f"{'  (NON-DESTRUCTIVE)' if mode == 'check' else '  (REGENERATES data/ + site/)'}")
    print("=" * 72)
    rows, gate_failed = [], False
    for loop, script, args, destr, gate in stages:
        code, summary = run_stage(script, args)
        ok = code == 0
        if gate and not ok:
            gate_failed = True
        status = "OK  " if ok else ("FAIL" if gate else "warn")
        flag = " *GATE*" if gate else ""
        rows.append((status, loop, script, summary, flag))
        print(f"  [{status}] {loop:<28}{flag}")
        print(f"         {script}: {summary}")
    print("=" * 72)
    npass = sum(1 for r in rows if r[0] == "OK  ")
    print(f"{npass}/{len(rows)} stages clean | gates: {'FAIL' if gate_failed else 'PASS'} | mode={mode}")
    if mode == "check":
        print("note: --check skips data-regenerating stages. Run --full to refresh records/site.")
    print("reports: data/eval_report.txt, data/industry_stress_report.txt, "
          "data/stress_test_report.txt, data/model_spec_verification.txt")
    return 1 if gate_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
