# Non-Firm Power Risk Index (NFRI)

UK insurance-market index for interruptible-power risk across energy assets and data centres.

## Quick start

```bash
cd ~/Developer/nfri
python3 -m pip install -r requirements.txt

# Live register pull (NESO TEC + DNO ECR) → re-score → rebuild site
python3 harness/ingest_live.py

# Open the index (serve locally)
python3 -m http.server 8080 --directory site
# → http://localhost:8080
```

## Pipeline

| Stage | Script | Output |
|---|---|---|
| Research | manual / agents | `data/records.json` |
| Live ingest | `harness/ingest_live.py` | `data/records.optimized.json` |
| Eval | `harness/evals.py` | `data/eval_report.txt` |
| Frontend | `harness/build_frontend.py` | `site/index.html`, `site/data/*` |

Downloads: CSV and JSON at `site/data/dataset.csv` and `site/data/records.optimized.json`.

## Project layout

See `METHODOLOGY.md` for rubric, data contract, and roadmap.
