# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, end of S07 Charts and assembly
(session `session_01Cw13Lf9vU36VbFFB3o3udA`).

## Where we are

- **S01 to S05 in `main`**. **S06 and S07 on the work branch**, in one pull request to `main` (Franco merges).
- **S07 done.** Palette: one source, [`whosedime/common/palette.json`](../../whosedime/common/palette.json) (charts, cards and
  `step4_scenes.md` read it; a test fails on any other colour). Charts: `charts.py`, eight kinds, verified facts only.
  Assembly: skill [`whosedime/whosedime-video/`](../../whosedime/whosedime-video/SKILL.md) (not `video-maker/`: Zehon's name),
  gate (checker + voice ready), timing on `words.json`, cards, `chapters.txt`, `verdict_<output>.json` with `branch@commit`;
  notebook and launcher `whosedime/notebooks/assembly_*.ipynb`.
  - **Measured**: the 25 Uber charts render (1920x1080); a `[TO VERIFY]` fact and a number not in its fact are refused;
    a 10-scene stub (generated images, test clip, tone-burst voice) renders at 1920x1080 and passes the technical
    check (68 s rendered in 34 s, ultrafast, 2 cores); an extract leaves `verdict_video.json` and `chapters.txt` byte-identical.
  - **Not run**: a real voice, real images, Colab. First real assembly: video 1, the skill's session 4.

## Branches

| Branch | Role |
|---|---|
| `claude/blissful-tesla-abtjgt` | **work branch** for build sessions (S06 + S07 on top of `main`); pull request open |
| `main` | production (Colab launchers); has S01 to S05; S06 + S07 once Franco merges |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`).
- Charts: `python3 whosedime/whosedime-video/scripts/charts.py FOLDER`. Assembly: `.../assemble.py FOLDER [--plan] [--scenes 1-10]`.
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **152 pass**, measured 07/11 (about 40 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07 | **done** 07/11 (S06 + S07 wait for Franco's merge) |
| S08 Drive and pilot | **next** — prompt ready: [`sessions/S08_drive_and_pilot.md`](sessions/S08_drive_and_pilot.md); needs the merge first |
| S09 | planned in `ROADMAP.md` |

## Open issues

- **For Franco** (S05 choices, assumed): the `title` card ("WHO PAYS?", navy, as S07 draws it); the palette in
  `palette.json` and its roles (gain green, loss coral, highlight mustard). Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan?
- **Voice, to check on video 1**: the qwen-tts calls (never run); the 25 dB "still loud" threshold; stitched pauses
  (`stretch_inner_pauses`); the T4 run time. **Not built**: a second voice for quoted lines; a speed lever. Blind test = 7 block pairs.
- **Assembly, to check on video 1**: render time on Colab (30-45 min assumed); clips slowed x1.35 then frozen; on-screen band size.
  Years said in pairs ("twenty ten") do not match "2010" in the alignment (scene found at ~90 %, harmless so far).
- **Assembly, not built** (not in S07's scope): music bed and `.srt` subtitles (Zehon had both).
- **Charts**: tone by keyword ("only 10 percent earned" in green); `icons` sits high in the frame; a cell phrased
  outside the patterns is refused (never drawn wrong): step 4 may have to rephrase it.
- **D12**: thumbnail A puts Kalanick by "$7.9 BILLION" (deficit to end 2018, F13); he left in June 2017 (F11). Untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block;
  `name-first` noisy; two tokenisers (2,103 vs 2,087 words); numbers match by value.
- Uber eval: beat 3 is the 2016 Saudi investment; no named taxi owner; F05 (an estimate) in 3 of 25 charts.
- Step 1 uses Zehon's `youtube.py` (French output). Fixture `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script. Critique log: 26 lines, none graded.
