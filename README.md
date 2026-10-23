# Rehsi support site

The privacy policy and help pages for the Rehsi iPhone app, in German, French and English, served by GitHub Pages at `https://stephan-christen.github.io/Rehsi-support/`.

| | Deutsch | Français | English |
|---|---|---|---|
| Privacy policy | [`de/datenschutz/`](de/datenschutz/index.html) | [`fr/confidentialite/`](fr/confidentialite/index.html) | [`en/privacy/`](en/privacy/index.html) |
| Help | [`de/hilfe/`](de/hilfe/index.html) | [`fr/aide/`](fr/aide/index.html) | [`en/help/`](en/help/index.html) |

The root page links to all six. App Store Connect takes one privacy policy URL and one support URL per localization, so de-DE, fr-FR and en-US each get their own language's pages.

## Loads nothing from third parties

Plain HTML and one local stylesheet: no analytics, no web fonts, no scripts. Every page carries a Content-Security-Policy that only allows the site's own stylesheet and images, so the browser itself refuses anything else. `.nojekyll` makes Pages serve the files as they are, without a Jekyll theme.

## The responsible person's details

Name, address and email live in **`.env-live`** in the repository root, which git ignores:

```
NAME=…
ADDRESS=…
EMAIL=…
```

Write them into the pages with:

```bash
python3 scripts/fill_details.py
```

Each detail is marked in the pages with `data-fill="name"`, `"address"` or `"email"` (the email also inside its `mailto:` link), so the script can be run again whenever `.env-live` changes. The filled-in pages are what gets committed and published. The details are public on the site either way; `.env-live` only keeps them out of the repository until you choose to publish them.

The policy's date (*Stand*, *État*, *Last updated*) is written directly in each privacy page. Change it whenever what the policy says changes.

## Checks

```bash
python3 scripts/check_site.py
```

Checks that every page exists, has a language and a Content-Security-Policy, that internal links resolve, that nothing is loaded from outside the site, and that the German pages use Swiss spelling (no `ß`). Before going live, run it with `--live`, which also fails while a detail is still a placeholder:

```bash
python3 scripts/check_site.py --live
```

## Going live

1. Run `scripts/fill_details.py`, then the check with `--live`.
2. Commit the pages, and merge them into `main`. Pages deploys `main` (`/`), so the site updates a minute later.
3. Put the URLs into App Store Connect and the app's About screen.

## Keeping it true to the app

The privacy policy must say the same as the App Privacy answers in App Store Connect and the app's privacy manifest. The help pages name the app's screens and buttons as the current build shows them. When a change to the app alters what leaves the phone, a permission, or a screen named here, these pages change in the same release.
