# S11 — Generation pipeline (images, clips, voice without Franco's hands)

> Changes from ROADMAP.md: a new build session, asked by Franco on 08/11 (D17-D19): he
> validates, Claude produces. Today Franco makes the images (Gemini), the clips (Flow) and
> the voice (Colab notebook, T4). This session measures what a cloud session can generate
> itself and builds it. Runs **in parallel** with video 1's session 2b and S10, on the same branch.

## Context

Video 1's script is being written (session 2b); scenes and prompts come next (session 3,
`03_scenes.md`: about 50-55 Gemini images in batches of 10, 4-5 Flow clips, charts drawn by
`charts.py`). The assembly (`whosedime-video`) already renders from the Drive folder. The gap
is the generation of images, clips and voice, and moving binaries into Drive.

## Setup

```bash
git fetch origin claude/affectionate-heisenberg-k7i85k && git checkout claude/affectionate-heisenberg-k7i85k   # stay on it
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg     # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                    # green before you start
```

Other sessions push to this branch: `git fetch` and rebase before every push; resolve
`STATE.md` and `critique_log.jsonl` by keeping both sides.

## Read (in this order)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D12, D17-D19), `ROADMAP.md` (rules, hand-off)
2. `whosedime/whosedime-maker/references/step4_scenes.md` (scene types, Gemini preamble and
   batches, Flow prompts, file names) and `whosedime/whosedime-video/SKILL.md` (what the assembly reads)
3. `whosedime/notebooks/voice_whosedime.py`, `voice_settings.json`, `README.md` (the voice pipeline, D6-D8)
4. The environment docs (`read_documentation`: `environment.secrets`, `environment.network`, `session.resources`)

## Do

0. **Measure the container** (one table, measured): GPU or not, CPU cores, RAM, disk allowance,
   hosts reachable (huggingface.co, generativelanguage.googleapis.com, Drive). No guess.
1. **Voice**: run the voice notebook's code on this container for a 50-word sample (CPU if no GPU).
   *Check:* the real-time factor, measured. If 14 min of voice fits in about 1 h, add a command
   that produces `voice/voice.wav` and `voice/words.json` in-session; otherwise keep Colab and say why.
2. **Images**: `whosedime/generate/images.py`: reads the Gemini batches of a `03_scenes.md`, calls
   the Gemini API image model with the preamble, writes `images/scene_NNN.png` at the size the
   assembly needs, resumes after a failure, logs cost and model per image. A key is needed: say in
   one line which host and why, then `request_credential` (host `generativelanguage.googleapis.com`).
   **Money is Franco's** (D18): before any paid call, give him the price per image read on Google's
   pricing page (with its date) and the total for one video; generate only 3 test images from a
   fixture until he agrees. *Check:* tests with a fake API; the 3 images opened and described.
3. **Clips**: same for image-to-video (Veo through the same API) if the key allows it: price per
   clip, 1 test clip at most. If not available, keep Flow by Franco and say so.
4. **Binaries into Drive**: measure the route (the Drive connector's base64 upload against an API
   route with a credential); pick the one that moves 60 images and 5 clips without filling the
   context; build it. *Check:* one image and one clip round-trip, sizes equal.
5. **One command per video**: `python3 whosedime/generate/run.py FOLDER` chains what works
   (images, clips, voice, charts, assembly) and writes a status file the skill's `00_state.md` reads.

## Do not

- Touch the content skill's wording rules, the checker, video 1's content files, or Franco's Colab notebooks' behaviour.
- Spend beyond the test budget (3 images, 1 clip) without Franco's word. Never print a key.
- Put a real person's name in an image prompt (D12 limits; the checker's `prompt-person` rule stands).

## Deliverables

`whosedime/generate/` (scripts, settings), tests, a measured report `docs/whosedime/generation_report.md`,
`STATE.md`, one critique line per deliverable.

## Hand-off

`ROADMAP.md` "The hand-off" (D17: open the next session yourself; D19: report to the orchestrator
`session_01Cw13LhWRZyGn7FWUAAzMb1`). Next: whatever video 1 needs from this pipeline once
`03_scenes.md` exists. Model: **Opus 5.5**.
