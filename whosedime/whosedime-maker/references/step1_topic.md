# Step 1: Topic

**Goal**: propose **3 topics** in the series form, with their payer lead
and a measured demand signal, recommend one, and ask **one question**.
Franco picks; you never pick for him.

## What a "Who Pays?" topic needs

1. **A brand everybody knows, and a thing that looks free or cheap**: a
   ride, points on a card, a free tier, a cheap pizza. The title must fit
   the template `[Brand] [free or cheap thing]: Who Pays?`, or `Who Paid?`
   for a closed story, **under 40 characters**, a number if possible
   (`docs/finance/PLAN_ACTION.md` § 2).
2. **A payer lead**: the people who really paid, in the order the video
   will reveal them (investors, then drivers and riders; merchants, then
   cash customers). One line, written as a lead, not a fact: it is
   checked at step 2.
3. **A decision with people**: a dated moment when someone chose to make
   the thing free or cheap (beat 3, "the decision"). No named decision
   maker, no video.
4. **Measured demand**: past videos on the brand drew viewers (below).
5. **Nothing the channel never does**: no stock tip, no political
   verdict (SKILL.md, "What the channel never does").

## Where to start: the plan's list of 10

`docs/finance/PLAN_ACTION.md` § 3 lists the first 10 videos, in order,
with title, payer lead, thumbnail idea and end-screen link (in French):

| # | Title (characters) | Payer lead |
|---|---|---|
| 1 | Uber Was Cheap. Who Paid? (25) | investors (losses in the tens of billions), then drivers and riders |
| 2 | Your Amex Points: Who Pays? (27) | merchants (2 to 3.5 % fees), then customers who pay cash |
| 3 | Airbnb's Cleaning Fee: Who Pays? (32) | guests, hosts, neighbours (rents) |
| 4 | Spotify's Free Tier: Who Pays? (30) | paying subscribers and artists (per-stream pay) |
| 5 | Rolex's Waitlist: Who Pays? (27) | grey-market buyers, dealers |
| 6 | Your Card Swipe: Who Pays? (26) | Visa and Mastercard interchange, paid by everyone through prices |
| 7 | Costco Sells at Cost. Who Pays? (31) | members (fees) |
| 8 | Wells Fargo's Fake Accounts: Who Paid? (38) | customers, employees, shareholders (fines) |
| 9 | Domino's $7.99 Pizza: Who Pays? (31) | franchisees, drivers, delivery fees |
| 10 | Chase's Free Checking: Who Pays? (32) | overdraft customers |

The leads and the numbers in these titles are **to verify** (the plan says
so): they become facts only at step 2. The reserve (videos 11-20):
Venmo, Apple Pay, Red Bull, Crocs, Starbucks, DoorDash, Zillow, Southwest,
Delta, Klarna; TurboTax in early February.

**Default**: propose the **next undone topic of the list** first, then two
others. A topic is done only if its video folder has a `04_publication.md`
(or, after S05, if the state file says published). The plan puts brands
with the highest demand (`D = 5`) first for videos 1 to 5: keep that order
unless a measurement below says otherwise.

## Measure the demand

Every demand line has a number, its source and its date. Never a view
count from memory.

1. **The brand table** `docs/finance/marques.md` (measured with the
   YouTube API on 2026-11-05, in French): for each brand, the best existing
   video (views, channel, year), its views divided by its channel's median
   (`rel`), the gap (strong videos in the last 12 months) and the score
   `D` (5 = a video of 1.4 M views or more with `rel` ≥ 2). Quote it with
   its date.
2. **A fresh check**, if `YOUTUBE_API_KEY` is set (Claude Code), from the
   repo root:
   `python3 zehon/content-maker/scripts/youtube.py chercher "<brand> story" --langue en --n 10`
   (about 100 quota units of 10,000 a day; its headings are in French, its
   numbers are what counts). Keep only videos that tell the brand's
   business story (not ads, not Shorts). Report: the best view count, its
   channel and year, and whether a video of 300 K views or more came out in
   the last 12 months (the gap).
3. **Without the key** (claude.ai, or the key unset): use `marques.md`
   alone and say "demand: measured 2026-11-05, not refreshed". If the brand
   is not in `marques.md`, write "demand: not measured".

## What you deliver (in the chat, no file)

For each of the 3 topics, 5 lines at most:

```
1. Uber Was Cheap. Who Paid? (25 characters)
   Who pays (lead): investors first, then drivers and riders
   The decision: <who, when, what they chose: to check at step 2>
   Demand: <best video, views, channel, year; rel; gap> (marques.md, 2026-11-05 | API, <date>)
   Risk: <none | what to watch: lawsuit, politics, a stock-tip trap>
```

Then **your recommendation in 2 sentences** (which one and why: demand,
gap, the list's order, the link to the end screen), and **one question**:
"Which one do we make?" (in French: « Lequel on fait ? »).

## Pause 1

When Franco has picked:

1. create the video folder `WhoseDime/Videos/<nn>_<topic>/` in Drive
   (`nn` = next number; until the S08 tree exists, the local work folder
   only) and say its name in one line;
2. append the critique line for step 1 (`"step": "1_topic"`,
   `"deliverable": "topic proposal"`) after his grade question;
3. go on with step 2 (research), unless the session ends there.
