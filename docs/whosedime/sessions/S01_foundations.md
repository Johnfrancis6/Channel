# S01 — Foundations

> Changes from ROADMAP.md: none (first session).

## Context

Franco froze Zehon and approved the audit corrections for Whose Dime only,
to be built in English, one session at a time (see `DECISIONS.md`, D1-D11).
This session builds the clean base every later session stands on. No
Whose Dime content yet.

## Setup

```bash
git fetch origin claude/admiring-ramanujan-k2uiqe claude/optimistic-bohr-5f78k4 main
git checkout claude/admiring-ramanujan-k2uiqe
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
```

Stay on `claude/admiring-ramanujan-k2uiqe`, even if the session was opened
on another branch. `git fetch` before every push.

## Read (in this order, nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `docs/whosedime/DECISIONS.md`, `docs/whosedime/ROADMAP.md`
2. `docs/whosedime/CRITIQUE_PROTOCOL.md`
3. After the merge (task 1): `zehon/synchroniser_skills.py`, `tests/test_zehon.py`,
   the first 60 lines of `docs/chaine2/CONTEXTE.md`, `CLAUDE.md`
4. For context only, if needed: `reports/Audit pipeline de production.md`
   § 2.2 (P1, P5, P6, P8) and § 3 (C3, C8)

## Do

1. **Merge the latest pipeline.** `git merge --no-ff origin/claude/optimistic-bohr-5f78k4`.
   A dry run on 07/11 merged cleanly (only `CLAUDE.md` auto-merged).
   *Check:* `git diff origin/claude/optimistic-bohr-5f78k4 -- zehon tests .claude`
   prints nothing; the audit files (`reports/`, `research_notes/`,
   `docs/audit/`, `docs/finance/`, `docs/whosedime/`) are still there.

2. **Tests in a fresh container.** Run `python3 -m unittest discover -s tests`.
   *Check:* all tests pass (26 on the merged base, measured on 07/11 after
   installing OpenCV). Then make it repeatable without anyone remembering
   the commands: call `get_environment`, and propose a setup script that
   installs FFmpeg (`apt-get update` first) and
   `opencv-python-headless pillow numpy`, following the environment tools'
   own rules (Franco approves it in a prompt). If he declines, write the
   commands in `CLAUDE.md` and move on.

3. **Freeze Zehon (one note, nothing else).** At the top of
   `docs/chaine2/CONTEXTE.md`, replace the "État" and "Suite" blocks with
   a short French block (the file must stay under 60 lines):
   - « Chaîne gelée le 07/11/2026 (décision D1) : tout l'effort va à Whose
     Dime. Reprendre ici seulement si Franco relance Zehon. »
   - the real state of the three videos: `01_sel` rendered and validated
     30/09, not published; `02_verre` rendered 01/10 from
     `claude/zelan-studio-analysis-rws9f6@15b0fe0`, re-render needed with
     the dark band; `03_aluminium` content finished 01/10 (research to
     publication), no pieces yet;
   - the parked decisions Z1 to Z3 of `docs/whosedime/DECISIONS.md`.
   Add one line at the top of `docs/audit/PROMPT_SESSION_1_AUDIT_PIPELINE.md`
   ("Done on 07/11: see reports/Audit pipeline de production.md") and of
   `docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md` ("Superseded by
   docs/whosedime/ROADMAP.md, sessions S02 and S09").
   *Check:* no other Zehon file changed (`git diff --stat` after this task
   touches only these three files).

4. **One sync tool for both channels, with a version stamp (C8).** Create
   `tools/sync_skills.py` (English code, docstring and messages). It does
   what `zehon/synchroniser_skills.py` does today, for every folder that
   holds a `SKILL.md` under `zehon/` **and** `whosedime/`:
   - mirror to `.claude/skills/<skill>/`, archive to `<channel>/<skill>.skill`
     (without `evals/`, fixed date, reproducible bytes);
   - write a generated `VERSION` file (first 12 hex characters of a SHA-256
     over the sorted source paths and bytes) into the mirror and the archive;
   - `--check` reports drift and exits 1, without writing.
   Keep `zehon/synchroniser_skills.py` as a thin wrapper that calls the new
   tool (its `--verifier` flag maps to `--check`), so `tests/test_zehon.py`
   and the Zehon docs stay valid.
   Add `tests/test_sync_skills.py`: same source gives the same `VERSION`
   and the same archive bytes; one changed byte changes `VERSION`; `evals/`
   is not in the archive; `--check` returns 1 after a hand edit in the
   mirror.
   *Check:* all tests pass; `python3 tools/sync_skills.py --check` prints no
   drift. The regenerated Zehon mirror only gains a `VERSION` file.

5. **Whose Dime skeleton.** Create `whosedime/README.md` (English, 30 lines
   at most): the planned layout (`whosedime-maker/`, `common/`,
   `notebooks/`, `video-maker/`, `research/`, `watch/`), one line each,
   with the session that fills it (from `ROADMAP.md`). No other file in
   `whosedime/` yet.

6. **`CLAUDE.md` in English (40 lines at most).** The project is Whose
   Dime; to resume, read `docs/whosedime/STATE.md`; the rules of
   `ROADMAP.md` § "Rules for every session" in short; the sync tool and the
   test command; one line saying Zehon is frozen (pointer to
   `docs/chaine2/CONTEXTE.md`, in French) and the archive branch of the old
   Shorts channel. Keep the critique-protocol rule, pointing to
   `docs/whosedime/CRITIQUE_PROTOCOL.md`.

7. **Pull request to `main` (C3, D5).** Commit, `git fetch`, push, then
   open a pull request from `claude/admiring-ramanujan-k2uiqe` to `main`
   with the GitHub tools (check the repo for a PR template first). Title
   and body in English: what the merge brings, the freeze, the sync tool,
   the test result. **Do not merge it**: Franco merges. Give him the link.

## Do not

- Change any Zehon content, skill source or notebook (except task 3's
  three files and the wrapper of task 4), or anything in Drive.
- Touch the Zehon Colab launchers or their `BRANCHE` (Zehon is frozen).
- Write any Whose Dime skill content (that is S04 and S05).
- Edit `.claude/skills/` or `*.skill` by hand.

## Deliverables

- Merged work branch, PR link
- `tools/sync_skills.py`, `tests/test_sync_skills.py`, wrapper in `zehon/synchroniser_skills.py`
- `whosedime/README.md`, `CLAUDE.md` (English)
- Freeze note in `docs/chaine2/CONTEXTE.md`, banners on the two old prompts
- `docs/whosedime/STATE.md` updated, one line in `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S02_storytelling_rules.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Write the S02 prompt from the S02 row
of the roadmap and from part 1 of
`docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md` ("Qualité du contenu, pour
le narrateur de « Who Pays? »"): translate its asks into English, keep its
inputs (Crayon Capital report, `PLAN_ACTION.md`, `marques.md`, Supadata and
YouTube API rules), drop its weekly-watch part (that is S09). The S02
prompt must name its output files and give each rule a measurable
threshold that S03's checker can test. Next session: **S02, model Opus 5.5**.
