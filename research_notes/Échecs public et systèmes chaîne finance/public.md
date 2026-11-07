# Audience of English-language finance / money-story YouTube channels (as of 2026-11-05)

Conventions. **Measured**: computed by me from 9,694 top-level comments pulled with the YouTube Data API v3 on 2026-11-05 (414 quota units). The pull covers *all* 305 English long-form videos of the 7 English channels (@CEOzoned, @MoneyCipher-t2z, @DAGOLDENTOOTH, @TradeoffLayer, @Bille_Finance, @thefinance_pov, @owenwealthUS); 296 videos had at least one comment. Every comment is tagged `top` (channel's 8 most-viewed), `bottom` (4 least-viewed among videos >14 days old) or `mid`. The data is in [commentaires.csv](commentaires.csv) (video_id, channel, group, UTC timestamp, likes, replies, relevance rank, language guess, themes, text ≤300 chars; no author names or ids, and @mentions of users are replaced by `@[user]`). Video metadata comes from `data_groupA.csv` / `data_groupB.csv` (in `research_notes/Croissance chaînes YouTube finance/`). "rel" = video views ÷ channel's median long-form views. @BlackoFinance (French) is excluded throughout. Scripts: `/tmp/claude-0/-home-user-Channel/9f700fd4-5e41-55ce-9aa2-10e2d6a252b9/scratchpad/public/` (pull.py, classify.py, analyze.py, timing.py). **Inference**: my interpretation. **External**: cited studies.

Method limits that apply to every measured figure:
- Themes come from **regex keyword rules**, not human coding. Spot checks of ~10 items per theme give rough precision of ~85–90% for "AI negative", ~60% for "correction/disagreement", ~70% for "topic request", ~60–70% for "personal story". 64.4% of non-spam comments match no theme (reactions, jokes, emojis, restated one-liners). Treat theme shares as **orders of magnitude**.
- 214 comments (2.2%) were flagged as spam/bots: book-promotion copypasta ("…book X by Y…", "sleepless nights"), repeated identical texts (≥3 copies), self-promotion and scam warnings. They are excluded from shares, giving **n = 9,480 non-spam**. Spam is concentrated on @Bille_Finance (4.1% of its comments).
- Commenters are a self-selected minority (median ≈1.3–2.2 comments per 1,000 views; see below). People who watch on a TV screen rarely comment, so comment data over-represents phone and desktop viewers.
- Only 15 "bottom" videos had any comments (59 comments). Flop comparisons therefore use rel<1 videos (1,007 comments) instead.

## Q1. Who watches? (self-revealed signals, not demographics)

### Takeaway
Few commenters say who they are: only ~2% of comments carry a life-stage signal and 0.6% state an age. Within those, the audience looks **adult, mostly male, and US-centred, but older than the "Gen Z hustle" stereotype**. The median stated age is 40 (n=53); ~40% of stated ages are 45+ and ~25% are 18–24. The profile varies sharply by format: career-ladder POVs skew young (students and junior finance workers), while "quiet millionaire / lottery" stories skew 50+ (married men, retirees). External data supports an older audience on TV: in Feb 2025, 50+ viewers were 36% of YouTube's TV-screen audience.

### Cited Findings
**Measured (comments, n = 9,480 non-spam; all are self-revealed signals, small n):**
- **Stated current age** ("I'm 26", "I am 58", "76 year old here"): n = 53 comments, **median 40**. 13–17: 1 · 18–24: 13 (25%) · 25–34: 7 (13%) · 35–44: 11 (21%) · 45–54: 7 (13%) · 55–64: 8 (15%) · 65+: 6 (11%). By channel: @Bille_Finance n=30, median 42 · @owenwealthUS n=9, median 37 · @thefinance_pov n=8, median 55.5 · @DAGOLDENTOOTH n=6, median 25. — [commentaires.csv](commentaires.csv)
- **Age milestones in first-person stories** ("I saved 50k at 23", "laid off at 57"): n = 120, median milestone age 38. This is a lower bound on the writers' current age. — [commentaires.csv](commentaires.csv)
- **Life-stage keywords** (strict patterns; one comment can carry several): early-career worker ("my first job", "my boss", "my salary", "intern") 57 · retiree ("I'm retired", "my pension") 34 · investor ("my 401k/Roth/portfolio") 27 (broad pattern 45) · personal debt ("my student loans", "paycheck to paycheck") 25 (broad 72) · business owner 23–27 · parent ("my kids/son/daughter") 23–24 · works in finance (banker, CPA, analyst) 7 · student 7 (school/college mentions, broad: 100, of which 26 on @DAGOLDENTOOTH and 50 on @Bille_Finance). In total **193 comments (2.0%)** carry at least one strict life-stage signal. — [commentaires.csv](commentaires.csv)
- **Own credit score** mentioned (e.g. "793 at 25", "813 now"): 82 comments, 81 of them on @Bille_Finance's credit videos. — [commentaires.csv](commentaires.csv)
- **Gender signals**: "my wife/girlfriend" 36 vs "my husband/boyfriend" 5, so **~88% male-coded among 41 partner mentions** (an indirect signal that assumes heterosexual couples). Explicit "as a man/guy" 4, explicit "as a woman/mom" 0. 31 of the 41 partner mentions are on @thefinance_pov (lottery, secret wealth, prenups). Comments about women/dating/gold-diggers/prenups: 222 (2.3%), mostly @thefinance_pov 119 and @owenwealthUS 54 (the "how women treat you at each wealth level" video). — [commentaires.csv](commentaires.csv)
- **Country cues** (currency, institutions, place names; 388 tagged comments): US 246 (63%) · UK 40 (10%) · Europe/EUR 30 (8%) · India 23 (6%) · Canada 23 (6%) · Africa 9 · Australia/NZ 9 · other Asia 8. The US share is inflated because US-specific words (401k, Roth, IRS, FICO) are also the topics of the videos. — [commentaires.csv](commentaires.csv)
- **Comment language**: 1.1% of comments are in a non-English script or language (105). @TradeoffLayer is the exception at **13.2%** (Arabic, Russian, Korean…): its tech-economics topic is global. The other channels are at 0–1.1%. — [commentaires.csv](commentaires.csv)
- **Comments in US time zones** (see Q3): comments carrying a US cue cluster in the US evening (33% between 18:00 and 23:59 ET). Comments carrying a non-US cue cluster at 00–05 ET (27%), consistent with Europe/Asia daytime. — [commentaires.csv](commentaires.csv)

**External:**
- 84% of US adults use YouTube, the highest of any platform; survey of 5,022 adults, Feb 5 – Jun 18, 2025. YouTube and Facebook are the only platforms used by a majority of every age group, and the youngest adults use YouTube most often. About half visit daily and 33% several times a day (separate survey of 5,123 adults, Feb 24 – Mar 2, 2025). — [Pew Research Center, "Americans' Social Media Use 2025", Nov 20 2025](https://www.pewresearch.org/internet/2025/11/20/americans-social-media-use-2025/), via [Inside Radio, Nov 21 2025](https://www.insideradio.com/free/pew-youtube-and-facebook-still-dominate-u-s-social-media/article_c8b75a8b-c4fc-4676-aa85-54c1d9c2aec3.html)
- More than nine in ten US adults under 50 use YouTube, and 86% of those aged 50–64. — [Pew short read, "5 facts about Americans and YouTube", Feb 28 2025](https://www.pewresearch.org/short-reads/2025/02/28/5-facts-about-americans-and-youtube/) (search snippet; the page returned 403 to my fetch). A 95% figure for ages 18–29 and 62–64% for 65+ circulates only in secondary sources and is **unverified**. Gender: 86% of men vs 83% of women, per a search summary of the [Pew fact sheet](https://www.pewresearch.org/internet/fact-sheet/social-media/) (not directly verified).
- In Feb 2025, viewers over 50 made up 36% of YouTube's TV-screen audience, vs 28% for teens and young adults combined. YouTube's share of US TV viewing was then 11.6%. — [Lindsey Gamble summarising Nielsen, Feb 2025 data](https://www.lindseygamble.com/blog/youtube-tops-nielsens-tv-viewing-chart-thanks-to-older-viewers)
- Young adults use YouTube for money information. Gallup: 42% of US adults under 30 get financial advice from social media. Forbes Advisor/Prolific: 79% of millennials and Gen Z have gotten financial advice from social media, and Gen Z prefers YouTube. One survey: Gen Z relies on YouTube (44%), Instagram/TikTok (34%). Credit Karma: YouTube is the most-used platform for financial advice (71%). Definitions vary widely (19%–79% depending on wording). — search summary of [Benzinga](https://benzinga.com/z/45540111), [Nasdaq/“Nearly 80%…”](https://www.nasdaq.com/articles/nearly-80-of-young-adults-get-financial-advice-from-this-surprising-place), [InvestmentNews](https://www.investmentnews.com/ria-news/truly-concerning-social-media-is-winning-gen-zs-wallets-over-financial-advisors/260522), [eMarketer](https://www.emarketer.com/content/gen-z-looks-ai-social-media-financial-ideas-education). Individual figures were not verified at the original study level.
- Australia (closest well-defined recent study, fieldwork Nov–Dec 2025): 63% of 18–28-year-olds use social media for money information, 56% trust it, and 52% trust "finfluencers". — [ASIC Moneysmart Gen Z financial behaviours report, 2026](https://download.asic.gov.au/media/3l1l0xpc/26-049mr-asic-moneysmart-gen-z-financial-behaviours-report-2026.pdf)

### Inferences
- The commenting audience is a mix of (a) 18–30 ambitious men, often students or junior finance/consulting staff, on career-ladder POVs; (b) 25–45 workers managing credit, debt and first savings; (c) 50–70 married men and retirees on "quiet wealth / lottery / retirement" stories. Nobody self-identifies as Gen Z or millennial (0 generation labels), while retirees and grandparents do. Older viewers are *more* likely to reveal their age, so the 18–34 share is probably under-counted in comments.
- Women seem under-represented, but the signal is weak (41 partner mentions). The male-coded "gold-digger/prenup" thread suggests that topics about women and money polarise viewers and pull the comment section toward male viewers.
- A US-targeted channel will still draw a ~30–40% non-US English audience (UK, India, Canada, Europe, Africa), more so for tech or company topics. US-specific mechanics (401k, FICO, IRS) act as a geographic filter that raises RPM.

### Gaps
- No YouTube Analytics (age/gender/geography) for any of these channels. Comments are a biased proxy (vocal, phone-based, older people disclose more).
- Pew's 2025 age-by-platform table could not be fetched (HTTP 403). I found no Think with Google, Statista, Morning Consult or Nielsen breakdown specific to *finance/business* YouTube viewers for 2024–2026.
- Comments cannot tell US from Canadian viewers unless they use cue words (only 23 Canada cues).

## Q2. What do viewers want, what do they complain about, and what differs between winners and flops?

### Takeaway
Comment sections on these channels are **overwhelmingly positive and confessional**. Praise makes up ~15% of comments, but personal money stories (~9%) collect the **most likes (14.7% of all likes)**. Complaints are rare: ~1.2% AI-negative, ~2% correction/disagreement, ~0.7% "unrealistic", and almost nothing on length, ads, clickbait or repetition. Viewers ask for **more ladders and more specific mechanics** (finance careers, insurance, real estate, taxes, country versions). **Hits attract more criticism than flops**: on videos ≥3× the median, a broader audience arrives, posts more corrections, "AI slop" and "fake story" comments, and comments less per view.

### Cited Findings
**Measured — theme shares (non-spam n = 9,480; % of comments; likes share = % of all likes):** — [commentaires.csv](commentaires.csv)

| Theme | Comments | % | % of likes |
|---|---|---|---|
| Generic praise ("great video", "thank you", "underrated") | 1,420 | 15.0 | 8.8 |
| Personal story (first-person money/life detail) | 887 | 9.4 | **14.7** |
| Format/production praise (animation, narration, "explained so well", "relaxing") | 419 | 4.4 | 3.7 |
| Wealth morality/politics (billionaires, Elon, God, greed) | 272 | 2.9 | 3.0 |
| First-person money struggle (debt, layoff, broke, can't afford) | 229 | 2.4 | 2.0 |
| Topic request ("do one for…", "next video", "part 2") | 227 | 2.4 | 1.1 |
| Correction / disagreement ("wrong", "not true", "you forgot") | 190 | 2.0 | 1.8 |
| Aspiration ("one day", "my goal", "manifesting") | 188 | 2.0 | 2.4 |
| AI-negative ("AI slop", "AI voice", "I'd rather a human-made video") | 114 | 1.2 | 0.5 |
| AI neutral/positive ("sounds human narrated", "so people are making fully generated AI content now") | 73 | 0.8 | 0.2 |
| "Unrealistic / fake story / fanfiction" | 70 | 0.7 | 0.6 |
| Length/pacing/sound (too long, sound effects, music) | 27 | 0.3 | 0.2 |
| Repetitive / recycled | 14 | 0.1 | 0.0 |
| Ads/sponsors | 10 | 0.1 | 0.0 |
| Asking which AI voice/tool | 10 | 0.1 | 0.0 |
| Clickbait / misleading title | 4 | 0.04 | — |

- Other measured counts: tax mentions 473 (5.0%), retirement/401k/Roth/pension 327 (3.4%), secrecy/"tell no one"/"quiet"/"invisible" 266 (2.8%, 158 of them on @thefinance_pov), career words 255 (2.7%), credit score/cards 233 (2.5%), lottery 213 (2.2%), restated one-liner lessons ("The real…", "Most people…") 115 (1.2%), relaxing/sleep/late-night viewing 40 (0.4%), timestamped comments ("4:26 …", a sign of attentive viewing) 287 (3.0%). Median comment length is 61 characters; 36.8% are under 40 characters and 16.2% over 200. — [commentaires.csv](commentaires.csv)
- **The most-liked comments are confessions and aphorisms, not praise.** Top likes (paraphrased): "I think $10k is a psychological trap: once over it you spend more" (921 likes, @owenwealthUS) · "the world is obsessed with FICO instead of savings" (711) · "worth ~$7M, drive a 2019 Silverado, shop at Walmart" (580) · "the best thing wealth can buy is invisibility" (552) · "ex-MBB here, reality is far less glamorous" (387). Visual nitpicks are also highly liked: "he should age as the video goes on", "for such a good credit score he always looks angry" (472–476). — [commentaires.csv](commentaires.csv)

**Measured — by channel (% of each channel's non-spam comments):** — [commentaires.csv](commentaires.csv)

| Channel (n) | Praise | Format praise | Topic req. | Personal | Correction | AI-neg | Unrealistic | Money struggle | Politics/moral |
|---|---|---|---|---|---|---|---|---|---|
| @Bille_Finance (3,386) | 15.4 | 5.2 | 1.2 | **12.8** | 1.8 | 1.1 | 0.7 | **4.1** | 2.9 |
| @thefinance_pov (2,182) | 11.9 | 3.4 | 0.7 | 9.9 | 2.0 | **1.9** | **1.3** | 1.9 | 2.3 |
| @DAGOLDENTOOTH (1,905) | 17.6 | 5.0 | **8.3** | 5.0 | **2.8** | 0.9 | 0.6 | 1.0 | 1.8 |
| @owenwealthUS (842) | 14.7 | 3.4 | 0.5 | 12.6 | 1.8 | 0.1 | 0.1 | 2.9 | 1.0 |
| @CEOzoned (717) | **19.8** | 4.2 | 0.7 | 2.5 | 1.7 | 1.5 | 0.6 | 0.3 | **9.8** |
| @TradeoffLayer (349) | 6.6 | 3.7 | 0.9 | 1.7 | 1.4 | 1.4 | 0.0 | 0.0 | 2.3 |
| @MoneyCipher-t2z (99) | 13.1 | 2.0 | 0.0 | 12.1 | 1.0 | 0.0 | 0.0 | 3.0 | 3.0 |

**Measured — topics viewers request (227 request comments, read manually):** — [commentaires.csv](commentaires.csv)
- **Career "every level" ladders** make up the large majority, mostly on @DAGOLDENTOOTH and @Bille_Finance's ladder videos. Investment banking / global markets / trading desks (FX, credit, commodities, prop/quant trading, market makers) ≈25 requests · consulting (MBB, economic, restructuring) ≈8 · wealth management / financial advisor / private bank ≈9 · insurance (agent, broker, underwriter, reinsurance) ≈8 · real estate (agent, REPE, fix-and-flip, developer, commercial) ≈12 · PE/VC/private credit/infrastructure/endowment/pension ≈12 · Big 4 / accounting / audit / FP&A / tax ≈9 · big law ≈4 · tech sales / product manager / data scientist ≈8 · non-finance (doctor, pilot, roofer, dump-truck owner, freight dispatcher, fry station to manager) ≈10.
- **Mechanics and country versions**: "taxes in the US", "a video for W-2 employees", "Canadian version" (×2), "India version", "how much insurance people pay", "top-paying careers to maximise net worth by 40", "silent millionaire with $15M", "new lottery winner", "how women/men treat you at each wealth level".
- **Company stories** (@CEOzoned, @TradeoffLayer): Pan Am, Rocket Lab, TSMC, imec, RISC-V.
- **Realism requests**: "make it more realistic, with layoffs", "show him aging", "make the character look older".

**Measured — what triggers negative comments:** — [commentaires.csv](commentaires.csv)
- **Detectable AI production plus implausible numbers.** AI-negative comments cluster where a script states a fact that insiders find absurd ("$10,000 a month for an intern?", "my lender never called to lower my rate") or where the visuals glitch ("AI art gets less accurate as the video goes on", "check the AI voice's pronunciation", "the breathing on your AI voice is unbearable"). Several commenters say AI makes them distrust the facts: "as soon as I saw it was AI I can't trust a word". A minority defend it: "I love these AI videos, they motivate and relax me".
- **"Fake story" fatigue on narrative fiction**: @thefinance_pov has the highest "unrealistic" share (1.3%): "Holy fanfiction", "these AI stories are so predictable and unrealistic, but I still watch them".
- **Insider corrections on career content**: @DAGOLDENTOOTH has the highest correction rate (2.8%): "Ex-MBB, far less glamorous", "an overly Hollywood version of a quant", "you forgot the health and social aspects".
- **Sound design** is the main production complaint outside AI: on @TradeoffLayer, "sound effects are distracting and jarring" and "watched at 2x to end the agony".
- **Politics and wealth morality** dominate on billionaire company histories (@CEOzoned 9.8%: Elon Musk, "morally bankrupt").
- Length, mid-roll ads and clickbait are almost absent as complaints (≤0.3% each) on 8–20 minute videos.

**Measured — winners vs flops:**
- Comments on videos at rel ≥3 (7,005 comments): praise 13.5%, personal 10.8%, correction 2.1%, AI-negative 1.2%, unrealistic 0.9%, money struggle 2.8%. On videos at rel <1 (1,007 comments): praise **20.0%**, format praise 6.3%, personal **5.5%**, topic requests 3.2%, unrealistic 0.3%, money struggle 1.4%. — [commentaires.csv](commentaires.csv)
- Per video (92 videos older than 14 days with ≥20 comments): Spearman correlation between rel and the share of negative comments (AI-negative + correction + unrealistic + repetitive + pacing + clickbait) is **+0.25**. Median negative share: 3.4% for rel ≥3 (68 videos), 0.0% for rel 1–3 (20), 1.7% for rel <1 (4). — [commentaires.csv](commentaires.csv), data_groupA/B.csv
- Engagement per view **falls** as videos break out. Median comments per 1,000 views: 1.26 for rel ≥3 (72 videos), 1.56 for rel 1–3 (75), 2.15 for rel <1 (144). Likes per 1,000 views: 21.3 / 18.3 / 23.0. — data_groupA/B.csv

### Inferences
- **What makes a hit, as seen in comments**: the video gives viewers a mirror (it invites "this is my life" confessions with numbers: credit score, savings, age) or a secret ("tell no one", "invisible wealth"). Personal-story share roughly doubles from flops (5.5%) to hits (10.8%). Flops get polite generic praise from a small core audience. Inviting viewers to comment with their own number ("what's your score?", "what would you do?") is aligned with what hits already do. This is a hypothesis to test, not a proven causal lever.
- **Criticism is a by-product of reach, not a cause of failure.** Hits reach outsiders and insiders who correct the numbers and call out AI. The main reputational risk for a faceless AI-illustrated channel is **verifiably wrong numbers**, since AI aesthetics are tolerated until a fact looks invented. Sourced, realistic figures (taxes, salaries, rates) directly defuse the most-liked negative comments.
- Ladder formats generate a **self-replenishing topic backlog** (8.3% of comments are requests). Mechanics topics (credit, taxes, retirement) generate confessions instead. Both are useful for a long-form US channel.
- For a Canada-based creator, the explicit "Canadian version please" requests (n=2) are weak evidence of demand. Canadian viewers exist (~6% of country cues) but are a small slice.

### Gaps
- No transcripts or retention data, so complaints cannot be tied to specific script moments beyond the timestamps quoted in comments.
- Only 59 comments on true bottom videos. Flop analysis uses rel <1 videos with 1,007 comments, dominated by @DAGOLDENTOOTH, @Bille_Finance and @thefinance_pov.
- Regex theme coding has moderate precision (see conventions). A human-coded sample of ~500 comments would firm up the shares.
- Reddit (where complaints about "AI finance slop" would be more candid) was blocked from this machine.

## Q3. When do they watch?

### Takeaway
Comment activity is **spread across the whole day, with a broad ET late-morning to mid-afternoon peak**. Raw counts run ~5.0–5.3% per hour at 10:00–15:00 ET versus ~3.3% per hour at 03:00–05:00 ET, a peak-to-trough ratio of only ~1.6. This is because ~30–40% of commenters are outside the US. Comments carrying a **US cue peak in the US evening (33% between 18:00 and 23:59 ET) and at lunch (17% between 12:00 and 14:59 ET)**. Weekdays are flat (13–16% each), with a slight Monday high. Most engagement is **long-tail**: only 15.5% of a video's comments arrive in the first 24h and 52% arrive more than 7 days after publication; hits have an even smaller first-day share (10.5% vs ~30–35% for non-hits). Publish hour shows **no measurable effect** on performance once channel is accounted for, because each channel posts at a fixed slot and its hits follow that slot. Recommended slot: **publish 12:00–15:00 ET (17:00–20:00 UTC in winter / EST; 16:00–19:00 UTC in summer / EDT)**, so the video is indexed and seeded before the US evening TV window. This is a convention, not a measured lever.

### Cited Findings
**Measured — (a) comment timestamps by hour/weekday:** — [commentaires.csv](commentaires.csv), timing.py (English-language non-spam comments, n = 9,375; DST handled by zoneinfo)
- Raw, by ET hour (% of comments): 00h 3.7 · 01h 3.5 · 02h 3.4 · 03h 3.3 · 04h 3.4 · 05h 3.3 · 06h 3.7 · 07h 3.8 · 08h 4.4 · 09h 4.8 · 10h 5.1 · 11h 5.1 · 12h 5.0 · **13h 5.3** · 14h 5.0 · 15h 5.1 · 16h 4.4 · 17h 4.0 · 18h 3.8 · 19h 3.9 · 20h 3.7 · 21h 3.9 · 22h 4.1 · 23h 4.3.
- The same distribution in PT peaks at 07–12h PT (5.0–5.3%/h). In UTC it peaks at 12–19h UTC (4.6–5.3%/h).
- **Viewing-activity proxy.** To approximate viewing rather than notification spikes, I kept only comments posted ≥48h after publication (n = 7,012) and gave each video equal weight. ET blocks: 00–05h **21.9%** · 06–08h 13.5% · 09–11h 15.7% · 12–14h 13.4% · 15–17h 13.3% · 18–20h 11.5% · 21–23h 10.7%. Raw (unweighted) blocks: 20.6 / 11.9 / 15.0 / 15.4 / 13.5 / 11.4 / 12.2.
- **By country cue**:
  - US-cue comments (n = 228), ET blocks: 00–05h 20% · 06–08h 7% · 09–11h 12% · 12–14h 17% · 15–17h 11% · **18–20h 19% · 21–23h 14%**. Note that 00–02h ET = 21–23h PT, the West Coast evening.
  - Non-US-cue comments (n = 99): 00–05h **27%** · 18–20h 8%.
  - Non-English comments (n = 105): 09–11h ET 27%, 00–05h 24%.
- Weekday (ET, raw): Mon 15.0 · Tue 13.5 · Wed 13.2 · Thu 13.8 · Fri 14.5 · Sat 14.9 · Sun 14.9. In the ≥48h subset, the weekend share is 29.2% vs 28.6% if uniform.
- By channel (≥48h subset), the four most active ET hours are: @Bille_Finance 10, 15, 14, 9 · @DAGOLDENTOOTH 10, 11, 12, 15 · @thefinance_pov 13, 11, 15, 12 · @owenwealthUS 12, 10, 15, 14 · @CEOzoned 13, 10, 6, 7. Evening share (18–23h ET) ranges from 16.6% (@CEOzoned) to 25.5% (@Bille_Finance).

**Measured — (b) comment velocity after publication** (videos >14 days old):
- Arrival curve, all comments: 0–1h 1.7% · 1–2h 1.1% · 2–3h 0.7% · 3–6h 2.3% · 6–12h 3.7% · 12–24h 6.0% · 24–48h 8.7% · 2–7 days 23.6% · **>7 days 52.0%**. — timing.py
- Per video (108 videos with ≥15 comments), median share in the first 24h is 17.6% and in the first 48h 28.2%. Hits (rel ≥3, n=69): **10.5% / 20.7%**. rel 1–3 (n=27): 35.5% / 54.8%. rel <1 (n=12): 29.5% / 53.0%. — timing.py
- By publish hour (ET), first-24h share and median hours to the 5th comment: 06–11h (n=8) 10.4%, 23.5h · **12–15h (n=63) 27.4%, 7.9h** · 16–19h (n=21) 3.1%, 38.1h · 20–05h (n=16) 19.5%, 11.1h. These groups are confounded by channel: 12–15h is mostly @Bille_Finance / @thefinance_pov / @owenwealthUS, and the evening slots are mostly @DAGOLDENTOOTH. — timing.py

**Measured — (c) publish hour/weekday vs performance** (291 English long-form videos >14 days old): — data_groupA/B.csv
- By ET publish block: 09–11h n=29, median rel 0.84, 21% ≥3× · **12–14h n=128, median rel 1.18, 27% ≥3×** · 15–17h n=41, 0.93, 24% · 18–20h n=74, 0.98, 23% · 21–23h n=13 (3 channels), 1.57, 38% · 00–08h n=6, 0.12–0.28, 0%.
- By weekday: Mon 1.29 (25% ≥3×, n=48) · Tue 0.96 (32%) · Wed 0.86 (**12%**) · Thu 1.03 (22%) · Fri 0.80 (22%) · **Sat 1.52 (38%, n=34)** · Sun 1.11 (26%).
- Each channel publishes at a fixed slot, and its hits fall in that slot:
  - @Bille_Finance: 41 of 73 videos at 12h ET; its 22 hits fall at 11–15h, plus one at 18h and one at 21h.
  - @DAGOLDENTOOTH: 50 of 92 at 20h ET; hits at 17–21h.
  - @owenwealthUS: 25 of 38 at 14h ET; all 9 hits at 14h.
  - @thefinance_pov: mostly 11–14h ET; hits at 11–19h.
  - So publish hour is not separable from channel.

**External:**
- YouTube held 15.8% of all US TV-screen viewing in Aug 2026 (a record), up from 12.7% in Jan 2026 and 14.2% in Jul 2026. Nielsen's Gauge counts TV screens only and is changing methodology from Sep 2026. — [Tubefilter on Nielsen The Gauge, Oct 22 2026](https://www.tubefilter.com/2026/10/22/nielsen-the-gauge-youtube-record-watch-time-share-us-tv/amp/); [Nielsen news center, Aug 2026 Gauge](https://www.nielsen.com/news-center/2026/tv-viewing-cools-off-in-nielsens-august-gauge-reports-as-sports-take-a-breather-and-school-resumes/); [PPC Land](https://ppc.land/youtube-gains-record-15-8-of-us-tv-time-in-nielsens-august-gauge/)
- "TV is now the primary device for YouTube viewing in the US" (by watch time), with over 1 billion hours a day on TVs. — [Neal Mohan's annual letter, Feb 2025, via Tubefilter](https://www.tubefilter.com/2025/02/11/neal-mohan-youtube-letter-2025-youtube-tv-watch-time-creator-studio-businesses/). A Dec 29 2025 Time profile put TV at about half of YouTube viewership (cited in search results, [Magzter/Time](https://www.magzter.com/nb/stories/news/Time/NEAL-MOHAN)). Digital i put TV at 36% of US YouTube viewer hours in H1 2025, a different measure. — [Señal News, Sep 15 2025](https://senalnews.com/en/data/usa-youtube-surpasses-45-billion-viewing-hours-in-h1-2025-as-tv-usage-overtakes-mobile)
- Viewing hours:
  - YouTube on TV screens peaks around prime time, like traditional TV (Google, 2016 US data; old). — [Think with Google PDF](https://www.thinkwithgoogle.com/_qs/documents/1686/online-video-on-tv-streaming-content-b.pdf)
  - YouTube is unusually strong in daytime TV: about 6.3M average daytime viewers on TV screens at 11 a.m. vs 2.8M for Netflix, per Nielsen data reported Dec 2025 (exact month unconfirmed). — [Boston Globe/NYT, Dec 24 2025](https://www.bostonglobe.com/2025/12/24/nation/youtube-firm-grip-daytime-tv/); [Gigazine, Dec 25 2025](https://gigazine.net/gsc_news/en/20251225-youtube-daytime-streaming/)
  - A vendor claims CTV prime time runs 19:00–23:00 local, with a 19–22h peak (no dataset disclosed). — [Adwave, Q4 2025](https://adwave.com/resources/youtube-tv-viewing-share-q4-2025)

### Inferences
- The flat, daytime-ET-heavy comment curve reflects (1) a global English audience (Europe evenings = 13–17h ET, Asia/Africa days = 00–08h ET) and (2) phone/desktop commenting during US work hours. The US-cue subset reproduces the expected US pattern: lunch bump plus 18–23h ET evening. Long-form US viewing on TV (≈half of YouTube watch time, older-skewing) is probably even more evening- and weekend-weighted than comments show, because TV viewers rarely comment.
- Because 52% of comments (and by extension much of the viewing) arrive after day 7, and hits are back-loaded, **the first-hours "publish-time" effect is small relative to browse/suggested long-tail distribution**. Consistency of slot matters more than the exact hour.
- **Recommended windows** (as conventions to A/B within the channel, not measured optima):
  - Primary: **Tue–Thu and Sat, 12:00–14:00 ET = 17:00–19:00 UTC (EST, Nov–Mar) / 16:00–18:00 UTC (EDT, Mar–Nov)**. This gives 5–8h of indexing and early-tester traffic before the 19–23h ET evening/TV window and the 19–23h PT West Coast evening. It also catches UK/Europe evening viewers and matches the slot used by three of the four strongest catalogues (@Bille_Finance, @owenwealthUS, @thefinance_pov).
  - Alternative: **15:00–17:00 ET (20:00–22:00 UTC in winter)**, closer to the US evening.
  - Weekday evidence is weak (n=34–49 per day, confounded by channel). Saturday's high median rel (1.52) and Wednesday's low share of ≥3× hits (12%) are suggestive only.
  - Note: US DST ended on 2026-11-01. ET is UTC−5 until 2027-03-14, then UTC−4. Canada (Toronto/Montréal) follows the same ET rules, so a creator in Eastern Canada can schedule in local time.

### Gaps
- No real viewing-time data (YouTube Analytics "When your viewers are on YouTube" is only visible to channel owners). Comments are a lagging, biased proxy.
- No 2024–2026 primary hourly breakdown of US YouTube viewing (Nielsen hourly data is not public). Prime-time and daytime claims come from a 2016 Google study, press reports and vendors.
- Publish-hour effects cannot be identified from cross-channel observational data. A within-channel A/B over 8–12 uploads would be needed.

## Q4. Money context of the US audience (anxieties, interests, aspirational content)

### Takeaway
The US audience watches money stories against **record-high financial pessimism**. 55% say their finances are getting worse (Gallup, Apr 2026), 62% worry about retirement, and only 63% could cover a $400 emergency with cash (Fed SHED, data from Oct 2025). Young adults have the thinnest cushions and the strongest wealth fantasies: ~45% of Gen Z and millennials say they are "obsessed with being rich" (Credit Karma, Dec 2023). This matches the comment data: confessions about credit, debt and first savings coexist with "silent millionaire" escapism.

### Cited Findings
- 55% of Americans say their financial situation is getting worse, a record in Gallup's tracking since 2001 (47% in 2024, 53% in 2025). 62% fear not having enough for retirement. 28% worry about paying credit-card minimums, up 11 points since 2021. 55% say price increases caused hardship. Fielded Apr 1–15 2026, n=1,001. — [CBS News on Gallup, Apr 28 2026](https://www.cbsnews.com/news/americans-finances-getting-worse-gallup-poll-2026/)
- 69% of non-retirees worry about retirement money: 82% of those earning under $40k vs 55% of those earning $100k+. Non-retirees expect to retire at 66 on average. — search summary of Gallup 2026 coverage ([InvestmentNews](https://www.investmentnews.com/retirement-planning/retirement-anxiety-deepens-even-as-americans-project-financial-confidence/266473), [Audacy](https://www.audacy.com/national/news/record-55-of-americans-believe-finances-are-worsening)); not verified against Gallup's own release.
- Fed SHED (survey fielded Oct 2025, released May 13 2026): 63% of adults would cover a $400 emergency with cash or equivalent, flat vs 2024 and down from 68% in 2021. ~73% say they are doing at least okay. 42% are concerned about finding or keeping a job, up from 38%. Well-being declined for young adults and low-income households. — [Federal Reserve press release, May 13 2026](https://www.federalreserve.gov/newsevents/pressreleases/other20260513a.htm); [InvestmentNews](https://www.investmentnews.com/practice-management/fed-survey-reveals-cracks-beneath-stable-surface-of-us-financial-health/266580)
- Bankrate emergency savings report (released Feb 2026; survey May 16–19 2025, n=1,030):
  - 44% of Americans have more emergency savings than credit-card debt; 58% say their emergency savings have not grown in a year.
  - Gen Z is the most likely to have neither debt nor savings (27%). Millennials (35%) and Gen X (33%) are the most likely to have more card debt than savings.
  - Only 30% would pay a $1,000+ emergency from savings.
  - Source: search summary of [Bankrate](https://www.bankrate.com/press-releases/44-of-americans-have-more-emergency-savings-than-credit-card-debt/) and [eMarketer](https://www.emarketer.com/content/gen-z-generation-least-likely-have-financial-cushion-things-go-wrong).
- 44% of Gen Z and 46% of millennials say they are "obsessed with the idea of being rich", vs 27% of all Americans. 59% of millennials and 48% of Gen Z feel behind on financial goals. Credit Karma/Qualtrics, fielded Dec 2023. — [Fox Business, Jan 25 2024](https://www-ak-ms.foxbusiness.com/media/nearly-half-young-adults-obsessed-being-rich-financial-consequences-ensue)
- The "RichTok"/"wealth porn" trend is described as escapism that is most attractive under money pressure. These are commentary pieces, not measurements. — [Thred](https://thred.com/newsletters/the-rise-of-richtok-gen-zs-latest-escape/); [SoFi on money dysmorphia](https://www.sofi.com/money-life/money-dysmorphia-is-warping-peoples-perception-of-their-finances)
- Older US data: 85% of Gen Z and 79% of millennials worried about covering one month of expenses after losing their income. — [Fortune on Bankrate, Mar 24 2023](https://fortune.com/2023/03/24/gen-zers-worried-about-covering-expenses-after-job-loss) (pre-2024, context only)
- Measured echo in comments: first-person money struggle 2.4% overall and 4.1% on @Bille_Finance, plus layoff stories (12 explicit, e.g. "laid off at 51 with 3 kids in college", 94 likes). Also "I'm liquid $50k, I still feel broke" (71 likes) and "I have $650 / No one knows" (218 likes, a parody of the secret-millionaire genre). — [commentaires.csv](commentaires.csv)

### Inferences
- Two emotional modes coexist, often in the same viewer: **anxiety → "show me the mechanics so I'm not the sucker"** (credit, taxes, emergency fund, layoffs, retirement gap), and **escapism → "let me live inside a money fantasy"** (silent millionaire, lottery, family office, career ladders to partner). The winning simulations mix both: a fantasy frame carrying real mechanics. That is the positioning the earlier report recommended.
- 2026 macro conditions (record pessimism, rising job worry, credit-card stress) favour content on layoffs, emergency funds, credit-card minimums and retirement shortfalls. These topics also match the highest-RPM advertiser categories.

### Gaps
- No YouTube Culture & Trends (2024–2026) finance-specific section found. No Morning Consult or Think with Google finance-viewer demographic study found.
- No 2025–2026 Gallup breakdown for under-35s, and no 2026 Bankrate "financial anxiety by generation" figure found.
- Several secondary figures (Credit Karma 71% YouTube, Forbes 79%) were not verified against the original methodology.

## Q5. Audience segments: format/topic fit, likely RPM, affiliate fit

### Takeaway
Four segments emerge from the comments and external data. For a US long-form channel from Canada, **Segment B (anxious builders, 23–40) and Segment C (quiet-wealth 45–70, TV viewers)** combine the largest observed engagement (personal stories, likes) with the highest-value advertiser categories (credit, retirement, tax). Segment A gives cheap topic ideas and loyal young viewers. Segment D gives reach at lower RPM.

### Cited Findings
- RPM context from earlier research. These are vendor estimates without methodology, so use them as orders of magnitude:
  - Planning RPM for US-majority long-form finance: **$8–$15**.
  - "Money-intent" topics (credit cards, taxes, investing, retirement): **$15–$25+**.
  - Business documentaries / company stories: **$5–$14**.
  - Insurance and credit cards rank highest: insurance $8–$60 RPM, credit cards $8–$40 depending on source.
  - Finance sponsorship CPM: $25–$80.
  - A 70% US audience earns ~3–4× the sponsor CPM of a 70% India/Pakistan audience.
  - Sources: `research_notes/Croissance chaînes YouTube finance/economie_niche.md`, citing [OutlierKit](https://outlierkit.com/blog/youtube-rpm-finance-niche), [Lenostube](https://www.lenostube.com/en/youtube-cpm-rpm-rates/), [vidIQ](https://vidiq.com/blog/post/most-profitable-youtube-niches/), [collabonly](https://blog.collabonly.com/blog/youtube-sponsorship-rates)
- Segment evidence (measured, [commentaires.csv](commentaires.csv)) and external context:

| Segment | Evidence in comments (measured) | External context | Formats/topics that serve it | Likely RPM (inference) | Affiliate fit (inference) |
|---|---|---|---|---|---|
| **A. Ambitious career climbers, 18–30, mostly men** (students, analysts, junior consultants/bankers) | @DAGOLDENTOOTH: topic requests 8.3%, corrections 2.8%, median stated age 25 (n=6), "school/college" mentions concentrated on ladder videos; requests for IB, PE, consulting, insurance, Big 4, trading | 42% of under-30s get financial advice from social media (Gallup, via search); Gen Z prefers YouTube (Forbes/Prolific) | "Your life at every level of [career]", salary/bonus breakdowns, "how X firm really makes money"; 15–18 min | Medium ($8–$15). Career/education advertisers, some investing | Finance course providers (modelling, CFA prep), resume/interview tools, brokerage sign-ups (FINRA rules apply), budgeting apps |
| **B. Anxious builders, 23–40** (early-career workers with credit cards, student loans, first $10k, layoff fear) | @Bille_Finance personal stories 12.8%, money struggle 4.1%, 81 own-credit-score comments; @owenwealthUS personal 12.6% ("I'm 23, my Acorns is at $2,830"); most-liked comment of the dataset is about the $10k "psychological trap" (921 likes) | Fed SHED: 63% can cover $400; job worry 42%; Bankrate: millennials most likely to carry more card debt than savings (35%); 28% worry about card minimums (Gallup 2026) | Simulations: "what happens when you hit $10k / 800 credit score / pay off debt", "every level of credit score", layoffs and emergency funds, W-2 tax mechanics; real, sourced US numbers; prompts for viewers to share their own number | **High ($15–$25+)**: credit cards, banking/HYSA, lending, tax software advertisers | **Best fit**: credit-card and HYSA affiliates, credit-builder and budgeting apps, tax software (seasonal Q1), robo-advisors |
| **C. Quiet-wealth and retirement audience, 45–70, mostly married men, many retirees** | @thefinance_pov median stated age 55.5 (n=8), 31 of 41 partner mentions, lottery 206 and secrecy 158 comments, "unrealistic" 1.3%; retiree signals 34 (24 on @Bille_Finance); top personal comment "worth ~$7M, Silverado, Walmart" (580 likes) | 50+ = 36% of YouTube's TV audience (Nielsen, Feb 2025); TV is the primary US YouTube device (Mohan, Feb 2025); 62% worry about retirement (Gallup 2026) | Long (15–20 min) lean-back narratives: silent millionaire, lottery/inheritance mechanics (taxes, trusts, annuity vs lump sum), retirement-at-every-level, Social Security/RMD stories; calm narration suits TV | **High ($15–$25+)**: retirement, wealth management, insurance, Medicare and annuity advertisers | Brokerage/IRA accounts, estate-planning/will services, insurance comparison; avoid gold-IRA-style offers (compliance and reputation risk) |
| **D. Business-story enthusiasts, global, mixed ages** | @CEOzoned/@TradeoffLayer: personal stories 1.7–2.5%, politics/morality 9.8% (@CEOzoned), 13.2% non-English (@TradeoffLayer), requests for company histories (Pan Am, TSMC, Rocket Lab) | Business documentaries pay less per view but reach broadly (economie_niche.md) | "The entire history of X in N minutes", rivalry/monopoly explainers; 9–18 min | **Lower ($5–$14)** because of the non-US share and general advertisers | Weak: investing apps, newsletters, book/audiobook offers |

### Inferences
- **Recommended core**: B as the primary segment, C as the secondary (TV/evening), with A as an occasional series for topic-backlog and subscriber growth. Covering B and C means anchoring each simulation in US money mechanics (credit, taxes, retirement accounts, Social Security). Those mechanics both raise RPM and filter for US viewers. D is a reach play that dilutes RPM and geography.
- Format implications from complaints:
  - Source every figure. Corrections are the most-liked negative comments.
  - Avoid salary or rate claims that insiders can debunk.
  - Fix AI voice artifacts (breathing, mispronunciations) and avoid jarring sound effects.
  - Keep the recurring character consistent and, where the story spans decades, aging. This is one of the most-liked visual requests.
  - Length is not a complaint at 8–20 minutes.
- Segment C is the most TV- and evening-oriented. Segment B comments at lunch and in the evening. Both support a midday-ET publish followed by evening viewing.
- Because 63% of country cues are US but ~30–40% of commenters are non-US, expect a blended RPM below the "US finance" headline, unless topics are explicitly US-mechanical.

### Gaps
- No measured RPM by segment or topic. All RPM figures are vendor estimates.
- Segment sizes cannot be estimated from comments (self-disclosure bias). Confirming them needs YouTube Analytics from a live channel (age/gender/geo per video).
- Affiliate conversion rates by segment were not found. FINRA/FTC constraints on brokerage and credit-card affiliates are covered in the earlier report, not re-researched here.
