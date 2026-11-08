# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-08**, end of S10 Live guard (session `session_01Cw13Lf765HZ3bZ6usZHfwA`).

## Where we are

- **S01 to S07b in `main`** (merged 08/11). S08 to S10 are on the work branch, not in `main` (no Colab code changed).
- **S10 done: live guard (D15).** `tools/guard/guard.py` runs on every tool call (hooks in `.claude/settings.json`). **Blocks**: edits of
  `.claude/skills/` or `*.skill`; `git push` to `main` or another branch; printing the API keys; a second watch run on a reported date;
  `git commit` after a failed test run, or after a code edit with no full `unittest discover` since. **Warns**: STATE.md over 60 lines,
  a watch report over 100, French in a new file under `whosedime/` or `docs/whosedime/`, a deliverable committed with no critique line
  from the session. Log: [`guard_log.jsonl`](guard_log.jsonl). `python3 tools/guard/guard.py rules` prints the table.
  **Measured**: the 3 live faulty calls stopped or warned, reason read by the agent; under 0.5 s a call; French detector 0 false
  alerts on 74 English files, 35 of 47 French files caught. It caught this STATE.md at 64 lines; 2 false blocks on good commands, fixed.
- **The watch checks its own run**: a "Checks" line at the top of the report (date already reported, refused without `--force`; a median
  on fewer than 5 videos; a handle that moved, 1 unit a run; no upload for 60 days; units of the day over budget). Not run live (no
  second run this week): it would flag the medians of How They Make Billions (2) and The Quiet Monopoly (4). S09 report: [`watch/2026-11-08.md`](watch/2026-11-08.md).
- **Video 1, "Uber Was Cheap. Who Paid?"**: steps 1-2 done (S08), **waiting for Franco's signature** of `02b_factcheck.md`
  (Pause 2; 43 facts, 42 verified, 1 `[TO VERIFY]`, fingerprint `sha256:18adbeeab4a0`). Drive tree `WhoseDime/` made in S08.

## Branches

| Branch | Role |
|---|---|
| `claude/whosedime-s10-live-guard-q6n73k` | **work branch**: S08 docs, S09 (watch), S10 (guard), on top of `main` (replaces `claude/affectionate-heisenberg-k7i85k`) |
| `main` | production (Colab launchers); has S01 to S07b |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER` (`scenes`, `voice SCRIPT VOICE`, `fingerprint FILE`). Skill sync:
  `python3 tools/sync_skills.py` (`--check`). Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`: about 60 units; `--force`: second run of a date; `--refresh-medians`:
  about 95, no report). Commit the report, `channels.csv` and `last_run.json` after each run.
- Tests: `python3 -m unittest discover -s tests` — **189 pass**, measured 08/11 (about 36 s). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S07b; S08, S09, S10 | **done**; S01-S07b merged 08/11 |
| S07c Chart follow-ups | prompt on branch `claude/funny-dijkstra-js9xbz` (its STATE is older); before video 1's assembly |
| Video 1, skill session 2 | **next**: Script (Opus 5.5), once Franco has signed the fact check; the guard runs during it |
| Incoherence skill (meaning half) | waits for about 30 graded lines (39 lines, 1 with a Franco comment, none graded) |

## Open issues

- **For Franco, video 1**: sign `02b_factcheck.md`; F33 (Mamdani, 2021 hunger strike): use it or not (Claude: leave it out).
  Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH.
- **Guard, assumed**: hooks load from the committed settings in cloud sessions (measured here: live within seconds of the write). Not
  seen: code edited by a shell command other than `>`, `tee`, `sed -i`, `cp`, `mv`; French in a file made by the shell; a partial test
  run never clears a code edit. The state of the commit rule lives in the temp folder: it starts empty in each container.
- **Watch, assumed**: hits from 10 K views, over 28 days; medians frozen at 5 Nov (`--refresh-medians` quarterly, never run);
  entrants from 2 fixed queries, 4-20 min; brands on titles only. No schedule. Company Man moved to `@companyman114` (S09).
- **For Franco, S05 choices** (assumed): `title` card ("WHO PAYS?", navy); `palette.json`. **D12** thumbnail A untested.
- **To check on video 1**: qwen-tts calls (never run); 25 dB threshold; T4 and Colab run times; narrator (D7). **Charts → S07c**:
  scene 82 colours people coral; scene 61's block floats high; phone sizes unchecked.
- **Checker limits**: `chart-source` checks numbers, not words; `prompt-person` sees only the people block; `name-first` noisy.
- **Out of scope**: brief's "externalities" planned nowhere; `factcheck_clean.md` from memory; ROADMAP rule 2 stale; no setup script.
