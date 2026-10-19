# Oroboro Press — website

Bilingual site (English default, Italian under `/it/`). Static HTML built by a small Python script, hosted on GitHub Pages, DNS on Cloudflare.

Live preview: **https://anteprima.oroboropress.com** (not indexed by search engines yet).

## How it's organised

```
build.py              builds the site into docs/
site/pages/en/*.html  English content, one file per page (no menu or footer)
site/pages/it/*.html  Italian content, same file names
site/static/          files copied as they are: css/, img/, favicons, CNAME
docs/                 the finished site that GitHub Pages serves (generated, don't edit)
```

The top bar, footer and `<head>` are written once in `build.py`, in both languages.

| Page id | English | Italian |
|---|---|---|
| `home` | `/` | `/it/` |
| `crumbs` | `/books/crumbs/` | `/it/libri/crumbs/` |
| `buy` | `/buy/` | `/it/acquista/` |
| `about` | `/about/` | `/it/chi-siamo/` |
| `nicola` | `/authors/nicola-nuti/` | `/it/autori/nicola-nuti/` |

Every page links to its twin in the other language (the language switch keeps the reader's section), and carries `hreflang` and canonical tags. `404.html` and `sitemap.xml` are generated too.

## Editing

1. Change the page in **both** `site/pages/en/` and `site/pages/it/`.
2. Link to other pages with tokens, not addresses: `href="@crumbs"`, `href="@about#contatti"`. The build turns them into the right address for each language. `href="#"` marks something not available yet (shown as inactive, "Coming soon").
3. Images: `/img/...`.
4. `python3 build.py`, check with `cd docs && python3 -m http.server 8080` → http://localhost:8080
5. Commit and push (including `docs/`).

To add a page: add it to `ROUTES` in `build.py` and create `site/pages/en/<id>.html` and `site/pages/it/<id>.html`.

## Going live on oroboropress.com

In `build.py` set `BASE = "https://oroboropress.com"` and `PREVIEW = False` (removes `noindex`, opens `robots.txt`, publishes the sitemap). Change `site/static/CNAME` to `oroboropress.com`. In Cloudflare add CNAME records `@` and `www` → `fpugliano.github.io` (DNS only), then rebuild and push.
