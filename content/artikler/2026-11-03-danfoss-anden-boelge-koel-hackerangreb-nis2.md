---
title: "Ny bølge af hackerangreb på Danfoss-køl – fem danske virksomheder ramt, men supermarkeder står uden for EU's cyberlov"
slug: danfoss-anden-boelge-koel-hackerangreb-nis2
date: 2026-11-03 18:05
section: forsvar
type: Nyhed
kicker: Cybersikkerhed
author: Europaposten-redaktionen
summary: Natten til mandag blev køle- og frostanlæg i butikker i mindst syv europæiske lande varmet op til omkring 50 grader. Danfoss bekræfter, at selskabets produkter er involveret, og fem danske virksomheder er ramt. Tre uger efter angrebet i Frankrig står hundredvis af kølestyringer stadig åbent på internettet. EU's cyberlov NIS2 dækker som udgangspunkt ikke supermarkeder, mens producenter som Danfoss har pligt til at indberette aktivt udnyttede sårbarheder.
featured: nej
draft: nej
illustration: 2026-11-03-danfoss-storeview-eksponering.png
illustration_alt: Søjlediagram over Danfoss StoreView-kølestyringer, der kan nås direkte fra internettet 2. november 2026, fordelt på firmwareversion. Frankrig har 220 anlæg, hvoraf 45 procent kører en version før 4.2, 13 procent version 4.2.4 og 41 procent version 4.3.1 eller nyere. Belgien har 138 anlæg: 28, 4 og 68 procent. Holland har 51 anlæg: 41, 22 og 37 procent. Sverige har 50 anlæg: 38, 4 og 58 procent.
illustration_caption: I Frankrig er antallet af åbne Danfoss-styringer faldet fra 1.825 før angrebet i oktober til 220. Men i alle fire lande kører en stor del stadig ældre firmware.
illustration_credit: "Grafik: Europaposten. Kilde: [Censys ARC](https://censys.com/blog/european-refrigerator-controller-redux-a-new-wave-of-refrigeration-attacks/), 2. november 2026."
sources:
  - DR, Det ved vi om hackerangreb på europæiske supermarkeder, 2. november 2026 | https://www.dr.dk/nyheder/udland/det-ved-vi-om-hackerangreb-paa-europaeiske-supermarkeder
  - DR, Danfoss-produkter ramt af hackerangreb mod frysere i Europa, 2. november 2026 | https://www.dr.dk/nyheder/penge/danfoss-produkter-ramt-af-hackerangreb-mod-frysere-i-europa
  - TV 2, Frysere og køleskabe hacket i flere europæiske supermarkeder (liveblog), 2. november 2026 | https://nyheder.tv2.dk/live/samfund/2026-11-02-frysere-og-koeleskabe-hacket-i-flere-europaeiske-supermarkeder/danfoss-koelesystemer-ramt-i-cyberangreb?entry=8c5bd38d-de31-49ea-9603-ccab9e391b20
  - BBC, Shop freezers in seven European countries hit by cyber-attack, 2. november 2026 | https://www.bbc.com/news/articles/cq1kd1nee80eo
  - The Hacker News, New Wave of Refrigeration Cyberattacks Hits Supermarkets Across Europe, 3. november 2026 | https://thehackernews.com/2026/11/second-wave-of-cyberattacks-hits.html
  - Censys ARC, European refrigerator controller redux, 2. november 2026 | https://censys.com/blog/european-refrigerator-controller-redux-a-new-wave-of-refrigeration-attacks/
  - Styrelsen for Samfundssikkerhed, Styrelsen følger sagen om cyberangreb mod køle- og frysesystemer i Europa, 2. november 2026 | https://samsik.dk/artikler/2026/11/styrelsen-for-samfundssikkerhed-foelger-sagen-om-cyberangreb-mod-koele-og-frysesystemer-i-europa/
  - NIS 2-loven (lov nr. 434 af 6. maj 2025), bilag 2, pkt. 4 | https://www.lovguiden.dk/loven/nis-2-loven/bilag-2
  - Fødevarestyrelsen, Kontrol af cybersikkerhed i fødevarevirksomheder: NIS 2-loven | https://foedevarestyrelsen.dk/kost-og-foedevarer/kontrol/cybersikkerhed-nis-2
  - DI Produktion, Har din virksomhed fået brev om NIS2?, august 2026 | https://www.danskindustri.dk/brancher/di-produktion/nyheder/Udsendelser/2026/august/har-din-virksomhed-faet-brev-om-nis2/
  - Forordning (EU) 2024/2847 om cyberrobusthed, art. 14, 69 og 71 | https://eur-lex.europa.eu/eli/reg/2024/2847/oj/dan
  - Europa-Kommissionen, Cyber Resilience Act – Reporting obligations | https://digital-strategy.ec.europa.eu/en/policies/cra-reporting
  - Europaposten, Hackere ramte Danfoss-køl i franske supermarkeder, 12. oktober 2026 | https://europaposten.dk/artikler/danfoss-koel-hackerangreb-frankrig-cra/
---

Tre uger efter angrebet på franske supermarkeder er det sket igen. Natten til mandag blev køle- og frostanlæg i butikker i Belgien, Luxembourg, Sverige, Irland, Holland, Estland og Finland sat til at varme, i flere tilfælde op til omkring 50 grader, [skriver BBC](https://www.bbc.com/news/articles/cq1kd1nee80eo). Butikkerne har måttet smide fødevarer for store beløb ud.

Den danske industrikoncern Danfoss fra Nordborg er igen i centrum. »Vi kan bekræfte, at de hændelser, der er blevet rapporteret i flere europæiske lande, også involverer vores produkter,« skriver Danfoss [til DR](https://www.dr.dk/nyheder/udland/det-ved-vi-om-hackerangreb-paa-europaeiske-supermarkeder).

Danmark er heller ikke gået fri. Styrelsen for Samfundssikkerhed har kendskab til fem danske virksomheder, der er ramt, men det er lykkedes dem »ganske hurtigt at komme af med hackerne«, siger kontorchef Morten Bro [til TV 2](https://nyheder.tv2.dk/live/samfund/2026-11-02-frysere-og-koeleskabe-hacket-i-flere-europaeiske-supermarkeder/danfoss-koelesystemer-ramt-i-cyberangreb?entry=8c5bd38d-de31-49ea-9603-ccab9e391b20).

Dansk Industris chefkonsulent Jeppe Engell har over for TV 2 fortalt om angreb på en dansk fødevareproducent, hvor leverandøren nåede at stoppe angrebet, og på en cateringvirksomhed og en biotekvirksomhed. Salling Group og Coop melder om normal drift i deres danske butikker.

:::fakta Det ved vi – og det ved vi ikke
- **Vi ved:** Butikker i mindst syv europæiske lande blev ramt natten til 2. november. Danfoss bekræfter, at selskabets produkter er involveret.
- **Vi ved:** Fem danske virksomheder er ramt ifølge Styrelsen for Samfundssikkerhed. Dansk Industri har fortalt om angreb på en fødevareproducent, en cateringvirksomhed og en biotekvirksomhed. Salling Group og Coop melder om normal drift.
- **Vi ved:** Lidt over 1.000 Danfoss StoreView-styringer kunne 2. november nås direkte fra internettet, og en stor del kører ældre firmware, viser en opgørelse fra Censys.
- **Vi ved ikke:** Hvem der står bag, og om det er de samme som i Frankrig. Ingen har taget ansvaret.
- **Vi ved ikke:** Om angriberne har udnyttet en sårbarhed i softwaren eller blot styringer, der stod åbent. Europaposten har ikke fundet en ny sikkerhedsadvarsel fra Danfoss om angrebene.
:::

## Fra Sjöbo til Mons

Omfanget er mindre end i Frankrig i oktober, hvor hundredvis af butikker blev ramt, men angrebene er spredt over flere lande. I Belgien har den føderale anklagemyndighed indledt en strafferetlig efterforskning, efter at mindst 76 supermarkeder hos blandt andre Delhaize, Carrefour, Spar, Ikea og Intermarché er ramt, oplyser DR med henvisning til det belgiske medie HLN. I Sverige er syv af Coops cirka 800 butikker ramt, og i Irland 13 af SuperValus butikker, skriver BBC. I Holland er mindst 17 virksomheder angrebet, blandt andet slagtere og små dagligvarebutikker, har Danfoss oplyst til det hollandske NOS.

En Delhaize-butik i Hoeilaart i Flandern har ifølge HLN mistet varer for 100.000 euro, mens butikschefen i en ramt ICA-butik i svenske Sjöbo ifølge DR har smidt mad ud for op mod en million svenske kroner.

EU's kommissær for landbrug og fødevarer, Christophe Hansen, kalder ifølge Reuters, som TV 2 gengiver, angrebene et bevidst forsøg på at forstyrre EU's fødevareforsyning og svække forbrugernes tillid til den. Fødevaresikkerheden i EU-landene er ikke i fare i øjeblikket, men der er et alvorligt madspild, siger han.

## Advarslerne var sendt ud

Ifølge Danfoss kunne mange af angrebene have været undgået. Efter angrebet i Frankrig rådede selskabet sine kunder til at tage styringerne af internettet og kun koble dem på igen via et sikkert netværk. »De fleste butikker reagerede dengang, men en lille gruppe gjorde ikke, og nu bliver de ramt af konsekvenserne,« siger Danfoss' talsmand i Holland ifølge NOS, [gengivet af DR](https://www.dr.dk/nyheder/penge/danfoss-produkter-ramt-af-hackerangreb-mod-frysere-i-europa).

Sikkerhedsfirmaet Censys har siden oktober talt de Danfoss-styringer af typen StoreView, som kan nås direkte fra internettet. [Mandag fandt firmaet](https://censys.com/blog/european-refrigerator-controller-redux-a-new-wave-of-refrigeration-attacks/) lidt over 1.000 på verdensplan. I Frankrig er tallet faldet fra 1.825 før angrebet i oktober til 220, men kun 41 procent af dem kører en opdateret firmwareversion. I Belgien er andelen 68 procent, i Sverige 58 procent og i Holland 37 procent.

Det belgiske firma Sabcobel, der driver Delhaizes anlæg, siger til nyhedsbureauet Belga, at nogle af de ramte enheder kræver fysiske ændringer og ikke kun en softwareopdatering, skriver BBC.

## Supermarkeder er som udgangspunkt uden for NIS2

Styrelsen for Samfundssikkerhed opfordrer [i en meddelelse](https://samsik.dk/artikler/2026/11/styrelsen-for-samfundssikkerhed-foelger-sagen-om-cyberangreb-mod-koele-og-frysesystemer-i-europa/) virksomheder til at undersøge, om køle- og frysestyringer står direkte på internettet, opdatere udstyret, begrænse fjernadgangen og politianmelde tegn på angreb. Virksomheder, der er omfattet af NIS2, skal desuden indberette hændelsen på virk.dk.

Men NIS2, EU's direktiv om cybersikkerhed, som Danmark har gennemført med [NIS 2-loven](https://www.lovguiden.dk/loven/nis-2-loven/bilag-2) fra maj 2025, dækker kun en del af fødevarekæden. Efter lovens bilag 2 er fødevarevirksomheder omfattet, når de beskæftiger sig med engrosdistribution og industriel produktion og tilvirkning. De skal også have mindst 50 årsværk eller en årlig omsætning og balance over 75 millioner kroner, [oplyser Fødevarestyrelsen](https://foedevarestyrelsen.dk/kost-og-foedevarer/kontrol/cybersikkerhed-nis-2), der fører tilsyn på området.

Detailhandel, restauranter og cateringvirksomheder falder derfor som udgangspunkt uden for NIS2-lovens fødevaresektor, [skriver DI Produktion](https://www.danskindustri.dk/brancher/di-produktion/nyheder/Udsendelser/2026/august/har-din-virksomhed-faet-brev-om-nis2/). Det betyder, at et supermarked, der får sine køleanlæg hacket, ikke har pligt til at indberette hændelsen efter NIS2 som fødevarevirksomhed, mens en stor industriel fødevareproducent eller grossist har. I Sverige ramte angrebet også frysere på et distributionscenter hos dagligvarekoncernen Axfood, oplyser TV 2 med henvisning til Reuters.

Selvstændig cybersikkerhedsrådgiver David Ulrik Kristiansen siger til TV 2, at ansvaret ligger hos den, der driver butikken, men at leverandøren skal levere anlægget sikkert og holde det opdateret. »Det er også dér, kæden typisk knækker,« siger han.

## Producentens pligt

For Danfoss gælder en anden EU-regel. Efter [forordningen om cyberrobusthed](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/dan) (Cyber Resilience Act) skal producenter siden 11. september 2026 indberette aktivt udnyttede sårbarheder i deres produkter med en tidlig varsling senest 24 timer efter, at de har fået kendskab til dem. Efter artikel 69, stk. 3, gælder pligten også produkter, der kom på markedet før forordningens øvrige krav træder i kraft i december 2027. Indberetningen sker via en fælles platform, som [Kommissionen oplyser](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting) har været i drift siden 11. september.

Pligten udløses kun, hvis angriberne har udnyttet en sårbarhed i produktet. Det er uklart, om det er sket, eller om de blot har fået adgang til styringer, der stod åbent på nettet. Danfoss' liste over sikkerhedsadvarsler indeholdt tirsdag ingen advarsel om angrebene, [skriver The Hacker News](https://thehackernews.com/2026/11/second-wave-of-cyberattacks-hits.html). Danfoss har ikke offentligt oplyst, om selskabet har indberettet hændelserne efter forordningen, hverken efter angrebet i Frankrig, [som Europaposten skrev om 12. oktober](https://europaposten.dk/artikler/danfoss-koel-hackerangreb-frankrig-cra/), eller nu.

Europaposten har tirsdag ikke fundet reaktioner fra regeringen eller de danske medlemmer af Europa-Parlamentet. Belgiens og Sveriges nationale cybersikkerhedsmyndigheder følger sagen, og i Danmark er Styrelsen for Samfundssikkerhed i dialog med virksomheder og myndigheder for at afdække, om flere danske virksomheder er berørt.
