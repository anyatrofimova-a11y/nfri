# NFRI — Claude (Cowork) ⇄ Cursor iterative setup

There is NO direct chat link between Cowork-Claude and Cursor's agent. The bridge is
**this folder + git**: each side edits, the other reviews the **diff**.

## One-time setup
1. Open the folder in Cursor: File ▸ Open Folder… → select this `nfri` folder.
2. Put a Claude agent inside Cursor (Claude Code):
   - Cursor integrated terminal → run: `claude`
   - Visual diffs: Cmd+Shift+P → "Extensions: Install from VSIX" →
     `~/.claude/local/node_modules/@anthropic-ai/claude-code/vendor/claude-code.vsix`
3. `git init` (if not already a repo).

## The review loop
- Cowork → Cursor: I edit files here; they show up in Cursor; you/Claude Code review the diff.
- Cursor → Cowork: you commit; next turn I `git diff` and review back.
- Use branches so each side reviews cleanly: `git checkout -b feature/x` … `git diff main`.
- Claude Code has `/review` for reviewing changes/PRs.

## Run the harness

**Start here — the loop orchestrator (ties all METHODOLOGY §6 loops together):**
    python3 harness/run_loop.py            # NON-DESTRUCTIVE: every gate that only reads data
    python3 harness/run_loop.py --list     # loop → script mapping
    python3 harness/run_loop.py --full     # ingest → score → optimize → eval → build (regenerates data/ + site/)

**Individual harnesses:**
    python3 harness/ingest_live.py            # live NESO TEC + DNO ECR pull → re-score → build
    python3 harness/score_and_validate.py     # offline hybrid score + validate (uses scoring.py fusion)
    python3 harness/optimize.py               # optimization loop (audited deltas + recalibration)
    python3 harness/evals.py                  # eval L0–L8 (L5 = publication gate, L8 = model-spec/knowledge)
    python3 harness/industry_stress.py        # RDS / Solvency / Felix-Strata scenarios
    python3 harness/stress_test.py            # methodology meta-stress (gate math + assumptions S1–S7)
    python3 harness/verify_model_spec.py      # model-spec ↔ knowledge integrity (citations, wiring, thresholds)
    python3 harness/knowledge_graph.py node <id> check   # validate one knowledge node

**Measured passes (need real inputs; --live reads contract/*_inputs.json):**
    python3 harness/measure_non_firm.py --fixture   # / --live (ECR/TEC adapters)
    python3 harness/measure_capital.py  --fixture   # / --live (contract/capital_inputs.json)
    python3 harness/measure_book.py     --fixture   # / --live (contract/book_inputs.json)

See **CURSOR_HANDOFF.md** for what changed, open items, and the one decision needed.

## Notes
- data/records.measured_demo.json is demo/fixture output — never the index.
- evals L5 (publication gate) stays FAIL until measured+disclosed share ≥ 60%.
- Cursor can load MCP servers via ~/.cursor/mcp.json (shares tools, not a Claude-to-Claude link).
