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

# Rebuild after contract / design changes
python3 harness/build_frontend.py
```

**Live site (GitHub Pages):** https://anyatrofimova-a11y.github.io/nfri/

Pages deploys from `site/` on push to `framework` via `.github/workflows/deploy-pages.yml`. In repo **Settings → Pages**, set **Build and deployment → Source** to **GitHub Actions** if the site 404s on first setup.

## Pipeline

| Stage | Script | Output |
|---|---|---|
| Research | manual / agents | `data/records.json` |
| Live ingest | `harness/ingest_live.py` | `data/records.optimized.json` |
| Eval | `harness/evals.py` | `data/eval_report.txt` |
| Industry stress | `harness/industry_stress.py` | `data/industry_stress_report.txt` |
| Methodology stress | `harness/stress_test.py` | `data/stress_test_report.txt` |
| Frontend | `harness/build_frontend.py` | `site/index.html`, `site/data/*` |

Downloads: CSV and JSON at `site/data/dataset.csv` and `site/data/records.optimized.json`.

## Model & citations

- **`contract/MODEL_SPEC.md`** — every formula, threshold, and fusion rule with industry/academic citations
- **`contract/citations.json`** — full bibliography (Solvency II, Lloyd's RDS, NESO CMP434, basis-risk literature, etc.)
- **`contract/knowledge/`** — curated extracts + [`graph.json`](contract/knowledge/graph.json) knowledge graph (DC exposure, non-firm grid, pricing models)
- **`contract/risk_model.json`** — machine-readable model; **`harness/scoring.py`** implements hybrid latent×deterministic fusion
