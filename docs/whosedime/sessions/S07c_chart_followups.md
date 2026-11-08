# S07c — Chart follow-ups (from S07b's self-critique)

> Changes from ROADMAP.md: a small build session added after S07b, at Franco's request
> (2026-11-08): it fixes the four defects of S07b's self-critique (`critique_log.jsonl`,
> `build_S07b_charts`). S07b is merged (Johnfrancis6/Channel#5); it runs
> once this prompt is in `main`, before the first real assembly of video 1 (the skill's
> session 4). It does not block S08. Model: Sonnet 5.5.

## Context

S07b colours chart figures by meaning (D13) and lays out `icons` charts with one
figure size, centred. Its self-critique left four points. Two need a yes from Franco
(1, 2), one needs his eyes on a phone (3), one is his choice (4).

## Setup

```bash
git fetch origin main && git checkout main && git pull origin main   # S07b merged: git log --oneline -3
git checkout -B <the branch this session is given>
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # green (155 tests) before you start
```

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D13), `CRITIQUE_PROTOCOL.md`
2. `whosedime/whosedime-video/settings.json` (`charts`, `_charts_tone_source`)
3. `whosedime/whosedime-video/scripts/charts.py`: `Item.tone`, `IconBlock`, `icons_layout`, `draw_icons`
4. `tests/test_whosedime_video.py`, class `Charts` (`test_colour_by_meaning`, `test_icons_layout`)

## First: Franco's answers

Look in `DECISIONS.md` for D14 (task 1), D15 (task 2) and a palette line (task 4).
For each one missing, ask Franco **one question at a time**, recommendation first, in
French, before touching the code of that task. Write each answer as a new line in
`DECISIONS.md` (never edit an old one). If he says no to tasks 1 or 2, skip them and say so.

## Do

1. **Colour only on a money figure** (defect `nuance`, scene 82). *Recommended (D14):*
   gain green and loss coral apply only when the figure is an amount of money (unit `$`).
   A count of people or a percentage stays navy ink, even next to "bankrupt" or
   "profit". D13's word lists do not change.
   - In `Item.tone`: return `"ink"` unless `self.value is not None and self.value.unit == "$"`,
     then apply `LOSS_RE`, `GAIN_RE` as today.
   - Add one sentence to `_charts_tone_source` in `settings.json` (D14, the date).
   - *Measured in S07b:* the tone changes on scenes 61, 82 and 87. Only **82** changes on
     screen: `draw_icons` (61) and `draw_timeline` (87) do not use `tone`.
   *Check:* `tones(82) == ["ink", "gain", "ink", "ink"]`; scene 82's PNG has no loss-coral
   pixel; scenes 11, 35, 76 and 77 are unchanged (`test_colour_by_meaning` still passes,
   with 82 added).

2. **Two `icons` grids aligned on their value line** (defect `formal`, scene 61: the
   15-day block floats high with an empty band under it). *Recommended (D15):* the two
   values ("950", "15") sit on the same line, and the grids stand on it like bars on one
   ground line. The empty space then lies above the short grid, where it reads as
   "fewer". This replaces S07b's "same top line" rule.
   - In `icons_layout`: add `value_y` (top of the value's line) to `IconBlock`. Place each
     grid's bottom at `value_y - between - <its qualifier height>`, so that "MORE THAN"
     sits above "950" and "15" (no qualifier) still lines up with "950".
   - Centre the whole (from the highest grid top to the lowest caption bottom) between
     `top` and `bottom`. The cell size stays shared and nothing else changes.
   - *Measured in S07b:* this whole is 711 px high for 809 px free on scene 61 (777 for
     842 on 70), so it fits without shrinking the figures.
   *Check:* in `test_icons_layout`, replace the "one top line" assertion with "one
   `value_y`". Keep centre within 40 px, one cell size, cell at least 36 px, the 5 x 3 grid.
   Look at the PNG of scene 61.

3. **Sizes checked on a phone** (defect `nuance`: 36 px, 60 % and 40 px were assumed).
   *Measured (arithmetic, not seen):* a 1920 px frame shown 390 pt wide (a phone in
   portrait) divides every size by about 4.9. Figures of 54 px become 11 pt, labels of
   46 px 9.3 pt, the qualifier (30 px) 6.1 pt, the source line (26 px) 5.3 pt.
   - Redraw the 25 Uber charts and send Franco, with `SendUserFile`, the PNGs of scenes
     61, 70 and 82 (82: four columns, the smallest labels).
   - Ask one question: « Ouvre-les en plein écran sur ton téléphone, en vertical. Tout
     se lit ? Sinon, quoi : figures, libellés, petites majuscules, source ? »
   - Apply his answer in `settings.json` only, one step at a time. Too small figures:
     `icons_min_cell` +8 and `icons_max` 100 → 50 if the floor is no longer reached.
     Small capitals: `small_size` +6. Labels: `label_size` +6. Source: `source_size` +4.
     Then redraw and send them again until he says yes (at most two rounds; after that,
     note it in "Open issues").
   - Write in `_charts_source` what was checked, on which phone, and the date.
   *Check:* tests green with the new values; the 25 charts still render (no text out of
   the frame: look at 82 and 87, the busiest).

4. **The palette** (defect `process`: S07b's task 0 skipped). Franco's choice. Ask:
   « On garde la palette proposée (crème, vert dollar, corail, moutarde, bleu
   marine) ? Oui, ou quelle couleur change ? » Show `contact_S07b` (or the three PNGs of
   task 3) so he sees it in use.
   - **Yes**: in `palette.json`, `status` becomes "chosen by Franco, <date>", and
     `_roles_source` the same. Add a line to `DECISIONS.md`. Nothing else changes.
   - **A change**: follow S07b's task 0 exactly. That means `colors`, `names`,
     `prompt_line`, `status`, then the two palette lines of `evals/files/01_uber/03_scenes.md`.
     Redraw and send the three PNGs.
   *Check:* the `Palette` tests pass; no other file holds a colour.

5. **Hand over.** `python3 tools/sync_skills.py`, `--check` clean, tests green; pull
   request to `main` (Franco merges).

## Do not

- Change D13's word lists, the chart cell format, `checker.py`, `step4_scenes.md` or the
  Uber `03_scenes.md` (except the palette lines of task 4).
- Fix the other chart issues of "Open issues" (a figure said twice; cells refused
  when phrased otherwise).
- Touch the assembly, the voice notebook, Drive or Zehon files.

## Deliverables

- `charts.py`, `settings.json` (`charts`), tests; `palette.json` (task 4); synced mirror
  and `.skill`
- `DECISIONS.md` (D14, D15, palette), `STATE.md` updated, one line in
  `critique_log.jsonl`; the pull request

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next: whatever `STATE.md` names (S08 if not done
yet, else S09).
