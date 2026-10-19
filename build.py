#!/usr/bin/env python3
"""Build the Oroboro Press website.

    python3 build.py

Reads the page content in site/pages/<lang>/<page>.html, wraps each one in the
shared layout (head, top bar, footer) and writes the finished site to docs/,
which GitHub Pages serves. Static files in site/static/ are copied as they are.

Links between pages are written as tokens in the content: href="@crumbs" or
href="@about#contatti". The build turns them into the right address for the
page's language, so the two languages can never point at each other by mistake.
"""
import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "site"
OUT = ROOT / "docs"

# Change to "https://oroboropress.com" and PREVIEW = False when the site goes live.
BASE = "https://anteprima.oroboropress.com"
PREVIEW = True

LANGS = ("en", "it")

# page id -> address and title in each language
ROUTES = {
    "home":   {"en": ("/", "Oroboro Press"),
               "it": ("/it/", "Oroboro Press")},
    "crumbs": {"en": ("/books/crumbs/", "Crumbs · Oroboro Press"),
               "it": ("/it/libri/crumbs/", "Crumbs · Oroboro Press")},
    "buy":    {"en": ("/buy/", "Buy Crumbs · Oroboro Press"),
               "it": ("/it/acquista/", "Acquista Crumbs · Oroboro Press")},
    "about":  {"en": ("/about/", "About · Oroboro Press"),
               "it": ("/it/chi-siamo/", "Chi siamo · Oroboro Press")},
    "nicola": {"en": ("/authors/nicola-nuti/", "Nicola Nuti · Oroboro Press"),
               "it": ("/it/autori/nicola-nuti/", "Nicola Nuti · Oroboro Press")},
}

DESCRIPTIONS = {
    "en": "Oroboro Press, an independent publisher in San Francisco, California. Memoir and fiction as eBooks and audiobooks, in Italian and English.",
    "it": "Oroboro Press, casa editrice indipendente di San Francisco, California. Memorie e narrativa in eBook e audiolibro, in italiano e in inglese.",
}

T = {  # words used by the layout
    "en": {
        "nav_label": "Main", "home_label": "Oroboro Press, home", "bag": "Bag", "menu": "Menu",
        "nav": [("@crumbs", "Books"), ("@home#audiolibro", "Audiobooks"), ("@nicola", "Authors"),
                ("@home#diario", "Journal"), ("@about", "About")],
        "switch": "Italiano", "switch_lang": "it",
        "note": "Prices include applicable taxes. eBooks are DRM-free EPUB files; audiobooks are MP3. Payments are handled by [PAYMENT PLATFORM].",
        "cols": [
            ("Books", [("@crumbs", "Crumbs"), ("@home#avvisami", "L'inatteso"), ("@home#audiolibro", "Audiobooks")]),
            ("Shop", [("@buy", "Store"), ("@about#aiuto", "How to read an EPUB"), ("@about#aiuto", "Download help")]),
            ("Oroboro", [("@about", "About"), ("@about#stampa", "Press"), ("@about#contatti", "Contact")]),
            ("Elsewhere", [("#", "Amazon Kindle"), ("#", "Spotify"), ("#", "Audible")]),
        ],
        "legal": [("#", "Privacy"), ("#", "Terms of sale")],
        "copyright": "Copyright © 2026 Oroboro Press, San Francisco, California.",
        "soon": "Coming soon",
        "not_found": ("Page not found.", "The page you were looking for isn't here. It may have moved when the site changed.", "Go to the home page"),
    },
    "it": {
        "nav_label": "Principale", "home_label": "Oroboro Press, home", "bag": "Borsa", "menu": "Menu",
        "nav": [("@crumbs", "Libri"), ("@home#audiolibro", "Audiolibri"), ("@nicola", "Autori"),
                ("@home#diario", "Diario"), ("@about", "Chi siamo")],
        "switch": "English", "switch_lang": "en",
        "note": "I prezzi includono le imposte. Gli eBook sono in formato EPUB senza DRM; gli audiolibri in MP3. Il pagamento è gestito da [PIATTAFORMA DI PAGAMENTO].",
        "cols": [
            ("Libri", [("@crumbs", "Crumbs"), ("@home#avvisami", "L'inatteso"), ("@home#audiolibro", "Audiolibri")]),
            ("Acquista", [("@buy", "Negozio"), ("@about#aiuto", "Come leggere un EPUB"), ("@about#aiuto", "Aiuto con i download")]),
            ("Oroboro", [("@about", "Chi siamo"), ("@about#stampa", "Stampa"), ("@about#contatti", "Contatti")]),
            ("Altrove", [("#", "Amazon Kindle"), ("#", "Spotify"), ("#", "Audible")]),
        ],
        "legal": [("#", "Privacy"), ("#", "Condizioni di vendita")],
        "copyright": "Copyright © 2026 Oroboro Press, San Francisco, California.",
        "soon": "Presto disponibile",
        "not_found": ("Pagina non trovata.", "La pagina che cercavi non è qui. Forse è stata spostata quando il sito è cambiato.", "Vai alla home"),
    },
}

BAG_ICON = ('<svg width="15" height="16" viewBox="0 0 15 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
            '<path d="M2 5h11l-.8 10H2.8z"></path><path d="M5 5V3.8a2.5 2.5 0 0 1 5 0V5"></path></svg>')

MENU_ICON = ('<svg width="18" height="12" viewBox="0 0 18 12" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">'
             '<path d="M0 1h18M0 6h18M0 11h18"></path></svg>')


def url(page, lang, frag=""):
    return ROUTES[page][lang][0] + frag


def resolve(text, lang):
    """Turn @page and @page#fragment tokens into this language's addresses."""
    def sub(m):
        page, frag = m.group(1), m.group(2) or ""
        if page not in ROUTES:
            raise SystemExit(f"Unknown page token @{page}")
        return f'href="{url(page, lang, frag)}"'
    text = re.sub(r'href="@([a-z]+)(#[^"]*)?"', sub, text)
    # links to content that doesn't exist yet: inactive, with a tooltip
    soon = html.escape(T[lang]["soon"], quote=True)
    return re.sub(r'<a href="#"(?![^>]*aria-disabled)', f'<a href="#" aria-disabled="true" title="{soon}"', text)


def head(page, lang):
    path, title = ROUTES[page][lang] if page else ("/404.html", T[lang]["not_found"][0])
    alts = ""
    if page:
        alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{url(page, l)}">\n' for l in LANGS)
        alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{url(page, "en")}">\n'
        alts += f'<link rel="canonical" href="{BASE}{path}">\n'
    robots = '<meta name="robots" content="noindex, nofollow">\n' if PREVIEW else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(DESCRIPTIONS[lang], quote=True)}">
{alts}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/img/icon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="/css/site.css">
</head>
"""


def topbar(page, lang):
    t = T[lang]
    links = "".join(
        f'<a class="nav-link" href="{href}"{" aria-current=\"page\"" if href == "@" + str(page) else ""}>{label}</a>\n'
        for href, label in t["nav"])
    other = t["switch_lang"]
    switch_to = url(page, other) if page else url("home", other)
    return resolve(f"""<nav class="topbar" aria-label="{t['nav_label']}">
<div class="topbar-inner">
<a class="brand" href="@home" aria-label="{t['home_label']}"><img src="/img/logo.png" alt=""><span>OROBORO PRESS</span></a>
{links}<a class="nav-link lang" href="{switch_to}" hreflang="{other}" lang="{other}">{t['switch']}</a>
<a class="nav-bag" href="@buy" aria-label="{t['bag']}">{BAG_ICON}</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-label="{t['menu']}">{MENU_ICON}</button>
</div>
</nav>
""", lang)


def footer(lang):
    t = T[lang]
    cols = "".join(
        f'<div><h2>{title}</h2><ul>' + "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in links) + "</ul></div>\n"
        for title, links in t["cols"])
    legal = " · ".join(f'<a href="{h}">{l}</a>' for h, l in t["legal"])
    return resolve(f"""<footer class="footer">
<div class="footer-inner">
<div class="footer-brand"><img src="/img/logo.png" alt=""><span>OROBORO PRESS</span></div>
<p class="footer-note">{t['note']}</p>
<div class="footer-cols">
{cols}</div>
<div class="footer-legal"><span>{t['copyright']}</span><span>{legal}</span></div>
</div>
</footer>
""", lang)


# the language link keeps the reader on the same section (#formati, #autore …);
# on phones the menu button opens and closes the list of links
KEEP_PLACE = """<script>
document.querySelectorAll('a.lang').forEach(function (a) {
  a.addEventListener('click', function () { if (location.hash) a.href = a.href.split('#')[0] + location.hash; });
});
document.querySelectorAll('.nav-toggle').forEach(function (b) {
  var bar = b.closest('.topbar');
  b.addEventListener('click', function () {
    var open = bar.classList.toggle('open');
    b.setAttribute('aria-expanded', open);
  });
  bar.querySelectorAll('.nav-link').forEach(function (a) {
    a.addEventListener('click', function () { bar.classList.remove('open'); b.setAttribute('aria-expanded', false); });
  });
});
</script>
"""


def page_html(page, lang, content):
    return (head(page, lang) + '<body>\n<div class="page">\n' + topbar(page, lang)
            + resolve(content, lang) + "\n" + footer(lang) + "</div>\n" + KEEP_PLACE + "</body>\n</html>\n")


def not_found():
    en, it = T["en"]["not_found"], T["it"]["not_found"]
    content = f"""<section style="text-align: center; padding: 120px 22px">
<h1 style="margin: 0; font-size: 56px; line-height: 1.05; font-weight: 700; letter-spacing: -0.03em">{en[0]}</h1>
<p style="margin: 14px auto 0; max-width: 560px; font-size: 21px; color: #6E6E73">{en[1]}</p>
<p style="margin: 24px 0 0; font-size: 19px"><a href="@home">{en[2]}</a></p>
<p lang="it" style="margin: 48px auto 0; max-width: 560px; font-size: 17px; color: #6E6E73">{it[1]} <a href="/it/">{it[2]}</a></p>
</section>"""
    return page_html(None, "en", content)


def sitemap():
    rows = []
    for page in ROUTES:
        for lang in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}{url(page, l)}"/>' for l in LANGS)
            rows.append(f"<url><loc>{BASE}{url(page, lang)}</loc>{alts}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)
    for page in ROUTES:
        for lang in LANGS:
            src = SRC / "pages" / lang / f"{page}.html"
            target = OUT / url(page, lang).strip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page_html(page, lang, src.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"  {url(page, lang)}")
    (OUT / "404.html").write_text(not_found(), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"Built {len(ROUTES) * len(LANGS)} pages + 404 + sitemap into docs/")


if __name__ == "__main__":
    main()
