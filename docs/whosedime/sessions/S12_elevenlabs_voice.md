# S12 — ElevenLabs voice route (D21)

> Changes from ROADMAP.md: a new build session. Franco decided at video 1's Pause 4 (D21) that the
> narrator is an ElevenLabs voice he picks, not the Qwen3-TTS clone of D8. Under D20 (no paid API
> while the channel earns nothing), **the default route is Franco in the ElevenLabs app**; Claude
> builds everything around it. Runs in parallel with video 1's session 3 (scenes), same branch.

## Context

The voice notebook (`whosedime/notebooks/voice_whosedime.py`, S06) already does everything after
the synthesis: blocks from `02_script_voice.txt`, Whisper transcription and word times, pause
insertion, dry-ending detector, loudness, both speaking rates, `voice.wav`, `words.json`,
`state.json`; the assembly reads those. Only the synthesis changes: audio Franco downloads from
the ElevenLabs app. S11 measured Whisper large-v3-turbo on CPU at x0.8 real time, similarity 1.0.

## Setup

```bash
git fetch origin claude/affectionate-heisenberg-k7i85k && git checkout claude/affectionate-heisenberg-k7i85k   # stay on it
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg     # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                    # green before you start
```

Other sessions push to this branch: `git fetch` and rebase before every push. The live guard
(`tools/guard/guard.py`) runs on your tool calls: read its messages and fix at once.

## Read (in this order)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D6-D8, D18, D20, D21), `ROADMAP.md` (rules, hand-off)
2. `whosedime/notebooks/README.md`, `voice_whosedime.py`, `voice_settings.json`, `whosedime/research/voice_direction.md`
3. `docs/whosedime/generation_report.md` § 1 (the CPU voice measurements)
4. ElevenLabs' own docs, read and dated: the app's text limit per generation, output formats, the
   pronunciation options (phoneme or alias dictionaries, which models honour them), price tiers.

## Do

1. **The import mode**: `MODE = "import"` in the voice notebook. Franco drops the ElevenLabs files in
   `WhoseDime/Videos/<video>/voice/elevenlabs/`; the mode turns them into `voice.wav`, `words.json`,
   `state.json` with the same checks as `full` (similarity, dry endings, pauses, rates), reusing the
   existing functions. Decide, from the app's limits and from what Franco can do in the fewest
   clicks, whether he exports **one file per block, per beat, or the whole text**, and make the
   alignment work for that cut (a long file is split back into blocks by the word times).
   *Check:* tests with fixture audio (any local TTS or tones; no network), a missing or extra file
   refused with a clear message, a file whose words drift from the voice text flagged.
2. **The 20 s sample first (D6)**: `MODE = "sample"` accepts Franco's `listen_20s` file the same
   way and writes `listen_20s.json` with its words-per-minute. The full import still needs
   `I_LISTENED` ticked.
3. **Names for this engine**: the respellings of `lexicon.tsv` were written for Qwen3-TTS. The voice
   text may use either the written or the respelled form (the checker accepts both). Recommend one
   form per name for ElevenLabs from its docs (and its pronunciation dictionary if the app offers
   it); do not change `lexicon.tsv` without Franco's word (pending proposals in STATE.md).
4. **Franco's guide**: `docs/whosedime/voice_elevenlabs_guide.md`, one page: which text to paste, the
   settings to keep the same across files, file names, where to drop them, then the Colab button.
   Give it to Franco in French in the chat (the file stays in English, D2).
5. **The API option, priced, not used**: ElevenLabs' price per character for a 2,100-word script,
   read with its date; a `synth` adapter behind a flag, tested with a fake API. No key requested
   unless Franco asks (D20).

## Do not

- Touch the script, the checker's rules, the registry or video 1's content files.
- Spend money or request a key. Never print a key.
- Remove the Qwen3-TTS path: it stays as the fallback (D8 is replaced for the narrator, not deleted).

## Deliverables

`voice_whosedime.py` (+ notebook cells, settings), tests, `voice_elevenlabs_guide.md`, README row,
`STATE.md`, one critique line per deliverable. Colab runs `main`: say in the report that Franco must
merge a pull request before he can use the import mode.

## Hand-off

`ROADMAP.md` "The hand-off" (D17; report to the orchestrator `session_01Cw13LhWRZyGn7FWUAAzMb1`, D19).
Next: none opened by you; the orchestrator opens the assembly session once images, clips and voice
are in video 1's Drive folder. Model: **Opus 5.5**.
