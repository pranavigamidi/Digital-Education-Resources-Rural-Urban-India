# Digital-Education-Resources-Rural-Urban-India

An exploratory data analysis of digital education resource availability and accessibility across rural and urban India, identifying regional disparities and patterns across states and school types to understand gaps in digital learning infrastructure.

This repository also serves a standalone interactive dashboard from `index.html`, with aggregated project data in `data/dashboard-data.json`. Visitors do not need Python, Jupyter, or a local server. Student names and roll numbers are not included in the public dashboard.

## Enable GitHub Pages

In the repository, open **Settings > Pages** and select **GitHub Actions** as the build and deployment source. The `Deploy public site` workflow publishes the report whenever a commit is pushed to `main`. Once it finishes, GitHub shows the public URL under **Settings > Pages**.

The website is a static dashboard: its filters and charts run in the visitor's browser using the published aggregate data. It does not run notebook code. To update the figures, regenerate `data/dashboard-data.json` from the project datasets and push the changes to `main`.
