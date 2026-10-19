# Oroboro Press — website

Preview of the Oroboro Press site (Apple Store style). Static HTML, no build step yet.

Live at **https://anteprima.oroboropress.com** (preview, `noindex`). The real site will move to `oroboropress.com`.

## Pages

- `index.html`: home
- `crumbs.html`: the *Crumbs* book page
- `acquista.html`: buy page with format picker (small inline script)
- `nicola-nuti.html`: author page (bio, timeline, books, archive placeholder)
- `chi-siamo.html`: about, help with eBooks/audio, contacts, press
- `en/index.html`: English landing page
- `img/`: logo (circular, OROBORO on top, PRESS below) and favicon

Prices, cover and bio are placeholders (`[PREZZO]`, `[MESE]` …).

## Hosting

Same as sailingoroboro.com: GitHub Pages from `main` / root. The `CNAME` file sets the custom domain.

DNS (Cloudflare, zone `oroboropress.com`):

| Type | Name | Target | Proxy |
|---|---|---|---|
| CNAME | `anteprima` | `fpugliano.github.io` | DNS only (grey cloud) |

When the real site goes live at the root domain: change `CNAME` to `oroboropress.com`, add a CNAME record for `@` → `fpugliano.github.io` (Cloudflare flattens it) and `www` → `fpugliano.github.io`, and remove `robots.txt` and the `noindex` meta tags.

## Local preview

```
python3 -m http.server 8080
```

then open http://localhost:8080

## Editing

From 19 October 2026 the HTML files here are the source of truth: edit them directly. (The first version was converted from the design mockups; those are no longer kept in sync.)

Pages: `index.html`, `crumbs.html`, `acquista.html`, `chi-siamo.html` (about, help, contacts, press), `en/index.html` (English landing). Links to content that doesn't exist yet are `href="#"` with `aria-disabled="true"` and the tooltip "Presto disponibile".
