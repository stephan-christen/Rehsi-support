#!/usr/bin/env python3
"""Writes the responsible person's details from .env-live into the pages.

    python3 scripts/fill_details.py

.env-live sits in the repository root, is ignored by git, and holds three lines:

    NAME=…
    ADDRESS=…
    EMAIL=…

Each detail is marked in the pages with data-fill="name", "address" or "email", so the
script can be run again whenever .env-live changes: it replaces whatever is there now.
It prints which pages it changed, never the values themselves.
"""

import html
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV = ROOT / ".env-live"

PAGES = [
    "de/datenschutz/index.html",
    "de/hilfe/index.html",
    "fr/confidentialite/index.html",
    "fr/aide/index.html",
    "en/privacy/index.html",
    "en/help/index.html",
]

REQUIRED = ("NAME", "ADDRESS", "EMAIL")


def read_env(path):
    values = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^export\s+", "", line)
        key, sep, value = line.partition("=")
        if not sep:
            sys.exit(f"{path.name} line {number}: expected KEY=value")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def main():
    if not ENV.exists():
        sys.exit(f"{ENV.name} not found in {ROOT}")
    env = read_env(ENV)
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        sys.exit(f"{ENV.name}: {', '.join(missing)} missing or empty")
    email = env["EMAIL"]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        sys.exit(f"{ENV.name}: EMAIL does not look like an email address")

    name = html.escape(env["NAME"], quote=False)
    address = html.escape(env["ADDRESS"], quote=False)
    link = (f'<a data-fill="email" href="mailto:{urllib.parse.quote(email, safe="@.+-_")}">'
            f'{html.escape(email, quote=False)}</a>')

    for rel in PAGES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        new, emails = re.subn(r'<a data-fill="email" href="mailto:[^"]*">.*?</a>',
                              lambda _: link, text)
        if emails == 0:
            sys.exit(f"{rel}: no data-fill=\"email\" link found")
        new = re.sub(r'(<span data-fill="name">).*?(</span>)',
                     lambda m: m[1] + name + m[2], new)
        new = re.sub(r'(<span data-fill="address">).*?(</span>)',
                     lambda m: m[1] + address + m[2], new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"updated {rel}")
        else:
            print(f"unchanged {rel}")


if __name__ == "__main__":
    main()
