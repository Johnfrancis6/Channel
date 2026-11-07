# S06 — Voice notebook (English)

> Changes from ROADMAP.md: S05 defined the per-video state (`00_state.md`,
> `whosedime-maker/references/memory.md`): the notebook writes its own
> state file in `voice/` and the speaking rate that `lessons.md` reads. The
> S05 pull request to `main` may still be open: work on the branch anyway.

## Context

The skill now writes everything up to `04_publication.md`; the voice
version `02_script_voice.txt` is one sentence per line, blocks of 2-4
sentences separated by a blank line. S06 builds the Colab notebook that
turns it into `voice/` (audit C6, decisions D6-D8).

## Setup

```bash
git fetch origin claude/blissful-tesla-abtjgt
git checkout claude/blissful-tesla-abtjgt
pip install -q opencv-python-headless pillow numpy
apt-get update -qq && apt-get install -y -qq ffmpeg   # skip if `ffmpeg -version` works
python3 -m unittest discover -s tests                  # must be green (100 tests) before you start
```

Stay on this branch. `git fetch` before every push. Never print
`YOUTUBE_API_KEY` or `SUPADATA_API_KEY`.

## Read (in this order; nothing else unless a task needs it)

1. `docs/whosedime/STATE.md`, `DECISIONS.md` (D2, D5, D6, D7, D8), `ROADMAP.md` (rules, S06 row), `CRITIQUE_PROTOCOL.md`
2. `whosedime/research/voice_direction.md` (narrator, rate, pauses, blind test)
3. `whosedime/whosedime-maker/references/step3_script.md` § 3c and the 20 s sample; `references/memory.md` (state, `lessons.md`)
4. `whosedime/whosedime-maker/evals/files/01_uber/02_script_voice.txt`, `02c_listen_20s.txt` (the test input)
5. `reports/Audit pipeline de production.md` § 2.1 symptom 2 (V1-V7) and § 3 C5, C6 — in French
6. For structure only: `zehon/notebooks/voix_zehon.ipynb`, `lanceur_voix.ipynb`, `lanceur.py` (do not edit; rewrite, do not translate)

## Do

1. **The notebook** `whosedime/notebooks/voice_whosedime.ipynb`, with its
   logic in an importable module (tests cannot run a notebook): reads
   `02_script_voice.txt` from the video folder; synthesises **one block at
   a time** (2-4 sentences, not one line: V1); pauses from punctuation
   (about 250 ms after a full stop, 450 ms after a question or a quoted
   line, 700 ms between blocks; values in one settings place, C5); a
   **dry-ending detector** (last word ends under 60 ms from the clip end, or
   sound still loud in the last 30 ms: redo with another seed, twice at
   most, then flag); writes `voice/voice.wav`, word timings
   `voice/words.json` (the assembly aligns `03_scenes.md` on them) and
   `voice/state.json`, rewritten whole on each run, with **both rates**
   (speech only and whole track, words a minute: C5). *Check:* runs end
   to end on a fake Drive folder with a **stub model** (no GPU), in a test.
2. **The 20 s sample first** (D6): a mode that synthesises only
   `02c_listen_20s.txt` and stops, before any full synthesis.
3. **VoiceDesign, then clone** (D8): the cell order that designs the
   American narrator from `voice_direction.md`, saves the reference, then
   clones it on the Base model; the blind test of D7 (block vs sentence) as
   an option that writes the pairs for Franco's vote.
4. **Detector test**: a test feeds it a clip cut mid-word (generated with
   numpy) and a clean one; it flags only the cut one.
5. **Launcher** `whosedime/notebooks/voice_launcher.ipynb` (or the shared
   launcher), pointing to `main` (D5), printing the commit it runs.
6. **Sync and tests**: tests green; no PR this session (S07 ends with one,
   ROADMAP rule 2), unless the S05 PR is merged and Franco asks.

## Do not

- Write the chart generator or the assembly (S07), or anything in Drive (S08).
- Edit `checker.py` rules, `style_thresholds.json` or the lists; a misfire goes to "Open issues".
- Touch Zehon files.

## Deliverables

- `whosedime/notebooks/` (notebook, module, launcher), tests
- `docs/whosedime/STATE.md` updated, one line per deliverable group in `docs/whosedime/critique_log.jsonl`
- `docs/whosedime/sessions/S07_charts_and_assembly.md`

## Hand-off

Follow `ROADMAP.md` § "The hand-off". Next session: **S07 — Charts and
assembly, model Opus 5.5**. Carry over: the S05 choices waiting for Franco
(the `title` card type, the channel palette, the unnamed caricature) and
the lexicon proposals (UK, LeWeb, Rumayyan).
