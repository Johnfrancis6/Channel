# Before / after: the cold open of "Uber Was Cheap. Who Paid?"

The first ~150 words of video 1, written twice: **before**, the way a Zehon
script would do it, translated to English; **after**, following
[`storytelling_rules.md`](storytelling_rules.md). Both are measured with
[`tools/measure.py`](tools/measure.py) against
[`style_thresholds.json`](style_thresholds.json). This is a demonstration,
not the video 1 script: S04 writes that from a signed `02b_factcheck.md`.

## Before (Zehon style, translated)

> You open the app. You tap a button, and a car arrives in four minutes
> [TO VERIFY]. You pay a few dollars, and you get out without thinking about
> it. This service exists in more than 70 countries [TO VERIFY]. It carries
> millions of people every day [TO VERIFY]. In 2015, the rider paid only 41%
> of the real cost of a ride.[^4] In 2022, the company still lost $9.1
> billion.[^6] In 2023, it made its first operating profit: $1.1 billion.[^5]
> So how can a ride cost less than it costs? And who pays the difference?
> The idea is simple. A driver uses his own car. The company connects him
> to a rider. It keeps a commission on each ride. Except that the commission
> does not cover the costs.

What makes it Zehon: an object in the viewer's hands first, a run of dated
figures, sentences of the same size, the process instead of a person, and
the block closed by the stock connector ("Except that" = « Sauf que »).

## After (rules applied)

> "In 2008, on a snowy night in Paris, Garrett Camp and I had trouble
> getting a cab."[^1] That's how Travis Kalanick tells it.[^1][^2] Two
> friends, one cold street, no taxi. What they built next became Uber: you
> tap your phone, a black car finds you,[^3] and the fare goes on your card
> before you even step out [TO VERIFY: card payment at launch]. But for
> years, that ride was strangely cheap. Cheaper than it had any right to be.
> A transport consultant went through the numbers Uber showed its own
> investors. The estimate: riders were paying about 41 percent of what each
> trip really cost.[^4] So who covered the rest? Not you. Somebody else paid
> the gap, ride after ride, city after city. Uber only turned a profit from
> its own business, over a full year, in 2023.[^5] This is the story of who
> paid for your cheap ride.

What changed: a named person and a first-hand line in the first sentence (S1,
S3, E1); a scene we can picture (E1); one "But" that turns the story
(S9, S10); three numbers instead of seven (S7, S8); "operating profit" said
in plain words (S13, E3); short and long sentences mixed (S4); the
"This is the story of…" line the Crayon hits use before 30 s.

## Measured against the thresholds

Command: `python3 whosedime/research/tools/measure.py whosedime/research/examples/uber_before.txt`
(and `uber_after.txt`): the two texts as plain files, without the source tags.

| Rule | Metric | Threshold | Before | After |
|---|---|---|---|---|
| S1 | `words_before_first_person` | ≤ 160 | 123 (no person: the metric is the text length) | **8** |
| S2 | `people_mentions_per_150` | ≥ 0.2 | **0.0 ✗** | 2.1 |
| S3 | `dialogue_per_1000` | ≥ 1 | **0.0 ✗** | 6.99 |
| S4 | `sentence_sd` | ≥ 5.3 | **3.0 ✗** | 6.42 |
| S5 | `sentence_mean` | ≤ 17.9 | 8.2 | 11.0 |
| S6 | `share_over_25` | ≤ 0.16 | 0.0 | 0.077 |
| S7 | `numbers_per_100` | ≤ 2.6 | **6.5 ✗** | 2.1 |
| S8 | `numbers_first_60` | 1 to 4 | **5 ✗** | 1 |
| S9 | `words_before_first_tension` | ≤ 100 | **123 ✗** (none) | 57 |
| S10 | `contrast_per_1000` | 1.6 to 10.6 | 8.13 | 6.99 |
| S11 | `you_per_1000` | ≥ 4.1 | 32.52 | 48.95 |
| S12 | `top_connector_per_1000` | ≤ 8.7 | 8.13 | 6.99 |
| S13 | `jargon_per_1000` | ≤ 5.8 | **8.13 ✗** | 0.0 |
| S14 | `jargon_explained_share` | ≥ 1.0 | **0.0 ✗** ("operating profit") | no jargon |
| | words | | 123 | 143 |

**Result**: the after passes all 14 rules; the before fails 8. All rules are
`warn` (no metric separated hits from flops, see the rules file), so the
`block` set is empty and "passes every `block` rule" holds trivially; the
meaningful check is the warn count, 0 against 8.

**Caveat on short extracts**: thresholds are calibrated on 13-25 min
transcripts. On 150 words one occurrence is worth ~7 per 1,000, so S10, S12
and S13 swing on a single word (a second "but" would push the after over
10.6). S03 should apply the per-1,000 rules to whole scripts only, and S1,
S8 and S9 to the cold open.

## Sources

[^1]: Quote: Travis Kalanick, "Five years and 311 cities later", Uber
    Newsroom, 1 June 2015, <https://www.uber.com/ma/en/newsroom/five-years-and-311-cities-later/>
    (exact sentence checked on 2026-11-07). Nuance for the script: Garrett
    Camp calls that evening "a pivotal moment" but not the beginning, and
    says the app was already designed (Bloomberg, reprinted as "How Much Is
    an Idea Worth? In Uber's Case, $3.7 Billion",
    <https://uk.finance.yahoo.com/news/much-idea-worth-uber-case-234917668.html>) [TO VERIFY: read the full article].
[^2]: Kalanick and Camp as the two friends and co-founders: Travis Kalanick,
    "Uber's Founding", Uber Newsroom, 22 December 2010,
    <https://www.uber.com/newsroom/ubers-founding> ("Garrett and I were
    hanging out in Paris for a week at … LeWeb").
[^3]: Black car: same post, the first idea was "a limo timeshare service"
    (a driver, a luxury car, a parking spot shared). "A black car finds you"
    as a description of the 2010 service is [TO VERIFY].
[^4]: 41 percent: estimate by transport consultant Hubert Horan (Naked
    Capitalism, late 2016) from revenue tables Uber gave investors, for the
    year to September 2015; one analyst's estimate, not audited accounts.
    Reported by SFist, 2 December 2016,
    <https://sfist.com/2016/12/02/day_around_the_bay_uber_loses_2_bil/>, and
    the Boston Globe, 9 February 2018,
    <https://www.bostonglobe.com/opinion/2018/02/09/you-not-paying-enough-for-uber/phrc5e051TFbvTRZze2d8N/story.html>.
    [TO VERIFY: Horan's original article.]
[^5]: First full-year operating profit, $1.1 billion, for 2023: City A.M.,
    "Uber reports first ever full-year operating profit…",
    <https://www.cityam.com/uber-reports-first-ever-full-year-operating-profit-as-chief-hails-an-inflection-point/>.
    [TO VERIFY against Uber's 2023 10-K.]
[^6]: 2022 net loss of $9.1 billion, inflated by revaluing equity stakes:
    Yahoo News, "Uber's smooth operator Dara Khosrowshahi…",
    <https://ca.news.yahoo.com/ubers-smooth-operator-dara-khosrowshahi-144348071.html>.
    [TO VERIFY against the 10-K.]
