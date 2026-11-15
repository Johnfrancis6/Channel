# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-15**, S10 live guard (session `session_01Cw13LezDKUUKtx6YCZp6ni`).

## Where we are

- **S01 to S09 in `main`** (PRs merged; the old work branch `claude/funny-dijkstra-js9xbz` is gone).
- **S10 done** (D15), on branch `claude/eloquent-cannon-ljbenz`, not in `main` (no Colab code changed).
  - Guard: [`tools/guard/guard.py`](../../tools/guard/guard.py), hooks in `.claude/settings.json`, log
    [`guard_log.jsonl`](guard_log.jsonl). Blocks: skills edits, push to `main`/another branch, printed keys,
    second watch run a day, commit with code edited and no green test run after. Warns: STATE.md > 60 lines,
    watch report > 100 lines, new French file, commit of a new deliverable with no critique line today.
  - **Measured**: live in this session, 3 deliberate faults stopped or warned (3 lines in the log); each call
    under 0.5 s in tests; French test: 0 false alerts on 61 English files, 14 of 14 Zehon French docs caught.
  - **Read, not measured**: hooks format from memory of the Claude Code docs (the live check confirms Pre and
    Post on Bash and Edit). Test memory: the post hook reads `Ran N tests`/`OK`/`FAILED` from unittest output
    into `.git/whosedime_guard.json`; code edits seen only via Edit/Write, not via shell heredocs.
  - Watch: report opens with a **Checks** line (date already reported → refused without `--force`; units over
    budget for the day; medians on < 5 long videos; moved handles; 60 days silent). Full-catalogue medians
    carry no count, so only How They Make Billions (n = 2) can be flagged today.
- **Video 1, "Uber Was Cheap. Who Paid?"**: fact check **signed** (`sha256:18adbeeab4a0`); outline `02a_outline.md`
  **validated** 08/11 (2,060 words; payers: investors, drivers, NY medallion owners).

## Branches

| Branch | Role |
|---|---|
| `claude/eloquent-cannon-ljbenz` | **work branch** (S10), on top of `main` |
| `main` | production (Colab launchers); has S01 to S09 |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`. Skill sync: `python3 tools/sync_skills.py` (`--check`).
- Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`, `--refresh-medians`, `--force`). Commit the report,
  `channels.csv` and `last_run.json` after each run.
- Tests: `python3 -m unittest discover -s tests` — **190 pass**, measured 15/11. Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S09 | **done**, merged |
| S10 Live guard | **done** 15/11; pull request to `main` when Franco wants the guard there |
| S07c Chart follow-ups | prompt ready ([`sessions/S07c_chart_followups.md`](sessions/S07c_chart_followups.md)); before video 1's assembly |
| Video 1, skill session 2b | **next**: script, voice, 20 s sample (Opus 5.5), [`sessions/V1_S2b_script.md`](sessions/V1_S2b_script.md) |
| Video 1, skill session 3 | after 2b: scenes and publication (Sonnet 5.5) |
| Incoherence skill (meaning half) | waits for about 30 graded lines |

## Open issues

- **For Franco, video 1**: F33 (Mamdani) left out of the outline. Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB,
  `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH.
- **Guard**: hooks reach only clones that have `.claude/settings.json`, so other branches get it once merged to `main`.
  The critique reminder checks a dated line today, not one per file.
- **Watch**: medians frozen at 5 Nov; no schedule. **Drive editor** re-escapes `.md`. **Video 1**: check qwen-tts, T4/Colab times, S07c, D12.
- **Out of scope**: the old brief's "externalities"; ROADMAP rule 2 names a stale branch; no setup script.
