#!/usr/bin/env python3
"""Europaposten – lille statisk site-generator uden eksterne afhængigheder.

Brug:
    python3 build.py                 Byg hele sitet til mappen ./public
    python3 build.py ny "Overskrift" [sektion]
                                     Opret en ny artikel-skabelon i content/artikler/
    python3 build.py serve [port]    Byg og start en lokal webserver (standard: 8080)

Artikler er Markdown-filer med "front matter" øverst (se README.md).
Kræver kun Python 3.9+ (standardbiblioteket).
"""
from __future__ import annotations

import configparser
import datetime as dt
import html
import re
import shutil
import sys
import unicodedata
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "artikler"
IMAGES = ROOT / "content" / "billeder"
STATIC = ROOT / "static"
OUT = ROOT / "public"
TZ = ZoneInfo("Europe/Copenhagen")

UGEDAGE = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MAANEDER = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
            "august", "september", "oktober", "november", "december"]


# ---------------------------------------------------------------- konfiguration
def load_config():
    cp = configparser.ConfigParser(inline_comment_prefixes=(";",))
    cp.optionxform = str  # bevar store/små bogstaver
    cp.read(ROOT / "config.ini", encoding="utf-8")
    site = dict(cp["site"])
    site["base_url"] = site.get("base_url", "").rstrip("/")
    site["vis_annoncepladser"] = site.get("vis_annoncepladser", "nej").lower() in ("ja", "yes", "true", "1")
    site["cf_analytics_token"] = site.get("cf_analytics_token", "").strip()
    sections = dict(cp["sektioner"])
    red = dict(cp["redaktion"]) if cp.has_section("redaktion") else {}
    site["redaktoer"] = red.get("ansvarshavende", "").strip()
    site["redaktoer_titel"] = red.get("titel", "Ansvarshavende redaktør").strip()
    return site, sections


# Artikeltyper (front matter 'type'). Rækkefølgen bruges på oversigtssider.
ARTIKELTYPER = {
    "nyhed": "Nyhed", "analyse": "Analyse", "forklaring": "Forklaring",
    "faktatjek": "Faktatjek", "ministersvar": "Ministersvar", "long-read": "Long read",
}
# Sager: løbende historier med egen side på /sag/<slug>/. Artikler knyttes til med 'sag: slug, slug' i front matter.
SAGER = {
    "budgetregler": ("Gæld og budgetregler", "EU's budgetregler, den danske budgetlov og hvordan oprustningen presser de offentlige finanser."),
    "eu-budget": ("EU-budgettet 2028–2034", "Forhandlingerne om EU's næste langtidsbudget: regeringens krav om et lavere udgiftsniveau, Parlamentets krav om mere og det irske formandskabs forhandlingsboks."),
    "groenland": ("Grønland og EU", "EU's voksende engagement i Grønland – fra Kommissionens udspil og beredskabssamarbejde til påvirkningsforsøg og stormagtspres."),
    "forsvar-droner": ("Forsvar og droner", "Droneobservationerne over Danmark, Borris-sagen og EU's nye forsvarsprojekter og -programmer – og hvor Danmark er med."),
    "rusland": ("Rusland og hybride trusler", "Russisk påvirkning, valg og hybride angreb – og hvordan Danmark og EU svarer igen."),
}
TYPE_BESKRIVELSE = {
    "nyhed": "Nyheder om beslutninger, afstemninger og forslag i EU – med dansk vinkel og link til primærkilderne.",
    "analyse": "Analyser sætter en sag i perspektiv. De er tydeligt markeret og adskilt fra nyhedsstoffet.",
    "forklaring": "Forklaringer gør en EU-sag eller et begreb forståeligt fra bunden.",
    "faktatjek": "Faktatjek efterprøver konkrete påstande om EU mod primærkilderne.",
    "ministersvar": "Ministres svar til Folketinget om EU-sager – læst og forklaret med link til svaret på ft.dk.",
    "long-read": "Længere, gennemresearchede artikler om de store EU-sager.",
}


def analytics_snippet(site) -> str:
    """Cloudflare Web Analytics: cookiefri, ingen persondata. Tom, hvis token mangler."""
    tok = site.get("cf_analytics_token", "")
    if not tok:
        return ""
    return ("<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
            f"data-cf-beacon='{{\"token\": \"{esc(tok)}\"}}'></script>")


# ---------------------------------------------------------------- hjælpere
def slugify(text: str) -> str:
    text = text.lower()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa"), ("ü", "u"), ("ö", "o"), ("ä", "a")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > 60:  # klip ved et ordskel
        text = text[:60].rsplit("-", 1)[0]
    return text.strip("-") or "artikel"


def dansk_dato(d: dt.datetime, med_ugedag=False, med_tid=False) -> str:
    s = f"{d.day}. {MAANEDER[d.month - 1]} {d.year}"
    if med_ugedag:
        s = f"{UGEDAGE[d.weekday()].capitalize()} {s}"
    if med_tid:
        s += f" kl. {d:%H.%M}"
    return s


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- front matter
def parse_front_matter(text: str, path: Path):
    """Simpel YAML-agtig parser: 'nøgle: værdi' og lister med '- '."""
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: mangler front matter (skal starte med ---)")
    # Del kun ved linjer, der består af "---" (URL'er kan indeholde "---")
    _, fm, body = re.split(r"^---[ \t]*$", text, maxsplit=2, flags=re.M)
    meta, current_list = {}, None
    for raw in fm.strip().splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and current_list is not None:
            meta[current_list].append(line.lstrip()[2:].strip())
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            meta[key] = []
            current_list = key
        else:
            current_list = None
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            meta[key] = val
    return meta, body.strip()


def parse_source(item: str):
    """'Titel | https://url' -> (titel, url)."""
    if "|" in item:
        title, url = item.rsplit("|", 1)
        return title.strip(), url.strip()
    return item, item


# ---------------------------------------------------------------- mini-markdown
def inline_md(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)",
               lambda m: f'<a href="{m.group(2)}"' + (' rel="noopener" target="_blank"' if m.group(2).startswith("http") else "") + f">{m.group(1)}</a>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    return s


# Citatboks: en blockquote, hvis sidste linje starter med "— " (lang tankestreg) eller "-- ",
# bliver til et fremhævet citat med afsender. Uden afsenderlinje: almindelig blockquote.
# (Kort tankestreg "– " bruges ikke, fordi den er dansk replikstreg i citater.)
ATTRIB_RE = re.compile(r"^(?:—|--)\s*(.+)$")


def render_quote(lines) -> str:
    lines = [l for l in lines if l]
    attrib = None
    if len(lines) >= 2:
        m = ATTRIB_RE.match(lines[-1])
        if m:
            attrib, lines = m.group(1).strip(), lines[:-1]
    text = inline_md(" ".join(lines))
    if not attrib:
        return f"<blockquote><p>{text}</p></blockquote>"
    # Fjern eventuelle anførselstegn rundt om citatet – citatboksen tegner selv sit tegn
    text = re.sub(r'^(?:&quot;|[”“»«"])\s*|\s*(?:&quot;|[”“»«"])$', "", text)
    return (f'<figure class="pullquote"><blockquote><p>{text}</p></blockquote>'
            f'<figcaption>— {inline_md(attrib)}</figcaption></figure>')


FAKTA_RE = re.compile(r"^:::fakta[ \t]*(.*?)[ \t]*\n(.*?)\n:::[ \t]*$", re.M | re.S)


def markdown(md: str) -> str:
    # Faktaboks: ':::fakta Titel' ... ':::' (fx "Det ved vi – og det ved vi ikke")
    boxes = []

    def _box(m):
        title = m.group(1).strip() or "Fakta"
        boxes.append(f'<aside class="factbox"><h2>{inline_md(title)}</h2>{markdown(m.group(2))}</aside>')
        return f"\n\n@@FAKTABOKS{len(boxes) - 1}@@\n\n"
    md = FAKTA_RE.sub(_box, md)
    out, para, listbuf, quote, table = [], [], [], [], []

    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    def flush():
        nonlocal para, listbuf, quote, table
        if table:
            rows = [r for r in table if not re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", r.strip())]
            head, body = rows[0], rows[1:]
            html = "<div class=\"table-wrap\"><table><thead><tr>" + "".join(f"<th>{inline_md(c)}</th>" for c in cells(head)) + "</tr></thead><tbody>"
            html += "".join("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells(r)) + "</tr>" for r in body)
            out.append(html + "</tbody></table></div>")
            table = []
        if para:
            out.append("<p>" + inline_md(" ".join(para)) + "</p>")
            para = []
        if listbuf:
            out.append("<ul>" + "".join(f"<li>{inline_md(i)}</li>" for i in listbuf) + "</ul>")
            listbuf = []
        if quote:
            out.append(render_quote(quote))
            quote = []

    for line in md.splitlines():
        st = line.strip()
        if not st:
            flush()
        elif re.fullmatch(r"@@FAKTABOKS\d+@@", st):
            flush()
            out.append(boxes[int(st[11:-2])])
        elif st.startswith("!billede "):
            # Billede i brødteksten: !billede fil.jpg | alt-tekst | billedtekst | kreditering (markdown)
            flush()
            parts = [x.strip() for x in st[len("!billede "):].split(" | ")]
            if len(parts) != 4 or not all(parts):
                raise ValueError(f"!billede kræver 4 felter (fil | alt | billedtekst | kreditering): {st}")
            fil, alt, cap, credit = parts
            if not (IMAGES / fil).exists():
                raise ValueError(f"billedet '{fil}' findes ikke i content/billeder/")
            out.append(
                f'<figure class="story-illustration inline-illustration">'
                f'<img src="../../billeder/{esc(fil)}" alt="{esc(alt)}" loading="lazy" decoding="async">'
                f'<figcaption class="illustration-credit"><span class="illustration-caption">{inline_md(cap)}</span> '
                f'<span class="illustration-credit-line">{inline_md(credit)}</span></figcaption></figure>')
        elif st.startswith("#"):
            flush()
            level = min(len(st) - len(st.lstrip("#")), 4)
            level = max(level, 2)  # h1 er forbeholdt overskriften
            htxt = st.lstrip('#').strip()
            out.append(f'<h{level} id="{slugify(htxt)}">{inline_md(htxt)}</h{level}>')
        elif st.startswith("|") and st.endswith("|"):
            if para or listbuf or quote:
                flush()
            table.append(st)
        elif st.startswith(("- ", "* ")):
            if para or quote or table:
                flush()
            listbuf.append(st[2:])
        elif st.startswith(">"):
            if para or listbuf or table:
                flush()
            quote.append(st[1:].strip())
        else:
            if listbuf or quote or table:
                flush()
            para.append(st)
    flush()
    return "\n".join(out)


# ---------------------------------------------------------------- artikler
class Article:
    def __init__(self, path: Path, sections: dict):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
        for req in ("title", "date", "summary", "section"):
            if req not in meta:
                raise ValueError(f"{path.name}: mangler feltet '{req}' i front matter")
        self.path = path
        self.title = meta["title"]
        self.summary = meta["summary"]
        self.section = meta["section"]
        if self.section not in sections:
            raise ValueError(f"{path.name}: ukendt sektion '{self.section}'. Gyldige: {', '.join(sections)}")
        self.section_name = sections[self.section]
        d = meta["date"].replace("T", " ")
        fmt = "%Y-%m-%d %H:%M" if ":" in d else "%Y-%m-%d"
        self.date = dt.datetime.strptime(d, fmt).replace(tzinfo=TZ)
        upd = meta.get("updated")
        self.updated = dt.datetime.strptime(upd.replace("T", " "), "%Y-%m-%d %H:%M").replace(tzinfo=TZ) if upd else None
        self.author = meta.get("author", "Europaposten-redaktionen")
        t = slugify(meta.get("type", "Nyhed"))
        if t not in ARTIKELTYPER:
            raise ValueError(f"{path.name}: ukendt type '{meta.get('type')}'. Gyldige: {', '.join(ARTIKELTYPER.values())}")
        self.type, self.type_name = t, ARTIKELTYPER[t]
        # Rettelser: liste af 'ÅÅÅÅ-MM-DD | Hvad blev rettet'
        self.corrections = [tuple(x.strip() for x in c.split("|", 1)) for c in meta.get("rettelser", []) or [] if "|" in c]
        self.kicker = meta.get("kicker", "")
        self.sager = [x.strip() for x in str(meta.get("sag", "") or "").split(",") if x.strip()]
        for sg in self.sager:
            if sg not in SAGER:
                raise ValueError(f"{path.name}: ukendt sag '{sg}'. Gyldige: {', '.join(SAGER)}")
        self.draft = str(meta.get("draft", "nej")).lower() in ("ja", "yes", "true")
        self.featured = str(meta.get("featured", "nej")).lower() in ("ja", "yes", "true")
        self.sources = [parse_source(s) for s in meta.get("sources", []) or []]
        self.slug = meta.get("slug") or slugify(self.title)
        # Lead-illustration: filnavn under content/billeder/ (jpg/png/svg/webp)
        ill = (meta.get("illustration") or "").strip()
        self.illustration = ill.lstrip("/") if ill else ""
        if self.illustration.startswith("billeder/"):
            self.illustration = self.illustration[len("billeder/"):]
        self.illustration_alt = (meta.get("illustration_alt") or "").strip()
        self.illustration_credit = (meta.get("illustration_credit") or "").strip()
        # Billedtekst og rettighedsoplysninger (bruges især ved arkivfotos)
        self.illustration_caption = (meta.get("illustration_caption") or "").strip()
        self.illustration_photographer = (meta.get("illustration_photographer") or "").strip()
        self.illustration_license = (meta.get("illustration_license") or "").strip()
        self.illustration_license_url = (meta.get("illustration_license_url") or "").strip()
        self.illustration_source = (meta.get("illustration_source") or "").strip()
        if self.illustration:
            if not (IMAGES / self.illustration).exists():
                raise ValueError(f"{path.name}: billedet '{self.illustration}' findes ikke i content/billeder/")
            if not self.illustration_credit and not self.illustration_photographer:
                raise ValueError(f"{path.name}: billedet mangler kreditering (illustration_credit eller illustration_photographer)")
            if self.illustration_photographer and not (self.illustration_license and self.illustration_source):
                raise ValueError(f"{path.name}: arkivfoto skal have både illustration_license og illustration_source")
        self.body_md = body
        self.body_html = markdown(body)
        words = len(re.findall(r"\w+", body))
        self.minutes = max(1, round(words / 200))
        self.url = f"artikler/{self.slug}/"


def load_articles(sections, include_drafts=False):
    arts = []
    for p in sorted(CONTENT.glob("*.md")):
        a = Article(p, sections)
        if a.draft and not include_drafts:
            continue
        arts.append(a)
    slugs = [a.slug for a in arts]
    dups = {s for s in slugs if slugs.count(s) > 1}
    if dups:
        raise ValueError(f"Samme slug bruges flere gange: {dups}")
    arts.sort(key=lambda a: a.date, reverse=True)
    return arts


# ---------------------------------------------------------------- skabeloner
def ad_slot(site, name, label="Annonceplads"):
    """Markeret plads til fremtidige annoncer/affiliate. Indeholder INGEN annoncekode."""
    comment = f"<!-- ANNONCEPLADS: {name} – indsæt annonce/affiliate-kode her senere -->"
    if not site["vis_annoncepladser"]:
        return comment
    return f'{comment}<aside class="ad-slot" data-slot="{name}" aria-hidden="true"><span>{label} ({name})</span></aside>'


def layout(site, sections, root, title, content, description=None, active=None, extra_head=""):
    now = dt.datetime.now(TZ)
    cur = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{root}sektion/{slug}/"{cur if slug == active else ""}>{esc(name)}</a></li>'
        for slug, name in sections.items())
    page_title = f"{title} | {site['navn']}" if title != site["navn"] else f"{site['navn']} – {site['undertitel']}"
    return f"""<!doctype html>
<html lang="{site.get('sprog', 'da')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(description or site['beskrivelse'])}">
<link rel="stylesheet" href="{root}static/style.css">
<link rel="alternate" type="application/rss+xml" title="{esc(site['navn'])}" href="{root}rss.xml">
<link rel="icon" href="{root}static/favicon.svg" type="image/svg+xml">
{extra_head}
</head>
<body>
<a class="skip" href="#indhold">Gå til indhold</a>
<header class="masthead">
  <div class="topbar wrap">
    <span class="today">{dansk_dato(now, med_ugedag=True)}</span>
    <span class="topbar-links"><a href="{root}arkiv/">Arkiv</a><a href="{root}om-eu/">Om EU</a><a href="{root}om-os/">Om os</a><a href="{root}rss.xml">RSS</a></span>
  </div>
  <div class="brand wrap">
    <a href="{root}" class="logo">{esc(site['navn'])}</a>
    <p class="tagline">{esc(site['undertitel'])}</p>
  </div>
  <nav class="sections" aria-label="Sektioner">
    <ul class="wrap"><li><a href="{root}"{' aria-current="page"' if active == 'forside' else ''}>Forside</a></li>{nav}</ul>
  </nav>
</header>
<main id="indhold" class="wrap">
{content}
</main>
<footer class="footer">
  <div class="wrap footer-grid">
    <div>
      <p class="logo small">{esc(site['navn'])}</p>
      <p>{esc(site['beskrivelse'])}</p>
    </div>
    <div>
      <p><strong>Sektioner</strong></p>
      <ul>{''.join(f'<li><a href="{root}sektion/{s}/">{esc(n)}</a></li>' for s, n in sections.items())}</ul>
    </div>
    <div>
      <p><strong>Om {esc(site['navn'])}</strong></p>
      <ul><li><a href="{root}om-os/">Om Europaposten og redaktionen</a></li><li><a href="{root}redaktionelle-retningslinjer/">Redaktionelle retningslinjer</a></li><li><a href="{root}saadan-bruger-vi-ai/">Sådan bruger vi AI</a></li><li><a href="{root}rettelser-og-klager/">Rettelser og klager</a></li><li><a href="{root}om-eu/">Om EU – forklaringer</a></li><li><a href="{root}emner/">Emner og artikeltyper</a></li><li><a href="{root}arkiv/">Arkiv</a> · <a href="{root}rss.xml">RSS</a></li></ul>
    </div>
  </div>
  <div class="wrap footer-legal">
    <p><strong>Ansvarshavende redaktør:</strong> {esc(site.get('redaktoer', ''))} · <strong>Kontakt:</strong> <a href="mailto:{esc(site['kontakt_email'])}">{esc(site['kontakt_email'])}</a></p>
    <p>{esc(site['navn'])} er anmeldt til Pressenævnet og omfattet af medieansvarsloven. Klager over indhold kan indbringes for <a href="https://www.pressenaevnet.dk/" rel="noopener" target="_blank">Pressenævnet</a> – se <a href="{root}rettelser-og-klager/">Rettelser og klager</a>.</p>
  </div>
  <p class="wrap fineprint">Europaposten er en AI-assisteret redaktion: Kunstig intelligens bruges som værktøj til research og udkast, og den ansvarshavende redaktør læser, redigerer og godkender hver artikel (<a href="{root}saadan-bruger-vi-ai/">sådan bruger vi AI</a>). Alle artikler linker til deres kilder. © {now.year} {esc(site['navn'])}</p>
</footer>
{analytics_snippet(site)}
</body>
</html>
"""


REDAKTOER = ""  # sættes i build()


def byline(a: Article, with_time=True):
    red = f'Redigeret af {esc(REDAKTOER)}' if REDAKTOER else f'Af {esc(a.author)}'
    s = f'<span class="byline">{red}</span> · <time datetime="{a.date.isoformat()}">{dansk_dato(a.date, med_tid=with_time)}</time>'
    return s


def teaser(a: Article, root, size="normal"):
    kicker = esc(a.kicker or a.section_name)
    tag = "h2" if size == "lead" else "h3"
    return f"""<article class="teaser teaser-{size}">
  <a class="teaser-link" href="{root}{a.url}">
    <p class="kicker kicker-{a.section}">{type_label(a)}{kicker}</p>
    <{tag} class="teaser-title">{esc(a.title)}</{tag}>
    <p class="teaser-summary">{esc(a.summary)}</p>
  </a>
  <p class="meta">{byline(a, with_time=False)} · {a.minutes} min. læsning</p>
</article>"""


def type_label(a: Article, root=None) -> str:
    """Lille mærke med artikeltypen (Nyhed, Analyse ...)."""
    inner = esc(a.type_name)
    if root is not None:
        inner = f'<a href="{root}type/{a.type}/">{inner}</a>'
    return f'<span class="type-label type-{a.type}">{inner}</span> '


def kort_tekst(s: str, maks: int = 120) -> str:
    """Første sætning af manchetten, højst `maks` tegn (klippes ved et ordskel)."""
    s = " ".join(s.split())
    first = re.split(r"(?<=[.!?])\s+(?=[A-ZÆØÅ»\"0-9])", s, maxsplit=1)[0]
    if len(first) <= maks:
        return first
    cut = first[:maks].rsplit(" ", 1)[0].rstrip(",;:–- ")
    return cut + "…"


def card_media(a: Article, root, lazy=True):
    """Billede til forsidekort – eller en neutral pladsholder i sitets stil."""
    if a.illustration:
        load = 'loading="lazy"' if lazy else 'loading="eager" fetchpriority="high"'
        return (f'<div class="card-media"><img src="{root}billeder/{esc(a.illustration)}" '
                f'alt="{esc(a.illustration_alt or a.title)}" width="1280" height="720" {load} decoding="async"></div>')
    return (f'<div class="card-media card-placeholder" aria-hidden="true">'
            f'<span class="ph-logo">E</span><span class="ph-sec">{esc(a.section_name)}</span></div>')


def card(a: Article, root, size="normal"):
    """Forsidekort: billede øverst, lille sektionsmærke, overskrift. Hele kortet er et link."""
    tag = "h2" if size == "lead" else "h3"
    extra = ""
    if size == "lead":
        extra = f'<p class="card-teaser">{esc(kort_tekst(a.summary))}</p>'
    noimg = "" if a.illustration else " card-noimg"
    return f"""<article class="card card-{size}{noimg}">
  <a class="card-link" href="{root}{a.url}">
    {card_media(a, root, lazy=(size != "lead"))}
    <div class="card-body">
      <p class="kicker kicker-{a.section}">{type_label(a)}{esc(a.section_name)}</p>
      <{tag} class="card-title">{esc(a.title)}</{tag}>
      {extra}
      <p class="card-meta"><time datetime="{a.date.isoformat()}">{dansk_dato(a.date)}</time></p>
    </div>
  </a>
</article>"""


def render_index(site, sections, arts):
    root = ""
    if not arts:
        content = "<p>Der er endnu ingen artikler.</p>"
        return layout(site, sections, root, site["navn"], content, active="forside")
    featured = [a for a in arts if a.featured]
    lead = featured[0] if featured else arts[0]
    rest = [a for a in arts if a is not lead]
    side, grid_arts = rest[:2], rest[2:14]
    side_html = "".join(card(a, root, "side") for a in side)
    grid = "".join(card(a, root) for a in grid_arts)
    more = ""
    if grid_arts:
        more = f'<section class="front-more"><h2 class="rubric">Flere nyheder</h2><div class="cards">{grid}</div></section>'
    content = f"""
<div class="front-top">
  {card(lead, root, "lead")}
  <div class="front-side-cards">{side_html}</div>
</div>
{ad_slot(site, "forside-banner")}
{more}
<p class="front-archive"><a href="{root}arkiv/">Se alle artikler i arkivet →</a></p>
{ad_slot(site, "forside-sidebar")}
"""
    return layout(site, sections, root, site["navn"], content, active="forside")


def illustration_html(a: Article, root: str) -> str:
    """Lead-illustration under overskriften, hvis front matter har 'illustration'."""
    if not a.illustration:
        return ""
    src = f"{root}billeder/{esc(a.illustration)}"
    alt = esc(a.illustration_alt or a.title)
    credit_md = a.illustration_credit
    if not credit_md and a.illustration_photographer:
        # Byg krediteringen af de strukturerede felter: Foto: Navn / Kilde, licens
        lic = a.illustration_license
        if a.illustration_license_url:
            lic = f"[{lic}]({a.illustration_license_url})"
        credit_md = f"Foto: {a.illustration_photographer} / [kilde]({a.illustration_source}), {lic}"
    parts = []
    if a.illustration_caption:
        parts.append(f'<span class="illustration-caption">{inline_md(a.illustration_caption)}</span>')
    if credit_md:
        parts.append(f'<span class="illustration-credit-line">{inline_md(credit_md)}</span>')
    caption = f'<figcaption class="illustration-credit">{" ".join(parts)}</figcaption>' if parts else ""
    return (
        f'<figure class="story-illustration">\n'
        f'  <img src="{src}" alt="{alt}" loading="eager" decoding="async">\n'
        f'  {caption}\n'
        f'</figure>'
    )


def render_article(site, sections, a: Article, arts):
    root = "../../"
    # Læs også: først samme emne (kicker), så samme sektion, så de nyeste
    others = [x for x in arts if x is not a]
    related = [x for x in others if set(a.sager) & set(x.sager)][:3]
    related += [x for x in others if a.kicker and x.kicker == a.kicker and x not in related][: 3 - len(related)]
    related += [x for x in others if x.section == a.section and x not in related][: 3 - len(related)]
    if len(related) < 3:
        related += [x for x in others if x not in related][: 3 - len(related)]
    rel_html = "".join(teaser(x, root, "small") for x in related)
    corr_html = ""
    if a.corrections:
        corr_html = ('<section class="corrections" id="rettelser"><h2>Rettelser</h2><ul>' + "".join(
            f"<li><strong>{esc(d)}:</strong> {inline_md(t)}</li>" for d, t in a.corrections) + "</ul></section>")
    # Samlet kildeliste kun i long reads; i øvrige artikler står kilderne som links i brødteksten
    sources = "" if a.type != "long-read" else "".join(
        f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(t)}</a></li>' for t, u in a.sources)
    rettet = ' · <a href="#rettelser">Artiklen er rettet</a>' if a.corrections else ""
    updated = (f' · Opdateret <time datetime="{a.updated.isoformat()}">{dansk_dato(a.updated, med_tid=True)}</time>'
               if a.updated else "")
    abs_url = f"{site['base_url']}/{a.url}"
    og_image = ""
    ld_image = ""
    if a.illustration:
        img_abs = f"{site['base_url']}/billeder/{a.illustration}"
        og_image = f'\n<meta property="og:image" content="{esc(img_abs)}">'
        ld_image = f',"image":{json_str(img_abs)}'
    import json as _json
    pub = {"@type": "NewsMediaOrganization", "name": site["navn"], "url": site["base_url"] + "/",
           "logo": {"@type": "ImageObject", "url": site["base_url"] + "/static/favicon.svg"},
           "email": site["kontakt_email"],
           "publishingPrinciples": site["base_url"] + "/redaktionelle-retningslinjer/",
           "correctionsPolicy": site["base_url"] + "/rettelser-og-klager/",
           "ethicsPolicy": site["base_url"] + "/rettelser-og-klager/",
           "actionableFeedbackPolicy": site["base_url"] + "/rettelser-og-klager/",
           "masthead": site["base_url"] + "/om-os/"}
    ld = {"author": {"@type": "Organization", "name": site["navn"], "url": site["base_url"] + "/om-os/"},
          "publisher": pub, "mainEntityOfPage": abs_url, "articleSection": a.section_name,
          "genre": a.type_name, "isAccessibleForFree": True}
    if site.get("redaktoer"):
        ld["editor"] = {"@type": "Person", "name": site["redaktoer"], "jobTitle": site.get("redaktoer_titel", "")}
    if a.updated:
        ld["dateModified"] = a.updated.isoformat()
    ld_extra = _json.dumps(ld, ensure_ascii=False)[1:-1].replace("</", "<\\/")
    head = f"""<link rel="canonical" href="{esc(abs_url)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(a.title)}">
<meta property="og:description" content="{esc(a.summary)}">
<meta property="og:url" content="{esc(abs_url)}">
<meta property="og:locale" content="da_DK">{og_image}
<meta property="article:published_time" content="{a.date.isoformat()}">
<script src="{root}static/laes-op.js" defer></script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"NewsArticle","headline":{json_str(a.title)},"description":{json_str(a.summary)},"datePublished":"{a.date.isoformat()}","inLanguage":"da",{ld_extra}{ld_image}}}</script>"""
    content = f"""
<article class="story">
  <header class="story-head">
    <p class="kicker kicker-{a.section}">{type_label(a, root)}<a href="{root}sektion/{a.section}/">{esc(a.section_name)}</a>{(" · " + esc(a.kicker)) if a.kicker and a.kicker not in (a.type_name, a.section_name, "Forklaret") else ""}</p>
    <h1>{esc(a.title)}</h1>
    {illustration_html(a, root)}
    <p class="standfirst">{esc(a.summary)}</p>
    <p class="meta">{byline(a)}{updated}{rettet} · {a.minutes} min. læsning</p>
    <div class="laes-op" role="group" aria-label="Oplæsning af artiklen" hidden>
      <button type="button" class="laes-op-knap" aria-label="Læs artiklen op" aria-pressed="false"><svg class="laes-op-ikon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path d="M3 9v6h4l5 4V5L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z" fill="currentColor"/></svg><span class="laes-op-tekst">Læs op</span></button>
      <button type="button" class="laes-op-stop" aria-label="Stop oplæsningen" hidden>Stop</button>
      <span class="laes-op-status visually-hidden" aria-live="polite"></span>
    </div>
  </header>
  {('<p class="sag-link">Følg sagen: ' + " · ".join(f'<a href="{root}sag/{sg}/">{esc(SAGER[sg][0])}</a>' for sg in a.sager) + '</p>') if a.sager else ''}
  <div class="story-body">
    {a.body_html}
    {ad_slot(site, "artikel-midt")}
  </div>
  <footer class="story-foot">
    {corr_html}
    {f'<section class="sources"><h2>Kilder</h2><ul>{sources}</ul></section>' if sources else ''}
    <p class="ai-note">Artiklen er læst, redigeret og godkendt af ansvarshavende redaktør {esc(site.get('redaktoer', ''))}, som står inde for indholdet. Kunstig intelligens er brugt som værktøj til research og første udkast på baggrund af de nævnte kilder. Har du fundet en fejl? <a href="mailto:{esc(site['kontakt_email'])}">Skriv til os</a> · <a href="{root}rettelser-og-klager/">Rettelser og klager</a> · <a href="{root}saadan-bruger-vi-ai/">Sådan bruger vi AI</a>.</p>
  </footer>
</article>
{ad_slot(site, "artikel-bund")}
<section class="related"><h2 class="rubric">Læs også</h2><div class="grid grid-3">{rel_html}</div></section>
"""
    return layout(site, sections, root, a.title, content, description=a.summary, active=a.section, extra_head=head)


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def render_list(site, sections, root, title, intro, arts, active=None):
    by_day = {}
    for a in arts:
        by_day.setdefault(a.date.date(), []).append(a)
    blocks = ""
    for day, items in by_day.items():
        d = dt.datetime.combine(day, dt.time(), TZ)
        lis = "".join(
            f'<li><p class="kicker kicker-{a.section}">{type_label(a)}{esc(a.section_name)}</p><a href="{root}{a.url}"><h3>{esc(a.title)}</h3></a><p>{esc(a.summary)}</p></li>'
            for a in items)
        blocks += f'<section class="day"><h2 class="rubric">{dansk_dato(d, med_ugedag=True)}</h2><ul class="list">{lis}</ul></section>'
    if not blocks:
        blocks = "<p>Der er endnu ingen artikler her.</p>"
    content = f'<header class="page-head"><h1>{esc(title)}</h1><p>{esc(intro)}</p></header>{blocks}'
    return layout(site, sections, root, title, content, active=active)


SIDER = ROOT / "content" / "sider"
PAGES = {
    "om-os": SIDER / "om-os.md",
    "redaktionelle-retningslinjer": ROOT / "content" / "redaktionelle-retningslinjer.md",
    "saadan-bruger-vi-ai": SIDER / "saadan-bruger-vi-ai.md",
    "rettelser-og-klager": SIDER / "rettelser-og-klager.md",
    "om-eu": SIDER / "om-eu.md",
}


def corrections_log(site, arts, root):
    """Offentlig rettelseslog: alle rettelser fra artiklernes front matter, nyeste først."""
    rows = sorted(((d, t, a) for a in arts for d, t in a.corrections), key=lambda x: x[0], reverse=True)
    if not rows:
        return ('<p class="meta">Der er endnu ikke registreret rettelser. Når vi retter en faktuel fejl, '
                'står rettelsen både nederst i artiklen og her.</p>')
    return '<ul class="list corrections-log">' + "".join(
        f'<li><p class="meta">{esc(d)}</p><a href="{root}{a.url}"><h3>{esc(a.title)}</h3></a><p>{inline_md(t)}</p></li>'
        for d, t, a in rows) + "</ul>"


def explainer_list(arts, root):
    ex = [a for a in arts if a.type in ("forklaring", "long-read", "faktatjek", "analyse")]
    if not ex:
        return "<p>Der er endnu ingen forklaringer.</p>"
    return '<ul class="list">' + "".join(
        f'<li><p class="kicker kicker-{a.section}">{type_label(a)}{esc(a.section_name)}</p><a href="{root}{a.url}"><h3>{esc(a.title)}</h3></a><p>{esc(a.summary)}</p></li>'
        for a in ex) + "</ul>"


def render_sag(site, sections, slug, arts):
    root = "../../"
    name, intro = SAGER[slug]
    sa = [a for a in arts if slug in a.sager]
    grid = "".join(card(a, root) for a in sa) or "<p>Der er endnu ingen artikler i sagen.</p>"
    content = (f'<header class="page-head"><p class="kicker">Sag</p><h1>{esc(name)}</h1><p>{esc(intro)}</p>'
               f'<p class="meta">{len(sa)} artikler · senest opdateret {dansk_dato(sa[0].date, med_tid=True) if sa else ""}</p></header>'
               f'<div class="grid grid-3">{grid}</div>')
    return layout(site, sections, root, name, content, description=intro)


def render_topics(site, sections, arts):
    root = "../"
    sag = "".join(
        f'<li><a href="{root}sag/{k}/"><h3>{esc(n)}</h3></a><p>{esc(d)} ({sum(1 for a in arts if k in a.sager)} artikler)</p></li>'
        for k, (n, d) in SAGER.items())
    sec = "".join(
        f'<li><a href="{root}sektion/{s}/"><h3>{esc(n)}</h3></a><p>{sum(1 for a in arts if a.section == s)} artikler</p></li>'
        for s, n in sections.items())
    typ = "".join(
        f'<li><a href="{root}type/{t}/"><h3>{esc(n)}</h3></a><p>{esc(TYPE_BESKRIVELSE[t])} ({sum(1 for a in arts if a.type == t)} artikler)</p></li>'
        for t, n in ARTIKELTYPER.items())
    content = (f'<header class="page-head"><h1>Emner og artikeltyper</h1><p>Find artikler efter emne eller efter type. '
               f'Alle artikler ligger også i <a href="{root}arkiv/">arkivet</a>.</p></header>'
               f'<section><h2 class="rubric">Sager vi følger</h2><ul class="list">{sag}</ul></section>'
               f'<div class="topics-grid"><section><h2 class="rubric">Emner</h2><ul class="list">{sec}</ul></section>'
               f'<section><h2 class="rubric">Artikeltyper</h2><ul class="list">{typ}</ul></section></div>')
    return layout(site, sections, root, "Emner og artikeltyper", content)


def render_page(site, sections, path: Path, arts=()):
    """Simpel side (fx redaktionelle retningslinjer) fra Markdown med front matter.
    Pladsholdere i teksten: {{rettelseslog}}, {{forklaringer}}, {{redaktoer}}, {{email}}, {{antal_artikler}}."""
    root = "../"
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    blocks = {"{{rettelseslog}}": corrections_log(site, arts, root), "{{forklaringer}}": explainer_list(arts, root)}
    body = (body.replace("{{redaktoer}}", site.get("redaktoer", "")).replace("{{email}}", site["kontakt_email"])
            .replace("{{antal_artikler}}", str(len(arts))))
    title = meta.get("title", path.stem)
    body_html = markdown(body)
    for k, v in blocks.items():
        body_html = body_html.replace(f"<p>{k}</p>", v)
    upd = f'<p class="meta">Senest opdateret: {esc(meta["updated"])}</p>' if meta.get("updated") else ""
    content = f"""
<article class="story about">
  <header class="story-head"><h1>{esc(title)}</h1>
  <p class="standfirst">{esc(meta.get("summary", ""))}</p>{upd}</header>
  <div class="story-body">
{body_html}
  </div>
</article>"""
    return layout(site, sections, root, title, content, description=meta.get("summary"))


def render_rss(site, arts):
    items = ""
    for a in arts[:30]:
        link = f"{site['base_url']}/{a.url}"
        items += f"""<item><title>{esc(a.title)}</title><link>{esc(link)}</link><guid isPermaLink="true">{esc(link)}</guid><pubDate>{format_datetime(a.date)}</pubDate><category>{esc(a.section_name)}</category><description>{esc(a.summary)}</description></item>\n"""
    last = format_datetime(arts[0].date if arts else dt.datetime.now(TZ))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>{esc(site['navn'])}</title>
<link>{esc(site['base_url'])}/</link>
<description>{esc(site['beskrivelse'])}</description>
<language>da</language>
<lastBuildDate>{last}</lastBuildDate>
<atom:link href="{esc(site['base_url'])}/rss.xml" rel="self" type="application/rss+xml"/>
{items}</channel>
</rss>
"""


def render_sitemap(site, sections, arts):
    urls = ["", "arkiv/", "emner/"] + [f"type/{t}/" for t in ARTIKELTYPER] + [f"{k}/" for k, v in PAGES.items() if v.exists()] + [f"sektion/{s}/" for s in sections] + [f"sag/{k}/" for k in SAGER] + [a.url for a in arts]
    body = "".join(f"<url><loc>{esc(site['base_url'])}/{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


# ---------------------------------------------------------------- build
def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build():
    global REDAKTOER
    site, sections = load_config()
    REDAKTOER = site.get("redaktoer", "")
    arts = load_articles(sections)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(STATIC, OUT / "static")
    if IMAGES.exists():
        shutil.copytree(IMAGES, OUT / "billeder")
    write(OUT / "index.html", render_index(site, sections, arts))
    for a in arts:
        write(OUT / a.url / "index.html", render_article(site, sections, a, arts))
    for slug, name in sections.items():
        sa = [a for a in arts if a.section == slug]
        write(OUT / "sektion" / slug / "index.html",
              render_list(site, sections, "../../", name, f"Alle artikler i sektionen {name}.", sa, active=slug))
    write(OUT / "arkiv" / "index.html",
          render_list(site, sections, "../", "Arkiv", "Alle artikler, nyeste først.", arts))
    for t, name in ARTIKELTYPER.items():
        ta = [a for a in arts if a.type == t]
        write(OUT / "type" / t / "index.html",
              render_list(site, sections, "../../", name, TYPE_BESKRIVELSE[t], ta))
    write(OUT / "emner" / "index.html", render_topics(site, sections, arts))
    for sg in SAGER:
        write(OUT / "sag" / sg / "index.html", render_sag(site, sections, sg, arts))
    write(OUT / "redaktionen" / "index.html",
          '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../om-os/#redaktionen">'
          '<link rel="canonical" href="../om-os/"><a href="../om-os/#redaktionen">Redaktionen</a>')
    for slug, path in PAGES.items():
        if path.exists():
            write(OUT / slug / "index.html", render_page(site, sections, path, arts))
    write(OUT / "rss.xml", render_rss(site, arts))
    write(OUT / "sitemap.xml", render_sitemap(site, sections, arts))
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site['base_url']}/sitemap.xml\n")
    nf = layout(site, sections, "/", "Siden findes ikke",
                '<header class="page-head"><h1>Siden findes ikke</h1><p><a href="/">Gå til forsiden</a></p></header>')
    write(OUT / "404.html", nf)
    (OUT / ".nojekyll").write_text("")  # GitHub Pages: spring Jekyll over
    host = re.sub(r"^https?://", "", site["base_url"]).split("/")[0]
    if host and not host.endswith((".example", "localhost")) and "github.io" not in host:
        (OUT / "CNAME").write_text(host + "\n")  # eget domæne på GitHub Pages
    today = dt.datetime.now(TZ).date()
    n_today = sum(1 for a in arts if a.date.date() == today)
    print(f"Bygget {len(arts)} artikler til {OUT}  (i dag: {n_today}/3 artikler)")


def new_article(title: str, section: str = "politik"):
    site, sections = load_config()
    if section not in sections:
        sys.exit(f"Ukendt sektion '{section}'. Vælg en af: {', '.join(sections)}")
    now = dt.datetime.now(TZ)
    slug = slugify(title)
    path = CONTENT / f"{now:%Y-%m-%d}-{slug}.md"
    if path.exists():
        sys.exit(f"Findes allerede: {path}")
    path.write_text(f"""---
title: {title}
slug: {slug}
date: {now:%Y-%m-%d %H:%M}
section: {section}
type: Nyhed
summary: Skriv en kort manchet på 1-2 sætninger her.
author: Europaposten-redaktionen
draft: ja
sources:
  - Kildens navn | https://eksempel.dk/link
---

Brødtekst i Markdown. Skriv i egne ord, og henvis til kilderne.

## Mellemrubrik

Fjern linjen 'draft: ja' (eller sæt 'draft: nej'), når artiklen er klar til udgivelse.
""", encoding="utf-8")
    print(f"Oprettet: {path.relative_to(ROOT)}")


def serve(port=8080):
    import functools, http.server
    build()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Kører på http://localhost:{port}/  (Ctrl+C for at stoppe)")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        build()
    elif args[0] == "ny" and len(args) >= 2:
        new_article(args[1], args[2] if len(args) > 2 else "politik")
    elif args[0] == "serve":
        serve(int(args[1]) if len(args) > 1 else 8080)
    else:
        print(__doc__)
