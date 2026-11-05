# Failure factors of new English finance / money-story YouTube channels (2025-2026)

Data as of 2026-11-05. All numbers below are **measured** from the YouTube Data API v3 (search.list, channels.list, playlistItems.list, videos.list) unless marked **inference**. Per-video data: `research_notes/Échecs public et systèmes chaîne finance/data_echecs.csv` (10,610 rows, one per video of the 315 classified channels, with group, format class and copy flag). Scripts: `/tmp/claude-0/-home-user-Channel/9f700fd4-5e41-55ce-9aa2-10e2d6a252b9/scratchpad/echecs/` (`yt.py`, `s1.py`–`s8.py`, `an2.py`–`an10.py`, `thumbs.py`). Quota used: 4,266 units (31 search calls).

**Sampling frame.** 26 video searches and 5 channel searches (publishedAfter 2025-01-01, relevanceLanguage=en, regionCode=US; mixed order=relevance and order=date, on "Your Life at Every Level of", "POV: You", "silent millionaire", "nobody knows", "holding company silent businessman", "The ENTIRE History of", "why no one can copy", "can … beat nvidia", "old money mindset", "escaped the rat race", "things wealthy people never buy", "habits keeping you poor", "how women treat you at every level of wealth", "won the lottery told no one", "what happens if you invest … a month", "quiet millionaire day in the life", "why everyone pays", "psychology of money you", etc.) plus 13 handle lookups (Willie Finance, Paper Wealth, Nick Invests, Alicia Invests, Dark Ledger, Sonny Finance and the 7 English winners already studied). 1,154 channels came back; 427 matched format + finance keywords and were created in 2025-2026; for each, up to the 200 most recent uploads were fetched (15,420 videos). **In scope (315 channels):** first upload on/after 2025-01-01, ≥3 long-form videos (>180 s; Shorts approximated as ≤180 s), ≥50% finance/business titles, English titles; the studied winners were forced in.

**Group definitions (my rules).**
- **Winner** (n=35): any long video ≥100k views, or ≥10k subs (non-anomalous).
- **Stalled** (n=36): not a winner, best long video ≥10k, and then either idle ≥60 days or median of last 10 long videos <25% of the best.
- **Failed** (n=170): ≥10 long uploads with median <1,000 views, or idle ≥60 days.
- **Early** (n=70): <10 long uploads, still active (excluded from most comparisons).
- **Anomalous** (n=3): ≥5k subs but subs/views >5% (bought or repurposed shells).
- **Modest**: 1 channel.

## Top failure factors, ranked by evidence strength

### Takeaway
What best separates failed channels from winners: (1) they **never get distributed at all** (median views of videos 1-10: 18 vs 6,110); (2) they arrive **late, with verbatim copies of a hit template** (copies get roughly 0.1% of the original's views); (3) their videos are **short** (37% of their long videos are under 10 min, vs 4% for winners); (4) they get **weaker engagement at equal views** (likes 1.1% vs 2.3%); (5) they lean more on **Shorts**. Several things the earlier winners study credited do *not* separate the groups: fast cadence, recurring mascot thumbnails, title wording, topic switching, country of the channel. Failed channels have them as often as winners do.

### Cited Findings

**Group comparison table** (median [IQR] per channel; long = >180 s) — [data_echecs.csv](data_echecs.csv), channels e.g. [@darkledger13](https://www.youtube.com/@darkledger13), [@noahwealth-h7z](https://www.youtube.com/@noahwealth-h7z), [@stealthwealthvip](https://www.youtube.com/@stealthwealthvip)

| Metric | Winners (35) | Stalled (36) | Failed (170) |
|---|---|---|---|
| Median views of long videos | 6,020 | 172 | 19 |
| Median views of videos #1-10 (channels ≥10 long) | 6,110 [519–12,829] | 115 [53–311] | 18 [8–44] |
| Share of channels whose videos #1-10 median <100 views | 9% | 45% | 87% |
| Channels with median <10 views ("zero distribution") | 0 | 0 | 62 (36%) |
| Median duration of long videos (min) | 16.9 [14.3–20+] | 14.6 [9.9–18] | 11.9 [9.0–16] |
| Share of long videos under 10 min | 4% | 19% | 37% |
| Like rate, videos with 200–2,000 views (same band) | 2.33% | 1.83% | 1.08% |
| Comment rate, same band | 0.160% | 0.125% | 0.000% |
| Channels with Shorts ≥30% of uploads | 1/35 (3%) | 3/36 (8%) | 28/170 (16%) |
| Long uploads in first 30 days | 9 [5–19] | 11 [7–18] | 12 [8–18] |
| Long uploads per week (active period) | 2.5 | 2.3 | 3.2 |
| Channel age (days since 1st long upload) | 170 | 118 | 57 |
| Days after the format's first ≥100k hit when the channel entered its main format | 121 [29–168] | 151 [81–184] | 176 [127–221] |
| Title length (chars) / contains "you" / "$" amount | 60 / 70% / 17% | 60 / 78% / 22% | 60 / 71% / 20% |
| Titles starting How/Why/What / question mark / "POV" | 19% / 2% / 16% | 7% / 3% / 26% | 14% / 2% / 19% |
| Channels with any crude English error in titles (u/ur/dont/double space…) | 29% | 42% | 27% |
| Declared country US | 60% | 64% | 59% |
| Main format changed between 1st and 2nd half of uploads | 33% | 42% | 37% |

**Ranked factors (evidence strength = consistency across measures × sample size)**

1. **No algorithmic distribution from the start (strong).**
   - 87% of failed channels have a median under 100 views on their first 10 videos, vs 9% of winners. 62 of 170 failed channels have a median **under 10 views**.
   - The extreme cases are mass-production channels:
     - [STEALTH WEALTH](https://www.youtube.com/@stealthwealthvip): 178 long videos since 2026-09-04 (about 3 a day), median 0, maximum 3 views.
     - [Noah Wealth](https://www.youtube.com/@noahwealth-h7z): 112 long videos, median 4.
     - [Wealth Signal](https://www.youtube.com/@wealthsignal-v8v): 80 long + 52 Shorts since 2026-09-24, median 1.
     - [Money Stories](https://www.youtube.com/@moneystories-w8l): 84 long videos, median 2.

2. **Late, verbatim copying of a hit template (strong).** I matched 92 title templates used by ≥4 channels (normalised titles, with numbers and $ amounts removed). Results for videos at least 21 days old:

   | Publication order within the template | n | Median views | Share ≥10k |
   |---|---|---|---|
   | 1st channel | 89 | 79,752 | 65% |
   | 2nd–3rd | 165 | 620 | 14% |
   | 4th–10th | 205 | 168 | 7% |
   | 11th and later | 35 | 39 | 6% |

   Copies made 60–120 days after the original reach ≥10k only 2% of the time (n=63). Three named cases:
   - **"How Banks Treat You at Every Level of Wealth — $0 to $25M"** made 1,174,882 views for Dark Ledger (2026-05-03) ([video](https://www.youtube.com/watch?v=2LXED3ENhck)). 26 channels then used the template. The identical-title copies got 3–790 views: Villy Finance 790, Money Mind Basics 519, WealthCraft 155, Finance Dose 124, Think Finance 31, Gary Finance 11, Financial Construct 10 ([Villy copy](https://www.youtube.com/watch?v=UbwmDfpMIKA)).
   - **"Why You Must Look Like a Loser to Escape the Rat Race"** made 911,127 views for Hidden Yield (2026-08-19) ([video](https://www.youtube.com/watch?v=QPW4mAjxBHM)). Copies: Chris Talks Money 4,677, The Missing Piece 896, Money Mechanics 712, FINANCE GURU 691, POV Finance Theory 568, Finance Dose 99, Quiet finance 1 ([Chris copy](https://www.youtube.com/watch?v=JUiHJ4tiqhY)).
   - **"POV You Adopted the Old Money Mindset — Your Life Changed"** made 690,759 views for POV Finance (2026-09-02) ([video](https://www.youtube.com/watch?v=avWK82b0fUU)). Even established winners failed with the copy: Another Story 7,994, Finance POV 7,665, Owen 3,474, Finance ANALYST 669. Failed channels' copies got 1–1,190 views ([Owen copy](https://www.youtube.com/watch?v=Alt6b5WbEE0); [Finance POV copy](https://www.youtube.com/watch?v=Er0-Nmz4rm0)).

3. **Short "long-form" (strong).** Among the 131 channels with ≥10 long uploads and a first long upload ≥60 days ago, the share reaching a ≥100k video rises with median video length ([data_echecs.csv](data_echecs.csv)):

   | Median video length | n | Share with a ≥100k video |
   |---|---|---|
   | <8 min | 13 | 0% |
   | 8–12 min | 37 | 8% |
   | 12–16 min | 38 | 16% |
   | 16–20 min | 26 | 46% |
   | ≥20 min | 17 | 41% |

   Inside winner channels, the flop rate (<0.3× the channel median) also falls with length: 22% at 8–12 min, 13% at 12–16 min, 7% at 20–30 min, 3% at 30+ min. Exception: the business-explainer winners ([@tradeofflayer](https://www.youtube.com/@tradeofflayer) median 9.6 min, [@ceozoned](https://www.youtube.com/@ceozoned) 11.6 min) succeed at 8–13 min.

4. **Weak engagement at equal reach (medium-strong).**
   - For videos in the same 200–2,000 view band, the like rate is 2.33% for winners, 1.83% for stalled and 1.08% for failed channels. The median comment rate is 0.000% for failed channels.
   - The same gap shows on videos 1-10: like rate 2.45% for winners vs 1.03% for failed channels.

5. **Shorts-heavy mix (medium).**
   - 16% of failed channels have ≥30% Shorts, vs 3% of winners.
   - Of 49 near-Shorts-only channels found in the same searches (<3 long videos), only 3 have ≥1,000 subs, and the median is 9 subs.
   - Example: [Victoria Sterling Wealth](https://www.youtube.com/@victoriasterlingwealth), 127 Shorts + 8 long videos, best long video 37,691, stalled.

6. **Late entry into a format (medium, confounded).**
   - Winners entered their main format a median 121 days after that format's first ≥100k hit, vs 176 days for failed channels.
   - By launch cohort, the share of channels that published a ≥100k video within 45 days of their first long upload:

     | Launch period | n | Share with a ≥100k video |
     |---|---|---|
     | Up to March 2026 | 32 | 25% |
     | April–May | 29 | 21% |
     | June–July | 58 | 5% |
     | August–September | 61 | 8% |

7. **Thumbnails off the winning pattern (medium-weak, qualitative, n=16).**
   - I looked at 4 thumbnails each from 16 randomly drawn failed channels with ≥15 long videos, 4 stalled channels and 7 winners. For winners I took the 2 best and the 2 latest; for failed channels the 2 latest and 2 random ones.
   - 9 of 16 failed channels show at least one off-pattern trait. Winners show none of these traits (0/7):
     - more than 10 words on at least one thumbnail: Stickman Philosopher, Fletcher Finance, Invisible Ledger, Forlan Finance, POV Wealth (@pov.wealthstories) ≈9–10 words;
     - dense whiteboard or infographic style: Fletcher, Invisible Ledger, Stickman, Wealthverse;
     - dark or photoreal images: Financial Construct (switched from a cartoon to photoreal silhouettes), STEALTH WEALTH, Allegedly Guy;
     - inconsistent style: Financial Construct, Wealthverse, POV:Old Money.
   - One failed channel shows AI artifacts: STEALTH WEALTH has garbled AI text ("Iinanile", "Incamile") and letterboxed frames. No Gemini watermark was visible at contact-sheet resolution.
   - **But 7 of 16 failed channels have winner-grade thumbnails**, with a recurring mascot, 0–5 words and a bright illustration. Examples are [The Finance POV club](https://www.youtube.com/@thefinancepovclub) (mascot plus "YOU" arrow, a near-clone of the winners' style, 0–1,440 views), [Money with Martin](https://www.youtube.com/@moneywithmartin) (3–13 views), [Quiet Cash POV](https://www.youtube.com/@quietcashpov) and [Layla's Money Circle](https://www.youtube.com/@laylasmoneycircle).
   - 10/16 failed channels use a recurring mascot or character, and 7/7 winners do.
   - Inside winners, flops use the same thumbnail style as hits: Money Life POV 88 views, Dark Ledger 6,757, Nick Invests 3,220 ([@moneylifepov](https://www.youtube.com/@moneylifepov), [@nickinvestsus](https://www.youtube.com/@nickinvestsus)).

8. **Generic money explainers or advice instead of a narrative frame (medium, within-winner evidence).** Inside the 35 winners (videos >14 days old, rel = views / channel median):

   | Format class | n | Flops (<0.3×) | Hits (≥3×) | Median rel |
   |---|---|---|---|---|
   | Generic money explainer | 650 | 17% | 17% | 0.88 |
   | Unclassified titles | 208 | 19% | 11% | 0.87 |
   | Company story | 14 | 43% | — | — |
   | Holding / business build | 114 | 6% | 29% | 1.60 |
   | Rat race / old money | 186 | 5% | 27% | 1.31 |

   The strongest single case is [POV Finance (@povfinanceus)](https://www.youtube.com/@povfinanceus).
   - It published 106 generic investing explainers from April to July. Monthly medians were 0.4k–1.2k views, e.g. "Why Bonds Could Save Your Retirement" 242.
   - On 2026-08-18 it switched to "POV:" money simulations. The August median jumped to 58.0k, and video #108 became its first ≥100k: "POV: You Chose Wealth Over Looking Rich", 374,869 views ([video](https://www.youtube.com/watch?v=nYgCcX-WiWU); [pre-pivot example](https://www.youtube.com/watch?v=I53VgiqDzzU)).

9. **Not discriminating (measured null results).**
   - **Cadence.** Failed channels upload as fast or faster: 12 long videos in the first 30 days and 3.2 a week, vs 9 and 2.5 for winners. Among the 131 mature channels, the ≥100k rate does not rise with first-30-day volume:

     | Long uploads in first 30 days | n | Share with a ≥100k video |
     |---|---|---|
     | 1–5 | 17 | 18% |
     | 5–10 | 46 | 26% |
     | 10–15 | 27 | 4% |
     | 15–30 | 34 | 26% |
     | 30+ | 7 | 43% |

   - **Title features.** Length, "you", "$", question marks and "POV" are all within a few points across groups (see table).
   - **Topic switching.** The main format changed between halves in 33–42% of channels in every group.
   - **Declared country.** 59–64% US in every group.
   - **Crude English errors.** 27–42% of channels in each group have at least one. The error *rate* rises from 0.7% (winners) to 4.3% (failed) of titles, a weak signal. One error propagated across copies: "You Silently/Quietly Building a Holding Company From $0 to $600M" appears at Varen Finance 125 views, Your Financial Life 185, Evan Explains Money 310.
   - **Exact template copying share.** Median 3% (winners) vs 5% (failed); 9% vs 15% of channels have ≥30% copied titles.

**Churn and anomalies seen in the frame** — [@fortunetales01](https://www.youtube.com/@fortunetales01), [@willie_finance](https://www.youtube.com/@willie_finance), [@theandreasjones](https://www.youtube.com/@theandreasjones)
- FORTUNE TALES: 107k subs but 518 total views and 7 videos since 2026-10-30. It looks like a repurposed or bought shell.
- Willie Finance: 28.8k subs, 5 public videos, 4,472 views. Its back catalogue was removed.
- Money Simplified: 34.3k subs for 123k views.

### Inferences
- **The dominant failure mode is upstream of packaging.** Most failed channels are never tested by the algorithm in any meaningful way. A median of 18 views over 10 videos means almost no impressions.
  - Plausible causes, none verifiable from outside: YouTube's mass-produced / "inauthentic content" (formerly "repetitious content") classifier on templated AI narration, especially at 2–3 uploads a day; duplicate-title collisions with a much larger original; very short sessions.
  - What the data does show: polished, winner-style thumbnails do not rescue these channels (7/16 failed channels already have them).
- **Copying a hit title verbatim is the most common failure behaviour.** It is also measurably useless. Rank 2–3 copies have a median of 620 views, and rank 4–10 copies 168 views. Even established winners get ≈1% of the original's views when they copy.
  - The earlier study's finding that "fast copies (<30 days) pay off" ([report](../../reports/Croissance%20chaînes%20YouTube%20finance.md)) is mostly true *for channels that already have an audience*. For a new channel, a copy competes against a video YouTube already ranks.
- **Video length is a cheap, controllable lever with a monotonic dose-response.** For simulation and story formats, the bar is 16–20+ min. Under 10 min is a red flag, except for company explainers built on famous brands.
- **The engagement gap (likes ≈half at the same views) suggests failed videos satisfy fewer viewers.** This is consistent with YouTube's satisfaction signals, but it is not proven: there is no retention or CTR data.
- **"Volume wins" is survivorship bias.** Volume amplifies a working format, but it does not create one. Failed channels publish more.

### Gaps
- No impressions, CTR, retention or traffic-source data, so I cannot prove "no distribution" vs "distributed but nobody clicked". Social Blade, watch pages and transcripts are blocked.
- All view counts are *current* totals, not views at the time of publication. Winners' early videos have been inflated by later back-catalogue traffic, which makes the early-warning thresholds look more favourable to winners than they were in real time.
- Channels that were deleted or fully privated are invisible, so the true failure rate is higher than measured. A surviving example is Willie Finance's removed catalogue.
- Sampling bias: order=relevance searches over-sample winners, while order=date searches over-sample brand-new tiny channels.
  - The October entry counts are inflated by date-ordered searches.
  - The 200-most-recent-uploads cap truncates the history of 8 large channels (Nick Invests, Alicia Invests, Money Tom, Alex Finance, Chris Talks Money, Frankie Finance, POV Finance, The Luxury Lane).
- Format classes come from title regexes (≈10% unclassified, 28% "generic money explainer"). Shorts are approximated as ≤180 s.
- I could not observe YouTube's "altered/synthetic content" label, monetisation status, voice type (human vs TTS), or whether thumbnails and titles were changed after launch.
- The thumbnail coding is a single-coder visual judgement on 27 channels.

## Uploads before breakout or abandonment, and the base rate of breakouts

### Takeaway
Breakouts come early or not at all. Winners hit their first ≥100k view video at a median of video #7 (day 23): 57% by video 10, 74% by video 20, 91% by video 30. Channels that give up stop after a median of 16 long videos and 43 days. Of 131 channels in these formats with ≥10 long videos and ≥60 days of history, **21% ever got a ≥100k video, 41% a ≥10k video, 14% reached 10k subs, and 79% have a median under 1,000 views**. These are upper-bound base rates, because the search sample is biased toward visible channels.

### Cited Findings
- **Time to first ≥100k video (n=35 winners).**
  - Median video #7 (IQR 3–21, max 108) and median day 23 after the first long upload (IQR 4–44).
  - Distribution of the video number: 1,1,1,1,1,1,3,3,3,3,4,4,4,4,5,6,7,7,8,10,11,14,15,15,16,17,21,22,23,27,29,30,34,53,108.
  - 57% hit by video 10, 74% by 20, 91% by 30.
  - Source: [data_echecs.csv](data_echecs.csv); examples [@dollarsanddimes](https://www.youtube.com/@dollarsanddimes) #1, [@darkledger13](https://www.youtube.com/@darkledger13) #10, [@owenwealthus](https://www.youtube.com/@owenwealthus) #22, [@ukfinancewithsam](https://www.youtube.com/@ukfinancewithsam) #53, [@povfinanceus](https://www.youtube.com/@povfinanceus) #108.
- **Time to first ≥10k video (all 71 channels that reached one):** median video #6, 75th percentile #14, 90th percentile #27 ([data_echecs.csv](data_echecs.csv)).
- **Abandonment.**
  - 29 failed or stalled channels have been idle ≥60 days. They stopped after a median of 16 long uploads (IQR 8–22) and 43 active days.
  - Among 125 channels started ≥90 days ago, the share idle ≥30 days is 2/26 winners, 3/25 stalled and 37/69 failed.
  - Examples: [Pete Invests](https://www.youtube.com/@peteinvests) (67 long, median 6 views, idle 172 days), [Mila Invests](https://www.youtube.com/@milainvests) (25 long, idle 172 days), [Ryan Invests](https://www.youtube.com/@ryaninvestsus) (31 long, idle 270 days).
- **Persistent failures that did not stop.**
  - [Money Mind Basics](https://www.youtube.com/@moneymindbasics): 114 long videos since May, median 119.
  - [Chris Talks Money](https://www.youtube.com/@christalksmoneyus): 200+ videos, median 324, best 36,632.
  - [Noah Wealth](https://www.youtube.com/@noahwealth-h7z): 112 long videos, median 4.
- **Base rate.** Among the 131 eligible channels (≥10 long videos, first long upload ≥60 days before 2026-11-05):

  | Outcome | Channels | Share |
  |---|---|---|
  | Any ≥100k video | 28 | 21% |
  | Any ≥10k video | 54 | 41% |
  | ≥1,000 subs | 36 | 27% |
  | ≥10k subs | 18 | 14% |
  | Median long-video views <1,000 | 103 | 79% |
  | Median long-video views <100 | 68 | 52% |

  Source: [data_echecs.csv](data_echecs.csv).
- **Cohort effect.** The share of channels publishing a ≥100k video within 45 days of launch falls with launch date ([data_echecs.csv](data_echecs.csv)):

  | Launch period | n | ≥100k within 45 days | ≥10k within 45 days |
  |---|---|---|---|
  | Up to March 2026 | 32 | 25% | 34% |
  | April–May 2026 | 29 | 21% | 48% |
  | June–July 2026 | 58 | 5% | 24% |
  | August–September 2026 | 61 | 8% | 16% |

- **"One-hit" winners.** 7 of the 35 winners have a long-video median under 1,000 despite a ≥100k hit:

  | Channel | Hit | Median |
  |---|---|---|
  | Hidden Yield | 911k | 652 |
  | Grey Finances | 864k | 231 |
  | Money Mechanics | 232k | 287 |
  | The Observer | 164k | 325 |
  | Theo Counts | 125k | 145 |
  | POV Finance Daily | 113k | 307 |
  | The Boring Path with Henry | 274k | 583 |

  Sources: [@hiddenyields](https://www.youtube.com/@hiddenyields), [@grey_finances](https://www.youtube.com/@grey_finances), [@moneymechanics33](https://www.youtube.com/@moneymechanics33).
- **Within-winner failures** — [@dagoldentooth](https://www.youtube.com/@dagoldentooth), [Money Cipher hit](https://www.youtube.com/watch?v=bNSmPdS1Oqw), [@bille_finance](https://www.youtube.com/@bille_finance)

  | Channel | What happened |
  |---|---|
  | Biz Life POV | Monthly median views: 88.9k (Mar, n=5), 41.3k (Apr, 17), 15.5k (May, 17), 7.4k (Jun), 5.4k (Jul), 5.1k (Aug), 3.8k (Sep), 4.9k (Oct, 14). It kept publishing 9–17 videos a month through the decline. |
  | Money Cipher | 4 videos in July (median 0.8k, including the 365,080-view hit), 1 in September (1.3k), then idle 54 days, with 979 subs. |
  | Bille | Monthly median 78.5k (Mar), down to 1.5k (Jun), then recovered to 12.1k (Sep). |
  | Dark Ledger | 58.6k (May), then 13–14k (Jul–Sep). |

### Inferences
- **A practical stopping rule from the data.** If 20–30 long videos of 15+ minutes have produced nothing above 10k, the odds of a later ≥100k breakout without a change of format are small. Among channels with no ≥100k in their first 20 videos and a best of 100–1,000 views, 1 of 32 broke out later.
  - POV Finance shows the exception: persistence works only *with* a format pivot. It broke out at video #108, right after switching format.
- **Rough base rate for a new channel launched today in these formats:** about 1 in 5 to 1 in 10 gets a ≥100k video within its first 2–3 months. This combines the 21% overall rate with the 5–8% for summer and autumn 2026 cohorts. Deleted channels are missing, so the true rate is probably lower.
- **A hit does not make a channel.**
  - Money Cipher and the "one-hit winners" show that a single viral video converts poorly: Money Cipher has 979 subs after a 365k video.
  - Biz Life POV and Bille show a dominant format decaying 80–95% in 2–4 months even for the originator.

### Gaps
- No subscriber history. "Breakout" uses current views of each video, so a video that went viral months later is counted at its upload position.
- Abandonment is inferred from public uploads only. Channels that privated or deleted everything are not in the sample.
- The cohort analysis cannot fully separate "late entry" from "less time to grow": the summer cohorts have had 3–4 months.

## Saturated formats vs still-open formats

### Takeaway
"Every Level of …", "How [X] Treats You at Every Level of Wealth" and generic "POV: You…" are **saturated**: performance collapsed by 70–90% between spring and summer 2026 while the number of channels publishing them quadrupled. Silent millionaire / "Nobody Knows", old money / rat race and holding-company simulations still work **for established channels** (their winners' hit rate held or rose into Sep–Oct). But dozens of new channels per month are now pouring in, and newcomers' verbatim copies fail. Company histories and business explainers ("The ENTIRE History of X", "Why No One Can Copy X") are the least crowded. They are not easy, though: the few non-winner entrants also fail, because success depends on famous-brand demand and research quality.

### Cited Findings

**All in-scope channels, by month of publication** (videos ≥30 days old; cell = videos / channels / median views / % ≥10k) — [data_echecs.csv](data_echecs.csv)

| Format | Spring 2026 | Summer–autumn 2026 |
|---|---|---|
| "Every Level" ladders | **Mar: 19 / 6 / 12,185 / 58%**; Apr: 37 / 13 / 8,405 / 49% | May: 67 / 18 / 1,322 / 19%; Jun: 50 / 23 / 512 / 12%; **Aug: 61 / 25 / 151 / 10%** |
| Generic "POV: You / Your Life" | **Mar: 17 / 11 / 7,089 / 47%**; Apr 33% | May 22%; **Jun: 97 / 32 / 633 / 6%**; Jul 8%; Aug 14%; Sep 15% |
| "Treats You at Every Level" | May: 23 / 13 / 2,216 / 26% | Jun 22%; **Jul: 46 / 22 / 356 / 4%**; Aug 9% |
| Rat race / old money | Mar: 3 / 2 / 25,629 / 67%; Apr 22%; May 25% | Jun 24%; Jul 17%; **Aug: 51 / 34 / 2,098 / 24%; Sep: 122 / 56 / 615 / 19%** |
| Silent millionaire / Nobody Knows | May: 9 / 8 / 7,466 / 44% | Jun 18%; Jul 10%; Aug 14%; **Sep: 89 / 43 / 404 / 14%** |
| Holding company / business empire | Apr: 3 / 3 / 578 / 0%; May 9% | Jun 12%; Jul 26%; Aug 4%; Sep 19% (median 1.2–2.0k throughout) |
| "What if you invest $X a month" | Apr 19%; May 29% | Jun 8%; Jul 8%; Aug 16%; Sep 24% |
| Listicles ("N things wealthy people…") | Apr 24%; May 24% | Jun 27%; **Jul 8%**; Aug 13%; Sep 10% |
| Company story / business explainer | Never more than 2–15 videos a month in the sample | Medians usually <1,000; ≥10k in only a handful of videos |

**Inside the 35 winner channels only** (controls for audience size; rel = views / channel median; ≥3× = share of videos at 3× the median or more) — [data_echecs.csv](data_echecs.csv)

| Format | Mar–Apr | May–Jun | Jul–Aug | Sep–Oct (to ≈Oct 6) |
|---|---|---|---|---|
| Every Level | rel 3.22, **51%** ≥3× (n=43) | 0.93, 18% | **0.74, 10%** (n=39) | 1.05, 20% |
| Treats You | 1 video | 1.03, 36% | **0.66, 11%** | 1.04, 20% |
| Generic POV | 2.02, 38% | 0.86, 15% | 0.97, 24% | 1.27, 31% |
| Silent / secret | — | 21% | 30% | **3.12, 55%** (n=20) |
| Holding / business | — | 28% | 21% | **2.74, 43%** (n=30) |
| Rat race / old money | 27% | 22% | 24% | 1.75, 35% |
| Invest simulation | 25% | 34% | 26% | 2.23, 36% |
| Generic money explainer | 26% | 16% | **7%** | 29% |

**When each format first produced a ≥100k video in the sample** — [Bille](https://www.youtube.com/watch?v=CZhf1RapjPQ), [Another Story](https://www.youtube.com/watch?v=gCYAAp4StVs), [Dark Ledger](https://www.youtube.com/watch?v=2LXED3ENhck)

| Format | First ≥100k video |
|---|---|
| Rat race | 2025-12-05 (Wayne Phipps) |
| Every Level | 2026-03-02 (Bille, "Your Life at Every Level of Financial Power", 208k) |
| Generic POV | 2026-04-09 (Biz Life POV) |
| Invest simulation | 2026-04-23 (Another Story, 312k) |
| Treats You | 2026-04-29 (Another Story, "How Banks Treat You…", 423k), then Dark Ledger's version 2026-05-03 (1.17M) |
| Holding company | 2026-05-16 (Frankie Finance) |
| Silent millionaire | 2026-05-19 (Finance POV) |
| Lottery | 2026-08-10 (Another Story) |
| Business explainer | 2026-09-30 (TradeoffLayer, "Can Google Beat Nvidia?", 1.46M) |
| Company history | 2026-10-09 (CEOzoned, Coca-Cola, 377k) |

**New channels entering each format** (first video in that class), March → October 2026 ([data_echecs.csv](data_echecs.csv)). The October figures are inflated by date-ordered search sampling.

| Format | Mar | Jun | Aug | Sep | Oct |
|---|---|---|---|---|---|
| Silent / Nobody Knows | 2 | 17 | 16 | 18 | 64 |
| Rat race / old money | 1 | 7 | 21 | 34 | 48 |
| Holding | 1 | 1 | 8 | 10 | 37 |
| Every Level | 5 | — | 12 | 7 | 26 |
| Generic POV | 8 | — | 19 | 57 | 62 |
| Company story | — | — | — | — | 15 |
| Business explainer | — | — | — | — | 12 |

Company story and business explainer stay at 0–4 new channels a month up to September.

**Company-history / business-explainer entrants that failed**

| Channel | Long videos | Median views | Note |
|---|---|---|---|
| [The Corporate Story](https://www.youtube.com/@thecorporatestoryyt) | 22 | 164 | Chibi mascot thumbnails |
| [Fletcher Finance](https://www.youtube.com/@fletcherfinance) | 18 | 0 | Whiteboard explainers ("Gas Stations Don't Make Money on Gas"), 0–3 views |
| [The Invisible Ledger](https://www.youtube.com/@theinvisibleledger-h7s) | 25 | 12 | Visa / movie theater economics, 0–50 views |
| Founder Files | 6 | — | 26.8k subs but only 15.6k total views (likely a repurposed channel) |

The winners in this space are [CEOzoned](https://www.youtube.com/@ceozoned) (10 videos, median 139k) and [TradeoffLayer](https://www.youtube.com/@tradeofflayer) (8 long videos, median 38k).

### Inferences
- **Saturated (avoid as a newcomer's main format):** "Your Life at Every Level of [wealth/net worth/salary]", "How [Banks/Women/Family] Treat You at Every Level of Wealth", and generic "POV: You Became Rich" titles. Performance fell 70–90% while the number of channels publishing them grew about 4×, and even winners' hit rates halved or worse.
- **Crowding fast, still paying for incumbents:** silent millionaire / Nobody Knows, old money / rat race, holding company, "invest $X a month". Hit rates held or rose for established winners into Sep–Oct, but new entrants are arriving in large numbers (tens per month). A new channel entering with verbatim titles lands as copy #10–#50 (median 39–168 views).
- **Least crowded:** company histories and "Can X beat Y / Why no one can copy X" explainers. They have low entry and big recent hits (TradeoffLayer 1.46M, CEOzoned 377k). But they depend on brand demand: CEOzoned's Instagram video made 4k vs 349k for Coca-Cola in the prior study. Their entrants fail with niche or generic subjects and infographic thumbnails.
- **Inference for the user's launch:** the open space is not a new title template. It is either (a) a *new frame* applied to high-RPM money mechanics (credit, tax, retirement, buying a business), with original titles; or (b) brand-driven business explainers. In both cases each title should be checked against the API: has the same normalised title already been used by ≥3 channels?

### Gaps
- Months with few videos (Mar–Apr for several classes, Sep–Oct for winners) give unstable percentages.
- Videos published in Sep–Oct have had less time to accumulate views. I used a ≥30-day age filter, but older months still had more time.
- Format classes are title-regex based, and some titles straddle two classes (e.g. "How Banks Treat You at Every Level of Wealth" is counted as "Treats You").
- I could not measure search demand (Google Trends or the YouTube search volume of each template), so the 'saturation' calls rest only on how much each format is supplied and how its views fell.

## Early-warning signals (KPIs at video 5 / 10 / 20)

### Takeaway
The best predictor is the **best view count in the first N long videos**. If no video in the first 5 or first 10 has passed 100 views, **0 channels in the sample later reached 100k** (0/85 and 0/49), and only 4/85 and 3/49 ever reached 10k. A best video of 1k–10k by video 10 gives about a 15% chance of a later ≥100k hit; 10k–100k gives about 27%. A like rate under about 1.2% at equal views, a median video under 12 minutes, and title templates already used by several channels are secondary warnings.

### Cited Findings
**Later ≥100k (or ≥10k) breakout, by the best views reached in the first N long videos.** Pool: channels with ≥N+5 long videos and no ≥100k video in the first N. Source: [data_echecs.csv](data_echecs.csv).

| Best of first N | N = 5 | N = 10 | N = 20 |
|---|---|---|---|
| <100 views | 0/85 (later ≥10k: 4/85) | **0/49** (later ≥10k: 3/49) | 0/14 (0/14) |
| 100–1,000 | 8/87 = 9% (22/87 later ≥10k) | 4/65 = 6% (9/65) | 1/32 = 3% (6/32) |
| 1,000–10,000 | 6/29 = 21% (12/29) | 5/34 = 15% (12/34) | 3/25 = 12% (6/25) |
| 10,000–100,000 | 6/15 = 40% (7/15) | 6/22 = 27% (10/22) | 5/21 = 24% (8/21) |

Channel-level signals over videos 1-10 (channels with ≥10 long uploads), from the same data:

| Signal (videos 1-10) | Winners (33) | Stalled (33) | Failed (162) |
|---|---|---|---|
| Median views | 6,110 | 115 | 18 |
| Like rate | 2.45% | 1.83% | 1.03% |

Same-band like rate (videos at 200–2,000 views): winners 2.33%, failed 1.08%. Comment rate: winners 0.16%, failed 0.000% (see the factor table above).

**Rule-of-thumb KPI ladder** (the thresholds are mine, derived from these measurements):

| Checkpoint | Red flag | On track |
|---|---|---|
| Video 5 | Best video <100 views (0/85 broke out later) | Best ≥1k |
| Video 10 | Best <1k (≤6% later ≥100k) | Best ≥10k (27% later ≥100k; winners' median of first 10 is 6.1k) |
| Video 20 | Best <1k (1/32 later ≥100k) and no title-frame change tested | 74% of winners had their first ≥100k by video 20 |
| Any time | Like rate <1.2% at 200–2k views; median length <12 min for stories/simulations; ≥3 other channels already used the same normalised title | Like rate ≥2% |

### Inferences
- **Treat videos 1–5 as a distribution test, not a content test.** A best of under 100 views after 5 uploads of 15+ min means the channel or the videos are not entering recommendation pools at all. The fix is not "keep posting the same thing".
  - Things to check: the copied-title collision, the length, and whether the voice and visuals look mass-produced.
  - Then change the frame: as an inference only, a new channel identity may be warranted. POV Finance's turnaround came from a format change, not a new channel.
- **Use the like rate at equal reach as a quality proxy.** Winners hold about 2–2.5% likes even on small videos; failed channels sit about 1%. This one is visible in public stats and Studio from day one.
- These thresholds are fitted on survivors' *current* views, so they are optimistic for winners. In real time a winner's video 1-5 had fewer views than it has today. A fair reading is "if even today's totals would be <100, stop and pivot".

### Gaps
- No CTR, average view duration or impressions, which are the real early-warning KPIs a creator sees in Studio. The public-data thresholds above are proxies.
- The sample sizes for later breakouts are small (single digits per cell). The 0/85 and 0/49 results are robust in direction, but the exact percentages for other cells are noisy.
- Views at day 7 or day 28 for each video (the usual Studio checkpoints) cannot be reconstructed from the API without repeated snapshots.
