# S02 — Storytelling rules for "Who Pays?"

> Changes from ROADMAP.md: adds `whosedime/research/style_thresholds.json`,
> so that S03's checker reads every threshold from one file (C5); raw
> transcripts stay out of git (only metrics and short quotes are committed).

## Context

Zehon scripts and voice were judged robotic, formal, flat and hard to
follow (audit, symptoms 1 and 2). Whose Dime is a different narrator: an
American storyteller of famous companies, one named person and one
decision at a time, then the money down to whoever pays. This session
turns the niche's hits and flops into **writing and voice rules with
numbers**, which S03 will check automatically. No skill content yet.

## Setup

```bash
git fetch origin claude/admiring-ramanujan-k2uiqe
git checkout claude/admiring-ramanujan-k2uiqe
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green before you start
```

Stay on this branch. `git fetch` before every push. Supadata
(`SUPADATA_API_KEY`) gives transcripts, YouTube Data v3
(`YOUTUBE_API_KEY`) gives views and durations: never print either key.
Reddit and Social Blade are blocked from the cloud: no workaround.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md`, `ROADMAP.md` (rules), `CRITIQUE_PROTOCOL.md`
2. `reports/Crayon Capital et concurrents.md` (French): § "L'ouverture",
   "Facteurs de réussite", "Facteurs de perte", "Ce que ça change pour
   Whose Dime". Its data and API helpers: `research_notes/Crayon Capital
   et concurrents/` (`crayon_videos.csv`, `chaines.csv`, `outils/yt2.py`).
3. `reports/Audit pipeline de production.md` (French): § 2 symptoms 1-2
   (V1 to V7), § 3 C6 and C7, and the list "Ce qu'il faut adapter".
4. `docs/finance/PLAN_ACTION.md` § 7 and the S1 voice row;
   `docs/finance/marques.md` (Uber's line, the title template).
5. For the before/after only: one Zehon script for contrast
   (`zehon/content-maker/evals/` or a Drive `02_script.md`), not as a model.

## Do

1. **Corpus.** From the storyteller channels (Crayon Capital, Built On
   You, CEOzoned, JunkBondInvestor, MagnatesMedia), pick **20 hits**
   (≥ 2× their channel's median views) and **10 flops** (≤ 0.5×), 8 to 25
   min long, published in the last 24 months. Fetch their transcripts
   (Supadata, 40 calls at most) into `whosedime/research/corpus/raw/`
   (add it to `.gitignore`: we do not republish other people's scripts).
   Commit `whosedime/research/corpus/index.csv` (video id, channel,
   title, published, duration, views, ratio to channel median, hit/flop).
   *Check:* 30 rows, every ratio recomputed from the API, quota and
   Supadata calls written at the bottom of the README of `research/`.

2. **Measure.** Write `whosedime/research/tools/measure.py` (English,
   standard library only, so S03 can import it): for one text, compute
   at least the metrics below. Run it on every transcript into
   `whosedime/research/corpus/metrics.csv`, and on two Zehon scripts for
   the gap. Add `tests/test_measure.py` with a short hand-counted text.
   - words per minute (transcript words / duration);
   - words before the first named person; words before the first
     tension marker (but, yet, then, until, instead, only to…);
   - named people per 150 words (proper names of persons, list method
     stated);
   - quoted dialogue lines per 1,000 words;
   - sentence length: mean, standard deviation, share above 25 words;
   - numbers per 100 words; numbers in the first 60 words;
   - contrast words (but, yet, however, although, except) per 1,000 words;
   - questions to the viewer per 1,000 words;
   - most repeated sentence opener and its count;
   - finance jargon per 1,000 words (list in the file) and share of jargon
     explained within the next 25 words (method stated).
   *Check:* the test passes; metrics.csv has 30 + 2 rows.

3. **Rules.** Write `whosedime/research/storytelling_rules.md` (English)
   and `whosedime/research/style_thresholds.json`. One rule per metric
   that separates hits from flops, plus the rules the audit already
   asks for (C7: repeated connector ≤ 3, sentence-length standard
   deviation ≥ 5 words, ≤ 1 number per 40 words: re-measure, do not copy).
   For every rule: id (`S1`, `S2`…), the plain-English rule, the metric,
   **the threshold**, hits median vs flops median and n, its source
   (niche transcripts, Zehon audit, or both), what changes from Zehon,
   and the level: `block` or `warn`. A rule with no measurable metric is
   listed apart as "by ear" (Franco's 20 s listening, D6), five at most.
   The JSON holds exactly the ids, metrics, thresholds and levels of the
   `.md`. *Check:* every `.md` rule has its JSON entry and vice versa;
   no threshold without n and source; `block` only where hits and flops
   do not overlap on their interquartile ranges (otherwise `warn`).

4. **Voice direction.** Write `whosedime/research/voice_direction.md`:
   the American narrator (D8: VoiceDesign, then clone on the Base model),
   target words per minute (measured range of the hits), pause lengths by
   punctuation (start from audit C6: 250 / 450 / 700 ms), energy, how the
   short dialogue lines are voiced, what made the Zehon voice robotic
   (V1-V7, measured or assumed), the VoiceDesign description to try,
   and the blind-test protocol for video 1 (D7: paragraph vs sentence
   synthesis; goal from C6: under 1 dry ending in 30, old way preferred
   under 1 time in 4). *Check:* every number has its source.

5. **Before/after.** In `whosedime/research/rewrite_uber_cold_open.md`,
   the first ~150 words of "Uber Was Cheap. Who Paid?" written twice:
   a "before" in Zehon's style translated to English, and an "after"
   that follows the rules. Run `measure.py` on both and show the table
   against the thresholds. Every number, date, name and quote is
   sourced in a footnote or tagged `[TO VERIFY]` (D4).
   *Check:* the "after" passes every `block` rule; the "before" fails
   at least two.

6. Write `whosedime/research/README.md` (20 lines at most): what each
   file is, how to rerun the measurement, the quota used.

## Do not

- Build the checker (S03) or write skill content (S04, S05).
- Build the weekly watch (S09): no competitor tracking tool, no `docs/veille/`.
- Commit full transcripts, or quote more than two sentences of any video.
- Touch Zehon files or Drive.

## Deliverables

- `whosedime/research/`: `README.md`, `storytelling_rules.md`,
  `style_thresholds.json`, `voice_direction.md`,
  `rewrite_uber_cold_open.md`, `corpus/index.csv`, `corpus/metrics.csv`,
  `tools/measure.py`; `tests/test_measure.py`; `.gitignore` line
- `docs/whosedime/STATE.md` updated, one line per deliverable group in
  `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S03_shared_checks.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". The S03 prompt must point the
checker to `style_thresholds.json` and `measure.py` (no threshold copied
into code), and list the faulty test files it needs. Next session:
**S03 — Shared checks, model Opus 5.5**.
