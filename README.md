# Digital-Education-Resources-Rural-Urban-India

An exploratory data analysis of digital education resource availability and accessibility across rural and urban India, identifying regional disparities and patterns across states and school types to understand gaps in digital learning infrastructure.

This repository also serves a standalone interactive dashboard from `index.html`, with aggregated project data in `data/dashboard-data.json`. Its “The five questions, answered” section presents NumPy internet-access statistics, Pandas-style rural/urban filtering, missing-value handling, access metrics grouped by state and school category, and barplots/histograms of the digital divide. Visitors do not need Python, Jupyter, or a local server. Student names and roll numbers are not included in the public dashboard.

## Python API backend

The read-only FastAPI service in `backend/` uses the same published aggregate data as the dashboard and applies the notebook's NumPy/Pandas analysis for API requests. It does not expose the source school-level CSV files.

### Run locally

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `/docs`.

Run the backend tests from the repository root with:

```powershell
python -m unittest backend.test_api -v
```

### Endpoints

- `GET /api/health` — confirms the service and dashboard data are available.
- `GET /api/dashboard` — supplies the aggregate dataset used by the frontend.
- `GET /api/summary?area=All&category=All` — filtered totals and average access/readiness.
- `GET /api/questions?area=All&category=All` — answers and visualization data for all five questions.
- `GET /api/questions/{1-5}?area=All&category=All` — one question's answer.
- `GET /api/groups?area=All&category=All` — state/category access and readiness statistics.

`area` accepts `All`, `Rural`, or `Urban`; `category` accepts `All`, `Higher Secondary`, `Primary`, `Secondary`, or `Upper Primary`.

### Deploy the API

GitHub Pages cannot run Python server code, so the API must be deployed separately. The root `render.yaml` describes a free Render web service. In Render, create a new Blueprint from this repository and deploy the `schooling-connected-api` service. Render will provide its public API URL; `/docs` is the interactive API reference. Free services may sleep when idle.

The FastAPI service also serves the dashboard at `/`, so a Render deployment provides a website and API on the same public URL. The GitHub Pages version tries `/api/dashboard` first and falls back to its static aggregate JSON when that API route is unavailable.

## Enable GitHub Pages

In the repository, open **Settings > Pages** and select **GitHub Actions** as the build and deployment source. The `Deploy public site` workflow publishes the report whenever a commit is pushed to `main`. Once it finishes, GitHub shows the public URL under **Settings > Pages**.

The website is a static dashboard: its filters and charts run in the visitor's browser using the published aggregate data. The separate Python API handles server-side analysis requests. To update the figures, regenerate `data/dashboard-data.json` from the project datasets and push the changes to `main`.
