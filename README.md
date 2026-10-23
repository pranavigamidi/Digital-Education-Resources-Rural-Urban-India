# Digital-Education-Resources-Rural-Urban-India

An exploratory data analysis of digital education resource availability and accessibility across rural and urban India, identifying regional disparities and patterns across states and school types to understand gaps in digital learning infrastructure.

This repository also serves a static copy of the rendered report as `index.html`. Visitors do not need Python, Jupyter, or a local server. Student names and roll numbers have been removed from the public copy.

## Enable GitHub Pages

In the repository, open **Settings > Pages** and select **GitHub Actions** as the build and deployment source. The `Deploy public site` workflow publishes the report whenever a commit is pushed to `main`. Once it finishes, GitHub shows the public URL under **Settings > Pages**.

The page is a static report: its existing text, tables, and plots are included in the exported HTML. It does not run notebook code or provide interactive analysis. To publish updated notebook results, export the notebook to HTML again, remove any personal details intended to remain private, and replace `index.html`.
