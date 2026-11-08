# Video 1, skill session 2b — Script and voice version (Uber)

> Second half of the whosedime-maker's session 2. Session 2a (2026-11-08,
> `session_01Cw13LhWRZyGn7FWUAAzMb1`) checked the signature, wrote the
> outline and stopped at Pause 3: **Franco validated the outline** ("Oui,
> je valide le plan", 08/11) and asked for the next steps to go to other
> sessions. This session does steps **3b and 3c only** and stops at Pause 4.

## Setup

```bash
git fetch origin claude/affectionate-heisenberg-k7i85k
git checkout claude/affectionate-heisenberg-k7i85k   # or the branch STATE.md names
python3 -m unittest discover -s tests                # green before you start (167 tests)
```

Fresh container: `apt-get update && apt-get install -y ffmpeg` and
`pip install opencv-python-headless pillow numpy` (needed by the tests only).
Model: Opus 5.5. Connector: Google Drive.

## Read (in this order)

1. `docs/whosedime/STATE.md`
2. The skill `whosedime-maker` (invoke it): `SKILL.md`, then `references/step3_script.md` and `references/memory.md`
3. In Drive, `WhoseDime/Videos/01_uber/`: `00_state.md`, `02a_outline.md` (**validated: follow it**),
   `02b_factcheck.md`, `01_research.md` (nuances, names to pronounce). Download them **raw**
   (`download_file_content`) into a scratchpad folder; the checker needs the exact text.
4. `whosedime/research/storytelling_rules.md` (S1-S14, E1-E5) and `whosedime/research/rewrite_uber_cold_open.md`

## First check (2 minutes)

`python3 whosedime/common/checker.py fingerprint <folder>/02b_factcheck.md` must print
`sha256:18adbeeab4a0`, the value on its `Signed:` line. If it does not, **stop** and tell Franco:
do not touch the signature line. (Session 2a found the Drive editor had re-escaped the file
— `\$`, `\_`, `\[TO VERIFY\]`, `&nbsp;` — and restored the exact S08 upload; see STATE.md.)

## Do

1. **3b, the script** (`02_script.md`): the six beats of `02a_outline.md`, exact headings of
   `step3_script.md`, `### Step 1: Investors`, `### Step 2: Drivers`, `### Step 3: Medallion owners`;
   2,000-2,250 words; `[^Fnn]` after each claim; quotes word for word from the people block.
   Decided: **F33 (Mamdani) is not used**; F43 is `[TO VERIFY]`: say "Mr Aslam and Mr Farrar".
   Run `python3 whosedime/common/checker.py script <folder>/02_script.md` after each draft: no
   `BLOCK`; each `WARN` fixed or kept with a one-line reason.
2. **3c, the voice version** (`02_script_voice.txt`) and the **20 s sample**
   (`02c_listen_20s.txt`, about 50 words), per `step3_script.md`. Then
   `python3 whosedime/common/checker.py all <folder>` must exit 0.
3. **E1-E5** by ear, one line each with its place; then **Pause 4** as `step3_script.md` says
   (3 lines, the link to the sample, one question).
4. After Franco's answer: grade question, one line in `docs/whosedime/critique_log.jsonl`
   (`3b_script` for the script, `3c_voice` for the voice version), `00_state.md` and the
   `videos.md` row rewritten in Drive (new file, then the old one to the bin), STATE.md, commit, push.
5. **Hand-off (D17, D19)**: write `docs/whosedime/sessions/V1_S3_scenes.md` (steps 4-5, Sonnet 5.5,
   with what this session learned), open it with `create_session` (repo, this branch as
   `source_revision` and `outcome_branch`, model `claude-sonnet-5-5`), give Franco its link, and
   send the orchestrator `session_01Cw13LhWRZyGn7FWUAAzMb1` your report (`send_message`: links,
   checker result with warning count, E1-E5, self-critique, grade).

## Watch out

- The weakest beat of the outline is **The decision** (390 words on one blog post and two
  quotes): tell the January 9, 2014 post as an announced reconstruction ("Picture the post
  going live."), never with invented lines in quotation marks.
- A fact the script needs that is not a `verified` line: leave it out. Adding a line changes
  the hash and Franco must sign again.
- Every capitalised word inside a sentence must be in the registry (`Britain` is not; `UK`,
  `London`, `Lyft`, `Expedia`, `Bloomberg`, `Airbnb` are).
- Lexicon proposals still waiting for Franco: `UK` → U-K, `LeWeb` → Luh-WEB,
  `Rumayyan` → Roo-MY-yan, `Kamel` → Kuh-MEL, `Bhairavi Desai` → BY-ruh-vee Deh-SIGH. Use only
  `lexicon.tsv` in the voice version until he agrees; ask him at Pause 4 only if the sample needs one.
- Write Drive files with `create_file` (`text/markdown`, `disableConversionToGoogleType: true`);
  never ask Franco to edit a `.md` in Drive's editor.
- Stop at Pause 4. Steps 4 and 5 (scenes, publication) are the next session (Sonnet 5.5).
- S10 (live guard) and S11 (generation pipeline) run in parallel on this branch: `git fetch`
  and rebase before every push; keep both sides of `STATE.md` and `critique_log.jsonl`.
