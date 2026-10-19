# Oroboro Press — website

Preview of the Oroboro Press site (Apple Store style). Static HTML, no build step yet.

Live at **https://anteprima.oroboropress.com** (preview, `noindex`). The real site will move to `oroboropress.com`.

## Pages and languages

English is the default, at the root; Italian lives in `it/`. Each page links to its twin in the other language, and carries `hreflang` tags for search engines.

| English (root) | Italian (`it/`) | What |
|---|---|---|
| `index.html` | `it/index.html` | Home |
| `crumbs.html` | `it/crumbs.html` | The *Crumbs* book page |
| `acquista.html` | `it/acquista.html` | Buy page with format picker |
| `chi-siamo.html` | `it/chi-siamo.html` | About, help, contacts, press |
| `nicola-nuti.html` | `it/nicola-nuti.html` | Author page: bio, timeline, archive preview |

- `img/`: logo, iPhone mockup, icons. Favicons and `site.webmanifest` at the root.
- Prices, cover and bio are placeholders (`[PREZZO]`, `[MESE]` …).

### How to edit

1. Edit the **Italian** page in `it/`.
2. Run `python3 tools/translate_en.py`. It rebuilds the English pages at the root from the Italian ones, using the translations listed in the script. If you added a new sentence, it stops and lists what needs translating: add it to the `EN` dictionary and run again.
3. Commit and push.

## Hosting

Same as sailingoroboro.com: GitHub Pages from `main` / root. The `CNAME` file sets the custom domain.

DNS (Cloudflare, zone `oroboropress.com`):

| Type | Name | Target | Proxy |
|---|---|---|---|
| CNAME | `anteprima` | `fpugliano.github.io` | DNS only (grey cloud) |

When the real site goes live at the root domain: change `CNAME` to `oroboropress.com` and `BASE` in `tools/translate_en.py`, add a CNAME record for `@` → `fpugliano.github.io` (Cloudflare flattens it) and `www` → `fpugliano.github.io`, and remove `robots.txt` and the `noindex` meta tags.

## Local preview

```
python3 -m http.server 8080
```

then open http://localhost:8080
