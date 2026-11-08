# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of S07c Chart follow-ups (session `session_01Cw13LfEmvF2UXEYu91tfaM`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). **S07c done** on the work branch: pull request to `main`, Franco merges.
  D14: green/coral only on an amount in `$` (scene 82's "950" owners now ink). D15: two `icons` grids
  stand on one value line (scene 61). D16: palette chosen as proposed. **Measured**: tones change on 61, 82, 87 only
  (on screen: 82); 61 whole 801 px for 809 free, centre 0 px; 25 charts render, no pixel at the frame's edge.
  **Seen by Franco on his phone** (model not named): 61, 70, 82 read after two rounds (labels 46→58, small capitals 30→42).
- **S07b done.** Colour by meaning (D13, `whosedime-video/settings.json` `charts`). **Assumed**: grid ≤ 60 % of free height.
- **S07 done.** Palette: one source, [`whosedime/common/palette.json`](../../whosedime/common/palette.json) (charts, cards and
  `step4_scenes.md` read it; a test fails on any other colour). Charts: `charts.py`, eight kinds, verified facts only.
  Assembly: skill [`whosedime/whosedime-video/`](../../whosedime/whosedime-video/SKILL.md) (not `video-maker/`: Zehon's name),
  gate, timing on `words.json`, cards, `chapters.txt`, `verdict_<output>.json`; notebook `whosedime/notebooks/assembly_*.ipynb`.
  - **Measured**: unverified facts and hand-typed numbers refused; a 10-scene stub renders and passes the check (68 s in
    34 s, 2 cores); an extract leaves the verdict intact. **Not run**: real voice, images, Colab (video 1, skill session 4).

## Branches

| Branch | Role |
|---|---|
| `claude/youthful-gates-n4y1rl` | **work branch**: S07c, on top of `main` (pull request) |
| `main` | production (Colab launchers); has S01 to S07b |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`).
- Charts: `python3 whosedime/whosedime-video/scripts/charts.py FOLDER`. Assembly: `.../assemble.py FOLDER [--plan] [--scenes 1-10]`.
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **155 pass**, measured 08/11 in S07c (about 35 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07c | **done** 08/11 (S07c: pull request to `main`) |
| S08 Drive and pilot | **next** — prompt ready: [`sessions/S08_drive_and_pilot.md`](sessions/S08_drive_and_pilot.md) (palette no longer asked) |
| S09 | planned in `ROADMAP.md` |

## Open issues

- **For Franco** (S05 choice, assumed): the `title` card ("WHO PAYS?", navy, as S07 draws it). Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan?
- **Voice, to check on video 1**: the qwen-tts calls (never run); the 25 dB "still loud" threshold; stitched pauses
  (`stretch_inner_pauses`); the T4 run time. **Not built**: a second voice for quoted lines; a speed lever. Blind test = 7 block pairs.
- **Assembly, to check on video 1**: render time on Colab (30-45 min assumed); clips slowed x1.35 then frozen; on-screen band size.
  Years said in pairs ("twenty ten") do not match "2010" (scene found at ~90 %). Not built: music bed, `.srt` subtitles.
- **Charts**: scene 61's figures stay 54 px (95 people; `icons_max` 50 would draw 950 as 10 figures, fewer than the 15
  days). 61 now fills 801 of 809 px: a longer caption is refused (new check in `icons_layout`). Source line (26 px) not
  flagged on the phone. Not done: a figure said twice; odd cells refused.
- **D12**: thumbnail A puts Kalanick by "$7.9 BILLION" (deficit to end 2018, F13); he left in June 2017 (F11). Untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block;
  `name-first` noisy; two tokenisers (2,103 vs 2,087 words); numbers match by value.
- Uber eval: beat 3 is the 2016 Saudi investment; no named taxi owner; F05 (an estimate) in 3 of 25 charts.
- Step 1 uses Zehon's `youtube.py` (French output). Fixture `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script. Critique log: 30 lines, none graded.
