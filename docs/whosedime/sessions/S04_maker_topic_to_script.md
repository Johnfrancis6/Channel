# S04 — `whosedime-maker`, part 1: topic to script

> Changes from ROADMAP.md: the checker exists (S03) and is the acceptance
> test of this session: the skill must produce files that
> `whosedime/common/checker.py` reads (`02b_factcheck.md` in the
> [FACTCHECK_FORMAT](../../../whosedime/common/FACTCHECK_FORMAT.md),
> `[^Fnn]` tags, `## Cold open`... headings, `02_script_voice.txt`).
> Added by Franco on 2026-11-07: task 0 fixes two S03 checker gaps first.

## Context

S02 wrote the storytelling rules (`whosedime/research/`); S03 built the
checker and the registry format (`whosedime/common/`). S04 writes the
skill's steps 1 to 3 in English: topic, research and signed fact check,
six-beat outline, script and voice version, validation by ear.

## Setup

```bash
git fetch origin claude/blissful-tesla-abtjgt
git checkout claude/blissful-tesla-abtjgt
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (70 tests) before you start
```

Stay on this branch. `git fetch` before every push. Web search is allowed
for the eval facts; never print `YOUTUBE_API_KEY` or `SUPADATA_API_KEY`.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D2, D4, D6, D7, D9, D10), `ROADMAP.md` (rules), `CRITIQUE_PROTOCOL.md`
2. `whosedime/common/README.md`, `FACTCHECK_FORMAT.md`, and the docstring of `checker.py`
3. `whosedime/research/storytelling_rules.md` (rules, by-ear rules E1-E5, limits), `voice_direction.md`, `rewrite_uber_cold_open.md`
4. `docs/finance/PLAN_ACTION.md` § 2 (six beats, titles, what the channel never does) and § 3 (first 10 topics) — in French
5. `reports/Audit pipeline de production.md` § 3 "Ce qu'il faut adapter" — in French
6. For structure only: `zehon/content-maker/SKILL.md`, `references/etape1_sujet.md` to `etape3_script.md`, `evals/evals.json` (do not edit; do not translate: rewrite for "Who Pays?")

## Do

0. **Two checker fixes (Franco, 07/11), before the skill.** In
   `whosedime/common/checker.py`, with tests in `tests/test_checker.py`:
   - **Signature bound to the content.** The signature line becomes
     `Signed: Franco, YYYY-MM-DD, sha256:<12 hex>`, the hash taken over the
     registry text without its `## Signature` section. A new command
     `checker.py fingerprint 02b_factcheck.md` prints the value to paste.
     A missing or different hash blocks `voice` ("registry changed since it
     was signed"). Update `FACTCHECK_FORMAT.md` and the fixtures
     (`factcheck_clean.md` gets its hash). *Check:* a test edits one
     verified line of a signed copy and `voice` blocks; the unchanged copy
     passes.
   - **Names at the start of a sentence.** A capitalised first word that
     is in no registry line, not in the not-names lists, and never written
     in lower case elsewhere in the file is collected; all of them go into
     **one** `WARN` line (not a block: a common word cannot be told from a
     name there). *Check:* a test where "Goldman" appears only as a first
     word gets the warning; the clean Uber script still has at most 3
     warnings (say the measured count).
   Then update the checker docstring, `whosedime/common/README.md` and the
   two lines of "Open issues" in `STATE.md`.

1. **Skill frame.** `whosedime/whosedime-maker/SKILL.md` (English, under
   250 lines): what the skill does, where it runs (Claude Code with the
   repo and the Drive connector), the files of a video folder, the pauses
   where Franco validates, one question at a time, the critique protocol
   after each deliverable. Say how it runs the checker: from the repo root,
   `python3 whosedime/common/checker.py ...`; the claude.ai archive has no
   checker, so the skill says so and stops before the voice step there.
   *Check:* `python3 tools/sync_skills.py` then `--check` reports no drift.
2. **Step 1, topic** (`references/step1_topic.md`): 3 topics in the
   "Brand + free thing: Who Pays?" form with the payer lead, a measured
   demand signal, a recommendation, one question. Start from the PLAN_ACTION
   list of 10.
3. **Step 2, research** (`references/step2_research.md`): `01_research.md`
   (sources read in full, the 3 scenes with a person, a place, a gesture,
   a line: audit C7), then `02b_factcheck.md` in the S03 format with its
   people block; Franco signs it. Nothing said aloud without a line.
4. **Step 3, outline and script** (`references/step3_script.md`): the six
   beats of PLAN_ACTION, `02_script.md` (2,000-2,250 words, `## ` heading
   per beat, `[^Fnn]` tags), `02_script_voice.txt` (numbers and symbols
   spelled out, respellings from `whosedime/common/lexicon.tsv`, nothing
   else changed), the 20 s listening sample (D6) and the E1-E5 by-ear
   checks. The step ends only when `checker.py all` has no block.
5. **Evals.** `whosedime/whosedime-maker/evals/evals.json`: at least 3
   prompts (topic; research and fact check for Uber; script from a signed
   fact check). Run the script eval once yourself on Uber, with facts you
   actually read (web), into a scratch folder: *Check:* `checker.py all`
   gives no block and at most 3 warnings on it. Do not reuse
   `tests/fixtures/whosedime/factcheck_clean.md`: its facts were written
   from memory and never checked.

## Do not

- Write steps 4-5 (scenes, publication: S05), the voice notebook (S06),
  or anything in Drive (S08).
- Edit `checker.py` beyond task 0, or `style_thresholds.json` or the lists
  to make an eval pass: a misfire goes to "Open issues" and the critique log.
- Touch Zehon files.

## Deliverables

- Task 0: `checker.py`, `FACTCHECK_FORMAT.md`, `README.md`, tests and fixtures updated
- `whosedime/whosedime-maker/` (SKILL.md, references 1-3, evals), synced
  mirror and `whosedime/whosedime-maker.skill`
- `docs/whosedime/STATE.md` updated, one line per deliverable group in
  `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S05_maker_scenes_to_publication.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S05 —
`whosedime-maker`, part 2: scenes to publication, and state, model
Sonnet 5.5**. S05 must keep the publication format the checker reads
(`## Titles` as a list, `## Thumbnail`, `## Description`, `## Sources`).
