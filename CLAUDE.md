# fwbg_collections

This repo is the *source* for the FWBG digital collections page. It is not a
website itself — `README.md` is treated as the page content, and CI renders
it into a static page published on a different repo entirely.

## What lives here

- `README.md` — the actual content of the published page (links to FWBG
  Living Collections, BRIT Herbarium, Library & Archives, etc). Edits here
  are what show up publicly.
- `styles.css` — stylesheet for the rendered page.
- `fwbg/` — shared design tokens (`fwbg/tokens/*.css`), the FWBG logo, and
  fonts, copied as-is into the published output so the page has no
  dependency on the hub site's design system.
- `tools/stage-pages.py` — renders `README.md` through GitHub's markdown API
  (`mode: gfm`, no local markdown parser dependency) into
  `_stage/collections/index.html`, wraps it in `PAGE_TEMPLATE` (header/logo,
  footer), copies `styles.css` and `fwbg/tokens` + `fwbg/assets` alongside
  it. It also patches `target="_blank"`/`rel="noopener noreferrer"` back
  onto external links, because GitHub's markdown API sanitizes those
  attributes out of raw HTML.
- `.github/workflows/publish.yml` — the CI job. Triggers on push to `main`
  when `README.md`, `styles.css`, `fwbg/**`, `tools/stage-pages.py`, or the
  workflow file itself change (or via manual `workflow_dispatch`). It runs
  `stage-pages.py`, checks out `FWBG/FWBG.github.io` using the
  `FWBG_PAGES_TOKEN` secret, `rsync --delete`s the staged output into that
  repo's `collections/` directory, and commits + pushes as
  `fwbg-pages-bot`.

## Publish flow, end to end

1. Edit `README.md` (and/or `styles.css`, `fwbg/tokens`, `fwbg/assets`) and
   push to `main`.
2. `publish.yml` fires, runs `stage-pages.py --out _stage/collections`.
3. The staged folder is synced (with deletes) into
   `FWBG/FWBG.github.io`'s `collections/` directory and pushed there
   directly — there's no PR/review step on the pages repo side.
4. The live page is `collections/index.html` on `FWBG.github.io`, i.e.
   whatever path that repo serves `collections/` at (e.g.
   `https://fwbg.github.io/collections/`).

## Things to keep in mind when editing

- Because `README.md` is rendered verbatim into the public page, don't add
  maintainer-only notes there — this file (or a future `CONTRIBUTING.md`)
  is the place for that instead.
- Any HTML written directly in `README.md` (e.g. `<a target="_blank">`)
  gets sanitized by GitHub's markdown API and then selectively restored by
  `restore_new_tab_links()` in `stage-pages.py` — only the `target`/`rel`
  attributes on `http(s)` links are patched back in. Other raw HTML
  attributes will still get stripped.
- The publish job pushes straight to `FWBG/FWBG.github.io` on every merge
  to `main` here — there's no staging/preview step, so treat `main` in
  this repo as effectively production for the collections page.
