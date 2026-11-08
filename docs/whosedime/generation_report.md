# Generation pipeline — measured report (S11, 2026-11-08)

What a cloud session can generate by itself for a Whose Dime video, measured on the
session's own container, and what was built. **Measured** and **assumed** are kept apart.

## 0. The container (measured, 08/11)

| What | Measured |
|---|---|
| GPU | **none** (`nvidia-smi` missing, no `/dev/nvidia*`) |
| CPU | 4 cores, Intel Xeon 2.30 GHz (`nproc`, `lscpu`) |
| RAM | 15 GB, no swap (`free -g`) |
| Disk allowance | 30 GB free at start (`df`); the voice models then took 10 GB |
| Python | 3.13 |
| huggingface.co | reachable (API 200, model files downloaded: 2 Qwen3-TTS models, Whisper) |
| generativelanguage.googleapis.com | reachable; answers Google's own 403 "unregistered callers" without a key (network open, **key missing**) |
| www.googleapis.com (Drive API) | reachable; same Google 403 without credentials |
| Drive connector | works: upload and download of base64 content |
| Network policy | unrestricted (environment "Default", no secrets, no setup script) |

## 1. Voice: stays in Colab (measured)

The voice notebook's own code (`qwen_designer`, `qwen_clone_synth`, `whisper_aligner` of
`voice_whosedime.py`), run as-is on the CPU (fp32, 4 threads) by
[`measure_voice_cpu.py`](../../whosedime/generate/measure_voice_cpu.py):

| Step | Time | Audio | Real-time factor |
|---|---|---|---|
| VoiceDesign, description A, reference text (67 words) | 117.2 s (+ 25 s load) | 23.5 s | **x5.0** |
| Clone on the Base model, 57-word sample | 101.6 s (+ 21.5 s load) | 16.6 s | **x6.1** |
| Whisper large-v3-turbo, int8 | 13.5 s | 16.6 s | x0.8; similarity **1.0** |

- **14 min of voice ≈ 840 s x 6.1 ≈ 85 min of synthesis**, plus Whisper (about 11 min)
  and the dry-ending redos: **about 1 h 45**, over the 1 h limit of the S11 prompt. RSS
  8.8 GB of 15 GB. **The voice stays in Colab (T4)**; no in-session voice command built.
  Fallback if Colab is ever unavailable: the same notebook functions run here, slowly.
- **New, measured**: the qwen-tts calls of the notebook (until now "read from the source,
  never run") work: both models load, synthesise, and Whisper hears every word.
- **Warning for Pause 4 / the 20 s sample**: this one CPU sample spoke fast: the designed
  reference **171 words a minute**, the cloned 57 words **206 a minute** (target 142-154,
  never above 161, `voice_settings.json`). One seed (42), one sample, CPU, raw clip without
  the notebook's pauses: assumed seed- or text-specific until the Colab 20 s sample
  (`listen_20s.json`) gives its own rate.

## 2. Images: built, no paid call (key declined)

- **Model and price** (read on [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), 08/11/2026):
  `gemini-nano-banana-2.1`, paid tier only, **$0.0504 per 2K image** (1,680 tokens at
  $30/M; 1K $0.0336, 4K $0.113; Batch half price). 16:9 at 2K = **2752x1536**, above
  the assembly's 1920x1080 x its 10 % margin (2112x1188); 1K (1376x768) would be enlarged.
- **One video**: 59 image prompts on the reference run → **$2.97** (`images.py --estimate`, measured on the eval folder).
- [`images.py`](../../whosedime/generate/images.py): one call per image (Interactions
  API), the preamble's style sentences in front (its chat sentences "reply OK, wait"
  dropped), the earlier image attached when a prompt says "Same setting ... as
  scene_NNN" (the Gemini chat did that by memory), resume, redo, ledger, budget.
- **Key**: requested in-session (host `generativelanguage.googleapis.com`); **Franco
  declined**. The 3 test images were therefore **not made**: no image to open and describe.
  *Check done instead*: 23 tests with a fake API (`tests/test_generate.py`).
- **Assumed** (not measured without a key): the exact answer shape (the code reads the
  REST `steps` and the SDK fields), that `image_size: "2K"` returns 2752x1536 (a smaller
  image is enlarged with a warning in the ledger), the time per image, that the style
  stays as steady across separate calls as in one chat per batch.

## 3. Clips: built, no paid call

- Veo 3.1 Preview **was shut down in the Gemini API on 2026-10-22**
  ([docs/video](https://ai.google.dev/gemini-api/docs/video)); the API's video model is
  now `gemini-omni-1.2-flash` (3-15 s, image to video, native audio).
- **Price** (same page, 08/11): **$0.104 per second at 1080p** (720p about $0.07/s) →
  **$0.83 per 8 s clip**, **$4.16 for 5 clips**.
- [`clips.py`](../../whosedime/generate/clips.py): the scene's image + its `anim_NNN`
  prompt, 1080p, 8 s, `delivery: uri` (clips over 4 MB), ffprobe check before the file
  takes its name; the image stays as the fallback. *Not measured*: time per clip, the real
  answer, how the clip follows the illustration's style. Until a key exists, **Flow by Franco**.

**Total per video: about $7.13** ($2.97 images + $4.16 clips), before redos. Test budget: **$0.98**.

## 4. Binaries into Drive: generate where Drive is (measured)

| Route | Measured | Verdict |
|---|---|---|
| Drive connector, `create_file` with `base64Content` | a 145-byte PNG and a 1,735-byte MP4 uploaded and downloaded back: **sizes equal (145, 1735), content identical**; then trashed | works, but the base64 goes **through the context**: +37 % size, one 2K PNG (several MB) is millions of characters. Fit for small files only (`.md`, `.json`) |
| Drive API with a stored credential | a stored network secret is a fixed header; Drive writes need an OAuth token (expires after 1 h), an API key cannot write | not storable as a fixed secret: **not built** |
| **Colab, Drive mounted** | the assembly and voice notebooks already write there | **chosen**: the pieces are made where they are stored; nothing crosses the session |

Built: [`generate_launcher.ipynb`](../../whosedime/notebooks/generate_launcher.ipynb)
(the Drive copy, form `VIDEO`, `MODE` estimate / test / full, `APPROVED_USD`) runs
[`generate_whosedime.ipynb`](../../whosedime/notebooks/generate_whosedime.ipynb) from
`main` (D5); the key is a **Colab secret** `GEMINI_API_KEY`, read only after the folder
and the mode are checked, never printed. The S11 round-trip check (one image, one clip)
was done on the connector route with small files; the Colab route has no transfer to check.

## 5. One command per video

`python3 whosedime/generate/run.py FOLDER [--test | --approved-usd X]` (the notebook calls
it): images → clips → voice state (read, not made) → charts → render (`assemble.py` once
every image and the voice are ready, else `--plan --no-files`), then
`generate/status.json` (each step in the words of `00_state.md`, counts, money spent,
the next action). Measured on the reference folder without a key: 2.8 s, 25 charts of 25,
nothing paid, next = "Images".

## Recommendation

Franco adds his Gemini key as a Colab secret, runs the launcher once with
`MODE = "test"` (3 images, 1 clip, $0.98), and the next session looks at them before any
`full` run ($7.13 per video). Until then, images in Gemini and clips in Flow, as today.
