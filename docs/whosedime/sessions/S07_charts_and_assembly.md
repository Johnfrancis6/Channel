# S07 — Charts and assembly

> Changes from ROADMAP.md: S06 is on the work branch, not in `main`: the
> S07 pull request carries S06 and S07 together. The assembly reads the
> voice's `words.json` as S06 defined it (`whosedime/notebooks/README.md`),
> not Zehon's `mots.json`. The S05 choices (title card, palette) are still
> Franco's: build with them as assumed and keep them in one source.

## Context

The skill writes `03_scenes.md` (91 scenes on Uber: 54 images, 25 charts
tied to fact ids, 5 clips, 1 title and 6 chapter cards); S06 writes
`voice/voice.wav` and `voice/words.json`. S07 draws the charts from
`02b_factcheck.md` and adapts the assembly (audit C4, P3).

## Setup

```bash
git fetch origin claude/blissful-tesla-abtjgt
git checkout claude/blissful-tesla-abtjgt
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (125 tests) before you start
```

Stay on this branch. `git fetch` before every push. Never print
`YOUTUBE_API_KEY` or `SUPADATA_API_KEY`.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D2, D4, D5, D10), `ROADMAP.md` (rules, S07 row), `CRITIQUE_PROTOCOL.md`
2. `whosedime/whosedime-maker/references/step4_scenes.md` (scene types, chart scenes, the file format, the palette)
3. `whosedime/whosedime-maker/evals/files/01_uber/03_scenes.md` and `02b_factcheck.md` (the test input)
4. `whosedime/notebooks/README.md` and `voice_whosedime.py` (`assemble`, the `words.json` shape), `voice_settings.json` (the one-place settings pattern to copy)
5. `whosedime/common/checker.py` (`check_scenes`, `settings.json` `scenes`): reuse its scene parser, do not write a second one
6. `reports/Audit pipeline de production.md` § 2.2 P3 and § 3 C4 (in French)
7. For structure only: `zehon/video-maker/SKILL.md`, `zehon/video-maker/scripts/monter.py`, `zehon/notebooks/montage_zehon.ipynb` (do not edit; rewrite, do not translate)

## Do

1. **One palette source** (C5): the channel palette in one file the chart
   tool, the assembly and `step4_scenes.md` all point to (assumed values
   from S05 until Franco decides). *Check:* a test fails if two places hold
   different colours.
2. **Chart tool**: `charts/scene_NNN.png` (1920×1080) for every `chart`
   scene, kinds `number`, `compare`, `split`, `timeline`, `icons`,
   `scale`, `shape`, `map` (`settings.json` `chart_kinds`), each number
   read from the `verified` fact the scene cites, never typed by hand;
   a fact still `[TO VERIFY]` blocks. *Check:* the 25 Uber charts render;
   a test feeds a chart citing an unverified fact and a number that is not
   in its fact, and both are refused.
3. **Assembly** `whosedime/video-maker/` (skill + script): scenes from
   `03_scenes.md`, aligned on `voice/words.json` (word times), images with
   the four motions, charts, clips, the `title` and `chapter` cards, then
   `render/video.mp4`, `render/chapters.txt` (times for the description,
   `0:00` first), and a verdict **named after its output**
   (`verdict_<output>.json`): an extract never overwrites the full video's
   verdict (P3). The verdict carries `main@<commit>` (C3).
   *Check:* a short test render (about 10 scenes, generated images and a
   stub voice) passes the technical check; an extract leaves the full
   verdict untouched.
4. **Notebook and launcher** for the assembly, as S06 did for the voice
   (`launcher.py` is shared; Colab runs `main`, prints the commit).
5. **Sync, tests, pull request**: tests green; `sync_skills.py --check`
   clean; one PR to `main` with S06 and S07 (ROADMAP rule 2), Franco merges.

## Do not

- Anything in Drive (S08), or edit the voice notebook beyond what the
  assembly needs from `words.json` (a change there goes to "Open issues").
- Edit `checker.py` rules, `style_thresholds.json` or the lists; a misfire goes to "Open issues".
- Touch Zehon files.

## Deliverables

- the palette source, the chart tool, `whosedime/video-maker/`, the assembly notebook and launcher, tests; synced mirror and `.skill`
- `docs/whosedime/STATE.md` updated, one line per deliverable group in `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S08_drive_and_pilot.md`; the pull request to `main`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S08 — Drive and
pilot launch, model Sonnet 5.5**. Carry over: the S05 choices (title card,
palette), the lexicon proposals (UK, LeWeb, Rumayyan), and S06's checks for
video 1 (first real voice run: the narrator design, the 20 s sample, the
blind test, the detector's thresholds, the `WhoseDime/Voice/` folder).
