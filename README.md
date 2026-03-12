# dneufeld.github.io

Minimal GitHub Pages blog scaffold for publishing exploration notes.

## What's here

- Jekyll site configured for a GitHub Pages user site
- A small set of published notes and supporting assets
- A minimal structure that is easy to extend with new posts

## Publishing workflow

This repo is already configured as a public GitHub Pages user site at `https://dneufeld.github.io/`.

1. Add a new post under `_posts/` using Jekyll's `YYYY-MM-DD-title.md` naming convention.
2. Add any supporting assets under `assets/`.
3. If needed, update site-level config in `_config.yml`.
4. Commit and push to `main`.
5. GitHub Pages will rebuild the site automatically.

## Post contract

Each post must set explicit front matter for the metadata we care about in social previews:

```yaml
---
layout: post
title: "Your post title"
permalink: /your-slug/
description: "The exact sentence that should appear in Slack or other unfurls."
image: /assets/your-social-card.png
---
```

Rules:

- `description` is the canonical preview text. Do not rely on the first paragraph or excerpt fallback.
- `image` should point to an explicit social card asset for the post. Do not rely on a generic default if the post has a chart, diagram, or strong headline.
- Keep disclaimer text out of `description`.
- If a post needs a legal disclosure, put it in the body, not in the preview sentence.

## Local checks

Build the site, then validate the rendered HTML contract:

```bash
bundle exec jekyll build --future
python3 script/validate_site_contract.py
```

The validator checks:

- required post front matter (`layout`, `title`, `permalink`, `description`, `image`)
- rendered `meta description`, `og:title`, `og:description`, `og:image`, `twitter:description`, and canonical URL
- the Cloudflare Web Analytics beacon snippet and configured token on every built post

## Optional integrations

### Cloudflare Web Analytics

This site has a conditional Cloudflare Web Analytics hook in `_includes/head.html`.

To enable it:

1. Create a Web Analytics site in Cloudflare and copy the token from their dashboard.
2. Set `cloudflare_web_analytics_token` in `_config.yml`.
3. Commit and push.

The token is used in Cloudflare's standard beacon script and is public client-side data, not a secret.

## Setup notes

GitHub user sites must live in a public repo named `<owner>.github.io`, and Pages can publish from the root of a branch. GitHub also notes that Jekyll builds run through GitHub Actions, so Actions must be enabled for the repo.

## Sources

- GitHub Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Docs: https://docs.github.com/articles/user-organization-and-project-pages
- GitHub Docs: https://docs.github.com/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll
