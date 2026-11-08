# Whose Dime generation pipeline (S11)

The pieces of a video from the prompts of `03_scenes.md`, by the Gemini API, and one
command that chains them up to the render. Measured report:
[`docs/whosedime/generation_report.md`](../../docs/whosedime/generation_report.md).

| File | Role |
|---|---|
| [`settings.json`](settings.json) | every number: models, prices **with the date they were read**, sizes, retries, the budget |
| [`gemini.py`](gemini.py) | the Interactions API client (key from `GEMINI_API_KEY` or the session proxy, never printed), the prompt reader (the checker's parser), the ledger and the budget gate |
| [`images.py`](images.py) | `images/scene_NNN.png`, 2752x1536 (Nano Banana 2.1, 2K, 16:9), the preamble's style in front of each prompt, the earlier scene attached for "Same setting as scene_NNN", resume |
| [`clips.py`](clips.py) | `clips/scene_NNN.mp4` from its image (Gemini Omni Flash, 1080p, 8 s; Veo 3.1 Preview is shut down in the Gemini API) |
| [`run.py`](run.py) | `run.py FOLDER`: images, clips, voice state, charts, render, then `generate/status.json` |
| [`measure_voice_cpu.py`](measure_voice_cpu.py) | the voice's real-time factor on a CPU (why the voice stays in Colab) |
| Colab | [`generate_launcher.ipynb`](../notebooks/generate_launcher.ipynb) (the Drive copy) runs [`generate_whosedime.ipynb`](../notebooks/generate_whosedime.ipynb) from `main` |

## Money (D18)

- `--estimate`: the price of what is missing, no call.
- `--test`: 3 images and 1 clip at most, whatever the amount (about $0.98).
- `--approved-usd X`: everything missing, stopping **before** a call that would take
  the ledger's total past `X`. Without one of these flags, nothing is paid.
- Every paid call is a line of `generate/ledger.jsonl` in the video folder: model, size,
  price, file, prompt hash, seconds, the API's usage counts. A failed call costs 0,
  except an answer without an image (counted, to be safe). Three failures in a row stop
  the run.

## Where it runs

In **Colab**, writing straight into the Drive folder: binaries never cross the session's
context (the Drive connector takes base64 inline, so a 2K PNG of several MB cannot go
through it; measured in S11). A cloud session can run the same commands on a local copy
if it has a key, for tests and a look at the images.

## Tests

`python3 -m unittest tests.test_generate` — a fake API: payloads, sizes, resume, redo,
continuity reference, key never printed, retries, budget gate, status file, the notebook
in `estimate` mode.
