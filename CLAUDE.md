# fwbg_collections

This repo is the *source* for the FWBG digital collections page. It is not a
website itself — `README.md` is treated as the page content, and CI renders
it into a static page published on a different repo entirely.

## Purpose and sibling repos

This repo is the source for **one public page**: a curated directory of links
to where FWBG and BRIT collections live (Garden Explorer, TORCH portal, UNT
Portal to Texas History, library catalog, etc.). It holds **no collection
data**, only links. Several sibling repos under `/media/jbest/DATA3-6TB/BRIT_git/`
have similar names or overlapping subject matter:

| Repo | What it is | Relation to this repo |
|---|---|---|
| `FWBG.github.io` | The hub website | This repo's output is synced into its `collections/` directory |
| `fwbg_collection_data` | Unifying collection data across FWBG and BRIT (early scaffold; schema, mappings, data) | Differs by one letter. It holds data; this repo only links out |
| `fwbg_living_collections_data` | IrisBG export tooling and weekly raw CSV snapshots | Source data, not published here; the page only links to Garden Explorer |
| `begonia_image_dataset` | Photographing Begonia plants and publishing image data packages with DOIs | Separate project; this page links to the Begonia site |
| `living_collections` | Static dashboards for the living collections | Separate site content; also carries its own copy of `fwbg/` |
| `begonia_demo`, `begonia-db`, `begonia_frictionless_test` | Begonia experiments | Unrelated to this page |
| `fwbg-design-system`, `fwbg-ds-toolkit`, `fwbg-brand-assets` | Visual identity: tokens/components, DS build scripts, brand source files | The `fwbg/` directory here is a deliberate copy so the page has no dependency on the hub site; it is not the source of truth |

If a request is about collection data, schemas, IrisBG exports, or Begonia
images, it probably belongs in one of those repos, not this one.

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
- **Write links as bare URLs** (`Label - https://example.org/`), not as raw
  `<a href="URL" target="_blank">URL</a>` HTML. GitHub's markdown API
  autolinks the bare URL, and `restore_new_tab_links()` in `stage-pages.py`
  then adds `target="_blank" rel="noopener noreferrer"` to every external
  `http(s)` link, so no extra markup is needed. Wrapping a URL in raw `<a>`
  HTML makes the API emit a duplicate empty anchor (an unnamed tab stop that
  fails Lighthouse's link-name audit; see PR #2).
- Any other HTML written directly in `README.md` gets sanitized by GitHub's
  markdown API; only the `target`/`rel` attributes on `http(s)` links are
  patched back in. Other raw HTML attributes will still get stripped.
- Use title-case labels such as `BRIT Mycology Collection`, matching the
  existing entries.
- The publish job pushes straight to `FWBG/FWBG.github.io` on every merge
  to `main` here — there's no staging/preview step, so treat `main` in
  this repo as effectively production for the collections page.
