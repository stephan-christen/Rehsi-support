#!/usr/bin/env python3
"""Checks the support site before it is merged or published.

    python3 scripts/check_site.py          # structure, links, nothing loaded from third parties
    python3 scripts/check_site.py --live   # also fails while a placeholder is still unfilled

The site promises that it loads nothing from third parties, so any stylesheet, script,
image, font or frame that is not a relative path fails the check. Ordinary links to
other sites are fine: a link is only followed when the reader chooses to.
"""

import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = [
    "index.html",
    "de/datenschutz/index.html",
    "de/hilfe/index.html",
    "fr/confidentialite/index.html",
    "fr/aide/index.html",
    "en/privacy/index.html",
    "en/help/index.html",
]

# Filled in by the owner before the site goes live (see README).
PLACEHOLDERS = re.compile(
    r"\[(Name|Adresse|E-Mail|Datum|Nom|adresse|e-mail|date|address|email)\]"
)

# Attributes that make the browser fetch something on its own.
LOADING = {
    "link": "href",
    "script": "src",
    "img": "src",
    "iframe": "src",
    "source": "src",
    "video": "src",
    "audio": "src",
    "object": "data",
    "embed": "src",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.loads = []
        self.links = []
        self.lang = None
        self.has_csp = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "meta" and a.get("http-equiv", "").lower() == "content-security-policy":
            self.has_csp = True
        link_loads = tag != "link" or a.get("rel") in ("stylesheet", "icon", "preload", "modulepreload")
        if tag in LOADING and a.get(LOADING[tag]) and link_loads:
            self.loads.append((tag, a[LOADING[tag]]))
        if "style" in a and "url(" in a["style"]:
            self.loads.append((tag, "inline style url()"))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])


def is_relative(url):
    return not re.match(r"^([a-z][a-z0-9+.-]*:|//)", url, re.I)


def main():
    live = "--live" in sys.argv
    problems = []

    for rel in PAGES:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)

        if not page.lang:
            problems.append(f"{rel}: <html> has no lang")
        if not page.has_csp:
            problems.append(f"{rel}: no Content-Security-Policy")
        for tag, url in page.loads:
            if not is_relative(url):
                problems.append(f"{rel}: <{tag}> loads {url} from outside the site")
        for href in page.links:
            if href.startswith("mailto:") or not is_relative(href):
                continue
            target = (path.parent / href.split("#")[0]).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                problems.append(f"{rel}: broken link {href}")
        if page.lang == "de" and "ß" in text:
            problems.append(f"{rel}: ß in a Swiss German page")
        if live:
            for m in sorted(set(PLACEHOLDERS.findall(text))):
                problems.append(f"{rel}: placeholder [{m}] not filled in")

    for css in ROOT.glob("assets/**/*.css"):
        for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", css.read_text(encoding="utf-8")):
            if not is_relative(url):
                problems.append(f"{css.relative_to(ROOT)}: loads {url} from outside the site")
        if re.search(r"@import", css.read_text(encoding="utf-8")):
            problems.append(f"{css.relative_to(ROOT)}: @import")

    for p in problems:
        print(p)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
