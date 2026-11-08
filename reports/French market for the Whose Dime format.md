# The Whose Dime format in French: most channels fail in both languages, and no French one has broken through yet

**Question (Franco, 2026-11-08):** how often do channels like the four Whose Dime references (Crayon Capital,
JunkBondInvestor, CEOzoned, Built On You) succeed in the French market?

**Answer.** Among new channels of the same format (company stories, collapses, scams, crises explained), measured
with the same method in both languages:

- **No French channel has broken through so far.** Of the 9 French channels at least 90 days old, **0 have a
  video at 100,000 views**. Of the 41 English channels at the same age, **15 do (37 %)**. Fisher's exact test,
  one-sided: p = 0.028. That is significant, but it rests on 9 French channels.
- **The typical channel fails in both languages.** The median channel gets about **2,400 long-video views a month**
  in French and in English alike. The gap is at the top. The best French channel (Dolus) gets **66,000 views a
  month**. The five best English ones get **440,000 to 1.37 million** (JunkBondInvestor is the first).
- **Money gap: about 20x at the top.** That is the view gap times an ad rate (RPM) about 1.5 to 3 times lower in
  France (third-party estimates).
- **What works in French is French stories.** The three French channels with the most views tell French or
  European scandals and the decline of French industry: Elf, the horse-meat lasagne scandal, the Vierzon factory,
  French tractors. The French translations of CEOzoned and Built On You get 0 to 219 views per video.

**Recommendation (inference).** Keep Whose Dime in English (D2). Do not open a French channel now: the measured
ceiling is too low. If a French test ever happens, use French scandals, not translated US brand stories.

Conventions: **measured** = YouTube Data API v3, 2026-11-08, or computed by me on the data file. **Estimate** =
a third-party figure with no published method. **Inference** = my reading.

## Method

1. **Search (measured).** I ran 8 queries in French (`relevanceLanguage=fr`, `regionCode=FR`) and their 8 English
   equivalents (`en`, `US`). Each query was sorted two ways: by views (the winners) and by date (active channels,
   small ones included; 4 to 20 min videos only). All searches cover videos published since 2025-01-01. The
   queries were "histoire de l'entreprise" / "company history", "l'histoire complète de" / "the entire history
   of", the fall of an empire, bankruptcy story, billion-dollar scam, financial crisis explained simply, and "the
   scandal that ruined". The searches returned 1,070 channels (410 FR, 660 EN).
2. **Videos (measured).** I collected every upload of the 763 channels with 300 videos or fewer: 48,612 videos.
   Larger channels are mostly media outlets and TV, not the same game.
3. **Filters.**
   - A long video is longer than 3 min and not a live.
   - Language: at least 60 % of the channel's audio tracks are in the target language.
   - Format: at least half of a channel's long-video titles name a company, a brand or money (regex), and the
     channel has at least 3 long videos.
   - I then read the titles by hand and removed 16 FR and 34 EN channels in another format: advice, interviews,
     fiction, crime news, POV simulations, stock picks.
   - Kept: **22 FR and 129 EN channels**. All 22 French channels and 125 English ones started in 2025 or later.
4. **Cohort.** Success needs time, so the rates use the channels whose first long video is **at least 90 days
   old**: 9 FR and 41 EN. The younger ones (13 FR, 84 EN) are reported apart.
5. **Quota.** About 6,100 units (search 3,200).
6. **Files.** Data: [`data/french_market_2026-11-08.csv`](data/french_market_2026-11-08.csv). Scripts:
   [`data/french_market_tools/`](data/french_market_tools/). Run them in this order, with `YOUTUBE_API_KEY` set:
   `search.py`, `channels.py`, `uploads.py`, `analyse.py`, `final.py`. The manual exclusion lists are in
   `final.py`.

## Success rates, same method in both languages

Channels started in 2025 or later, at least 90 days old:

| Measure (measured) | French (n = 9) | English (n = 41) |
|---|---|---|
| At least one video at 100,000 views or more | **0 (0 %)** | **15 (37 %)** |
| 1,000 subscribers or more | 5 (56 %) | 17 (41 %) |
| Median long-video views of 10,000 or more | 1 (11 %) | 7 (17 %) |
| Monetisation proxy: 1,000 subscribers and 100,000 long-video views in total | 4 (44 %) | 16 (39 %) |
| Long-video views per month, median channel | 2,437 | 2,401 |
| Long-video views per month, best channel | 65,991 (Dolus) | 1,365,871 (JunkBondInvestor) |
| Best video, median channel | 3,921 | 2,149 |
| Subscribers per 1,000 views, median | 6.6 | 4.9 |
| First video at 100,000 views or more | none yet | median: video no. 6, day 29 |

Channels younger than 90 days: 0 of 13 French channels and 3 of 84 English ones have a video at 100,000 views or
more.

**Reading (inference).**

- Reaching 1,000 subscribers is about as likely in French: the French audience subscribes slightly more per view.
- Getting one video pushed to a large audience has not happened in French. English channels do it at the median
  video no. 6, within a month.
- The French market for this format is also **5 to 6 times smaller in supply**: 22 channels against 129 with the
  same queries.
- It is filling up fast. 13 of the 22 French channels are less than 90 days old. Several are direct copies of the
  references, with French titles in the same template ("L'histoire COMPLÈTE de … en N minutes"):
  - "Bâti Sur Toi" and "Fondé sur vous" (Built On You);
  - "Le Dossier Capital" and "Fleuron" (CEOzoned);
  - "Côté Caché" (Crayon Capital's "explained like you're 5").

## The 22 French channels (measured, 2026-11-08)

| Channel | First long video | Subscribers | Long videos | Median views | Best video | Most-viewed title |
|---|---|---|---|---|---|---|
| Fatimmond | 2025-11-18 | 1,850 | 154 | 410 | 14,579 | De secrétaire à milliardaire la femme qui réécrit les règles |
| Échos d'Acier | 2026-04-07 | 1,650 | 47 | 838 | 58,864 | Dans l'usine de Vierzon : comment la France a construit… |
| Dolus | 2026-07-23 | 1,420 | 14 | 12,765 | 74,181 | Le scandale des lasagnes au cheval qui a secoué l'Europe |
| Rich And Famous Insider | 2025-02-26 | 1,260 | 7 | 124 | 546 | À l'intérieur du penthouse de 49 millions de dollars… |
| La Chute des Usines Françaises | 2026-04-10 | 1,200 | 48 | 289 | 54,295 | Ils construisaient les meilleurs tracteurs de France… |
| Dossier Noir | 2026-10-12 | 175 | 6 | 43 | 96 | Mort avec les clés de 200 millions : l'affaire QuadrigaCX |
| Le Dossier Capital | 2026-10-26 | 166 | 7 | 77 | 135 | Toute l'histoire de la Tesla Roadster en 12 minutes |
| Ascensions & Chutes | 2026-05-28 | 76 | 33 | 202 | 3,844 | L'erreur fatale qui a détruit l'empire Auchan |
| Grandes Arnaques | 2026-10-13 | 68 | 12 | 43 | 512 | La Grande Fraude du Vin |
| SecretWealth | 2026-03-05 | 46 | 24 | 37 | 3,921 | L'Histoire de Mia Khalifa… |
| Les Coulisses du Business | 2026-10-02 | 38 | 10 | 31 | 132 | Hermès : l'empire qui ne fait jamais de soldes |
| Empires Racontés | 2026-10-23 | 29 | 10 | 78 | 231 | McDonald's : les 2 frères et l'homme qui a tout pris |
| Fleuron | 2026-10-26 | 26 | 10 | 144 | 1,007 | Toute l'Histoire de Chanel en 21 Minutes |
| Histoires de Milliards | 2026-04-28 | 21 | 5 | 387 | 533 | De Zéro à Milliardaire : Comment Patrice Talon… |
| Lore et Histoires | 2026-10-15 | 13 | 4 | 89 | 159 | 613 milliards de dettes : la chute de Lehman Brothers |
| Le Monde de la Finance | 2026-10-21 | 4 | 6 | 55 | 217 | Le krach du siècle : la chute de Lehman Brothers |
| Côté Caché | 2025-12-18 | 3 | 12 | 11 | 56 | La Grande Dépression expliquée comme si tu avais 5 ans |
| Des Idées aux Empires | 2026-10-30 | 2 | 6 | 54 | 211 | OpenAI : Comment ChatGPT est devenu un empire… |
| Dernier Bilan | 2026-10-02 | 2 | 4 | 43 | 135 | Comment la Suisse a coulé la Sabena |
| Bâti Sur Toi | 2026-10-23 | 1 | 14 | 5 | 219 | L'histoire COMPLÈTE d'Airbus en 10 Minutes |
| (no name) | 2026-10-29 | 0 | 5 | 0 | 2 | TOUTE l'histoire de Michelin en 14 minutes |
| Fondé sur vous | 2026-10-31 | 0 | 4 | 0 | 2 | L'histoire COMPLÈTE de McDonald's en 16 minutes |

**The pattern (inference from titles and views).** The three French channels above 20,000 views a month (Dolus,
Échos d'Acier, La Chute des Usines Françaises) tell **French or European** stories: scandals (Elf, the horse-meat
lasagne) and French industry and its decline (Vierzon, tractors, mopeds). The fourth, Fatimmond (13,000 a month),
tells rags-to-riches billionaires for a French-speaking African audience.
The American brand stories that the references tell in English (McDonald's, Tesla, Airbus "COMPLÈTE") get almost
nothing in French so far. An adjacent channel, ElecTruc (car-industry commentary such as "BYD : la plus grosse
arnaque…", 55,000 subscribers since May 2025), shows that French business commentary can grow. It is not the same
format, so it is excluded from the rates.

## The four references, for scale (measured, 2026-11-08)

| Channel | Created | Subscribers | Total views | Videos |
|---|---|---|---|---|
| Crayon Capital | 2025-03-31 | 299,000 | 25.0 M | 33 |
| JunkBondInvestor | 2025-02-09 | 79,000 | 17.8 M | 134 |
| CEOzoned | 2026-09-30 | 14,600 | 1.49 M | 12 |
| Built On You | 2026-07-23 | 14,600 | 1.06 M | 9 |

All four are in English. No French channel is within 10x of any of them.

## Money (estimates)

- **RPM** (what the creator keeps per 1,000 views; never published by YouTube):
  - French-language business content: about **€3.50–7** ([ibrahimkamara.com](https://ibrahimkamara.com/blog/rpm-cpm-youtube-france-2026)).
    Other guides say €4–15 for finance and business ([formalive.fr](https://www.formalive.fr/remuneration-youtube/)).
  - The US pays about **1.5 to 3 times** France for the same kind of content
    ([Dynamoi](https://dynamoi.com/learn/statistics/youtube-rpm-by-country-2025), [Fluxnote](https://fluxnote.io/guides/youtube-rpm-by-country)).
  - Zehon's 2026-09-29 study assumed €1–5 for French and €2–8 for English popular-science content
    ([`revenus_2026-09-29.md`](../docs/chaine2/revenus_2026-09-29.md)). French-language views from francophone Africa
    pay much less.
- **Best measured French channel** (Dolus): 66,000 views a month × €3.50–7 ≈ **€230–460 a month**.
- **Fifth-best English channel**: 440,000 views a month × an RPM 1.5 to 3 times higher ≈ **€2,300–9,300 a month**
  (inference).

## Limits

- **Small French sample.** 9 French channels in the cohort. The 0 % may become 1 or 2 hits within months: 13 young
  channels are coming.
- **Search bias.** I only see channels that YouTube's search returns for my 16 queries. A French channel with
  other wording (no "histoire", "chute", "arnaque"…) can be missed. Sorting by date reduces the survivor bias: 11 of
  the 22 French and 98 of the 129 English channels were found only that way. It does not remove it.
- **Scope.** Only new faceless-style channels (300 videos or fewer, started 2025 or later). Established French
  channels with a face that tell business stories, and media outlets, are out of scope. They show the French
  audience exists, not that a new faceless channel can reach it.
- **Manual filter.** I removed channels in another format by reading titles. A different reader may draw the line
  elsewhere (for example ElecTruc, Rich And Famous Insider).
- **Not measurable from outside.** Watch hours (the monetisation threshold), click-through, retention, and whether
  a channel is monetised.
- **Not tested.** YouTube's multi-language audio tracks (one video, a French dub) were not measured. They would be
  the cheapest way to test French on Whose Dime without a second channel.
