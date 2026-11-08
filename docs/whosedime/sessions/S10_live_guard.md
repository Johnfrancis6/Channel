# S10 — Live guard

> Changes from ROADMAP.md: a new session, asked by Franco after S09 (D15):
> incoherent actions must be flagged **while the agent works**, and the
> agent corrected in time, not at the end-of-task self-critique. This is
> the rule-based half of the incoherence-detection plan (audit report § 5,
> "un script déterministe"): it needs no graded log lines. The half that
> judges meaning (script against outline, title promise kept) still waits
> for about 30 graded lines.

## Context

The critique protocol only looks back, after a deliverable. In S09 the
agent ran the watch twice (520 units in a day against a 300-unit run), wrote a
184-line report where "one page" was asked, and wrote a 62-line STATE.md
(limit 60): all caught late, by the agent itself. Claude Code hooks run
on every tool call and can block one with a reason the agent reads at once.

## Setup

```bash
git fetch origin claude/affectionate-heisenberg-k7i85k && git checkout claude/affectionate-heisenberg-k7i85k
git checkout -B <the branch this session is given>
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (167 tests) before you start
```

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `ROADMAP.md` (rules, hand-off), `CRITIQUE_PROTOCOL.md`, `DECISIONS.md` (D14, D15)
2. `reports/Audit pipeline de production.md`, § 5 only (French): the controller's plan
3. `docs/whosedime/critique_log.jsonl`: every `process` and `inconsistency` defect is a candidate rule
4. The Claude Code hooks documentation (ask the `claude-code-guide` agent: PreToolUse,
   PostToolUse, Stop; input on stdin; how a block's reason reaches the agent; project
   `.claude/settings.json` in cloud sessions). Say what is measured and what is read.
5. `whosedime/watch/watch.py` (task 3)

## Do

1. **The guard**: `tools/guard/guard.py` (standard library only, English) and the
   hooks in `.claude/settings.json` (committed; `.claude/skills/` stays untouched).
   - **Before an action (block, with the rule and the fix in one line)**: editing
     `.claude/skills/` or `*.skill`; `git push` to `main` or to a branch other than the
     current one; a command that prints `YOUTUBE_API_KEY` or `SUPADATA_API_KEY`
     (`echo $…`, `env`, `printenv`); a second watch run on a date that already has a
     report, without `--force`; `git commit` when the last test run in the session failed
     or none ran after the last code edit (decide how to know this cheaply; say it).
   - **Right after an action (warn: the agent reads it and fixes before going on)**:
     `docs/whosedime/STATE.md` over 60 lines; a watch report over 100 lines; a new
     file under `whosedime/` or `docs/whosedime/` with French text (accents test
     plus a short word list; false alerts counted); a deliverable written with no
     critique-log line yet (reminder, not a block).
   - Every block and warning is appended to `docs/whosedime/guard_log.jsonl`
     (date, session, rule, tool call summary, block or warn) — data for the future skill.
   - Rules live in one table at the top of `guard.py`; the hooks stay a few lines.
   - A rule enters only if it would have caught a real case (the log, or the
     S09 cases above). *Check:* `tests/test_guard.py` feeds each rule a faulty call
     (hook JSON on stdin) and a clean one: each faulty call is blocked or warned with
     its rule; clean calls pass silently; the guard answers in under 0.5 s a call.
2. **Live check**: in this session, after the hooks are on, make 3 deliberately
   faulty calls (edit a `.claude/skills/` file, push to `main` with `--dry-run`, add blank
   lines to STATE.md past 60, then revert them) and
   show the agent being stopped or warned, quoting the reason it received.
   *Check:* the 3 lines in `guard_log.jsonl`.
3. **The watch flags its own incoherences**, in a "Checks" line at the top of its
   report: run date already reported (refused without `--force`); a channel's median
   resting on fewer than 5 videos (How They Make Billions: 2); a handle that moved;
   a channel with no upload for 60 days; units over budget. *Check:* tests with the fake API.

## Do not

- Touch the content skill, the checker, the voice or the assembly, video 1's Drive folder, `marques.md`.
- Block anything the rules in `CLAUDE.md` and `ROADMAP.md` do not forbid: a guard that
  blocks good work is worse than none. When unsure, warn, do not block.
- Make the guard call the network or a model.

## Deliverables

- `tools/guard/guard.py`, `.claude/settings.json`, `tests/test_guard.py`, `docs/whosedime/guard_log.jsonl`
- `whosedime/watch/watch.py` checks and their tests
- `CLAUDE.md` and `ROADMAP.md`: one line each on the guard (what it blocks, where its log is)
- `docs/whosedime/STATE.md` updated, one line per deliverable in `critique_log.jsonl`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next: video 1, skill session 2 (Script,
Opus 5.5), once Franco has signed its fact check; the guard then runs during it.
Model for S10: **Opus 5.5** (hooks run in every later session: a wrong block costs every session).
