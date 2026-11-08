# S09 — Weekly competitor watch

> Changes from ROADMAP.md: the report goes to `docs/whosedime/watch/`
> (not `docs/veille/`, the old French brief's path: D2, everything in
> English). The "externalities" part of the old brief (news calendar,
> competitors' weaknesses) is **not** in scope: one line in "Open issues".

## Context

Video 1 (Uber) waits for Franco's signature of its fact check (S08). This
session builds the weekly watch of the niche's channels, from the old
session-2 brief (`docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md`, task 2,
in French). It depends only on S01 and touches no production code.

## Setup

```bash
git fetch origin main && git checkout main && git pull origin main
git log --oneline -3          # S08's pull request merged? If not: git fetch origin claude/great-planck-7hqn59 and start from it
git checkout -B <the branch this session is given>
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (155 tests) before you start
```

`YOUTUBE_API_KEY` must be set (`[ -n "$YOUTUBE_API_KEY" ] && echo set`);
never print it. Without it, stop and tell Franco, one line.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `ROADMAP.md` (rules, S09 row), `CRITIQUE_PROTOCOL.md`
2. `docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md`, task 2 only (French)
3. `research_notes/Balayage niche C/balayage.md` (the method, its costs and biases) and
   `outils/yt.py` (API helpers with a unit counter and a local cache: reuse its logic)
4. `research_notes/Balayage niche C/chaines_C.csv` (47 channels: the watch list) and
   `docs/finance/marques.md` (the brand table, its "gap" column)

## Do

1. **The tool**: `whosedime/watch/watch.py` (English, standard library only),
   `whosedime/watch/channels.csv` (handle, uploads playlist id, median views of
   long videos, from `chaines_C.csv`; refreshed by the tool) and a state file
   `whosedime/watch/last_run.json` (titles and views seen, for the next diff).
   One run reports, for the 7 days before the run date:
   - **new long videos** (over 3 min) per channel: title, date, views, views ÷ channel median;
   - **hits**: a video at 5× its channel's median or more (measured on the run date: say so);
   - **title changes** on videos seen at the previous run;
   - **new entrants**: at most 2 `search.list` calls (100 units each), published
     in the last 7 days, English, long, sorted by views; a channel not in the list
     with a video at 100 K views or more is proposed, never added without Franco;
   - **brands covered**: titles that name a brand of `marques.md`, so its "gap"
     column can be reread (the tool proposes; it does not edit `marques.md`).
   **Budget**: under 300 units a run, counted by the tool (`playlistItems` and
   `videos` cost 1, `search` 100) and written in the report. *Check:* a test
   with a fake API (no network) feeds a channel with a hit, a renamed title and
   a Short, and the report lists the hit, the rename, and not the Short.
2. **The first run**: `python3 whosedime/watch/watch.py`, report in
   `docs/whosedime/watch/<YYYY-MM-DD>.md` (one page: measured numbers with the
   run date; what is inferred, marked as such). *Check:* units spent under 300,
   read from the tool's counter; the first run has no previous titles, so the
   rename section says "first run".
3. **For Franco**, one question, only if the report shows it: a hit or a new
   entrant on **Uber** (video 1) changes the angle or the title? Recommend.

## Do not

- Touch the content skill, the checker, the voice or the assembly, or video 1's Drive folder.
- Add a channel to the list, or edit `marques.md`, without Franco's yes.
- Use Reddit or Social Blade (blocked from the cloud: no workaround).

## Deliverables

- `whosedime/watch/` (tool, channel list, state), `tests/test_watch.py`
- `docs/whosedime/watch/<date>.md`, the first weekly report
- `docs/whosedime/STATE.md` updated, one line per deliverable in `docs/whosedime/critique_log.jsonl`
- the next prompt, if Franco names one (else STATE.md says what waits on him)

## Hand-off

Follow `ROADMAP.md` § "The hand-off". S09 is the last build session of the
roadmap: after it, video 1 continues with the skill's session 2 (Script,
Opus 5.5) once Franco has signed its fact check; the incoherence-detection
skill waits for about 30 graded lines in the critique log.
