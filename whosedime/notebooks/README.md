# Whose Dime notebooks (Colab)

Voice built in session S06, assembly in S07. Colab always runs `main` (decision D5).

| File | Role |
|---|---|
| [`voice_launcher.ipynb`](voice_launcher.ipynb) | the copy Franco keeps in Drive: a form, then it clones `main`, **prints the commit it runs** and runs the notebook below |
| [`voice_whosedime.ipynb`](voice_whosedime.ipynb) | the voice notebook: thin cells, in order: settings, setup, **narrator (VoiceDesign, D8)**, clone on the Base model, **20 s sample (D6)**, full voice, **blind test (D7)** |
| [`voice_whosedime.py`](voice_whosedime.py) | all the logic, importable, tested without a GPU (`tests/test_voice_whosedime.py`, stub model) |
| [`voice_settings.json`](voice_settings.json) | **every number** of the voice (pauses, detector, rates, seeds, model names, narrator descriptions): the one place (audit C5) |
| [`launcher.py`](launcher.py) | runs a notebook's code cells; the launcher's form overrides the `settings` cell |
| [`assembly_launcher.ipynb`](assembly_launcher.ipynb) | (S07) the Drive copy for the assembly: `VIDEO`, `MODE` (`plan`, `extract`, `full`), `SCENES`, `ROOT`; clones `main`, prints the commit |
| [`assembly_whosedime.ipynb`](assembly_whosedime.ipynb) | (S07) the assembly notebook: thin cells around [`whosedime-video/scripts/assemble.py`](../whosedime-video/scripts/assemble.py) (skill [`whosedime-video`](../whosedime-video/SKILL.md)); no GPU |

## What a run writes, in `WhoseDime/Videos/<video>/voice/`

| Mode | Files |
|---|---|
| `sample` | `listen_20s.wav`, `listen_20s.json` (from `02c_listen_20s.txt`) |
| `full` | `voice.wav`, `words.json`, `state.json` (rewritten whole), `cache/` (one WAV and one transcription per block, for resuming) |
| `blind_test` | `blind_test/pair_NN_X.wav`, `pair_NN_Y.wav`, `vote.md`, `key.json` |

The narrator lives in `WhoseDime/Voice/`: `candidates/` (A, B, C), then
`ref.wav`, `ref.txt`, `ref.json` once Franco keeps one (older ones in `old/`).

## How a block is made

1. `02_script_voice.txt` is cut into blocks at blank lines (2-4 sentences, one per line).
2. Gates: the checker's `voice` target must pass (D4); `full` needs the
   20 s sample made with the same narrator and `I_LISTENED` ticked (D6).
3. One synthesis per block (V1). Whisper transcribes it (without being
   given the text, so the similarity is honest); the voice text's own words
   get the transcribed times, unmatched ones are interpolated.
4. **Dry-ending detector** (C6.3): last transcribed word less than 60 ms
   from the clip end, or the last 30 ms within 25 dB of the speech level:
   redone with another seed, twice at most, then flagged in `state.json`.
5. Pauses (C6.2): inside a block, a sentence-end gap shorter than its
   target (250 ms after a full stop, 450 ms after a question or a quoted
   line) is lengthened at its quietest point; 700 ms between blocks.
6. `state.json`: both rates, `rate_total_wpm` (whole track, the one for
   `lessons.md`, target 142-154) and `rate_speech_wpm` (sentence spans only).

**Measured** in S06: the chain runs end to end on the Uber eval text with a
stub model; the detector flags a clip cut mid-word and passes a clean one.
**Assumed**, to check on video 1: the 25 dB loudness threshold, the 40 ms
trim margin, that lengthened pauses do not sound stitched, the run time on
a T4, and the qwen-tts calls (read from qwen-tts 0.1.1's source, never run).
