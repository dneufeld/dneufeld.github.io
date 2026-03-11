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
3. Commit and push to `main`.
4. GitHub Pages will rebuild the site automatically.

## Setup notes

GitHub user sites must live in a public repo named `<owner>.github.io`, and Pages can publish from the root of a branch. GitHub also notes that Jekyll builds run through GitHub Actions, so Actions must be enabled for the repo.

## Sources

- GitHub Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Docs: https://docs.github.com/articles/user-organization-and-project-pages
- GitHub Docs: https://docs.github.com/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll
