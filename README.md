# dneufeld.github.io

Minimal GitHub Pages blog scaffold for publishing the Shopify/Common Crawl posts in this repo.

## What's here

- Jekyll site configured for a GitHub Pages user site
- Three posts imported from the draft branches
- `assets/pipeline-diagram.svg` for the first post

## Publish steps

GitHub Docs currently require user sites to live in a public repo named `<owner>.github.io`, and Pages can publish from the root of a branch. GitHub also notes that Jekyll builds now run through GitHub Actions, so Actions must be enabled for the repo.

1. Re-authenticate GitHub CLI:
   - `gh auth login -h github.com`
2. Push this directory as a public repo:
   - `cd /home/dneufeld/code/shopify-dataset-project/dneufeld.github.io`
   - `gh repo create dneufeld.github.io --public --source=. --remote=origin --push`
3. In GitHub repo settings:
   - `Settings -> Pages -> Build and deployment -> Source -> Deploy from a branch`
   - Branch: `main`
   - Folder: `/(root)`

After GitHub finishes the first build, the site should be available at `https://dneufeld.github.io/`.

## Sources

- GitHub Docs: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Docs: https://docs.github.com/articles/user-organization-and-project-pages
- GitHub Docs: https://docs.github.com/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll
