# Evals of whosedime-maker

`evals.json` holds the prompts and what a good answer does. `files/01_uber/`
is the output of the script eval (id 3) run once in build session S04 on
2026-11-07, from facts read on the web that day:

- `02b_factcheck.md`: the input of evals 3 and 4. Every `verified` line was
  read at its source in S04. Its signature is a **stand-in for the eval**,
  not Franco's: video 1's real registry is made and signed in session S08.
- `01_research.md`, `02a_outline.md`, `02_script.md`, `02_script_voice.txt`,
  `02c_listen_20s.txt`: the reference outputs. Measured on 2026-11-07 with
  `python3 whosedime/common/checker.py all whosedime/whosedime-maker/evals/files/01_uber`:
  exit 0, 0 blocks, 1 warning (`name-first`, 10 common words, no name);
  script 2,087 words, voice 2,126 words, 0 drift.

Not graded by Franco yet. The tests do not run these evals (a model has to);
`tests/test_whosedime_maker.py` only checks that the reference outputs still
pass the checker.
