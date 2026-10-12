---
title: "Hackere ramte Danfoss-køl i franske supermarkeder – EU's nye indberetningspligt gælder også gamle anlæg"
slug: danfoss-koel-hackerangreb-frankrig-cra
date: 2026-10-12 18:50
section: forsvar
type: Nyhed
kicker: Cybersikkerhed
author: Europaposten-redaktionen
summary: Hundredvis af franske supermarkeder har smidt frost- og kølevarer ud, efter at hackere fik køleanlæg styret af Danfoss-systemer til at varme op. Danfoss siger, at de fleste ramte anlæg er ældre produkter, og at flere af dem ikke længere får sikkerhedsopdateringer. Men siden 11. september skal producenter efter EU's forordning om cyberrobusthed indberette aktivt udnyttede sårbarheder inden for 24 timer – også i produkter, der blev solgt for mange år siden.
draft: nej
illustration: danfoss-hovedsaede-nordborg-2008.jpg
illustration_alt: Danfoss' hovedsæde i Nordborg på Als, en lang hvid kontorbygning med en høj glasfacade
illustration_caption: Danfoss' hovedsæde i Nordborg på Als. Arkivfoto fra maj 2008.
illustration_photographer: Schnatzel
illustration_license: Public domain
illustration_source: https://commons.wikimedia.org/wiki/File:Danfoss_Hauptgeb%C3%A4ude_in_Nordborg.jpg
illustration_credit: Foto: Schnatzel via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Danfoss_Hauptgeb%C3%A4ude_in_Nordborg.jpg), public domain. Beskåret af Europaposten.
sources:
  - Ritzau via Berlingske: Danfoss-systemer ramt i cyberangreb på franske supermarkeder (12. oktober 2026) | https://www.berlingske.dk/business/danfoss-systemer-ramt-i-cyberangreb-paa-franske-supermarkeder
  - AFP: French supermarkets suffer refrigerator shutdown after 'unprecedented' cyberattack (12. oktober 2026) | https://www.afp.com/en/french-supermarket-chains-say-cyberattack-forced-refrigerator-shutdown
  - BFMTV: Au moins 300 supermarchés touchés, un système danois visé (12. oktober 2026) | https://www.bfmtv.com/economie/entreprises/au-moins-300-supermarches-touches-un-systeme-danois-vise-ce-que-l-on-sait-des-cyberattaques-qui-ont-frappe-les-systemes-frigorifiques-des-supermarches_AV-202610120616.html
  - Dominique Schelcher (adm. direktør, Coopérative U) på X (12. oktober 2026) | https://x.com/schelcher/status/2109564928881308012
  - Christophe Hansen (EU-kommissær for landbrug og fødevarer) på X (12. oktober 2026) | https://x.com/CHansenEU/status/2109597651390071291
  - Danfoss: Security advisories (liste over sikkerhedsadvarsler) | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/
  - Danfoss: DSA-2023-08-01, AK-SM 800A (21. august 2023) | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2023-08-01/
  - Danfoss: DSA-2025-03-01, CVE-2025-41450 (24. marts 2025) | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2025-03-01/
  - Danfoss: DSA-2025-08-01, CVE-2025-41451/41452 (1. august 2025) | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2025-08-01/
  - Danfoss: Coordinated vulnerability disclosure | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/
  - Claroty Team82: Freeze the Controller, Defrost the Food (9. august 2026) | https://claroty.com/team82/research/freeze-the-controller-defrost-the-food-uncovering-vulnerabilities-in-danfoss-refrigeration-controllers
  - Forordning (EU) 2024/2847 om cyberrobusthed (Cyber Resilience Act), EUT L 20.11.2024 – art. 13, 14, 64, 69, 71 og bilag I | https://eur-lex.europa.eu/eli/reg/2024/2847/oj/dan
  - Europa-Kommissionen: Cyber Resilience Act – Reporting obligations | https://digital-strategy.ec.europa.eu/en/policies/cra-reporting
  - Europa-Kommissionen: Cyber Resilience Act implementation – FAQ, version 1.1 (december 2025), afsnit 1.4 og 5.3 | https://digital-strategy.ec.europa.eu/en/library/cyber-resilience-act-implementation-frequently-asked-questions
  - Styrelsen for Samfundssikkerhed: Nu skal virksomheder i hele EU underrette om digitale sårbarheder i produkter (11. september 2026) | https://samsik.dk/artikler/2026/09/nu-skal-virksomheder-i-hele-eu-underrette-om-digitale-saarbarheder-i-produkter/
  - HowTheyVote.eu: Europa-Parlamentets afstemning om Cyber Resilience Act (12. marts 2024) | https://howtheyvote.eu/votes/166177
---

Natten til mandag begyndte køle- og frostdiske i hundredvis af franske supermarkeder at varme op. Hackere havde ifølge BFMTV fået styringssystemerne til at køre en tvungen afrimning i timevis, og om morgenen måtte butikkerne smide friske varer og frostvarer ud. Kæderne E. Leclerc, Intermarché og Coopérative U [har bekræftet angrebet over for AFP](https://www.afp.com/en/french-supermarket-chains-say-cyberattack-forced-refrigerator-shutdown), og anklagemyndigheden i Paris har indledt en efterforskning.

Systemerne kommer fra den danske industrikoncern Danfoss fra Nordborg på Als. Danfoss bekræfter i [en skriftlig udtalelse til Ritzau](https://www.berlingske.dk/business/danfoss-systemer-ramt-i-cyberangreb-paa-franske-supermarkeder), at et »begrænset antal« af selskabets kølestyringssystemer er ramt, og at »størstedelen af de berørte systemer er ældre produkter«.

> Danfoss er bekendt med hændelserne i Frankrig, der har berørt et begrænset antal kølestyringssystemer. Vi tager situationen alvorligt og er i tæt dialog med de berørte kunder for at hjælpe dem med at håndtere den.
> — [Danfoss i skriftlig udtalelse til Ritzau](https://www.berlingske.dk/business/danfoss-systemer-ramt-i-cyberangreb-paa-franske-supermarkeder) 12. oktober 2026

Sagen sætter fokus på en ny EU-regel for Danfoss og andre danske producenter af netforbundne produkter. Siden 11. september skal producenter efter EU's forordning om cyberrobusthed, Cyber Resilience Act (CRA), indberette sårbarheder, som hackere aktivt udnytter, og pligten gælder også for produkter, der blev solgt for mange år siden.

:::fakta Det ved vi – og det ved vi ikke
- **Vi ved:** Natten til 12. oktober blev køleanlæg i hundredvis af franske supermarkeder manipuleret, og varer måtte kasseres. Leclerc, Intermarché og Coopérative U har bekræftet angrebet.
- **Vi ved:** Danfoss bekræfter, at et begrænset antal af selskabets kølestyringssystemer er ramt, og at de fleste er ældre produkter. Flere af dem får ikke længere sikkerhedsopdateringer.
- **Vi ved:** Efter CRA's artikel 14 og 69 skal producenter siden 11. september 2026 indberette aktivt udnyttede sårbarheder inden for 24 timer – også i produkter, der kom på markedet før reglerne.
- **Vi ved ikke:** Hvem der står bag, og hvilken sårbarhed angriberne udnyttede. Ingen af de kilder, Europaposten har læst, har knyttet angrebet til en bestemt fejl.
- **Vi ved ikke:** Om Danfoss har indberettet sagen efter CRA. Danfoss' udtalelser til medierne nævner det ikke.
- **Vi ved ikke:** Hvor mange Danfoss-anlæg der er ramt, og om butikker uden for Frankrig er ramt. Europaposten har ikke fundet oplysninger om ramte butikker i Danmark.
:::

## Op til 50 grader i kølediskene

Det præcise omfang er stadig uklart, og kæderne har givet forskellige tal. Les Mousquetaires, der ejer Intermarché og Netto, har ifølge Ritzau sagt til Reuters, at 150 butikker blev ramt, og at køleskabene blev varmet op til 50 grader i seks timer. Over for AFP og BFMTV har kæderne talt om mindst 300 Intermarché- og Netto-butikker, omkring 100 af Coopérative U's butikker og flere E. Leclerc-butikker. En kilde i branchen siger til [BFMTV](https://www.bfmtv.com/economie/entreprises/au-moins-300-supermarches-touches-un-systeme-danois-vise-ce-que-l-on-sait-des-cyberattaques-qui-ont-frappe-les-systemes-frigorifiques-des-supermarches_AV-202610120616.html), at tabet kan løbe op i flere millioner euro. Carrefour Market og Monoprix nævnes også af et fransk branchemedie, men de to kæder har ikke selv bekræftet det.

Anklagemyndigheden i Paris skal ifølge AFP kortlægge ofrene og sammenhængen med de tab af fødevarer og de brande, butikkerne har anmeldt. Coopérative U's administrerende direktør, Dominique Schelcher, [skriver på X](https://x.com/schelcher/status/2109564928881308012), at angrebet er »af yderste alvor« og »uden fortilfælde«, fordi det rammer udstyr, der er afgørende for franskmændenes fødevareforsyning (Europapostens oversættelse).

EU's kommissær for landbrug og fødevarer, luxembourgske Christophe Hansen, [fordømmer angrebet på X](https://x.com/CHansenEU/status/2109597651390071291). Han skriver, at fødevaresikkerheden kræver mere opmærksomhed på alle niveauer, »for instrumentaliseringen af fødevarer er blevet en realitet« (Europapostens oversættelse).

## Kendte huller i Danfoss' systemer

En person tæt på den franske premierminister, Sébastien Lecornu, siger ifølge AFP og BFMTV, at det franske cybersikkerhedsagentur ANSSI har fundet en sårbarhed i software fra Danfoss og har kontaktet virksomheden. Ifølge samme kilde er ANSSI i kontakt med sine europæiske kolleger, fordi andre lande kan være ramt.

Danfoss oplyser til BFMTV, at de fleste ramte anlæg er ældre produkter, især AK-SM800- og AK-SC355-systemer, som er udtjente og ikke længere får software- eller sikkerhedsopdateringer. De ramte anlæg af den nyere model AK-SM800A kørte med forældet firmware. Danfoss har »gennem flere år anbefalet kunder at skifte til nyere løsninger« og at holde de systemer, der stadig understøttes, opdateret, skriver selskabet til Ritzau. Danfoss' egne it-systemer og drift er ikke ramt.

Sårbarheder i AK-SM 800A-serien har været kendt i flere år. På [Danfoss' egen liste over sikkerhedsadvarsler](https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/) står tre advarsler om serien. [I august 2023](https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2023-08-01/) advarede selskabet om fejl, der kunne føre til »fuld kompromittering« af systemet. [I marts 2025](https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2025-03-01/) kom en advarsel om en fejl, der gjorde det muligt at omgå login-kontrollen. [I august 2025](https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/dsa-2025-08-01/) fulgte en advarsel om en fejl, der kunne lade en angriber, som allerede var logget ind, køre kommandoer på systemet. Til alle tre har Danfoss udsendt opdateringer.

I august i år offentliggjorde sikkerhedsfirmaet Claroty, der fandt de seneste fejl, [en gennemgang af dem](https://claroty.com/team82/research/freeze-the-controller-defrost-the-food-uncovering-vulnerabilities-in-danfoss-refrigeration-controllers). Ved en søgning i tjenesten Censys fandt Claroty 2.765 AK-SM 800A-enheder, der kunne nås direkte fra internettet. Europaposten ved ikke, om nogen af de kendte fejl blev brugt i angrebet.

## Hvad kræver EU-loven?

[Forordningen om cyberrobusthed](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/dan) blev vedtaget i 2024 og gælder fuldt ud fra 11. december 2027. En del af den gælder dog allerede nu. Efter artikel 71 har indberetningspligten i artikel 14 gældet siden 11. september 2026, og [ifølge Kommissionen](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting) har ENISA's fælles indberetningsplatform været i drift siden samme dag.

Pligten gælder, når en producent får kendskab til en »aktivt udnyttet sårbarhed« i sit produkt. Det betyder, at der er pålidelig dokumentation for, at en ondsindet aktør har udnyttet fejlen i et system uden ejerens tilladelse. Producenten skal så indsende en tidlig varsling senest 24 timer efter at have fået kendskab til fejlen og en egentlig meddelelse senest 72 timer efter. En endelig rapport skal følge senest 14 dage efter, at der findes en rettelse. Indberetningen går via platformen til CSIRT'en, den nationale it-sikkerhedsenhed, i det land, hvor producenten træffer sine beslutninger om cybersikkerhed, og samtidig til EU's cybersikkerhedsagentur ENISA. Alvorlige hændelser, der påvirker et produkts sikkerhed, skal indberettes på samme måde.

Det er afgørende for Danfoss-sagen, at de fleste af forordningens krav ikke gælder for produkter, der kom på markedet før 11. december 2027. Indberetningspligten er dog en undtagelse. Efter artikel 69, stk. 3, gælder pligten i artikel 14 for »alle produkter med digitale elementer«, der er omfattet af forordningen, og som er bragt i omsætning før den dato. Kommissionens tjenestegrene skriver i deres [FAQ om forordningen](https://digital-strategy.ec.europa.eu/en/library/cyber-resilience-act-implementation-frequently-asked-questions), at producenten af ældre produkter skal indberette sårbarheden eller hændelsen, men at forordningens øvrige krav, fx om håndtering af sårbarheder, ikke gælder for dem. Hverken forordningen eller FAQ'en undtager produkter, som producenten er holdt op med at opdatere.

Pligten gælder kun hændelser, som producenten får kendskab til efter 11. september 2026. Producenten skal også orientere de berørte brugere, og hvis det ikke sker i tide, kan CSIRT'en selv orientere dem. Forordningens bødeparagraf, artikel 64, giver mulighed for bøder på op til 15 millioner euro eller 2,5 procent af den globale omsætning for brud på bl.a. artikel 14. Den er dog ikke blandt de bestemmelser, der gælder før 11. december 2027.

Danfoss skriver på sin [side om håndtering af sårbarheder](https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/), at selskabet håndterer sårbarheder og sikkerhedshændelser i overensstemmelse med gældende regler, »herunder EU Cyber Resilience Act«. Selskabet har ikke offentligt oplyst, om det har indberettet hændelserne i Frankrig.

## Hvad betyder det for danske producenter?

Reglerne rammer langt flere end Danfoss. [Styrelsen for Samfundssikkerhed skriver](https://samsik.dk/artikler/2026/09/nu-skal-virksomheder-i-hele-eu-underrette-om-digitale-saarbarheder-i-produkter/), at de omfatter alt fra varmepumper og netforbundet køkkenudstyr til software og hardware.

Fra 11. december 2027 skal nye produkter desuden opfylde forordningens sikkerhedskrav i bilag I. De skal blandt andet sælges uden kendte sårbarheder, der kan udnyttes, have en sikker standardindstilling og kunne rettes med sikkerhedsopdateringer. Producenten skal fastsætte en supportperiode, som efter artikel 13 som udgangspunkt er på mindst fem år. Produkter, der allerede er solgt inden da, behøver ikke leve op til kravene, medmindre de bliver væsentligt ændret.

Forordningen fik bred opbakning blandt de danske medlemmer af Europa-Parlamentet, da Parlamentet [godkendte den endelige aftale 12. marts 2024](https://howtheyvote.eu/votes/166177) med 517 stemmer for, 12 imod og 78, der hverken stemte for eller imod. Elleve af de dengang 14 danske medlemmer stemte for, og tre stemte ikke. Blandt dem, der stemte for og stadig sidder i Parlamentet, er Christel Schaldemose (S), Niels Fuglsang (S) og Morten Løkkegaard (V).

Europaposten har mandag ikke fundet reaktioner på angrebet fra regeringen eller de danske medlemmer af Europa-Parlamentet.

Den franske anklagemyndigheds efterforskning er i gang, og ANSSI leder efter flere ramte virksomheder. Europaposten følger sagen og opdaterer artiklen, når Danfoss, ANSSI eller EU-institutionerne oplyser mere.
