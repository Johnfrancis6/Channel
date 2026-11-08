# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of S07b Chart fixes (session `session_01Cw13LgR83sp5FmkpGUvBWU`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). The S07c prompt is on the work branch (pull request to `main`).
- **S07b done.** Colour by meaning (D13, words in `whosedime-video/settings.json` `charts`); `icons_layout`: one figure
  size, block centred, 15 % gap. **Measured**: scene 50 has no green; 61 at 54 px (both grids), 70 at 110 px, centre
  0 px off. **Assumed**: 36 px reads on a phone; grid at most 60 % of the free height.
- **S07 done.** Palette: one source, [`whosedime/common/palette.json`](../../whosedime/common/palette.json) (charts, cards and
  `step4_scenes.md` read it; a test fails on any other colour). Charts: `charts.py`, eight kinds, verified facts only.
  Assembly: skill [`whosedime/whosedime-video/`](../../whosedime/whosedime-video/SKILL.md) (not `video-maker/`: Zehon's name),
  gate, timing on `words.json`, cards, `chapters.txt`, `verdict_<output>.json`; notebook `whosedime/notebooks/assembly_*.ipynb`.
  - **Measured**: 25 Uber charts at 1920x1080; unverified facts and hand-typed numbers refused; a 10-scene stub renders
    and passes the technical check (68 s in 34 s, ultrafast, 2 cores); an extract leaves the verdict and chapters intact.
  - **Not run**: a real voice, real images, Colab. First real assembly: video 1, the skill's session 4.

## Branches

| Branch | Role |
|---|---|
| `claude/funny-dijkstra-js9xbz` | **work branch**: S07c prompt, on top of `main` |
| `main` | production (Colab launchers); has S01 to S07b |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`).
- Charts: `python3 whosedime/whosedime-video/scripts/charts.py FOLDER`. Assembly: `.../assemble.py FOLDER [--plan] [--scenes 1-10]`.
- Skill sync: `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests` — **155 pass**, measured 08/11 (about 36 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07b | **done**, merged 08/11 |
| S07c Chart follow-ups | prompt ready: [`sessions/S07c_chart_followups.md`](sessions/S07c_chart_followups.md) (S07b's critique); after this prompt's merge, before video 1's assembly |
| S08 Drive and pilot | **next** — prompt ready: [`sessions/S08_drive_and_pilot.md`](sessions/S08_drive_and_pilot.md); S07c can run before or after |
| S09 | planned in `ROADMAP.md` |

## Open issues

- **For Franco** (S05 choices, assumed): the `title` card ("WHO PAYS?", navy, as S07 draws it); the palette in
  `palette.json` and its roles (gain green, loss coral, highlight mustard). Lexicon: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan?
- **Voice, to check on video 1**: the qwen-tts calls (never run); the 25 dB "still loud" threshold; stitched pauses
  (`stretch_inner_pauses`); the T4 run time. **Not built**: a second voice for quoted lines; a speed lever. Blind test = 7 block pairs.
- **Assembly, to check on video 1**: render time on Colab (30-45 min assumed); clips slowed x1.35 then frozen; on-screen band size.
  Years said in pairs ("twenty ten") do not match "2010" (scene found at ~90 %). Not built: music bed, `.srt` subtitles.
- **Charts → S07c**: scene 82 colours people coral; scene 61's short block floats high; sizes unchecked on a phone;
  palette not chosen. Not in S07c: a figure said twice; odd cells refused.
- **D12**: thumbnail A puts Kalanick by "$7.9 BILLION" (deficit to end 2018, F13); he left in June 2017 (F11). Untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block;
  `name-first` noisy; two tokenisers (2,103 vs 2,087 words); numbers match by value.
- Uber eval: beat 3 is the 2016 Saudi investment; no named taxi owner; F05 (an estimate) in 3 of 25 charts.
- Step 1 uses Zehon's `youtube.py` (French output). Fixture `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script. Critique log: 29 lines, none graded.
