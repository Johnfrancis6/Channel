# Groupe A — Growth profiles of @CEOzoned, @MoneyCipher-t2z, @BlackoFinance, @DAGOLDENTOOTH (data as of 2026-11-05)

Method: all numbers below were measured by me through the YouTube Data API v3 (channels, playlistItems, videos, channelSections, playlists) on 2026-11-05, covering 100% of public uploads (153 videos). Raw per-video data: `research_notes/Croissance chaînes YouTube finance/data_groupA.csv` (columns: channel, video_id, title, published_at, duration_s, is_short (<=180 s), views, likes, comments, views_per_day, outlier_score = views / channel median of long-form views). Long-form = >180 s. Thumbnails of the top 5 and bottom 3 long-form videos of each channel were downloaded and inspected visually. Each finding links the channel or video page that the API data describes. "Inference" = my interpretation, not measured.

Important scope warnings for the report writer:
- **@BlackoFinance is a FRENCH-language channel** (defaultAudioLanguage `fr` on all 39 videos, euro amounts, French description, country ES). It is not an English/US channel. It is still useful as evidence of how English formats get localized (see "Playbook").
- **@DAGOLDENTOOTH is the handle of a channel titled "Biz Life POV"** (the handle and the display name do not match).
- **Transcripts could not be retrieved**: YouTube blocks transcript and watch-page requests from this machine (youtube-transcript-api returned `RequestBlocked`, the watch page returned `LOGIN_REQUIRED`). Hook and voice analysis therefore relies on descriptions, chapters, titles and thumbnails, not on spoken text.
- Subscriber history over time is not available from the API and Social Blade is blocked, so growth curves are reconstructed from per-video views by upload month, not from daily subscriber counts.

---

## 1. Channel-level stats and speed of growth

### Takeaway
Three of the four channels are 1 to 8 months old and grew very fast from zero: CEOzoned reached 11.7K subs / 1.15M views in 35 days with 10 videos; Biz Life POV (@DAGOLDENTOOTH) reached 39.5K subs / 2.86M views in 230 days with 99 videos. Money Cipher has one viral video and almost nothing else. Blacko Finance (French) is a 2020 shell that only started publishing in July 2026.

### Cited Findings

| Metric (API, 2026-11-05) | [@CEOzoned](https://www.youtube.com/@CEOzoned) | [@MoneyCipher-t2z](https://www.youtube.com/@MoneyCipher-t2z) | [@BlackoFinance](https://www.youtube.com/@BlackoFinance) | [@DAGOLDENTOOTH](https://www.youtube.com/@DAGOLDENTOOTH) ("Biz Life POV") |
|---|---|---|---|---|
| Channel created | 2026-09-30 | 2026-06-12 | 2020-10-13 | 2026-03-19 |
| Country (declared) | US | none | ES | US |
| Language | English | English | **French** | English |
| Subscribers | 11,700 | 960 | 5,580 | 39,500 |
| Total views | 1,146,147 | 357,403 | 756,127 | 2,858,584 |
| Public videos | 10 | 5 | 39 | 99 |
| Channel age (days) | 35 | 145 | 2,213 | 230 |
| Subs/day since creation | 334.3 | 6.6 | 2.5 | 171.7 |
| Views/day since creation | 32,747 | 2,465 | 342 | 12,429 |
| First public upload | 2026-10-05 (5 days after creation) | 2026-07-01 (19 days) | 2026-07-27 (2,113 days after creation) | 2026-03-24 (5 days) |
| Subs/day since first upload | 390.0 | 7.6 | 55.8 | 175.6 |
| Views/day since first upload | 38,205 | 2,837 | 7,561 | 12,705 |
| Subs gained per 1,000 views | 10.2 | 2.7 | 7.4 | 13.8 |
| Views per video (total/count) | 114,615 | 71,481 | 19,388 | 28,875 |

- All figures above — [CEOzoned](https://www.youtube.com/@CEOzoned), [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z), [Blacko Finance](https://www.youtube.com/@BlackoFinance), [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH) (YouTube Data API v3, `channels` endpoint).
- Channel descriptions: CEOzoned "Just a guy who loves exploring companies and dreams to become the CEO of Apple." + email johnunraveled@gmail.com — [CEOzoned](https://www.youtube.com/@CEOzoned). Money Cipher has an empty channel description — [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z). Biz Life POV describes itself as "immersive POV storytelling … real-life inspired situations based on actual financial data … Step into the role of an investor, CEO, trader, or entrepreneur", with keywords including "POV storytelling", "animated finance", "CEO mindset" — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH). Blacko: "l'argent prend vie à travers des histoires, des simulations et des scénarios … différents niveaux de richesse" + a "not a financial professional" disclaimer — [Blacko Finance](https://www.youtube.com/@BlackoFinance).
- Blacko Finance's API `videoCount` (39) equals the number of videos in its uploads playlist, and the oldest is dated 2026-07-27, so the channel has no public video from its first ~5.8 years — [Blacko Finance](https://www.youtube.com/@BlackoFinance).

### Inferences
- CEOzoned is the fastest grower per video and per day of the four (≈115K views per video; ≈390 subs/day). It is a "new channel boosted by the algorithm" case: 10 videos were enough.
- Biz Life POV has the best subscriber conversion (13.8 subs per 1,000 views), consistent with a recognizable, binge-able series format (each video is "Every Level of X", which invites watching the next one).
- Money Cipher's 2.7 subs per 1,000 views shows that a single viral video with no follow-up converts poorly.
- Blacko Finance: a 2020 channel that published nothing visible until 2026 looks like an older or bought/repurposed channel, or one whose earlier videos were deleted (not verifiable).

### Gaps
- No historical subscriber time series (Social Blade blocked; the API only gives current totals).
- The owners' identities are unknown, and there is no evidence of revenue.

---

## 2. Upload history and cadence; Shorts vs long-form; durations

### Takeaway
All four are essentially 100% long-form (152 of 153 videos are >180 s). The two winners publish fast and regularly: CEOzoned put out 9 videos in its first 15 days (daily from Oct 7 to 12); Biz Life POV publishes ≈3 videos/week (every other day) at 15–20 min. Durations sit in the 9–20 min range.

### Cited Findings

| | CEOzoned | Money Cipher | Blacko Finance | Biz Life POV |
|---|---|---|---|---|
| Videos (long / Shorts) | 10 / 0 | 5 / 0 | 39 / 0 | 98 / 1 |
| Uploads per week since first upload | 2.33 | 0.28 | 2.73 | 3.08 |
| Median gap between uploads (days) | 1 | 6.5 | 2 | 2 |
| Longest gap (days) | 15 (Oct 19 → Nov 3) | 53 (Jul 20 → Sep 11); nothing since Sep 11 | 4 | 6 |
| Long-form duration min / median / max (min) | 8.9 / 11.6 / 17.7 | 13.0 / 13.9 / 16.1 | 8.7 / 13.4 / 23.5 | 10.4 / 17.6 / 23.9 |

- Uploads per month — CEOzoned: Oct 9, Nov 1 — [CEOzoned](https://www.youtube.com/@CEOzoned). Money Cipher: Jul 4, Sep 1 — [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z). Blacko: Jul 3, Aug 13, Sep 10, Oct 11, Nov 2 (a Mon/Wed/Fri rhythm) — [Blacko Finance](https://www.youtube.com/@BlackoFinance). Biz Life POV: Mar 5, Apr 17, May 17, Jun 9, Jul 11, Aug 12, Sep 12, Oct 15, Nov 1 — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH).
- Biz Life POV's only Short ("You Become an Nvidia Employee. The Stock Isn't Yours Yet", 58 s, 2026-10-15) has 1,763 views — [video](https://www.youtube.com/watch?v=3dMB-rXgFiY).
- No channel has uploaded manual captions (`caption=false` on all 153 videos); all are HD — [CEOzoned](https://www.youtube.com/@CEOzoned), [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH).

### Inferences
- A fast start (5 to 9 videos in the first 2 weeks) shows up in both fast growers. It gives the algorithm several tries to find a breakout early (CEOzoned's breakout was video #4).
- Money Cipher stopped after its hit (1 video in the 3.5 months after it went viral). This is the clearest missed opportunity in the set.
- The 15-min-plus durations of Biz Life POV (median 17.6 min) maximize watch time per view, which matters for the 4,000 watch-hour YPP threshold and for mid-roll ads (inference; retention data is not public).

### Gaps
- Upload times of day and possible scheduling rules were not analyzed (timestamps are in the CSV).
- Deleted or private videos are not visible.

---

## 3. Performance distribution, top videos, time to breakout, hits vs steady

### Takeaway
- CEOzoned: steady and high (median 82.8K views, 5 of 10 videos above 100K), with its breakout on video #4, 4 days after its first upload.
- Money Cipher: a pure one-hit (99.1% of views from one video, 426x its median).
- Biz Life POV: a "burst then decay" curve. Its first video got 89K, it had 8 videos above 100K in March to June, and since July most videos get 2–10K. The first 3 months still carry the channel.
- Blacko: its first video was its best (128K); views per video have decayed since August.

### Cited Findings

**Long-form views summary**

| | CEOzoned | Money Cipher | Blacko | Biz Life POV |
|---|---|---|---|---|
| Median views | 82,849 | 843 | 7,803 | 7,651 |
| Mean views | 119,747 | 72,565 | 19,471 | 29,219 |
| P25 / P75 | 21,165 / 234,369 | 734 / 1,264 | 5,263 / 17,596 | 4,328 / 18,058 |
| Share of views, top 1 / top 3 / top 10 | 29.1% / 68.6% / 100% | 99.1% / 99.7% / 100% | 16.8% / 40.5% / 73.1% | 10.6% / 27.0% / 60.5% |
| Videos ≥10x median | 0 | 1 | 3 | 11 |
| Videos ≥100K views | 5 | 1 | 1 | 8 |
| First video ≥50K | #4, 2026-10-09 (day 4) | #4, 2026-07-20 (day 19) | #1, 2026-07-27 (day 0) | #1, 2026-03-24 (day 0) |

Source: per-video API data — [CEOzoned](https://www.youtube.com/@CEOzoned), [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z), [Blacko Finance](https://www.youtube.com/@BlackoFinance), [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH).

**CEOzoned — all 10 videos (all titled "The ENTIRE History of [X] in [N] Minutes")**

| Subject | Duration | Views | Published | Outlier | Views/day |
|---|---|---|---|---|---|
| [Coca-Cola](https://www.youtube.com/watch?v=_OuJBX6Q4Cc) | 11:01 | 348,952 | 2026-10-09 | 4.21 | 13,341 |
| [SpaceX](https://www.youtube.com/watch?v=TZIOfwN7bVI) | 8:52 | 237,675 | 2026-10-11 | 2.87 | 9,817 |
| [Elon Musk](https://www.youtube.com/watch?v=idTq9ArggVc) | 9:18 | 234,369 | 2026-10-12 | 2.83 | 10,182 |
| [ChatGPT](https://www.youtube.com/watch?v=ITdjQVhTua8) | 12:05 | 158,923 | 2026-10-10 | 1.92 | 6,356 |
| [NVIDIA](https://www.youtube.com/watch?v=tBhMUTp4FVc) | 13:34 | 136,360 | 2026-10-14 | 1.65 | 6,467 |
| Facebook | 16:15 | 29,338 | 2026-10-08 | 0.35 | 1,079 |
| [Apple](https://www.youtube.com/watch?v=UABTTt-DRSY) | 13:47 | 22,190 | 2026-10-05 | 0.27 | 736 |
| [TSMC](https://www.youtube.com/watch?v=0sUrH8uYhtA) | 10:25 | 21,165 | 2026-10-19 | 0.26 | 1,295 |
| [Tesla Roadster](https://www.youtube.com/watch?v=ReFf4VeRDB8) | 10:34 | 4,272 | 2026-11-03 (2 days old) | 0.05 | 3,263 |
| [Instagram](https://www.youtube.com/watch?v=tUDQGCq_Gaw) | 17:44 | 4,223 | 2026-10-07 | 0.05 | 149 |

**Money Cipher — all 5 videos**

| Title | Duration | Views | Published | Outlier |
|---|---|---|---|---|
| [You Escaped the Rat Race and Nobody Noticed](https://www.youtube.com/watch?v=bNSmPdS1Oqw) | 16:06 | 359,682 | 2026-07-20 | 426.7 |
| [The Millionaire Next Door: Why You Miss Them](https://www.youtube.com/watch?v=a53-YzTzcWE) | 13:56 | 1,264 | 2026-09-11 | 1.5 |
| [Why The First $100,000 Is The Most Disappointing Milestone](https://www.youtube.com/watch?v=cAOqhiuoYU0) | 14:34 | 843 | 2026-07-14 | 1.0 |
| [From $1,000 to $1 Billion: The Business System Behind Every Giant](https://www.youtube.com/watch?v=wVbzYBh_3_8) | 12:58 | 734 | 2026-07-06 | 0.87 |
| [How Your Boss Treats You at Every Salary Level -- From $30K → $300K](https://www.youtube.com/watch?v=hmXBx2ARQYw) | 13:28 | 304 | 2026-07-01 | 0.36 |

**Biz Life POV (@DAGOLDENTOOTH) — top 11 long-form**

| Title | Duration | Views | Published | Outlier |
|---|---|---|---|---|
| [Pov: Building a Holding Company — $0 to $500M, Level by Level](https://www.youtube.com/watch?v=g4ImbLZAIo8) | 19:13 | 304,769 | 2026-06-30 | 39.8 |
| [Every Level of a Goldman Sachs Banker](https://www.youtube.com/watch?v=FN6sBpyg6Ko) | 15:09 | 263,674 | 2026-05-20 | 34.5 |
| [Your Life as Every Jane Street Rank — From $300K Intern to Member Partnership Profit Share](https://www.youtube.com/watch?v=vBCUH2piPf0) | 17:58 | 204,744 | 2026-05-21 | 26.8 |
| [Every Level of a Family Office — From Inheritor to Architect](https://www.youtube.com/watch?v=ZJTowEKKY58) | 19:38 | 196,301 | 2026-03-29 | 25.7 |
| [Your Life as Every Quant Researcher Level](https://www.youtube.com/watch?v=InH25PzMqpk) | 17:20 | 171,955 | 2026-04-14 | 22.5 |
| Your Life at Every Level of MBB Consulting | 19:39 | 161,271 | 2026-04-19 | 21.1 |
| Your Life as Every Private Equity Rank | 21:49 | 131,272 | 2026-04-09 | 17.2 |
| Your Life as Every Level of a Commodity Trader | 16:51 | 107,670 | 2026-04-03 | 14.1 |
| POV: Your Life at Every Startup Founder Stage | 19:53 | 99,314 | 2026-03-30 | 13.0 |
| Your Life at Every Real Estate Developer Level \| From Analyst to $100M Deals | 16:45 | 91,060 | 2026-04-07 | 11.9 |
| [POV: Your Life as Every Tech Company Rank](https://www.youtube.com/watch?v=APTf7XDUewQ) | 18:04 | 88,927 | 2026-03-24 (first video) | 11.6 |

Flops: [Every Level of a Car Collection — From a $71K Porsche to the Cars Nobody Is Allowed to See](https://www.youtube.com/watch?v=JIpEMqeR91Q) 1,282 views; [The Roofing Crew You Build Becomes an Empire](https://www.youtube.com/watch?v=7hyjqfLnNRM) 1,785; [Your Life as Every Rank of a Sports Franchise CFO](https://www.youtube.com/watch?v=Hz2GN8MzEfw) 1,846.

**Biz Life POV — decay by upload month (views measured on 2026-11-05)**

| Month | Uploads | Views of that month's uploads | Median views per video | Like/view |
|---|---|---|---|---|
| 2026-03 | 5 | 418,252 | 88,927 | 2.40% |
| 2026-04 | 17 | 949,141 | 41,176 | 2.28% |
| 2026-05 | 17 | 767,751 | 15,334 | 1.42% |
| 2026-06 | 9 | 357,354 | 7,344 | 2.34% |
| 2026-07 | 11 | 91,022 | 5,429 | 2.31% |
| 2026-08 | 12 | 116,752 | 5,123 | 1.47% |
| 2026-09 | 12 | 63,094 | 3,775 | 0.54% |
| 2026-10 | 15 | 100,023 | 4,903 | 0.50% |

Source: [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH) API data. The newest videos are younger, so recent months are partly understated. Still, the 2026-07 and 2026-08 videos are 3–4 months old and sit at about 5K median.

**Blacko Finance (French) — top 10 long-form**

| Title | Duration | Views | Published | Outlier |
|---|---|---|---|---|
| [Comment La Banque Te Traite Selon Ton Solde : De 0€ à 1 Million](https://www.youtube.com/watch?v=fkChEBWvQTs) | 19:51 | 127,680 | 2026-07-27 (first video) | 16.4 |
| [Pourquoi Paraître Pauvre Est la Vraie Stratégie des Riches?](https://www.youtube.com/watch?v=7U_ifUYhreE) | 17:23 | 92,791 | 2026-08-12 | 11.9 |
| [Votre Vie En Gardant La Même Voiture Pendant 10 Ans](https://www.youtube.com/watch?v=etXon8J0ISE) | 19:17 | 86,984 | 2026-08-10 | 11.2 |
| [POV: Tu commences Avec 500€ et Tu Dois Devenir Millionnaire](https://www.youtube.com/watch?v=JozJnyla954) | 15:38 | 59,877 | 2026-09-04 | 7.7 |
| [POV: Tu Deviens le Premier Millionnaire de Toute l'Histoire de Ta Famille](https://www.youtube.com/watch?v=kvvTBUVDXd0) | 10:09 | 43,310 | 2026-08-14 | 5.6 |
| POV : Ta Vie en Faisant de l'Achat-Revente à Chaque Niveau | 12:49 | 39,483 | 2026-08-05 | 5.1 |
| POV : Tu Gagnes 600 Millions à la Loterie et Tu Ne Le Dis à Personne | 14:05 | 34,479 | 2026-08-21 | 4.4 |
| Comment Les Hôtels de Luxe te Traitent Selon ta Fortune | 10:51 | 26,739 | 2026-10-14 | 3.4 |
| Comment les Compagnies Aériennes Te Traitent Selon Ta Richesse | 12:04 | 26,108 | 2026-08-24 | 3.4 |
| Ta Vie Selon Ton Salaire : De 20 000 € à 1 Million | 16:40 | 17,596 | 2026-08-07 | 2.3 |

Blacko's views by upload month: Aug (13 videos) 387,816; Sep (10) 141,983; Oct (11) 86,818 — [Blacko Finance](https://www.youtube.com/@BlackoFinance).

### Inferences
- CEOzoned shows "lift after breakout": the first 3 videos (Apple, Instagram, Facebook) got 4–29K. After Coca-Cola (video #4) took off, every one of the next 4 videos exceeded 136K. The breakout probably made the algorithm push the channel's next uploads to the same audience.
- Biz Life POV started strong (video #1 at 89K, video #3 at 196K), so its format had demand from day 1. Its decline since June coincides with (a) running out of elite-finance employers/jobs and moving to generic or lifestyle topics, and (b) a title change from "Your Life as Every [Firm/Job] Rank" to narrative sentences (see §4). Its like/view ratio collapsed from about 2.3% to about 0.5% in Sep–Oct, which suggests either a less-engaged audience (browse traffic outside the core) or weaker content. This is not verifiable without Studio analytics.
- Money Cipher's hit has a 0.45% like/view ratio (1,627 / 359,682) versus 1.5–3.7% on its other videos. The views likely came from broad browse/suggested traffic to non-core viewers. Low-intent viral traffic converts poorly into subscribers (2.7 per 1K views).

### Gaps
- No retention, CTR or traffic-source data (these are only available to the owners in YouTube Studio).
- Outlier scores are not age-normalized; videos less than ~2 weeks old (e.g., CEOzoned Tesla Roadster, Biz Life POV's Nov 3 video) are understated.

---

## 4. Packaging: title patterns and thumbnails (top vs flops)

### Takeaway
Each winning channel uses one rigid, repeatable title template plus one consistent AI-illustration thumbnail style, so the series is recognizable at a glance. Within a channel, the topic (a famous brand or an elite job) explains success better than packaging changes. When packaging departs from the template (longer narrative titles, cluttered thumbnails full of numbers), performance drops.

### Cited Findings

**Titles**
- CEOzoned: 10/10 titles follow "The ENTIRE History of [Company/Person] in [N] Minutes", with "ENTIRE" in caps and the minute count equal to the rounded duration. The top 3 and bottom 3 have identical structure (8.3 words on average). What separates winners from flops is the subject: Coca-Cola, SpaceX, Elon Musk, ChatGPT and NVIDIA (mass-appeal or hot names) vs Instagram, TSMC and Tesla Roadster — [CEOzoned](https://www.youtube.com/@CEOzoned).
- Biz Life POV: the top third (32 videos) has 31/32 titles containing "Every/Level/Rank" and averages 10.7 words. The bottom third has 19/32 and averages 12.5 words. Top titles name an elite brand or job: Goldman Sachs, Jane Street, Quant Researcher, MBB Consulting, Private Equity, Family Office, Holding Company. Flops are long two-part titles with "—" and dollar ranges ("Every Level of a Car Collection — From a $71K Porsche to the Cars Nobody Is Allowed to See"), or later narrative titles ("You Marry Into Old Money. Nothing in the House Is Yours", "You Join Rockstar at 23, GTA 6 Ships When You're 36"). Zero titles use a question mark — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH).
- Money Cipher: the hit, "You Escaped the Rat Race and Nobody Noticed", is second-person, number-free, 8 words, with a secret/recognition hook ("Nobody Noticed"). The 4 flops all lead with money amounts or a "How/Why" construction ("How Your Boss Treats You at Every Salary Level -- From $30K → $300K", "Why The First $100,000 Is…") — [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z).
- Blacko: 6/13 top-third titles use the tiered "selon / niveau / chaque" ("according to your wealth / every level") format vs 1/13 in the bottom third. Question titles: 1/13 at the top vs 5/13 at the bottom. "POV:" appears equally (4 vs 4). The best formats are "How [institution] treats you according to your [balance/wealth]" (bank 128K, airlines 26K, luxury hotels 27K) and "secret wealth / looking poor" — [Blacko Finance](https://www.youtube.com/@BlackoFinance).

**Thumbnails (inspected visually: top 5 + bottom 3 per channel)**
- CEOzoned — one fixed template on all 8 inspected: a hand-drawn/comic-style illustrated portrait of the founder or CEO (Musk, Jensen Huang, Morris Chang, a Pemberton-like pharmacist) on the left with arms crossed and a warm outline glow. Top right: huge black serif text "[NAME] / [FOUNDING YEAR] – 2026" (2–3 words + a date range) next to the brand's app-style logo icon. The rest is a dense isometric "Where's Waldo"-style panorama of company milestones (factories, rockets, GPUs). Light blue-sky palette. Style looks AI-generated (consistent rendering, invented detail). Flops use the exact same template, so packaging does not explain the gap — [Coca-Cola](https://www.youtube.com/watch?v=_OuJBX6Q4Cc), [SpaceX](https://www.youtube.com/watch?v=TZIOfwN7bVI), [Instagram](https://www.youtube.com/watch?v=tUDQGCq_Gaw), [TSMC](https://www.youtube.com/watch?v=0sUrH8uYhtA).
- Biz Life POV — clean flat-cartoon illustration with "white round-head, dot-eyes" faceless characters (plus some Asian-cartoon-style characters with glasses) in offices/boardrooms with a city skyline. Status props: gold coin stacks, private jet, mansion, sports car on podium steps. Text is 2–3 words in heavy serif or sans: "HOLDING COMPANY LEVELS", "Goldman Sachs LEVELS" (rendered like a wall logo), "JANE STREET LEVELS". The #4 video (Family Office, 196K) has no text at all. The Jane Street thumbnail even has black letterbox bars, which did not stop 205K views. Flops have more text and numbers: "COLLECTOR LEVELS" + "$25M"/"$2M"/"INVITE ONLY" price plaques; "$19K EVERY FRIDAY" in a big green box; a football player with a "$32M CONTRACT" and an "OVER THE CAP -$8M" chart — [Holding Company](https://www.youtube.com/watch?v=g4ImbLZAIo8), [Goldman Sachs](https://www.youtube.com/watch?v=FN6sBpyg6Ko), [Jane Street](https://www.youtube.com/watch?v=vBCUH2piPf0), [Car Collection](https://www.youtube.com/watch?v=JIpEMqeR91Q), [Roofing](https://www.youtube.com/watch?v=7hyjqfLnNRM), [Sports CFO](https://www.youtube.com/watch?v=Hz2GN8MzEfw).
- Money Cipher — anime/manga-influenced cartoon with one recurring protagonist (black messy hair, blue shirt), AI-generated look. The hit is the only one with conflict and emotion: the protagonist walks out calmly ("YOU QUIT." in big white outlined text, 2 words, red arrow) while a red-faced boss points and shouts and coworkers look shocked. The flops show the protagonist alone and calm at a laptop, with money text ("THE FIRST $100K", "$1,000 → $1 Billion", "$30K→$300K") or "SILENT MILLIONAIRE." + a bank balance card — [hit](https://www.youtube.com/watch?v=bNSmPdS1Oqw), [flop](https://www.youtube.com/watch?v=hmXBx2ARQYw).
- Blacko — one recurring mascot: a white round-faced dot-eyes "meme" character in a dark green suit with a red tie, rendered in glossy, saturated AI-illustration style. Luxury props: black metal card and stacks of cash in a gold bank lounge, Lamborghini/Bugatti/private jet, a "CLUB PRIVÉ" doorman refusing entry, an old Renault Clio with a "BLACKO" plate parked among supercars. **None of the top 5 has any text.** Only a flop ("ACHETER VS LOUER") uses big text — [bank](https://www.youtube.com/watch?v=fkChEBWvQTs), [paraître pauvre](https://www.youtube.com/watch?v=7U_ifUYhreE), [voiture 10 ans](https://www.youtube.com/watch?v=etXon8J0ISE).

### Inferences
- Exploitable rules: (1) a fixed title template where only the subject changes; (2) choose subjects with built-in search and browse demand (household brands, elite prestige employers); (3) thumbnails with one character plus 0–3 words, with status or conflict shown visually rather than written; (4) avoid long two-part titles with several dollar figures.
- An emotional contrast or conflict in the thumbnail (the angry boss vs calm protagonist; the Clio among supercars; being refused entry at a private club) appears on the biggest hits of Money Cipher and Blacko.
- All four channels use AI-generated illustration rather than stock footage or a real face. This is visual inference from the rendering; no channel discloses it.

### Gaps
- CTR per thumbnail is not public, and A/B thumbnail tests (YouTube "Test & Compare") cannot be seen from outside. Current thumbnails may differ from those at launch.

---

## 5. Content, sub-niche, narrative format, production (face, voice)

### Takeaway
- CEOzoned: chronological company/founder biographies ("business history"), about 10 min.
- Biz Life POV: second-person "career-ladder / every level" stories inside elite finance (IB, PE, quant, hedge funds, family offices), ~17 min, chaptered by level with a twist ending, backed by real sourced numbers on invented characters.
- Money Cipher and Blacko: second-person "money psychology / quiet wealth / how institutions treat you by wealth" fiction.
- All are faceless and illustrated. Voice type (AI vs human) could not be verified.

### Cited Findings
- CEOzoned describes itself as "complete company histories in fast, clear, whiteboard-style stories: how the biggest companies in the world were built, almost destroyed, and rebuilt". Descriptions are dense SEO summaries packed with dated facts (e.g., Apple "months from bankruptcy" in 1997, Microsoft's $150M investment). They end with "Which company or person should we break down next? Drop it in the comments!". Category 27 (Education). Tags include "company history" (10/10) and "business documentary" — [Apple video](https://www.youtube.com/watch?v=UABTTt-DRSY), [Tesla Roadster video](https://www.youtube.com/watch?v=ReFf4VeRDB8).
- Biz Life POV structure, from its chapters. Holding Company video: "0:00 The folder, the $90K, and why 4 out of 5 businesses never sell → Level 1 The Searcher → … Level 6 The Holding Company → 16:06 The Final Turn → 18:36 Watch next" — [video](https://www.youtube.com/watch?v=g4ImbLZAIo8). Goldman Sachs video: "0:00 The Wall Street Machine; Level 1 Summer Analyst … Level 7 Partner; 13:06 The Twist: Who Actually Owns It?; 14:49 Was It Worth It?" — [video](https://www.youtube.com/watch?v=FN6sBpyg6Ko). First tech video: 7 levels, Intern → CTO, ~2–3 min per level — [video](https://www.youtube.com/watch?v=APTf7XDUewQ).
- Biz Life POV descriptions state: "It is a narrated story built on researched numbers and it is not financial advice", and in other videos "Every company and person in the story is invented. The market figures … come from the sources below". 55 of 99 descriptions carry a "SOURCES" list (domains cited include sec.gov ×15, cnbc.com ×12, bls.gov ×9, irs.gov ×7, fortune.com ×7, levels.fyi ×5, federalreserve.gov ×4, carta.com ×4). 52 youtu.be links point to "Watch next" internal videos. Category 22 (People & Blogs) — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH), [Holding Company description](https://www.youtube.com/watch?v=g4ImbLZAIo8).
- Money Cipher's hit description includes a disclaimer: "a fictionalized story inspired by common personal finance, wealth-building, and financial independence concepts". Its last video is a story of a 29-year-old who auto-invests $400/month (themes: compound growth, lifestyle inflation, delayed gratification) — [hit](https://www.youtube.com/watch?v=bNSmPdS1Oqw), [Millionaire Next Door](https://www.youtube.com/watch?v=a53-YzTzcWE).
- Blacko organizes its uploads into two playlists: "Histoires d'Argent 📈" (22 videos) and "Les Niveaux de Richesse💰" (21) — [Blacko Finance](https://www.youtube.com/@BlackoFinance).
- Transcripts for the top 2–3 videos per channel could not be fetched (the YouTube transcript endpoint blocks this machine's IP), so hook wording and voice type are not verified — [CEOzoned Coca-Cola](https://www.youtube.com/watch?v=_OuJBX6Q4Cc) (attempted).

### Inferences
- Hook structure (from chapters and descriptions only): Biz Life POV opens with a 40–50 s "cold open" stating the stakes or paradox ("why 4 out of 5 businesses never sell", "How much of your startup is still yours?"). It then climbs levels, saves a "Twist/Final Turn" for the last 2–3 minutes and ends on a "Watch next" link. This is a ladder structure with a payoff withheld to the end, designed for retention.
- CEOzoned's descriptions open with a curiosity question ("Want to know how a failed medicine, invented by a wounded Civil War colonel addicted to morphine, grew into a drink poured around two billion times every…") and an "almost destroyed, rebuilt" story arc. The spoken hook likely mirrors this (unverified).
- Production: an output of 1 video/day (CEOzoned, Oct 7–12) or 3 × 17-min researched videos/week (Biz Life POV), plus uniform AI-style illustrations, strongly suggests an AI-assisted pipeline (AI images and probably an AI or cloned voice). This cannot be confirmed without audio.
- Faceless on all four channels: no face, no personal brand, only a mascot or illustrated founders.

### Gaps
- AI voice vs human voice is unverified (no transcript or audio access). Whether these are animated or slideshow-style visuals is also unverified (only thumbnails were seen).

---

## 6. Engagement and monetization signals

### Takeaway
Engagement is modest (0.5–2% likes/view). None of the four shows any affiliate link, sponsor, product or newsletter. Revenue would come only from AdSense. CEOzoned, Blacko and Biz Life POV meet the subscriber threshold for the YouTube Partner Program; Money Cipher (960 subs) does not.

### Cited Findings

| | CEOzoned | Money Cipher | Blacko | Biz Life POV |
|---|---|---|---|---|
| Like/view (aggregate, long-form) | 0.77% | 0.47% | 1.56% | 1.94% |
| Like/view (median per video) | 1.00% | 2.02% | 1.49% | 1.81% |
| Comment/view (aggregate) | 0.075% | 0.036% | 0.183% | 0.109% |
| External links in descriptions | none | none | none | sources only (no affiliate or sponsor) |
| Contact | johnunraveled@gmail.com (channel description) | none | none | none |
| Category | 27 Education | 22 People & Blogs | 27 Education | 22 People & Blogs |

- Sources: API statistics and descriptions — [CEOzoned](https://www.youtube.com/@CEOzoned), [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z), [Blacko Finance](https://www.youtube.com/@BlackoFinance), [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH).
- Blacko's most-commented video is "Votre Vie En Gardant La Même Voiture Pendant 10 Ans" (552 comments on 86,984 views, 0.63%). It is a debate-bait topic — [video](https://www.youtube.com/watch?v=etXon8J0ISE).
- YPP eligibility requires 1,000 subscribers plus 4,000 valid public long-form watch hours in the past 12 months (or 10M valid Shorts views in 90 days) — [YouTube Help: YPP overview](https://support.google.com/youtube/answer/72851).
- The API marks `licensedContent: true` on all videos of CEOzoned, Blacko and Biz Life POV, and `false` on all 5 Money Cipher videos — [CEOzoned](https://www.youtube.com/@CEOzoned), [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z).

### Inferences
- Watch hours: even at an assumed 3-min average view duration (unmeasured), CEOzoned's 1.15M views ≈ 57K hours and Biz Life POV's 2.86M ≈ 143K hours, far above 4,000. Both are almost certainly eligible and likely monetized. Blacko likely too. Money Cipher's watch hours are probably enough, but it is below 1,000 subs.
- `licensedContent=true` is usually set when the uploader's channel is linked to a content-owner/CMS or claims its content. It is a weak hint of monetization or an MCN/agency setup, not proof.
- Biz Life POV's source lists and "not financial advice" disclaimers look like defensive signals against YouTube's "reused/inauthentic content" and finance-misinformation policies, and add credibility (inference).

### Gaps
- Actual monetization status and RPM are not observable externally.

---

## 7. Playbook and owner-network signals; cross-channel copying

### Takeaway
There is no hard evidence that these channels share an owner. They do share one niche playbook: second-person "Your life at every level of wealth/rank", "How [institution] treats you by wealth", "quiet/secret millionaire", faceless AI illustration, 10–20 min. Formats visibly travel between channels and languages within weeks. Blacko's French remakes of English concepts outperformed the English originals.

### Cited Findings
- Money Cipher's "You Escaped the Rat Race and Nobody Noticed" (EN, 2026-07-20, 359,682 views) was followed 14 days later by Blacko's word-for-word French title "Tu as échappé à la course des rats. Et personne ne s'en est aperçu." (2026-08-03, 6,534 views) — [Money Cipher video](https://www.youtube.com/watch?v=bNSmPdS1Oqw), [Blacko Finance](https://www.youtube.com/@BlackoFinance).
- Biz Life POV's "How Banks Treat You at Every Level of Wealth - From a $4 Overdraft to a $25M Client" (2026-06-25, 7,711 views) preceded Blacko's first video "Comment La Banque Te Traite Selon Ton Solde : De 0€ à 1 Million" (2026-07-27, 127,680 views) — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH), [Blacko video](https://www.youtube.com/watch?v=fkChEBWvQTs).
- Other parallel titles: Money Cipher "How Your Boss Treats You at Every Salary Level" (2026-07-01) and Biz Life POV "How Insurance Companies Treat You at Every Level of Wealth" (2026-09-08). Biz Life POV "You Can Retire at 34. Your Boss Has No Idea" (2026-09-03) and Blacko "Tu As Pris ta Retraite à 30 Ans et Personne Ne Le Sait" (2026-09-29). Biz Life POV "Pov: You Have $10 Million and Nobody Knows" (2026-07-02) and Blacko "Voici Comment Vit Un MILLIONNAIRE Discret" / "Vivre Riche en Secret…". Biz Life POV "You Are Laid Off .. Six Years Later, You Own the Company" (2026-10-01) and Blacko "POV: Ton Patron Te Licencie… Alors Tu Rachètes Son Entreprise" (2026-11-01) — [Biz Life POV](https://www.youtube.com/@DAGOLDENTOOTH), [Blacko Finance](https://www.youtube.com/@BlackoFinance), [Money Cipher](https://www.youtube.com/@MoneyCipher-t2z).
- Visual similarity: Blacko and Biz Life POV both use white round-faced dot-eyed faceless characters in suits (seen on the thumbnails inspected in §4) — [Blacko bank](https://www.youtube.com/watch?v=fkChEBWvQTs), [Biz Life POV Goldman](https://www.youtube.com/watch?v=FN6sBpyg6Ko).
- The "Your Life as Every Rank" job-ladder POV format also exists on at least one other channel ("Chill Pov Guy"), per a third-party channel listing — [vling.net channel info](https://vling.net/en/channel/UCxKDDGPXDAZIY_vt9_qEBfQ/channel-info).
- No featured-channel sections, shared links or shared emails link the four channels. Only Blacko has channel sections/playlists, and only CEOzoned shows an email. The handle @unraveled belongs to an unrelated 2020 trivia channel (1,580 subs), so "johnunraveled" cannot be tied to another channel — [CEOzoned](https://www.youtube.com/@CEOzoned), [@unraveled](https://www.youtube.com/@unraveled).
- Web searches for "Biz Life POV", "CEOzoned" and "johnunraveled" found no articles, Reddit threads or podcasts about these channels — [search result example: vling listing](https://vling.net/en/channel/UCxKDDGPXDAZIY_vt9_qEBfQ/channel-info).

### Inferences
- These look like small independent operators (or faceless-channel "automation" operators) who copy whatever format is currently overperforming in the "money POV / every level" cluster, translate it, and re-skin it. The cluster itself — not any one creator — is the opportunity.
- A French channel translating English finance-POV hits got 128K on its first video, while the English original of the same idea got 7.7K. Localization arbitrage works, and the reverse direction (adapting proven non-English or adjacent-niche formats to English) is worth testing.
- Ranked success factors for a new English long-form finance channel, from this data:
  1. A **serial title template** where only the subject changes ("The ENTIRE History of X in N Minutes"; "Every Level of a [Goldman Sachs Banker]").
  2. **Subjects with built-in demand**: household brands or famous founders (Coca-Cola, SpaceX, Musk, ChatGPT, NVIDIA) and elite, aspirational employers or jobs (Goldman, Jane Street, PE, quant, MBB, family office). Generic or lifestyle subjects flopped.
  3. **A fast start**: 5–10 videos in the first 2–3 weeks; breakouts came at videos #1–#4.
  4. **Consistent AI-illustrated thumbnails** with 0–3 words, a central character, and status/conflict props.
  5. **Second-person immersion** ("You", "POV", "Your life") for money-psychology content.
  6. **Ladder/chapter structure with a withheld twist**, 10–20 min.
  7. **Don't stop after a hit** (Money Cipher) and **don't drift off the winning subject class** (Biz Life POV after June).

### Gaps
- No proof of a shared owner or network. Reverse lookups on the email and WHOIS-like signals are not available for YouTube.
- The origin of the "every level" format and who started it were not established in this research.
