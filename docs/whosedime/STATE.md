# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of S09 Competitor watch (session `session_01Cw13LgvyfSBBRJdw5oChae`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). S08 and S09 are on the work branch, not in `main` (no Colab code changed).
- **S09 done.** Franco: "the tool is good", and asked for a guard during the work (D15 → S10). `python3 whosedime/watch/watch.py` once a week writes
  `docs/whosedime/watch/<date>.md` (new long videos, hits, title changes, new entrants, brands of `marques.md`).
  **Measured**, first run 08/11: **259 units** (budget 300); 90 new long videos on 31 of 47 channels; 11 channels with a
  hit at 10 K views or more; 1 entrant proposed; 11 brands named; nothing on Uber. Report: [`watch/2026-11-08.md`](watch/2026-11-08.md).
- **Video 1, "Uber Was Cheap. Who Paid?"**: steps 1-2 done (S08), **waiting for Franco's signature** of `02b_factcheck.md`
  (Pause 2; 43 facts, 42 verified, 1 `[TO VERIFY]`, fingerprint `sha256:18adbeeab4a0`). Drive tree `WhoseDime/` made in S08.

## Branches

| Branch | Role |
|---|---|
| `claude/affectionate-heisenberg-k7i85k` | **work branch**: S08 docs, S09 (watch), S10 prompt, on top of `main` |
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
| Video 1, skill session 2 | Script (Opus 5.5), once Franco has signed the fact check; best after S10 |
| Incoherence skill (meaning half) | waits for about 30 graded lines (35 lines, 1 with a Franco comment, none graded) |

## Open issues

- **For Franco, video 1**: sign `02b_factcheck.md`; F33 (Mamdani, 2021 hunger strike): use it or not (Claude: leave it out).
  Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH.
- **Watch list: 48 channels**: How They Make Billions added 08/11 (D14; its median rests on 2 videos). `@companyman` is now
  another channel: the tool moved Company Man to `@companyman114` (same channel id).
- **Watch, assumed**: hits from 10 K views, over 28 days; medians frozen at 5 Nov (Claude: `--refresh-medians` quarterly, never
  run); entrants from 2 fixed queries, 4-20 min; brands on titles only. No schedule: someone starts the run each week.
- **For Franco, S05 choices** (assumed): the `title` card ("WHO PAYS?", navy); the palette in `palette.json`.
- **Research tools**: WebFetch's summariser never returns a page word for word; web.archive.org refused; uber.com answers 406.
- **Voice, to check on video 1**: qwen-tts calls (never run); 25 dB threshold; stitched pauses; T4 run time; narrator design (D7).
- **Assembly, to check on video 1**: Colab render time; clips x1.35 then frozen; band size; years said in pairs. No music, no `.srt`.
- **Charts → S07c**: scene 82 colours people coral; scene 61's block floats high; phone sizes unchecked. **D12** thumbnail A untested.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block; `name-first` noisy.
- **Out of scope**: the old brief's "externalities" (news calendar, competitors' weaknesses) are planned nowhere. Fixture
  `factcheck_clean.md`: facts from memory. Stale: ROADMAP rule 2 branch. No setup script.
