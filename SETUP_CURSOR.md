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
    python3 harness/score_and_validate.py
    python3 harness/optimize.py
    python3 harness/evals.py
    python3 harness/measure_non_firm.py --fixture
    python3 harness/measure_capital.py  --fixture
    python3 harness/measure_book.py     --fixture
    # add --live after wiring contract/*_inputs.json + the ECR/TEC adapters

## Notes
- data/records.measured_demo.json is demo/fixture output — never the index.
- evals L5 (publication gate) stays FAIL until measured+disclosed share ≥ 60%.
- Cursor can load MCP servers via ~/.cursor/mcp.json (shares tools, not a Claude-to-Claude link).
