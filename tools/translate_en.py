"""Build the English pages (site root) from the Italian pages in it/.

Edit the Italian pages in it/, then run from anywhere:
    python3 tools/translate_en.py
Every visible Italian string needs an entry in EN below; the script stops and
lists any it can't find, so a new sentence never slips through untranslated.
"""
import re
import sys
from pathlib import Path

# change to https://oroboropress.com when the site moves to the main domain
BASE = "https://anteprima.oroboropress.com"

PAGES = ["index.html", "crumbs.html", "acquista.html", "chi-siamo.html", "nicola-nuti.html"]

TITLES = {
    "Oroboro Press": "Oroboro Press",
    "Crumbs · Oroboro Press": "Crumbs · Oroboro Press",
    "Acquista Crumbs · Oroboro Press": "Buy Crumbs · Oroboro Press",
    "Chi siamo · Oroboro Press": "About · Oroboro Press",
    "Nicola Nuti · Oroboro Press": "Nicola Nuti · Oroboro Press",
}

EN = {
    # navigation, footer, shared
    "Libri": "Books", "Audiolibri": "Audiobooks", "Autori": "Authors", "Diario": "Journal",
    "Chi siamo": "About", "Principale": "Main", "Borsa": "Bag", "Presto disponibile": "Coming soon",
    "Negozio": "Store", "Come leggere un EPUB": "How to read an EPUB", "Aiuto con i download": "Download help",
    "Stampa": "Press", "Contatti": "Contact", "Altrove": "Elsewhere", "Privacy": "Privacy",
    "Condizioni di vendita": "Terms of sale", "· Italia": "· English",
    "Copyright © 2026 Oroboro Press, San Francisco, California.": "Copyright © 2026 Oroboro Press, San Francisco, California.",
    "Copyright © 2026 Oroboro Press, San Francisco, California. Prima edizione: SMITH Editore, 2024.": "Copyright © 2026 Oroboro Press, San Francisco, California. First edition: SMITH Editore, 2024.",
    "Copyright © 2026 Oroboro Press, San Francisco, California. Contatti:": "Copyright © 2026 Oroboro Press, San Francisco, California. Contact:",
    "I prezzi includono l'IVA. Gli eBook sono in formato EPUB senza DRM; gli audiolibri in MP3. Il pagamento è gestito da [PIATTAFORMA DI PAGAMENTO].":
        "Prices include applicable taxes. eBooks are DRM-free EPUB files; audiobooks are MP3. Payments are handled by [PAYMENT PLATFORM].",
    "nome@esempio.it": "name@example.com", "Email": "Email",
    # home
    "Crumbs arriva a [MESE] in eBook e audiolibro.": "Crumbs arrives in [MONTH] as an eBook and audiobook.",
    "Avvisami quando esce": "Notify me when it's out",
    "Libri da leggere e da ascoltare.": "Books to read and to listen to.",
    "Casa editrice indipendente a San Francisco, California. Libri in italiano e in inglese.": "Independent publisher in San Francisco, California. Books in Italian and English.",
    "Firenze, l'arte, la memoria. A briciole.": "Florence, art, memory. In crumbs.",
    "Il nuovo libro di Nicola Nuti.": "The new book by Nicola Nuti.",
    "Scopri di più": "Learn more", "Acquista": "Buy",
    "[Opera: «Il cane»]": "[Artwork: “Il cane”]",
    "Audiolibro": "Audiobook",
    "Ascoltalo. Dalla sua voce.": "Listen. In his own voice.",
    "Ventidue racconti letti da Nicola Nuti. Circa due ore, da scaricare in MP3 o da ascoltare su Spotify e Audible.":
        "Twenty-two stories read by Nicola Nuti. About two hours, as an MP3 download or on Spotify and Audible.",
    "Ascolta un estratto": "Listen to a sample",
    "Il prossimo libro di Nicola Nuti.": "Nicola Nuti's next book.",
    "In scrittura. Ti avvisiamo noi.": "Being written. We'll let you know.",
    "Avvisami": "Notify me", "Leggi gratis": "Read for free",
    "Le prime pagine di Crumbs.": "The first pages of Crumbs.",
    "Scarica l'estratto": "Download the sample",
    "[Prime righe del racconto]": "[First lines of the story]",
    "In arrivo nel 2027": "Coming in 2027",
    "Il diario": "The journal", "Come nasce un libro, da vicino.": "How a book is made, up close.",
    "Firenze, 4 novembre 1966": "Florence, 4 November 1966",
    "Chi è chi in Crumbs": "Who's who in Crumbs",
    "Registrare un audiolibro in casa": "Recording an audiobook at home",
    "Copertina di Crumbs, segnaposto": "Crumbs cover, placeholder",
    "L'audiolibro di Crumbs su iPhone": "The Crumbs audiobook on iPhone",
    # Crumbs page
    "Panoramica": "Overview", "Racconti": "Stories", "Formati": "Formats", "L'autore": "The author",
    "Novità Oroboro Press": "New from Oroboro Press",
    "Ventidue ricordi. Una città. Mezzo secolo d'arte.": "Twenty-two memories. One city. Half a century of art.",
    "eBook e audiolibro da € [PREZZO]": "eBook and audiobook from [PRICE]",
    "Leggi le prime pagine": "Read the first pages",
    "Chi incontrerai.": "Who you'll meet.",
    "Scrittore": "Writer", "Pittore": "Painter", "Regista": "Filmmaker", "Poeta": "Poet", "Curatore": "Curator",
    "[Immagine]": "[Image]",
    "Nel racconto «Io e Pratolini»": "In the story “Io e Pratolini”",
    "Nel racconto «Giuro, non lo conoscevo!»": "In the story “Giuro, non lo conoscevo!”",
    "Nel racconto «[TITOLO]»": "In the story “[TITLE]”",
    "racconti brevi, più una prefazione": "short stories, plus a preface",
    "~2 ore": "~2 hours",
    "di audiolibro, letto dall'autore": "of audio, read by the author",
    "l'alluvione che attraversa tutto il libro": "the flood that runs through the whole book",
    "Scegli come leggerlo.": "Choose how to read it.",
    "EPUB senza DRM": "DRM-free EPUB", "€ [PREZZO]": "[PRICE]",
    "Download immediato": "Instant download", "Con le immagini delle opere": "With images of the artworks",
    "Conviene": "Best value", "eBook + Audiolibro": "eBook + Audiobook", "Entrambi i formati": "Both formats",
    "Leggi e ascolta": "Read and listen", "EPUB e MP3": "EPUB and MP3", "Un unico acquisto": "One purchase",
    "MP3, circa 2 ore": "MP3, about 2 hours", "Letto da Nicola Nuti": "Read by Nicola Nuti",
    "Ogni racconto è una traccia": "Each story is a track", "Da ascoltare offline": "Listen offline",
    "Preferisci il tuo negozio? Crumbs è anche su": "Prefer your usual store? Crumbs is also on",
    "e": "and",
    "[Ritratto]": "[Portrait]",
    "[Biografia breve, tre o quattro righe, scritta da Nicola.]": "[Short bio, three or four lines, written by Nicola.]",
    "Biografia e archivio": "Biography and archive",
    "Ritratto dell'autore, segnaposto": "Author portrait, placeholder",
    # buy page
    "Novità": "New", "Acquista Crumbs": "Buy Crumbs", "[«Il cane»]": "[“Il cane”]",
    "Leggi e ascolta, in un solo acquisto.": "Read and listen, in one purchase.",
    "Formato.": "Format.", "Quale preferisci?": "Which do you prefer?",
    "EPUB senza DRM, con le immagini delle opere": "DRM-free EPUB, with images of the artworks",
    "MP3, circa 2 ore, letto da Nicola Nuti": "MP3, about 2 hours, read by Nicola Nuti",
    "Tutti e due, a un prezzo ridotto": "Both, at a reduced price",
    "Lingua.": "Language.", "In che lingua?": "Which language?",
    "Italiano": "Italian", "Disponibile": "Available",
    "Crumbs · eBook + Audiolibro · Italiano": "Crumbs · eBook + Audiobook · Italian",
    "IVA inclusa. Download immediato dopo il pagamento.": "Taxes included. Instant download after payment.",
    "Aggiungi alla borsa": "Add to bag",
    "Subito tuo.": "Yours right away.",
    "Ricevi il link per scaricarlo via email, e puoi riscaricarlo quando vuoi.": "You get a download link by email, and can download it again any time.",
    "Paga come preferisci.": "Pay your way.",
    "Carta, Apple Pay, Google Pay o PayPal.": "Card, Apple Pay, Google Pay or PayPal.",
    "Serve aiuto?": "Need help?", "Scrivici": "Write to us",
    "e ti spieghiamo come aprire il file sul tuo Kindle o telefono.": "and we'll show you how to open the file on your Kindle or phone.",
    "Copertina di Crumbs": "Crumbs cover", "Audiolibro di Crumbs su iPhone": "Crumbs audiobook on iPhone",
    # about page
    "Chi siamo.": "About us.",
    "Una piccola casa editrice. Pochi libri, seguiti uno per uno.": "A small publishing house. A few books, each one closely looked after.",
    "Cosa facciamo": "What we do",
    "Oroboro Press pubblica memorie e narrativa in eBook e audiolibro, in italiano e in inglese. È nata nel 2026 da un'amicizia e da un libro:":
        "Oroboro Press publishes memoir and fiction as eBooks and audiobooks, in Italian and English. It was born in 2026 from a friendship and a book:",
    "di Nicola Nuti.": "by Nicola Nuti.",
    "Ogni libro lo seguiamo dall'inizio alla fine: la revisione del testo, la copertina, la voce, la traduzione, l'uscita su Amazon, Spotify e Audible e qui sul sito.":
        "We follow every book from start to finish: editing, cover, voice, translation, and release on Amazon, Spotify and Audible, and here on our site.",
    "Perché Oroboro": "Why Oroboro",
    "L'oroboro è il serpente che si morde la coda, antico simbolo di rinascita: un cerchio che finisce dove comincia. Ci è sembrato il segno giusto per libri fatti di memoria e di storie che tornano.":
        "The ouroboros is the snake that bites its own tail, an ancient symbol of renewal: a circle that ends where it begins. It felt like the right sign for books made of memory, and of stories that come back.",
    "è anche il nome della barca a vela con cui Francesco e Yuka girano il mondo dal 2018. Il logo lo ha disegnato Yuka: una rosa dei venti chiusa nel cerchio del serpente, con la testa rivolta a nord.":
        "is also the name of the sailboat Francesco and Yuka have been sailing around the world since 2018. Yuka designed the logo: a wind rose inside the snake's circle, its head pointing north.",
    "Come lavoriamo con gli autori": "How we work with authors",
    "Sul testo l'ultima parola è sempre dell'autore.": "The author always has the last word on the text.",
    "Noi suggeriamo, l'autore decide.": "We suggest, the author decides.",
    "I diritti restano all'autore.": "Rights stay with the author.",
    "Noi pubblichiamo per suo conto.": "We publish on the author's behalf.",
    "Prezzi, copertine e piattaforme li scegliamo insieme.": "We choose prices, covers and platforms together.",
    "Ogni libro può avere una seconda vita in inglese": "Every book can have a second life in English",
    ", tradotto da noi.": ", translated by us.",
    "Editore": "Publisher",
    "Italiano, ha lavorato per molti anni nella tecnologia nella Silicon Valley, tra cui a eBay. Nel 2018 ha lasciato il lavoro e, con sua moglie Yuka, è partito dal Sudafrica a bordo del catamarano":
        "Italian-born, he spent many years in tech in Silicon Valley, including at eBay. In 2018 he left his job and, with his wife Yuka, set sail from South Africa aboard the catamaran",
    "per un giro del mondo. Da allora hanno attraversato due volte l'Atlantico, dal Sudafrica al Brasile e dai Caraibi alle Azzorre, e navigato in tre oceani, fino al Mediterraneo.":
        "on a voyage around the world. Since then they have crossed the Atlantic twice, from South Africa to Brazil and from the Caribbean to the Azores, and sailed three oceans, all the way to the Mediterranean.",
    "Oggi vivono tra la Grecia, la California e il Giappone. Francesco racconta i viaggi su":
        "Today they live between Greece, California and Japan. Francesco writes about their travels on",
    "e scrive app per chi vive in barca. In Oroboro Press cura l'editing, la traduzione in inglese, gli eBook e gli audiolibri.":
        "and builds apps for people who live on boats. At Oroboro Press he handles editing, English translation, eBooks and audiobooks.",
    "Il nostro primo autore": "Our first author",
    "Nato a Firenze nel 1960, giornalista e critico d'arte. Ha cominciato negli anni Ottanta scrivendo per":
        "Born in Florence in 1960, journalist and art critic. He started out in the 1980s writing for",
    "e curando testi per cataloghi d'arte. Ha dedicato studi e monografie all'Astrattismo Classico, il movimento fondato a Firenze nel 1950 da un gruppo di pittori tra cui suo padre, Mario Nuti (1923–1996).":
        "and editing texts for art catalogues. He has written studies and monographs on Classical Abstractionism (Astrattismo Classico), the movement founded in Florence in 1950 by a group of painters including his father, Mario Nuti (1923–1996).",
    "In": "In",
    "ha raccolto in ventidue ricordi brevi e ironici gli incontri con pittori, scrittori e critici della Firenze degli ultimi sessant'anni, da Vasco Pratolini a Karel Appel. In copertina c'è":
        "he gathers, in twenty-two short and wry memories, his encounters with the painters, writers and critics of Florence over the last sixty years, from Vasco Pratolini to Karel Appel. The cover shows",
    ", un quadro di Mario Nuti. Sta scrivendo il suo prossimo libro,": ", a painting by Mario Nuti. He is now writing his next book,",
    "Aiuto con eBook e audiolibri": "Help with eBooks and audiobooks",
    "eBook (EPUB).": "eBook (EPUB).",
    "Si apre con Apple Libri su iPhone e iPad, con Kobo, con Google Play Libri su Android e con l'app Kindle (tramite «Invia a Kindle»).":
        "Opens in Apple Books on iPhone and iPad, on Kobo, in Google Play Books on Android, and in the Kindle app (via “Send to Kindle”).",
    "Audiolibro (MP3).": "Audiobook (MP3).",
    "Ogni racconto è un file: si ascolta con qualsiasi lettore musicale o di podcast, anche offline.":
        "Each story is a separate file: play it in any music or podcast app, even offline.",
    "Qualcosa non funziona? Scrivici a": "Something not working? Write to",
    "e ti aiutiamo.": "and we'll help.",
    "Per domande e proposte:": "Questions and proposals:",
    "Per recensioni, interviste e copie per la stampa scrivi a": "For reviews, interviews and press copies, write to",
    ". Cartella stampa in arrivo.": ". Press kit coming soon.",
    # Nicola's page
    "Autore": "Author", "Giornalista e critico d'arte.": "Journalist and art critic.", "Biografia": "Biography",
    "Nato a Firenze nel 1960, Nicola Nuti è giornalista, consulente e critico d'arte. Ha cominciato negli anni Ottanta scrivendo per":
        "Born in Florence in 1960, Nicola Nuti is a journalist, consultant and art critic. He started out in the 1980s writing for",
    "e curando testi per cataloghi d'arte.": "and editing texts for art catalogues.",
    "Ha dedicato studi, articoli e monografie all'Astrattismo Classico, il movimento nato a Firenze nel 1950 attorno a un gruppo di pittori tra cui suo padre, Mario Nuti (1923–1996).":
        "He has written studies, articles and monographs on Classical Abstractionism (Astrattismo Classico), the movement that grew up in Florence in 1950 around a group of painters including his father, Mario Nuti (1923–1996).",
    "ha raccolto in ventidue ricordi gli incontri con pittori, scrittori e critici della Firenze degli ultimi sessant'anni. Sta scrivendo":
        "he gathers in twenty-two memories his encounters with the painters, writers and critics of Florence over the last sixty years. He is now writing",
    "[Biografia completa: da scrivere con Nicola.]": "[Full biography: to be written with Nicola.]",
    "Una vita nell'arte": "A life in art",
    "Nasce a Firenze Mario Nuti, il padre di Nicola, pittore.": "Mario Nuti, painter and Nicola's father, is born in Florence.",
    "Mario Nuti firma con Vinicio Berti, Bruno Brunetti, Alvaro Monnini e Gualtiero Nativi il manifesto dell'Astrattismo Classico.":
        "Mario Nuti signs the manifesto of Classical Abstractionism with Vinicio Berti, Bruno Brunetti, Alvaro Monnini and Gualtiero Nativi.",
    "Nicola Nuti nasce a Firenze.": "Nicola Nuti is born in Florence.",
    "Anni '80": "1980s",
    "Comincia a scrivere d'arte per": "Starts writing about art for",
    "e cura i testi di cataloghi di mostre.": "and edits texts for exhibition catalogues.",
    "Dona alla Galleria d'arte moderna di Palazzo Pitti": "Donates to the Gallery of Modern Art at Palazzo Pitti",
    "(1950) di Mario Nuti.": "(1950) by Mario Nuti.",
    "Esce": "Publishes", ", SMITH Editore, Firenze.": ", SMITH Editore, Florence.",
    "Retrospettiva di Mario Nuti all'Accademia delle Arti del Disegno, Firenze.": "Mario Nuti retrospective at the Accademia delle Arti del Disegno, Florence.",
    "in eBook e audiolibro con Oroboro Press. In arrivo": "as eBook and audiobook from Oroboro Press. Coming next:",
    "Memorie · 2024, nuova edizione 2027": "Memoir · 2024, new edition 2027",
    "Ventidue ricordi della Firenze dell'arte. In eBook e audiolibro.": "Twenty-two memories of Florence's art world. As eBook and audiobook.",
    "Romanzo · in scrittura": "Novel · in progress",
    "Avvisami quando esce.": "Let me know when it's out.",
    "In preparazione": "In preparation",
    "L'archivio di Nicola Nuti.": "The Nicola Nuti archive.",
    "Quarant'anni di scritti sull'arte, raccolti in un unico posto e consultabili per artista, anno e mostra. Per studenti, studiosi, gallerie e giornalisti.":
        "Forty years of writing on art, gathered in one place and searchable by artist, year and exhibition. For students, scholars, galleries and journalists.",
    "Cataloghi di mostre": "Exhibition catalogues", "Articoli di giornale": "Newspaper articles", "Recensioni": "Reviews",
    "Studi e monografie": "Studies and monographs", "Interviste": "Interviews", "Fotografie e documenti": "Photos and documents",
    "Cerca nell'archivio": "Search the archive", "Cerca": "Search",
    "Sei uno studioso o una galleria? Scrivici a": "Scholar or gallery? Write to",
    "Ritratto di Nicola Nuti, in arrivo": "Portrait of Nicola Nuti, coming soon",
    "Artista, mostra, anno…": "Artist, exhibition, year…",
}

# strings that are the same in both languages (names, titles, brands)
SAME = {
    "OROBORO PRESS", "Crumbs", "NICOLA NUTI", "CRUMBS", "L'inatteso", "Giottino", "In English",
    "Crumbs, in English.", "With a short guide to Florence, the 1966 flood and the artists in the book.",
    "Notify me", "Oroboro", "Amazon Kindle", "Spotify", "Audible", "Oroboro Press", "Crumbs.", "Vasco Pratolini",
    "Karel Appel", "Joris Ivens", "Franco Loi", "Harald Szeemann", "eBook", "Kindle, Kobo, iPhone, Android",
    "Nicola Nuti", "Francesco Pugliano", "sailingoroboro.com", "La Città", "Il cane", "info@oroboropress.com",
    "Oroboro Press, San Francisco, California", "Composizione", "English",
}

# the buy page's small script
JS = [
    ('"name": "Audiolibro"', '"name": "Audiobook"'),
    ('"name": "eBook + Audiolibro"', '"name": "eBook + Audiobook"'),
    ('"detail": "EPUB senza DRM, con le immagini delle opere"', '"detail": "DRM-free EPUB, with images of the artworks"'),
    ('"detail": "MP3, circa 2 ore, letto da Nicola Nuti"', '"detail": "MP3, about 2 hours, read by Nicola Nuti"'),
    ('"detail": "Tutti e due, a un prezzo ridotto"', '"detail": "Both, at a reduced price"'),
    ('"both": "Leggi e ascolta, in un solo acquisto."', '"both": "Read and listen, in one purchase."'),
    ('"ebook": "Su Kindle, Kobo, iPhone, Android o computer."', '"ebook": "On Kindle, Kobo, iPhone, Android or computer."'),
    ('"audio": "Ogni racconto è una traccia."', '"audio": "Each story is a track."'),
    ("' · Italiano'", "' · Italian'"),
]


def translate(html, page, missing):
    head, body = html[: html.index("<body")], html[html.index("<body"):]
    keep = {}

    def stash(m):
        keep[len(keep)] = m.group(0)
        return f"\x00{len(keep) - 1}\x00"
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", stash, body, flags=re.S)

    def text(m):
        lead, t, trail = m.group(1), m.group(2), m.group(3)
        if t in EN:
            return f">{lead}{EN[t]}{trail}<"
        if t not in SAME and re.search(r"[A-Za-zÀ-ÿ]", t):
            missing.add((page, t))
        return m.group(0)
    body = re.sub(r">(\s*)([^<>\x00]*?[^\s<>\x00])(\s*)<", text, body)

    def attr(m):
        name, t = m.group(1), m.group(2)
        if t in EN:
            return f'{name}="{EN[t]}"'
        if t not in SAME:
            missing.add((page, f'{name}="{t}"'))
        return m.group(0)
    body = re.sub(r'\b(alt|aria-label|title|placeholder)="([^"]+)"', attr, body)

    for i, s in keep.items():
        if s.startswith("<script"):
            for a, b in JS:
                s = s.replace(a, b)
        body = body.replace(f"\x00{i}\x00", s)

    head = head.replace('<html lang="it">', '<html lang="en">')
    for a, b in TITLES.items():
        head = head.replace(f"<title>{a}</title>", f"<title>{b}</title>")
    out = head + body
    # English pages sit at the root: assets are one level closer
    out = out.replace('="../img/', '="img/')
    # language switch: English -> Italiano, pointing at the same Italian page
    out = re.sub(r'<a href="[^"]*"([^>]*)>English</a>', rf'<a href="it/{page}"\1>Italiano</a>', out)
    # links from Italian pages to the English home become same-page links
    out = out.replace('href="../index.html#', 'href="index.html#')
    return out


def url(lang, page):
    path = "" if page == "index.html" else page
    return f"{BASE}/{'it/' if lang == 'it' else ''}{path}"


def hreflang(html, page):
    """Tell search engines each page's twin in the other language."""
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', "", html)
    tags = (f'<link rel="alternate" hreflang="en" href="{url("en", page)}">\n'
            f'<link rel="alternate" hreflang="it" href="{url("it", page)}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{url("en", page)}">\n')
    return html.replace("</head>", tags + "</head>", 1)


def main():
    root = Path(__file__).resolve().parent.parent
    missing = set()
    built = {}
    for page in PAGES:
        src = root / "it" / page
        it = src.read_text(encoding="utf-8")
        # Italian page: its English link points at the same page in English
        it_new = re.sub(r'<a href="[^"]*"([^>]*)>English</a>', rf'<a href="../{page}"\1>English</a>', it)
        it_new = hreflang(it_new, page)
        if it_new != it:
            src.write_text(it_new, encoding="utf-8")
        built[page] = translate(it_new, page, missing)
    if missing:
        print("Untranslated strings — add them to EN or SAME:")
        for page, t in sorted(missing):
            print(f"  {page}: {t!r}")
        sys.exit(1)
    for page, html in built.items():
        (root / page).write_text(html, encoding="utf-8")
    print("built", ", ".join(PAGES))


if __name__ == "__main__":
    main()
