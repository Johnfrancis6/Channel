# Whose Dime — state

Short by rule (60 lines at most). Updated at the end of every session.
Plan: [`ROADMAP.md`](ROADMAP.md). Decisions: [`DECISIONS.md`](DECISIONS.md).

**Last update: 2026-11-07**, after the pipeline audit (session
`session_01Cw13LfHTQxQekv3rqzspUm`).

## Where we are

- The production pipeline was audited:
  [`reports/Audit pipeline de production.md`](../../reports/Audit%20pipeline%20de%20production.md)
  (French). Franco approved the corrections for Whose Dime only and froze
  Zehon (D1, D3).
- **Nothing of the Whose Dime pipeline is built yet.** The latest Zehon
  pipeline, which Whose Dime will start from, is still on
  `claude/optimistic-bohr-5f78k4`; it is not yet on `main` nor on the work
  branch.
- No Whose Dime Drive folder exists yet.

## Branches

| Branch | Role |
|---|---|
| `claude/admiring-ramanujan-k2uiqe` | **work branch** for build sessions |
| `main` | production (Colab launchers); still the 30/09 state (`f5ceed8`) |
| `claude/optimistic-bohr-5f78k4` | latest Zehon pipeline; to be merged in S01 (dry run on 07/11: no conflict) |
| `claude/zelan-studio-analysis-rws9f6` | old branch used by the Zehon Drive launchers; leave it (Zehon frozen) |

## Tools

- Skill sync: `python3 zehon/synchroniser_skills.py` (until S01 replaces it
  with `tools/sync_skills.py`).
- Tests: `python3 -m unittest discover -s tests`. A fresh container needs
  `pip install opencv-python-headless pillow numpy` and FFmpeg
  (`apt-get update && apt-get install -y ffmpeg`) for the video tests.

## Sessions

| # | Status |
|---|---|
| S01 Foundations | **next** — prompt ready: [`sessions/S01_foundations.md`](sessions/S01_foundations.md) |
| S02 to S09 | planned in `ROADMAP.md` |

## Open issues

- The critique log has no graded line yet (Franco's grades start with the
  Whose Dime deliverables).
- The old session-2 brief (`docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md`,
  French) is replaced by S02 (storytelling rules) and S09 (weekly watch).
