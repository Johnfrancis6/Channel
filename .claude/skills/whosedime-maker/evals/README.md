# Evals of whosedime-maker

`evals.json` holds the prompts and what a good answer does. `files/01_uber/`
is the output of the script eval (id 3) run once in build session S04 on
2026-11-07, from facts read on the web that day, then of the scenes and
publication evals (ids 6 and 7) run once in S05 on the same folder:

- `02b_factcheck.md`: the input of evals 3 and 4. Every `verified` line was
  read at its source in S04. Its signature is a **stand-in for the eval**,
  not Franco's: video 1's real registry is made and signed in session S08.
- `01_research.md`, `02a_outline.md`, `02_script.md`, `02_script_voice.txt`,
  `02c_listen_20s.txt`: the reference outputs. Measured on 2026-11-07 with
  `python3 whosedime/common/checker.py all whosedime/whosedime-maker/evals/files/01_uber`:
  exit 0, 0 blocks, 1 warning (`name-first`, 10 common words, no name);
  script 2,087 words, voice 2,126 words, 0 drift.

- `03_scenes.md`, `04_publication.md` (S05): 91 scenes (54 image, 25 chart,
  5 video, 1 title, 6 chapter), 59 image prompts, 5 clip prompts. Measured on
  2026-11-07 with `checker.py all` on the folder: exit 0, 0 blocks;
  warnings: script 1 (`name-first`), scenes 0, publication 1 (`name-first`:
  Cold, Nothing, Twice; no name). The first publication draft had 6 blocks
  (thumbnail texts in quotation marks read as quotations; "Payer" in chapter
  labels read as a name), fixed in the file, not in the checker.

**Eval 8 ("where are the videos?", audit C4)**, run once in S05: a fresh
general-purpose agent on the Haiku model, told to read only a scratch folder
holding a copy of the skill and a fake Drive tree (`Memory/videos.md`,
`lessons.md`, three video folders with `00_state.md`). Two traps were planted:
31 images in `01_uber/images/` that its state calls "not started", and a script
and voice version in `03_airbnb/` whose state stops at the outline. Measured:
it read `SKILL.md`, `memory.md`, `videos.md`, the three states, then the
folders; answered in French, one block per video, found both traps and said
the folder wins; it also caught two inconsistencies of the fake tree itself
(Uber's registry signed by the eval stand-in while the fake state said
"Franco signed"; Airbnb's registry a placeholder), wrote nothing, and ended
on one question. Limits: one run, the agent had the files on disk (not the
Drive connector), and it was told where the skill was.

Not graded by Franco yet. The tests do not run these evals (a model has to);
`tests/test_whosedime_maker.py` only checks that the reference outputs still
pass the checker.
