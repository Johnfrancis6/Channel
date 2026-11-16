# S14 — Voice reference by upload in Colab (D32)

> Written 2026-11-16 by session `session_01Cw13LeFBwzXQBL4SqwTyRi` (orchestrator) after S13. Model: Opus 5.5.
> Repo only: no Drive edit, no video content. Franco steps in only for permissions and his answers (D33).

## Why

D32: Franco chooses the narrator's voice and its reference text himself and **uploads the clip and its text in
Colab**, instead of dropping them in Drive `WhoseDime/Voice/elevenlabs/` (S12, D22). Today `MODE = "reference"`
reads only that Drive folder (`find_reference_clip`, `import_reference` in `whosedime/notebooks/voice_whosedime.py`).
The rest of the import stays: trim, 24 kHz, Whisper check of the text, `ref.wav` / `ref.txt` / `ref.json`, old ones
to `Voice/old/`, words-a-minute advice.

## Setup

```bash
git fetch origin main claude/s13-reconcile
git checkout -b claude/s14-voice-upload origin/claude/s13-reconcile   # S13 not yet merged into main
apt-get update && apt-get install -y ffmpeg && pip install opencv-python-headless pillow numpy
python3 -m unittest discover -s tests        # 233 pass, measured 16/11 after S13
```

Read first: `docs/whosedime/STATE.md`, DECISIONS D21-D23 and D30-D33, `voice_elevenlabs_guide.md`,
`whosedime/notebooks/README.md`, `voice_launcher.ipynb`, `voice_whosedime.ipynb` / `.py`, `voice_settings.json`
(`reference_import`), `tests/test_voice_reference.py`.

## Do

1. **Upload in the notebook.** With `MODE = "reference"`, the notebook asks Franco for the files with
   `google.colab.files.upload()`: one audio file (the `audio_ext` of `reference_import`) and its text, either a
   `.txt` uploaded with it or a form field `REFERENCE_TEXT` (paste the text he had the voice say). It saves them in
   `Voice/elevenlabs/` (moving what was there to `Voice/old/` with the date, never deleting), then runs the existing
   import. Refuse with one clear line: no audio, two audio files, no text, an empty text. If Franco uploads nothing
   but `Voice/elevenlabs/` already holds a clip, say so and use it (the S12 route stays a fallback).
   Keep the upload in a small function that takes the uploader as an argument, so tests pass a fake one.
2. **Launcher form** (`voice_launcher.ipynb`): add `REFERENCE_TEXT` (string, empty by default) and update the
   comments: "reference: upload your clip and its text when asked (D32)". The launcher still runs `main` (D5).
3. **Guide** `voice_elevenlabs_guide.md` § 2-3: Drive step replaced by the upload; text from Franco's choice, the
   guide's text only a suggestion. One page.
4. **Tests** in `tests/test_voice_reference.py`: fake uploader for each case of task 1 (ok with `.txt`, ok with the
   form text, refusals, old clip archived, Drive fallback). Then the full suite green; say the measured count.
5. Self-critique and the critique line (`"step": "S14_voice_upload"`), STATE.md (≤ 60 lines), commit, `git fetch`,
   push, then **open a pull request to `main`** (base `main`; if pull request 12 is not merged yet, say in the body
   that it holds S13's commits and must be merged after 12). Give its link.

## Hand-off (D17, D19, D33)

- Write the next prompt: **video 1 voice in Colab** is Franco's, not a session: after both pull requests are merged,
  he runs the launcher `MODE = "reference"` (upload), then `"sample"`, listens (D6), then `"full"`. The next build
  session is the one that checks his upload and the 20 s sample once he says it is done; name it, write its prompt
  only if its scope is clear, else put it in STATE.md.
- Open the next session yourself with `create_session` if a prompt was written; report to the orchestrator
  session `session_01Cw13LeFBwzXQBL4SqwTyRi` with `send_message` (links, tests, self-critique). Then stop.

## Watch out

- Do not touch Drive or the video files. Do not run the voice model.
- Everything committed in English (D2, D31); answer Franco in the language he writes in.
- Never edit `.claude/skills/` or `*.skill`. Push without `2>&1` after the branch name.
