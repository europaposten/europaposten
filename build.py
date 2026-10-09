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
    sections = dict(cp["sektioner"])
    return site, sections


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
    _, fm, body = text.split("---", 2)
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


def markdown(md: str) -> str:
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
        elif st.startswith("#"):
            flush()
            level = min(len(st) - len(st.lstrip("#")), 4)
            level = max(level, 2)  # h1 er forbeholdt overskriften
            out.append(f"<h{level}>{inline_md(st.lstrip('#').strip())}</h{level}>")
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
        self.kicker = meta.get("kicker", "")
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
    <span class="topbar-links"><a href="{root}arkiv/">Arkiv</a><a href="{root}om-os/">Om os</a><a href="{root}rss.xml">RSS</a></span>
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
      <ul><li><a href="{root}om-os/">Om os og vores metode</a></li><li><a href="{root}redaktionelle-retningslinjer/">Redaktionelle retningslinjer</a></li><li><a href="{root}arkiv/">Arkiv</a></li><li><a href="{root}rss.xml">RSS-feed</a></li><li><a href="mailto:{esc(site['kontakt_email'])}">Kontakt / ret en fejl</a></li></ul>
    </div>
  </div>
  <p class="wrap fineprint">Artiklerne skrives med hjælp fra kunstig intelligens og gennemgås af redaktionen. Alle artikler linker til deres kilder. © {now.year} {esc(site['navn'])}</p>
</footer>
</body>
</html>
"""


def byline(a: Article, with_time=True):
    s = f'<span class="byline">Af {esc(a.author)}</span> · <time datetime="{a.date.isoformat()}">{dansk_dato(a.date, med_tid=with_time)}</time>'
    return s


def teaser(a: Article, root, size="normal"):
    kicker = esc(a.kicker or a.section_name)
    tag = "h2" if size == "lead" else "h3"
    return f"""<article class="teaser teaser-{size}">
  <a class="teaser-link" href="{root}{a.url}">
    <p class="kicker kicker-{a.section}">{kicker}</p>
    <{tag} class="teaser-title">{esc(a.title)}</{tag}>
    <p class="teaser-summary">{esc(a.summary)}</p>
  </a>
  <p class="meta">{byline(a, with_time=False)} · {a.minutes} min. læsning</p>
</article>"""


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
      <p class="kicker kicker-{a.section}">{esc(a.section_name)}</p>
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
    related = [x for x in arts if x is not a and x.section == a.section][:3]
    if len(related) < 3:
        related += [x for x in arts if x is not a and x not in related][: 3 - len(related)]
    rel_html = "".join(teaser(x, root, "small") for x in related)
    sources = "".join(
        f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(t)}</a></li>' for t, u in a.sources)
    updated = (f' · Opdateret <time datetime="{a.updated.isoformat()}">{dansk_dato(a.updated, med_tid=True)}</time>'
               if a.updated else "")
    abs_url = f"{site['base_url']}/{a.url}"
    og_image = ""
    ld_image = ""
    if a.illustration:
        img_abs = f"{site['base_url']}/billeder/{a.illustration}"
        og_image = f'\n<meta property="og:image" content="{esc(img_abs)}">'
        ld_image = f',"image":{json_str(img_abs)}'
    head = f"""<link rel="canonical" href="{esc(abs_url)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(a.title)}">
<meta property="og:description" content="{esc(a.summary)}">
<meta property="og:url" content="{esc(abs_url)}">
<meta property="og:locale" content="da_DK">{og_image}
<meta property="article:published_time" content="{a.date.isoformat()}">
<script src="{root}static/laes-op.js" defer></script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"NewsArticle","headline":{json_str(a.title)},"description":{json_str(a.summary)},"datePublished":"{a.date.isoformat()}","inLanguage":"da","author":{{"@type":"Organization","name":{json_str(a.author)}}},"publisher":{{"@type":"Organization","name":{json_str(site['navn'])}}}{ld_image}}}</script>"""
    content = f"""
<article class="story">
  <header class="story-head">
    <p class="kicker kicker-{a.section}"><a href="{root}sektion/{a.section}/">{esc(a.section_name)}</a></p>
    <h1>{esc(a.title)}</h1>
    {illustration_html(a, root)}
    <p class="standfirst">{esc(a.summary)}</p>
    <p class="meta">{byline(a)}{updated} · {a.minutes} min. læsning</p>
    <div class="laes-op" role="group" aria-label="Oplæsning af artiklen" hidden>
      <button type="button" class="laes-op-knap" aria-label="Læs artiklen op" aria-pressed="false"><svg class="laes-op-ikon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false"><path d="M3 9v6h4l5 4V5L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z" fill="currentColor"/></svg><span class="laes-op-tekst">Læs op</span></button>
      <button type="button" class="laes-op-stop" aria-label="Stop oplæsningen" hidden>Stop</button>
      <span class="laes-op-status visually-hidden" aria-live="polite"></span>
    </div>
  </header>
  <div class="story-body">
    {a.body_html}
    {ad_slot(site, "artikel-midt")}
  </div>
  <footer class="story-foot">
    <section class="sources">
      <h2>Kilder</h2>
      <ul>{sources}</ul>
    </section>
    <p class="ai-note">Denne artikel er skrevet med hjælp fra kunstig intelligens på baggrund af de nævnte kilder og gennemgået af redaktionen. Har du fundet en fejl? <a href="mailto:{esc(site['kontakt_email'])}">Skriv til os</a>. <a href="{root}om-os/">Læs om vores metode</a>.</p>
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
            f'<li><p class="kicker kicker-{a.section}">{esc(a.section_name)}</p><a href="{root}{a.url}"><h3>{esc(a.title)}</h3></a><p>{esc(a.summary)}</p></li>'
            for a in items)
        blocks += f'<section class="day"><h2 class="rubric">{dansk_dato(d, med_ugedag=True)}</h2><ul class="list">{lis}</ul></section>'
    if not blocks:
        blocks = "<p>Der er endnu ingen artikler her.</p>"
    content = f'<header class="page-head"><h1>{esc(title)}</h1><p>{esc(intro)}</p></header>{blocks}'
    return layout(site, sections, root, title, content, active=active)


def render_about(site, sections):
    root = "../"
    n = esc(site["navn"])
    content = f"""
<article class="story about">
  <header class="story-head"><h1>Om {n}</h1>
  <p class="standfirst">{n} er et lille, uafhængigt dansk nyhedssite om EU-politik. Vi forklarer, hvad beslutningerne i Bruxelles, Strasbourg og Luxembourg betyder for Danmark og danskerne.</p></header>
  <div class="story-body">
    <h2>Sådan arbejder vi</h2>
    <ul>
      <li><strong>Åbenhed om kunstig intelligens:</strong> Vores artikler skrives med hjælp fra kunstig intelligens. Et menneske vælger historierne, kontrollerer fakta mod kilderne og godkender teksten før udgivelse.</li>
      <li><strong>Altid kilder:</strong> Hver artikel slutter med en liste over de kilder, den bygger på – typisk EU-institutionernes egne pressemeddelelser, danske ministerier og etablerede nyhedsmedier. Vi opfordrer dig til at læse med i originalkilderne.</li>
      <li><strong>Ingen opdigtede citater eller tal:</strong> Vi bruger kun citater og tal, som fremgår af kilderne, og vi oplyser, hvem der har sagt hvad. Kan vi ikke bekræfte en oplysning, udelader vi den.</li>
      <li><strong>Fakta og holdning holdes adskilt:</strong> Vores nyhedsartikler er neutrale. Skulle vi en dag bringe analyser eller kommentarer, vil de være tydeligt markeret.</li>
      <li><strong>Redaktionelle retningslinjer:</strong> Læs, hvordan vi finder, vinkler og skriver EU-historier, i vores <a href="{root}redaktionelle-retningslinjer/">redaktionelle retningslinjer</a>.</li>
      <li><strong>Vi retter fejl:</strong> Finder du en fejl, så skriv til <a href="mailto:{esc(site['kontakt_email'])}">{esc(site['kontakt_email'])}</a>. Rettelser markeres i artiklen med dato.</li>
    </ul>
    <h2>Økonomi og uafhængighed</h2>
    <p>{n} drives som et privat sideprojekt. Sitet kan på sigt blive finansieret af annoncer eller affiliate-links. Hvis det sker, vil kommercielt indhold altid være tydeligt markeret og adskilt fra den redaktionelle dækning. {n} har ingen tilknytning til EU-institutionerne, politiske partier eller interesseorganisationer.</p>
    <h2>Privatliv</h2>
    <p>Sitet bruger i øjeblikket ingen cookies, ingen sporing og ingen eksterne skrifttyper.</p>
    <h2>Kontakt</h2>
    <p>Tips, rettelser og spørgsmål: <a href="mailto:{esc(site['kontakt_email'])}">{esc(site['kontakt_email'])}</a></p>
  </div>
</article>"""
    return layout(site, sections, root, "Om os", content)


PAGES = {"redaktionelle-retningslinjer": ROOT / "content" / "redaktionelle-retningslinjer.md"}


def render_page(site, sections, path: Path):
    """Simpel side (fx redaktionelle retningslinjer) fra Markdown med front matter."""
    root = "../"
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    title = meta.get("title", path.stem)
    upd = f'<p class="meta">Senest opdateret: {esc(meta["updated"])}</p>' if meta.get("updated") else ""
    content = f"""
<article class="story about">
  <header class="story-head"><h1>{esc(title)}</h1>
  <p class="standfirst">{esc(meta.get("summary", ""))}</p>{upd}</header>
  <div class="story-body">
{markdown(body)}
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
    urls = ["", "arkiv/", "om-os/"] + [f"{k}/" for k, v in PAGES.items() if v.exists()] + [f"sektion/{s}/" for s in sections] + [a.url for a in arts]
    body = "".join(f"<url><loc>{esc(site['base_url'])}/{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


# ---------------------------------------------------------------- build
def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build():
    site, sections = load_config()
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
    write(OUT / "om-os" / "index.html", render_about(site, sections))
    for slug, path in PAGES.items():
        if path.exists():
            write(OUT / slug / "index.html", render_page(site, sections, path))
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
