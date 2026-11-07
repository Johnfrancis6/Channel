# S03 — Shared checks

> Changes from ROADMAP.md: S02 found that no style metric separates hits
> from flops, so **every style rule is `warn`**; only facts, tags, titles
> and forbidden phrases block. Per-1,000-word style rules apply to whole
> scripts only (they swing on one word in a 150-word extract).

## Context

S02 turned the niche's hits and flops into 14 measurable style rules
(`whosedime/research/`). S03 builds the shared checker that every later
step runs: facts against the registry (C1, C2, D4), script against voice
version, forbidden phrases, title length, and the S02 style warnings.

## Setup

```bash
git fetch origin claude/blissful-tesla-abtjgt
git checkout claude/blissful-tesla-abtjgt
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (46 tests) before you start
```

Stay on this branch. `git fetch` before every push. No API calls are
needed; never print `YOUTUBE_API_KEY` or `SUPADATA_API_KEY`.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D4, D9), `ROADMAP.md` (rules), `CRITIQUE_PROTOCOL.md`
2. `whosedime/research/README.md`, `storytelling_rules.md` (rules, limits),
   `style_thresholds.json`, `tools/measure.py` (its docstring states every method)
3. `whosedime/research/rewrite_uber_cold_open.md` (the source-tag format in use)
4. `reports/Audit pipeline de production.md` (French): § 3 C1, C2, C5, C7,
   and "Ce qu'il faut adapter" (people registry, voice version in English,
   end of video, financial advice)
5. `docs/finance/PLAN_ACTION.md` § 2 (title template, "what the channel never does")
6. For reference only, the Zehon checker it replaces: `zehon/content-maker/scripts/verifier.py` (do not edit it)

## Do

1. **Registry format.** Define `02b_factcheck.md` (D4): one line per fact
   with an id (`F01`…), the exact text as it may appear (number, date,
   name), the source (URL or document and page), the date read, and a
   status; a people block (name, role, date, decision, exact quote with
   source); a signature line for Franco. Write it in
   `whosedime/common/FACTCHECK_FORMAT.md` with one complete example (Uber,
   from the S02 footnotes). *Check:* the parser reads the example back.

2. **Checker.** `whosedime/common/checker.py` (standard library only),
   one command per target: `script`, `voice`, `publication`, `all`.
   Exit 1 on any `block`. Blocks:
   - a number, date or name in the script or publication absent from the
     registry; a quotation not word for word in the people block;
   - any `[TO VERIFY]` tag; an unsigned registry blocks `voice`;
   - a title over 40 characters (PLAN_ACTION § 2);
   - a forbidden phrase (buy/sell advice, price target, "undervalued",
     narrator as adviser: PLAN_ACTION § 2, list in a file, not in code);
   - the voice version differing from the script beyond allowed rewrites
     (numbers and symbols spelled out, lexicon respellings).
   Warns: every rule of `style_thresholds.json`, computed by importing
   `whosedime/research/tools/measure.py` (`importlib`, no copy). **No
   threshold, metric or rule id is written in the checker's code**: it
   loops over the JSON. S1, S8 and S9 are measured on the cold open (first
   ~110 words, or the "Cold open" section); the others on the whole script.
   Also warn if the last 60 words do not announce the next video
   (audit, "adapt" list).

3. **Faulty files and tests.** `tests/test_checker.py`, with fixtures in
   `tests/fixtures/whosedime/`, each feeding one fault:
   - `script_unknown_number.md` (a figure not in the registry) → block
   - `script_to_verify.md` (a `[TO VERIFY]` tag) → block
   - `script_misquote.md` (a quote one word off the people block) → block
   - `factcheck_unsigned.md` → `voice` blocks
   - `publication_long_title.md` (41 characters) → block
   - `publication_unknown_number.md` (description figure not in the registry) → block
   - `script_advice.md` ("you should buy the stock") → block
   - `voice_drift.txt` (a sentence changed, not just respelled) → block
   - `script_zehon_style.md` (built from `research/examples/uber_before.txt`) → ≥ 2 style warnings
   - `script_clean.md` + `factcheck_clean.md` (a real-looking 2,000-word
     Uber script, facts all in the registry) → no block, **≤ 3 warnings**
   - one test that edits a threshold in a temporary copy of the JSON and
     sees the warning change (proves nothing is hard-coded).
   *Check:* all tests pass; the clean pair passes with ≤ 3 warnings.

4. `whosedime/common/README.md` (20 lines at most): commands, exit codes,
   where each list lives.

## Do not

- Write skill content (S04, S05) or the voice notebook (S06).
- Change a threshold in `style_thresholds.json` to make a fixture pass:
  if a rule misfires, note it in "Open issues" and in the critique log.
- Touch Zehon files or Drive.

## Deliverables

- `whosedime/common/`: `checker.py`, `FACTCHECK_FORMAT.md`, forbidden
  phrases list, `README.md`; `tests/test_checker.py`, `tests/fixtures/whosedime/`
- `docs/whosedime/STATE.md` updated, one line per deliverable group in
  `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S04_maker_topic_to_script.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S04 —
`whosedime-maker`, part 1: topic to script, model Opus 5.5**.
