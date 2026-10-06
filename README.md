# Europaposten – nyheder om EU-politik med dansk vinkel

Et lille, statisk nyhedssite. Artikler skrives som Markdown-filer, og et Python-script (`build.py`) laver hele hjemmesiden: forside, artikelsider, sektionssider, arkiv, "Om os", RSS-feed og sitemap.

**Krav:** Python 3.9 eller nyere. Ingen andre programmer eller pakker skal installeres.

## Mappestruktur

```
eu-nyheder/
├── build.py              # site-generatoren
├── config.ini            # sitets navn, adresse, sektioner m.m.
├── content/artikler/     # én .md-fil pr. artikel
├── static/               # style.css og favicon
├── public/               # det færdige site (laves af build.py – ret ikke her)
├── content/kladder/      # kladder (ignoreres af git – kommer aldrig i det offentlige repo)
└── .github/workflows/    # automatisk udgivelse på GitHub Pages
```

## Sådan tilføjer du en ny artikel

1. Opret en skabelon (vælg sektion: `politik`, `oekonomi`, `migration`, `klima-miljoe`, `forsvar`):

   ```bash
   python3 build.py ny "Overskriften på artiklen" politik
   ```

   Det laver en fil i `content/artikler/` med dags dato i navnet.

2. Åbn filen og udfyld felterne øverst (front matter):

   ```yaml
   ---
   title: Overskriften på artiklen
   slug: kort-url-navn            # valgfri – bliver til /artikler/kort-url-navn/
   date: 2026-10-04 08:00         # dato og klokkeslæt (dansk tid)
   section: politik
   kicker: Europa-Parlamentet     # valgfri lille overrubrik
   summary: Manchet på 1-2 sætninger, som vises på forsiden.
   author: Europaposten-redaktionen
   featured: ja                   # valgfri – gør artiklen til forsidens tophistorie
   draft: ja                      # kladder bygges ikke; skriv nej, når artiklen skal udgives
   sources:
     - Kildens navn og titel | https://link-til-kilden
     - Endnu en kilde | https://...
   ---
   ```

3. Skriv brødteksten under den sidste `---` i almindelig Markdown:
   `## Mellemrubrik`, `**fed**`, `*kursiv*`, `[linktekst](https://...)`, `> citat` og punktlister med `- `.

4. Byg sitet og se resultatet lokalt:

   ```bash
   python3 build.py serve      # åbn http://localhost:8080
   ```

   Eller kun byg: `python3 build.py`. Scriptet skriver også, hvor mange artikler der er udgivet i dag (målet er 3).

### Godkendelse af artikler (pull requests)

Repositoriet er offentligt, så kladder må ikke ligge på `main`. Arbejdsgangen er:

1. Kladder ligger lokalt i `content/kladder/` (ignoreres af git).
2. Dagens artikler lægges i `content/artikler/` med `draft: nej` på en gren, fx `artikler/2026-10-06`, og der oprettes en pull request til `main`.
3. Redaktøren læser artiklerne i pull requesten (også fra mobilen) og merger, når de er godkendt. Merge til `main` udgiver automatisk sitet.

Skriv aldrig interne noter (`#`-linjer i front matter) i filer, der skal i det offentlige repository.

### Redaktionelle regler (vigtigt for troværdigheden)

- Skriv altid i egne ord – kopiér ikke tekst fra andre medier.
- Brug kun tal og citater, der står i kilderne, og skriv hvem der har sagt det ("siger X til Ritzau").
- Kan noget ikke bekræftes, så udelad det.
- Alle artikler skal have mindst én kilde – helst en primærkilde (EU-institution, ministerium, Folketinget).
- Ret fejl åbent, og tilføj `updated: 2026-10-04 12:00` i front matter, når en artikel ændres.

## Indstillinger (`config.ini`)

- `navn`, `undertitel`, `beskrivelse`: sitets navn og tekster.
- `base_url`: den rigtige adresse, når sitet er online (fx `https://europaposten.dk`). Bruges i RSS og sitemap.
- `kontakt_email`: vises i "Om os" og under artiklerne.
- `vis_annoncepladser = ja`: viser de markerede annoncepladser (stiplede bokse) til layout-test. Der er **ingen** annoncekode i sitet. Pladserne ligger i `build.py` (søg efter `ANNONCEPLADS`): forside-banner, forside-sidebar, artikel-midt og artikel-bund.
- `[sektioner]`: tilføj eller omdøb sektioner (slug = visningsnavn).

## Udgivelse (gratis)

Mappen `public/` er hele sitet og kan lægges på enhver statisk webhost.

### GitHub Pages (sådan kører Europaposten)
- Repository: `europaposten/europaposten`, gren `main`.
- *Settings → Pages → Source: GitHub Actions*. Custom domain: `europaposten.dk`.
- Hvert push/merge til `main` bygger og udgiver sitet via `.github/workflows/pages.yml`.
- `build.py` skriver en `CNAME`-fil i `public/` ud fra `base_url` i `config.ini`. Ved udgivelse via GitHub Actions er det dog indstillingen *Custom domain* under Settings → Pages, der gælder.

### Alternativer
- **Cloudflare Pages:** forbind GitHub-repositoriet, build-kommando `python3 build.py`, output-mappe `public`. Gratis, hurtigt og god til eget domæne.
- **Netlify:** samme opsætning (build: `python3 build.py`, publish: `public`), eller træk `public/`-mappen ind på app.netlify.com/drop for en hurtig test.

Bemærk: Siden "404.html" bruger links fra domænets rod (`/`) og virker derfor bedst med eget domæne eller Cloudflare/Netlify.

## Senere: annoncer og affiliate
Når der er trafik, kan der indsættes annonce- eller affiliate-kode på de markerede pladser. Husk så samtidig en cookie-/samtykkeløsning (GDPR) og tydelig markering af kommercielt indhold – og opdatér afsnittet om privatliv på "Om os".
