# Whose Dime — state

Short by rule (60 lines at most), updated at the end of every session. Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-16**, resync and Pause 5 (session `session_01Cw13Lexea2GUn6fJXKqEuH`). **D25: pause lifted.**

## Where we are

- **Two lines of work, not yet joined** (measured 15/11 with `git merge`):
  - `main` = S01-S09, video 1 session 2a, and **S10 live guard** (PR #11, merged 15/11).
  - `claude/affectionate-heisenberg-k7i85k` (last commit 08/11) = **S11** generation pipeline (parked, D20), **S12**
    ElevenLabs reference voice (D21-D23), **video 1 sessions 2b and 3**, **D20-D24**, and its own S10 version.
    A merge into `main` conflicts in `tools/guard/guard.py`, `whosedime/watch/watch.py`, `tests/test_guard.py`,
    `STATE.md`, `ROADMAP.md`, `CLAUDE.md`, logs. Its STATE.md is the fuller record of 08/11.
- **Video 1, "Uber Was Cheap. Who Paid?"** (Drive `WhoseDime/Videos/01_uber/`, its `00_state.md` rewritten 15/11):
  - Steps 1-5 written (fact check signed `sha256:18adbeeab4a0`; script 2,089 words; 94 scenes; publication).
  - **Measured 15/11**: `checker.py all` exit 0 on the raw Drive files; fingerprint = Signed line.
  - **Pause 5 answered 16/11**: title "Uber Lost $7.9 Billion. Uber's history" (F26; Franco's, Claude had recommended
    "Uber Was Cheap. Who Paid?"), thumbnails A, B, C made by Franco, checked, A first. Content done.
  - Pieces: `miniatures/` 3 of 3 (+ 1280x720 copies), `images/` 0 of 55, `clips/` 0 of 5. Then voice (D23), S07c, assembly.

## Branches

| Branch | Role |
|---|---|
| `claude/v1-s2b-script-uber` | **work branch** (this resync), from `main` |
| `claude/affectionate-heisenberg-k7i85k` | 08/11 work (S11, S12, video 1 2b and 3, D20-D24); to reconcile with `main` |
| `main` | production (Colab launchers): S01-S10 |
| `claude/zelan-studio-analysis-rws9f6` | old Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Checker: `python3 whosedime/common/checker.py all FOLDER`. Skill sync: `python3 tools/sync_skills.py` (`--check`).
- Charts and assembly: `whosedime/whosedime-video/scripts/charts.py`, `assemble.py`.
- Watch: `python3 whosedime/watch/watch.py` (`--no-search`, `--refresh-medians`, `--force`).
- Tests: `python3 -m unittest discover -s tests` (190 on `main`, 15/11; 221 on the 08/11 branch). Fresh container: see `CLAUDE.md`.

## Sessions

| # | Status |
|---|---|
| S01 to S10, video 1 session 2a | **done**, in `main` |
| S11, S12, video 1 sessions 2b and 3 | **done** 08/11, on `affectionate-heisenberg` only |
| Video 1, Pause 5 | **done** 16/11 |
| S13 Reconcile branches | **next** (Opus 5.5): [`sessions/S13_reconcile_branches.md`](sessions/S13_reconcile_branches.md); before the voice session |
| Video 1 pieces | Franco: 55 images, 5 clips, reference voice |
| S07c Chart follow-ups | prompt [`sessions/S07c_chart_followups.md`](sessions/S07c_chart_followups.md); before video 1's assembly |
| Incoherence skill (meaning half) | waits for about 30 graded lines |

## Open issues

- **Stale session prompt**: [`sessions/V1_S2b_script.md`](sessions/V1_S2b_script.md) was opened on 15/11 though 2b was done on 08/11
  (the S10 STATE.md was written from a base without the 08/11 work). Read the folder before any video prompt.
- **For Franco, video 1**: F33 (Mamdani) left out. Lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB,
  `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. E1-E5 passed on a generic TTS, not the channel voice.
- **Guard**: hooks reach only clones with `.claude/settings.json`. False block 15/11: `git push -u origin BRANCH 2>&1` read `2>&1` as a ref (push-branch); push without redirection.
- **Watch**: medians frozen at 5 Nov; no schedule. **Drive editor** re-escapes `.md` (breaks the hash): never edit video files there.
- **Out of scope**: the old brief's "externalities"; ROADMAP rule 2 names a stale branch; no setup script.
