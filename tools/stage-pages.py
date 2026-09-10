#!/usr/bin/env python3
"""Stage README.md as a styled page for GitHub Pages publishing.

Converts the README through GitHub's markdown API (no markdown-parsing
dependency needed) and assembles a self-contained folder: the rendered
index.html, styles.css, and a copy of fwbg/tokens + fwbg/assets — so the
published page never depends on the hub site's own design system.

    python3 tools/stage-pages.py --out _stage/collections

Set GITHUB_TOKEN to authenticate the markdown API call (raises the rate
limit); it works unauthenticated too. The result is meant to be synced into
a folder of the same name at the root of the FWBG.github.io repo (e.g. via
rsync --delete in CI).
"""

import argparse
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_SLUG = "FWBG/collections"

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>FWBG Collections</title>
<link rel="stylesheet" href="styles.css" />
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="https://fwbg.github.io/" aria-label="Fort Worth Botanic Garden home">
      <img src="fwbg/assets/logo-primary.svg" alt="Fort Worth Botanic Garden" />
    </a>
  </div>
</header>
<main>
<div class="container prose">
__BODY__
</div>
</main>
<footer class="site-footer">
  <div class="container">
    <p>&copy; 2026 Fort Worth Botanic Garden.</p>
  </div>
</footer>
</body>
</html>
"""


def render_markdown(text: str) -> str:
    headers = {
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        "https://api.github.com/markdown",
        data=json.dumps({"text": text, "mode": "gfm", "context": REPO_SLUG}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def stage(out_dir: Path) -> None:
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        sys.exit(f"{readme} not found")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    body = render_markdown(readme.read_text(encoding="utf-8"))
    page = PAGE_TEMPLATE.replace("__BODY__", body)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    shutil.copy2(REPO_ROOT / "styles.css", out_dir / "styles.css")
    shutil.copytree(REPO_ROOT / "fwbg" / "tokens", out_dir / "fwbg" / "tokens")
    shutil.copytree(REPO_ROOT / "fwbg" / "assets", out_dir / "fwbg" / "assets")

    print(f"staged {out_dir}")
    for p in sorted(out_dir.rglob("*")):
        if p.is_file():
            print(" ", p.relative_to(out_dir))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", type=Path, default=Path("_stage/collections"), help="staging output directory")
    args = p.parse_args()
    stage(args.out)


if __name__ == "__main__":
    main()
