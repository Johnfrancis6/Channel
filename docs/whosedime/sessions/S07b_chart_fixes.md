# S07b — Chart fixes (colour and layout)

> Changes from ROADMAP.md: a small build session added after S07, from Franco's
> request (2026-11-08) on two defects of S07's self-critique (`critique_log.jsonl`,
> `build_S07_charts`: `nuance` on the tone, `formal` on `icons`). It runs after the
> S06+S07 pull request is merged and before the first real assembly of video 1 (the
> skill's session 4); it does not block S08. Model: Opus 5.5.

## Context

`whosedime/whosedime-video/scripts/charts.py` draws the 25 Uber charts, but (1) the
colour of a figure is guessed from words, so "only 10 percent earned $90,000"
(scene 50) comes out in gain green; (2) the `icons` charts (scenes 61, 70) sit high
in the frame with an empty band under them, and two grids side by side use
different figure sizes.

## Setup

```bash
git fetch origin main && git checkout main && git pull origin main   # S06+S07 merged
git checkout -B <the branch this session is given>
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # green (152 tests) before you start
```

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md`, `CRITIQUE_PROTOCOL.md`
2. `whosedime/whosedime-video/SKILL.md` (§ "The charts"), `settings.json` (`charts`)
3. `whosedime/whosedime-video/scripts/charts.py`: `LOSS_RE`, `GAIN_RE`, `Item.tone`, `draw_compare`, `draw_icons`
4. `whosedime/common/palette.json` (`roles`)
5. `tests/test_whosedime_video.py`, class `Charts`

## Do

0. **The palette, only if Franco has chosen it** (`DECISIONS.md` holds a line for
   it). Else skip, and say so in one line. Change `whosedime/common/palette.json`
   only: `colors`, `names`, `prompt_line` (`<name> <hex>, ...` in the order of
   `colors`), `status` ("chosen by Franco, <date>"), `roles` if he changed them; then
   copy `prompt_line` into the two lines of `evals/files/01_uber/03_scenes.md`
   (`Palette (channel, every image and chart): ...` and the preamble's `Palette: ...`).
   *Check:* the `Palette` tests pass; no other file holds a colour.

1. **Colour by meaning, not guessed** (defect `nuance`). Recommended rule, the one
   Franco approved on 2026-11-08:
   - gain green only for the company's money coming in: `profit`, `revenue`;
   - loss coral only for money lost: `loss`, `losses`, `lost`, `deficit`, `bankrupt*`, `crash*`;
   - everything else navy ink; in a `compare` without gain or loss, the last item in
     mustard (the figure to look at), as today.

   So: reduce `GAIN_RE` to `profit|revenue`; keep `LOSS_RE` but remove `fell`,
   `cut off`, `warnings` (they are not money: scene 68 keeps its coral note because
   `draw_scale` colours it itself, not through `tone`). Put both word lists in
   `settings.json` (`charts.gain_words`, `charts.loss_words`, with a `_source` line):
   the one-place rule (C5). No new field in the chart cell: the checker reads that
   format and must not change.
   *Check:* a test: scene 50 has no item in gain green; scene 77 keeps the 2022 loss in
   coral and the 2023 profit in green; scene 11 keeps losses coral, revenue green.

2. **The `icons` layout** (defect `formal`). In `draw_icons`:
   - compute the layout first, draw after: split it into `icons_layout(spec, top,
     bottom) -> [(cell size, cols, rows, grid box, caption box)]` (no drawing), so a
     test can measure it;
   - **one figure size for the whole chart**: with two grids, use the smaller of
     the two cell sizes for both, so 95 owners and 15 days read at the same scale;
   - **centre the block vertically**: grid + value + caption, as one block, centred
     between `top` and `bottom` (as `Canvas.stack` does for text); the two items'
     blocks share the same top line;
   - a gap between figures of about 15 % of the cell (today they touch), and a cell
     size of at least 36 px at 1920x1080; if 100 figures cannot reach it, lower
     `icons_max` in `settings.json` rather than shrink further.
   *Check:* a test on scenes 61 and 70: the block's centre is within 40 px of the
   free area's centre; with two grids, both cell sizes are equal; every cell is at
   least 36 px. Then look at the PNGs yourself (scenes 61, 70).

3. **Look, then hand over.** Redraw the 25 Uber charts into a scratch folder and look
   at scenes 11, 25, 42, 50, 61, 70, 77, 82 (a contact sheet is enough). Then
   `python3 tools/sync_skills.py`, `--check` clean, tests green; pull request to
   `main`, Franco merges.

## Do not

- Change the chart cell format, `checker.py`, `step4_scenes.md`'s chart rules or the
  Uber `03_scenes.md` (except the palette lines of task 0).
- Fix the other S07 chart defects (`robotic`: a figure said twice; cells refused when
  phrased otherwise): they stay in "Open issues".
- Touch the assembly, the voice notebook or Zehon files.

## Deliverables

- `charts.py`, `settings.json` (`charts`), tests; `palette.json` and the eval's palette
  lines only with task 0; synced mirror and `.skill`
- `docs/whosedime/STATE.md` updated, one line in `critique_log.jsonl`; the pull request

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next: whatever `STATE.md` names (S08 if not done
yet, else S09).
