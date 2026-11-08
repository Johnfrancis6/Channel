# S08 — Drive and pilot launch

> Changes from ROADMAP.md: the assembly skill is `whosedime/whosedime-video/`, not
> `video-maker/` (Zehon's skill already has that name; the sync tool refuses two).
> Drive gets two launchers, voice and assembly. S08 starts only once Franco has
> merged the S06+S07 pull request into `main` (the launchers run `main`).
>
> After S07c (2026-11-08): the palette is chosen by Franco (D16), so task 3 no longer
> asks about it; chart text is larger (labels 58 px, small capitals 42 px, checked on
> his phone).

## Context

Every build piece exists: the content skill (`whosedime-maker`), the checker, the
voice notebook (S06), the charts and the assembly (S07, skill `whosedime-video`).
Nothing is in Drive yet. This session makes the `WhoseDime/` tree and starts
video 1, "Uber Was Cheap. Who Paid?", with the skill's own session 1.

## Setup

```bash
git fetch origin main
git checkout main && git pull origin main      # S06+S07 merged: check `git log --oneline -3`
git checkout -B <the branch this session is given>
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (152 tests) before you start
```

If `main` does not hold `whosedime/whosedime-video/`, stop: Franco has not merged
the pull request yet; tell him, one line.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md`, `ROADMAP.md` (rules, S08 row), `CRITIQUE_PROTOCOL.md`
2. `whosedime/whosedime-maker/SKILL.md` and `references/memory.md` (the Drive tree, `00_state.md`, `videos.md`)
3. `whosedime/notebooks/README.md` (what the voice notebook writes, the narrator in `WhoseDime/Voice/`)
4. `whosedime/whosedime-video/SKILL.md` (what the assembly needs in a video folder)

## Do

1. **The Drive tree** (Google Drive connector), exactly as `memory.md` draws it:
   `WhoseDime/Memory/` (`videos.md`, `lessons.md`), `WhoseDime/Videos/`,
   `WhoseDime/Voice/` (`candidates/`), plus the two launchers at the root:
   `voice_launcher.ipynb` and `assembly_launcher.ipynb`, copied from
   `whosedime/notebooks/` on `main`. *Check:* list the tree back from Drive; no
   duplicate (search before creating, audit P5).
2. **Video 1, the skill's session 1** (steps 1 and 2: topic and angle, research,
   fact check with its people block): follow `whosedime-maker` as written, in
   `WhoseDime/Videos/01_uber/`. The eval run (`evals/files/01_uber/`) is a guide,
   not a source: every fact is read again at its source this session. *Check:*
   Franco has validated topic and angle (Pause 1); `02b_factcheck.md` is in Drive,
   ready for his signature; `00_state.md` and `Memory/videos.md` say so.
3. **Carried over for Franco** (one question at a time, only when the step needs it):
   - the S05 choice, assumed until he decides: the `title` card ("WHO PAYS?",
     drawn by the assembly). The palette is chosen (D16, S07c): do not ask again;
   - the lexicon proposals: `UK` → U-K, `LeWeb` → Luh-WEB, `Rumayyan` → Roo-MY-yan;
   - S06's checks for video 1, when the voice comes (not this session): the narrator
     design in `WhoseDime/Voice/`, the 20 s sample, the blind test (D7), the
     dry-ending thresholds.

## Do not

- The voice, scenes or assembly of video 1: later sessions of the skill's table.
- Edit `checker.py` rules, `style_thresholds.json`, the lists, or any code: a misfire
  goes to "Open issues" in `STATE.md`.
- Touch Zehon files or Zehon's Drive folder.

## Deliverables

- the Drive tree and the two launchers in it; `WhoseDime/Videos/01_uber/` with the
  files of steps 1 and 2 and `00_state.md`; `Memory/videos.md`
- `docs/whosedime/STATE.md` updated, one line per deliverable in `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S09_competitor_watch.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S09 — Weekly competitor
watch, model Sonnet 5.5** (it depends only on S01 and can run while video 1 waits
for Franco). Video 1 itself continues with the skill's session 2 (Script, Opus 5.5)
once Franco has signed the fact check.
