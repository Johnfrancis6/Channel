# S05 — `whosedime-maker`, part 2: scenes to publication, and state

> Changes from ROADMAP.md: S04 ran the script eval on Uber with facts read
> on the web; its outputs in `whosedime/whosedime-maker/evals/files/01_uber/`
> are the input of S05's scenes and publication evals. The signature is now
> bound to the registry's content (`sha256:` hash, `checker.py fingerprint`).

## Context

S04 wrote steps 1 to 3 of the skill (topic, research and signed fact
check, outline, script, voice version, 20 s listening). S05 writes steps 4
and 5 (scenes and image prompts, publication), the per-video state and the
session table, then opens the pull request to `main` (ROADMAP rule 2).

## Setup

```bash
git fetch origin claude/blissful-tesla-abtjgt
git checkout claude/blissful-tesla-abtjgt
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (84 tests) before you start
```

Stay on this branch. `git fetch` before every push. Never print
`YOUTUBE_API_KEY` or `SUPADATA_API_KEY`.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D2, D4, D5, D10), `ROADMAP.md` (rules, S05 row), `CRITIQUE_PROTOCOL.md`
2. `whosedime/whosedime-maker/SKILL.md` and `references/step3_script.md` (what S05 continues), `evals/README.md`
3. `whosedime/common/README.md`, `FACTCHECK_FORMAT.md` (§ Tags), `settings.json`
4. `docs/finance/PLAN_ACTION.md` § 2 (scenes, thumbnails, title template) — in French
5. `reports/Audit pipeline de production.md` § 3: C2, C4 and "Ce qu'il faut adapter" (scenes, thumbnails) — in French
6. For structure only: `zehon/content-maker/references/etape4_scenes.md`, `etape5_publication.md`, `memoire.md` (do not edit; do not translate: rewrite for "Who Pays?")

## Do

1. **Step 4, scenes** (`references/step4_scenes.md`): `03_scenes.md`, 85 to
   95 scenes of 9-10 s whose spoken text is the script **word for word**;
   types `image` (50-55 Gemini images), `chart` (25-30, each citing the
   `verified` fact id it draws, e.g. `chart: F07`), `video` (4-5 Flow
   clips), `chapter` (6 cards: the beats, the 3 dollar steps); image
   prompts in English, shown in full in the chat, one code block each.
   No real person drawn realistically; no exact brand logo.
2. **Step 5, publication** (`references/step5_publication.md`):
   `04_publication.md` in the format the checker reads: `## Titles` (a
   list, each ≤ 40 characters, each citing its fact id `[^Fnn]` when it
   holds a number: C2), `## Thumbnail` (1-3 words or one number, the
   "WHO PAYS?" badge, cartoon caricature only of a well-known executive,
   PLAN_ACTION § 2), `## Description`, `## Sources`; chapters from the
   `chapter` scenes. *Check:* `checker.py publication` has no block.
3. **State and sessions** (C4): `references/memory.md` (Drive memory
   files), a per-video state file in the video folder that lists every
   step (content, pieces, voice, render, publication) and is rewritten at
   the end of each step, and the session table in `SKILL.md` (phase,
   model, where it stops). Keep `SKILL.md` under 250 lines. *Check:* a
   fresh Haiku session given only the files answers "where are the
   videos?" correctly (say how you tested it, or that you could not).
4. **Evals**: add scenes and publication prompts to `evals/evals.json`,
   from `files/01_uber/`; run the publication eval once: `checker.py all`
   on the folder gives no block. A chart that cites no verified id must be
   caught: if that needs a new `scenes` check in the checker, write it
   with a test that feeds it a faulty file (ROADMAP rule 5).
5. **Sync and PR**: `python3 tools/sync_skills.py`, `--check` clean, tests
   green; pull request to `main` with what Colab needs (Franco merges).

## Do not

- Write the voice notebook (S06), the chart generator or the assembly (S07), or anything in Drive (S08).
- Edit the checker's existing rules, `style_thresholds.json` or the lists to make an eval pass: a misfire goes to "Open issues" and the critique log.
- Touch Zehon files.

## Deliverables

- `whosedime/whosedime-maker/references/step4_scenes.md`, `step5_publication.md`, `memory.md`; `SKILL.md` (session table, state); evals; synced mirror and `.skill`
- `docs/whosedime/STATE.md` updated, one line per deliverable group in `docs/whosedime/critique_log.jsonl`
- the pull request to `main`; `docs/whosedime/sessions/S06_voice_notebook.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S06 — Voice
notebook (English), model Opus 5.5**. Carry over from S04's open issues:
the lexicon proposals (UK, LeWeb, Rumayyan) wait for Franco's answer.
