# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of video 1 skill session 2a, outline (session `session_01Cw13LhWRZyGn7FWUAAzMb1`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). S08 and S09 are on the work branch, not in `main` (no Colab code changed).
- **S09 done.** Franco: "the tool is good", and asked for a guard during the work (D15 → S10). Weekly watch:
  `python3 whosedime/watch/watch.py`; first report (259 units, nothing on Uber): [`watch/2026-11-08.md`](watch/2026-11-08.md).
- **Video 1, "Uber Was Cheap. Who Paid?"**: fact check **signed** (`sha256:18adbeeab4a0` = fingerprint); outline
  `02a_outline.md` **validated** by Franco 08/11 (Pause 3; 2,060 words planned; payers: investors, drivers, NY medallion owners).
  **Measured**: Drive's editor had re-escaped the signed file (hash `adbb19fb1ab6`, F43 unparsable); the exact S08 upload,
  equal once unescaped, hashes `18adbeeab4a0`: restored with Franco's signature line unchanged (old copy in the Drive bin).

## Branches

| Branch | Role |
|---|---|
| `claude/affectionate-heisenberg-k7i85k` | **work branch**: S08 docs, S09 (watch), S10 prompt, video 1 session prompts, on top of `main` |
| `main` | production (Colab launchers); has S01 to S07b |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`). Skill sync:
  `python3 tools/sync_skills.py` (`--check`). Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`: about 60 units; `--refresh-medians`: about 95, no report). Commit the
  report, `channels.csv` and `last_run.json` after each run: the next run diffs titles against `last_run.json`.
- Tests: `python3 -m unittest discover -s tests` — **167 pass**, measured 08/11 (about 37 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07b | **done**, merged 08/11 |
| S07c Chart follow-ups | prompt on branch `claude/funny-dijkstra-js9xbz` (its STATE is older); before video 1's assembly |
| S08 Drive and pilot | **done** 08/11 |
| S09 Competitor watch | **done** 08/11; first weekly report written |
| S10 Live guard | **next build** (D15) — prompt ready: [`sessions/S10_live_guard.md`](sessions/S10_live_guard.md) (Opus 5.5) |
| Video 1, skill session 2a | **done** 08/11: signature checked, outline validated (Pause 3) |
| Video 1, skill session 2b | **next** for video 1: script, voice, 20 s sample (Opus 5.5), [`sessions/V1_S2b_script.md`](sessions/V1_S2b_script.md); S10 session advised "best after S10" |
| Video 1, skill session 3 | after 2b: scenes and publication (Sonnet 5.5); the skill resumes from the files, no prompt |
| Incoherence skill (meaning half) | waits for about 30 graded lines (36 lines, 1 with a Franco comment, none graded) |

## Open issues

- **For Franco, video 1**: F33 (Mamdani) left out of the outline (Claude's advice; Franco did not object). Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH.
- **Watch**: 48 channels (D14 added How They Make Billions; Company Man now `@companyman114`). Assumed: hits from 10 K views
  over 28 days; medians frozen at 5 Nov (`--refresh-medians` never run); 2 fixed entrant queries; no schedule.
- **For Franco, S05 choices** (assumed): the `title` card ("WHO PAYS?", navy); the palette in `palette.json`.
- **Drive editor** re-escapes a `.md` it saves (breaks the hash): never edit video files there; no checker warning built.
- **Research tools**: WebFetch's summariser never returns a page word for word; web.archive.org refused; uber.com answers 406.
- **Voice, to check on video 1**: qwen-tts calls (never run); 25 dB threshold; stitched pauses; T4 run time; narrator design (D7).
- **Assembly, to check on video 1**: Colab render time; clips x1.35 then frozen; band size; years said in pairs. No music, no `.srt`.
- **Charts → S07c**: scene 82 colours people coral; scene 61's block floats high; phone sizes unchecked. **D12** thumbnail A untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block; `name-first` noisy.
- **Out of scope**: the old brief's "externalities" (news calendar, competitors' weaknesses) are planned nowhere. Fixture
  `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script.
