# Digital-Education-Resources-Rural-Urban-India

An exploratory data analysis of digital education resource availability and accessibility across rural and urban India, identifying regional disparities and patterns across states and school types to understand gaps in digital learning infrastructure.

This repository also serves a standalone interactive dashboard from `index.html`, with aggregated project data in `data/dashboard-data.json`. Its “The five questions, answered” section presents NumPy internet-access statistics, Pandas-style rural/urban filtering, missing-value handling, access metrics grouped by state and school category, and barplots/histograms of the digital divide. Visitors do not need Python, Jupyter, or a local server. Student names and roll numbers are not included in the public dashboard.

## Public API on GitHub Pages

GitHub Pages cannot run Python server code. Instead, the Pages workflow runs the FastAPI analysis against the published aggregate data and publishes static JSON responses alongside the website. The public endpoints are read-only snapshots, regenerated whenever the workflow deploys; they do not execute Python in response to a visitor's request. They do not expose the source school-level CSV files.

The dashboard fetches `api/dashboard.json` from the same GitHub Pages site. Its interactive filters continue to work in the browser using the published aggregate data.

### Public static endpoints

The public base URL is `https://<owner>.github.io/<repository>/api/`. For example:

- `GET dashboard.json` — aggregate dataset used by the frontend.
- `GET health.json` — publication health response.
- `GET summary/{area}/{category}.json` — filtered totals and average access/readiness.
- `GET questions/{area}/{category}.json` — answers and visualization data for all five questions.
- `GET questions/{question-id}/{area}/{category}.json` — one question's answer; question ID is `1` through `5`.
- `GET groups/{area}/{category}.json` — grouped state/category statistics.

Use `all`, `rural`, or `urban` for `{area}`. Use `all`, `higher-secondary`, `primary`, `secondary`, or `upper-primary` for `{category}`. For example:

```text
https://<owner>.github.io/<repository>/api/questions/rural/primary.json
https://<owner>.github.io/<repository>/api/questions/4/all/all.json
```

Because GitHub Pages only serves files, these are pre-generated paths rather than query-parameter endpoints; a request such as `/api/questions?area=Rural` is not dynamically filtered by GitHub.

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

### Run the dynamic API locally

The dynamic FastAPI service supports query-parameter filtering and interactive API docs at `/docs` when run locally or deployed to a Python hosting service. GitHub Pages publishes the static API snapshots above; it does not host this running service.

## Enable GitHub Pages

In the repository, open **Settings > Pages** and select **GitHub Actions** as the build and deployment source. The `Deploy public site` workflow publishes the report whenever a commit is pushed to `main`. Once it finishes, GitHub shows the public URL under **Settings > Pages**.

The website and static API are published when the `Deploy public site` workflow runs. To update the figures, regenerate `data/dashboard-data.json` from the project datasets and push the changes to `main`; the workflow regenerates the API responses from that data.
