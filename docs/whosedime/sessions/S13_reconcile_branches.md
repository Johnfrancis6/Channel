# S13 — Reconcile the two branches into one (repo only)

> Written 2026-11-16 by session `session_01Cw13Lexea2GUn6fJXKqEuH`. Model: Opus 5.5. No Drive, no video content.

## Why

`main` has S01-S10 (S10 live guard merged by PR #11 on 15/11). The work of 08/11 lives only on
`claude/affectionate-heisenberg-k7i85k`: S11 generation pipeline (parked, D20), S12 ElevenLabs reference
voice (`MODE = "reference"`, D21-D23), video 1 sessions 2b and 3 (state and critique lines), D20-D24, and
**its own S10 version**. Measured 15/11: `git merge origin/main` on that branch conflicts in
`tools/guard/guard.py`, `tests/test_guard.py`, `whosedime/watch/watch.py`, `.claude/settings.json`,
`docs/whosedime/guard_log.jsonl`, `CLAUDE.md`, `ROADMAP.md`, `STATE.md`, `critique_log.jsonl`.
The voice session (S12's notebook needs `main`) and the assembly wait for this.

## Setup

```bash
git fetch origin main claude/affectionate-heisenberg-k7i85k claude/v1-s2b-script-uber
git checkout -b claude/s13-reconcile origin/claude/v1-s2b-script-uber   # main + the 15-16/11 STATE
apt-get update && apt-get install -y ffmpeg && pip install opencv-python-headless pillow numpy
python3 -m unittest discover -s tests        # 190 pass on main, 15/11
```

## Do

1. `git merge origin/claude/affectionate-heisenberg-k7i85k`. Resolve each conflict:
   - **Guard and watch code** (`guard.py`, `test_guard.py`, `watch.py`, `settings.json`): keep `main`'s S10 (the
     reviewed, merged one) and port only what the 08/11 branch adds that `main` lacks; list each ported hunk in the report.
   - **Logs** (`guard_log.jsonl`, `critique_log.jsonl`): keep every line of both, sorted by date, no duplicates.
   - **Docs** (`STATE.md`, `ROADMAP.md`, `CLAUDE.md`, `DECISIONS.md`): one version holding both; DECISIONS keeps
     D20-D25 newest first; STATE.md ≤ 60 lines, built from `claude/v1-s2b-script-uber`'s STATE plus the 08/11 facts.
   - Never edit `.claude/skills/` or `*.skill` by hand: `python3 tools/sync_skills.py`, then `--check`.
2. Tests green (expect about 221 + the S10 tests of `main`; say the measured count).
3. Report in `docs/whosedime/reconcile_report.md` (one page): conflicts, choice per file, tests before and after.
4. Commit, push the work branch, then **open a pull request to `main`** (Franco merges it). Give its link.
5. Critique line (`"step": "S13_reconcile"`), STATE.md, then stop.

## Watch out

- Do not touch Drive or video files. Do not rerun the watch.
- The guard blocks a push with `2>&1` after the branch name (false block, 15/11): push without redirection.
- Out of scope goes to STATE.md "Open issues".
