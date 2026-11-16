# S15 — Voice pace advice and the launcher's output (after the first ElevenLabs sample)

> Written 2026-11-16 by the orchestrator `session_01Cw13LeFBwzXQBL4SqwTyRi`. Model: Opus 5.5. Repo only.

## Measured in Colab, 16/11 (Franco's runs on `main` @ 186db37)

- `MODE = "reference"`: upload OK (D32); Whisper fell back to the CPU (S14b) and worked; similarity 0.967;
  reference 67 words in 20.3 s = **197.6 words a minute** (range 135-155: too fast). The reference step advised
  "Speed 1.0 -> about 0.78" (`reference_rate`).
- `MODE = "sample"`: 19.33 s, **189.3 wpm on the whole sample** (target 142-154), **220.9 in speech only**; block 1
  redone twice for a dry ending. Clone/reference speech ratio: 220.9 / 197.6 = **1.12** (one measure; S11 measured 1.2).
- The sample step advised "lower Speed by **about 0.1**": too small, and not the same advice as the reference step.
- After the run, Colab printed the whole notebook namespace (settings, form history): `launcher.run(...)` is the
  last expression of the launcher cell and returns the namespace, so Colab displays it.
- `WARNING:sox:SoX could not be found!` and the flash-attn warning: harmless (no SoX use in our code; assumed).
- Guard false block 16/11: `git checkout -b NEW ... && git push -u origin NEW` in one call is blocked, because the
  guard reads the current branch before the checkout runs. Put in STATE.md open issues; fix only if quick.

## Do

1. **One pace advice, proportional.** The sample's advice (the "The clone follows the reference's pace" line in
   `voice_whosedime.py`) gives the factor to aim the *whole sample* at `rate_wpm.aim` (149): F = aim / rate_total_wpm,
   said as "multiply your ElevenLabs Speed by F" (the notebook does not know his Speed), with ElevenLabs' floor 0.7:
   if Speed x F would need less than 0.7, say so and suggest a slower voice. The reference step (`reference_rate`)
   uses the same wording. Record the clone/reference ratio in `listen_20s.json`. Tests for both.
2. **No namespace dump.** Make the launcher cells print nothing after the run (e.g. `_ = launcher.run(...)` in every
   launcher of `whosedime/notebooks/`, or `run` returns None if nothing reads its value). Tests if any cover launchers.
3. `voice_settings.json`, `_reference_import_source`: add the 16/11 measure (reference 197.6 -> clone speech 220.9,
   x1.12). Do not change the ranges on one measure.
4. Tests green, critique line (`"step": "S15_voice_rate_advice"`), STATE.md (60 lines at most), commit, push,
   **pull request to `main`**; report to `session_01Cw13LeFBwzXQBL4SqwTyRi` with `send_message`. Then stop: the next
   step is Franco's (new reference at a lower Speed, then `sample`, listen, `full`).

## Watch out

No Drive, no voice model run. Everything committed in English (D31). Push without `2>&1` after the branch name.
