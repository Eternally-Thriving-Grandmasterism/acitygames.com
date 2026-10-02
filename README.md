# Autonomicity Games

Static website for Autonomicity Games Inc. Sherif Botros is the founder and current steward.

The pages live in [`site/`](site/). GitHub Pages is set up to publish that folder only. `README.md` and `LICENSE` stay at the repository root and are not part of the published site.

## Preview

From the repository root:

```bash
python3 -m http.server 8080 --directory site
```

Open [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

Links are relative, so the same files work on the GitHub Pages project URL and, later, on the apex domain.

## What is on the site

Home, About, Powrush-MMO, Rathor.ai, Careers, and Contact. The pages are plain HTML and CSS: no build step, no trackers, and no external fonts.

Contact: [info@Rathor.ai](mailto:info@Rathor.ai)

## Publishing

`.github/workflows/pages.yml` deploys on a push to `main`, or when someone runs the workflow by hand. It uploads only `site/`.

The repository owner turns GitHub Pages on in the repository settings and chooses GitHub Actions as the source. This repository does not change that setting.
