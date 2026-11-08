# Whose Dime — YouTube channel "Who Pays?"

English videos (13-15 min) telling how famous companies grew and who
really paid for it. Franco decides topics and validates at each pause;
Claude writes the content and builds the tools; Franco produces the pieces
(images, voice in Colab).

**To resume: read [docs/whosedime/STATE.md](docs/whosedime/STATE.md)**
(where we are, the work branch, the next session). The build plan is
[docs/whosedime/ROADMAP.md](docs/whosedime/ROADMAP.md); decisions are in
[docs/whosedime/DECISIONS.md](docs/whosedime/DECISIONS.md).

## Rules (short form of ROADMAP.md, "Rules for every session")

- Everything committed for Whose Dime is in English. Talk to Franco in
  English (his choice since 2026-11-08, D17; French before).
- Work on the branch named in `STATE.md`; `git fetch` before every push.
  Colab runs `main`; it changes only through a pull request Franco merges.
- Do only what the session prompt lists; anything else goes to "Open
  issues" in `STATE.md`. Stop at the end of the scope.
- Never edit `.claude/skills/` or `*.skill`: edit `<channel>/<skill>/`,
  then `python3 tools/sync_skills.py` (`--check` reports drift).
- Tests: `python3 -m unittest discover -s tests`, green before the final
  commit. A fresh container first needs:
  `apt-get update && apt-get install -y ffmpeg` and
  `pip install opencv-python-headless pillow numpy`.
- After every deliverable: self-critique, Franco's grade, one line in the
  log, per [docs/whosedime/CRITIQUE_PROTOCOL.md](docs/whosedime/CRITIQUE_PROTOCOL.md).
- Say what is measured and what is assumed. Recommend; one question at a time.
- Never print `YOUTUBE_API_KEY` or `SUPADATA_API_KEY`. Always give the
  link to every report written.

## Other channels

- **Zehon** (French) is frozen since 2026-11-07: see
  [docs/chaine2/CONTEXTE.md](docs/chaine2/CONTEXTE.md) (in French).
- The old English Shorts channel is archived on branch
  `archive/pipeline-shorts-2026-09-30`.
