# S13 — reconcile report (2026-11-16)

Session `session_01Cw13LeFBwzXQBL4SqwTyRi`. Work branch `claude/s13-reconcile`, from `claude/v1-s2b-script-uber`
(`main` + the 15-16/11 STATE). Repo only: no Drive, no video file, no watch run.

## What was merged

1. **`claude/affectionate-heisenberg-k7i85k`** (08/11: S11, S12, video 1 sessions 2b and 3, D16-D24, its own S10).
2. **`origin/main`**, not foreseen by the S13 prompt: pull request 8 (S07c, D17 "English with Franco", French market report)
   was merged into `main` on 15/11 at 20:57, after the work branch was made. Without it the pull request would conflict.

## Conflicts and the choice per file

| File | Choice |
|---|---|
| `tools/guard/guard.py` | **`main`'s S10 kept** (exit 2 + stderr, `pre`/`post` args, state in `.git/`). Ported hunks below. |
| `tests/test_guard.py` | `main`'s 12 tests kept; 5 added for the ported hunks (the 08/11 file tested another API). |
| `.claude/settings.json` | `main`'s (hooks call `guard.py pre` / `post`, 10 s). |
| `whosedime/watch/watch.py` | **`main`'s S10 kept** (`AlreadyReported`, Checks line format). Ported hunks below. |
| `tests/test_watch.py` | auto-merged into both test sets; the 08/11 checks tests (other format) rewritten as 3 tests in `main`'s format. |
| `guard_log.jsonl`, `critique_log.jsonl` | every line of all sides, sorted by date, exact duplicates dropped: guard 33 lines, critique 55. |
| `CLAUDE.md` | 16/11 guard line; 08/11 "open the next session" line; D24 pause banner **removed** (D25 lifted it). |
| `ROADMAP.md` | `main`'s rule 10 + the 08/11 "a wrong block: fix the guard and its test"; 08/11 hand-off (D17-D19) kept. |
| `DECISIONS.md` | D25, then D24-D16 of 08/11, then `main`'s sections (D15, D14, D17 language, S07c D14-D16), all as written. |
| `STATE.md` | rebuilt from the 16/11 STATE + 08/11 facts + S07c; 60 lines. |
| Skills | `python3 tools/sync_skills.py`, `--check`: no drift. |

**Language rule**: `main`'s D17 says English; Franco wrote French on 15-16/11. `CLAUDE.md` and ROADMAP rule 1 now say
"the language he writes in", citing both; to confirm (STATE open issue).

## Hunks ported from the 08/11 branch

Guard (`guard.py`):
- heredoc bodies are data, not commands (a Python heredoc naming `watch.py` or `git push` was blocked);
- operators split outside quotes (a quoted `&& git push origin main` was read as a push);
- redirections dropped: `2>&1`, `> f`, `2> f` are not push targets (**the false block of 15/11**);
- `git push --tags` and `refs/tags/...` are not branch pushes;
- `cat /proc/*/environ` blocked as a secret print; `env | wc`, `env | grep -c`, `env | cut -d= -f1`, `sed 's/=.*//'` allowed;
- `watch-rerun` only when a segment *runs* `watch.py` (an assignment or a patch script naming it was blocked).

Watch (`watch.py`):
- `check_handles`: one `channels.list` call per 50 known channels **on every run** (1 unit): moved handle updated, gone channel named;
- `median_n` + `scan_long_counts`: a "full catalogue" median takes its count from `chaines_C.csv`, so it can be flagged;
- `day_units` in `last_run.json`: units summed over every run of a day, not just the last two.

Not ported (08/11 features, not fixes): French check of files made by shell commands; critique match by file name;
the 08/11 JSON hook output. `main`'s choices stand.

## Tests (`python3 -m unittest discover -s tests`, measured)

| Tree | Result |
|---|---|
| `main` / work branch before the merge | 190 pass |
| 08/11 branch alone | 221 pass |
| after merging the 08/11 branch | 233 pass |
| after merging `main` as well (final) | **233 pass** (190 + 35 new from 08/11: generate 23, voice reference 12; + 5 guard, + 3 watch) |

**Measured**: tests above, skill drift. **Assumed**: hooks run the merged guard in the next session (not checked live
beyond this session's own calls); the watch's extra unit per run is fine within the 300-unit budget (not run).
